"""Self-contained, SQLite-backed stand-in for the supabase-py Client.

The services were written against Supabase's query builder
(`table(...).select(...).eq(...).execute()`). This module implements that same
surface over a local SQLite file so the whole app runs with no external
database -- the services don't know which one they're talking to.

Rows are stored as JSON documents (one SQLite row per record), and filtering
happens in Python. That's deliberately simple: the community/reward tables are
small, and the large read-only corpus (the Knowledge Hub) is searched by
app.services.knowledge_base, not through here.
"""

from __future__ import annotations

import json
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Mirrors the column defaults in supabase/migrations, so a row inserted here
# has the same shape it would have coming back from Postgres.
TABLE_DEFAULTS: dict[str, dict[str, Any]] = {
    "users": {"role": "contributor", "coin_balance": 0, "email": None, "name": None},
    "observations": {
        "status": "submitted",
        "assigned_researcher": None,
        "community_id": None,
        "like_count": 0,
        "species": None,
        "description": None,
        "location": None,
        "media_url": None,
    },
    "community_members": {"role": "member"},
    "user_streaks": {
        "current_streak": 0,
        "longest_streak": 0,
        "last_answered_date": None,
        "freezes_available": 0,
        "freezes_used_total": 0,
    },
    "email_confirmations": {"confirmed_at": None},
}

# Extra timestamp columns some tables use in place of / alongside created_at.
EXTRA_TIMESTAMPS: dict[str, tuple[str, ...]] = {
    "community_members": ("joined_at",),
    "daily_question_attempts": ("answered_at",),
    "observations": ("updated_at",),
    "user_streaks": ("updated_at",),
}

# Tables whose primary key is not `id`.
PRIMARY_KEYS: dict[str, tuple[str, ...]] = {
    "user_streaks": ("user_id",),
    "community_members": ("community_id", "user_id"),
    "observation_likes": ("observation_id", "user_id"),
    "user_cards": ("user_id", "card_id"),
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class StoreError(Exception):
    """Raised for constraint violations, mirroring a PostgREST APIError."""


class LocalResult:
    def __init__(self, data: Any, count: int | None = None):
        self.data = data
        self.count = count


class LocalQuery:
    def __init__(self, store: "LocalStore", table: str):
        self._store = store
        self._table = table
        self._columns: list[str] | None = None
        self._count = False
        self._filters: list[tuple[str, str, Any]] = []
        self._orders: list[tuple[str, bool]] = []
        self._limit: int | None = None
        self._offset = 0
        self._action = "select"
        self._payload: Any = None
        self._on_conflict: list[str] | None = None

    # -- actions ---------------------------------------------------------
    def select(self, columns: str = "*", count: str | None = None) -> "LocalQuery":
        if columns.strip() != "*":
            self._columns = [column.strip() for column in columns.split(",") if column.strip()]
        self._count = count is not None
        return self

    def insert(self, values: dict | list[dict]) -> "LocalQuery":
        self._action, self._payload = "insert", values
        return self

    def upsert(self, values: dict | list[dict], on_conflict: str | None = None) -> "LocalQuery":
        self._action, self._payload = "upsert", values
        if on_conflict:
            self._on_conflict = [column.strip() for column in on_conflict.split(",")]
        return self

    def update(self, values: dict) -> "LocalQuery":
        self._action, self._payload = "update", values
        return self

    def delete(self) -> "LocalQuery":
        self._action = "delete"
        return self

    # -- filters ---------------------------------------------------------
    def eq(self, column: str, value: Any) -> "LocalQuery":
        self._filters.append(("eq", column, value))
        return self

    def neq(self, column: str, value: Any) -> "LocalQuery":
        self._filters.append(("neq", column, value))
        return self

    def gt(self, column: str, value: Any) -> "LocalQuery":
        self._filters.append(("gt", column, value))
        return self

    def gte(self, column: str, value: Any) -> "LocalQuery":
        self._filters.append(("gte", column, value))
        return self

    def lt(self, column: str, value: Any) -> "LocalQuery":
        self._filters.append(("lt", column, value))
        return self

    def lte(self, column: str, value: Any) -> "LocalQuery":
        self._filters.append(("lte", column, value))
        return self

    def ilike(self, column: str, pattern: str) -> "LocalQuery":
        self._filters.append(("ilike", column, pattern))
        return self

    def is_(self, column: str, value: Any) -> "LocalQuery":
        self._filters.append(("is", column, value))
        return self

    def in_(self, column: str, values: list) -> "LocalQuery":
        self._filters.append(("in", column, set(values)))
        return self

    # -- modifiers -------------------------------------------------------
    def order(self, column: str, desc: bool = False) -> "LocalQuery":
        self._orders.append((column, desc))
        return self

    def limit(self, count: int) -> "LocalQuery":
        self._limit = count
        return self

    def range(self, start: int, end: int) -> "LocalQuery":
        self._offset, self._limit = start, end - start + 1
        return self

    # -- execution -------------------------------------------------------
    def _matches(self, row: dict) -> bool:
        for op, column, value in self._filters:
            actual = row.get(column)
            if op == "eq" and actual != value:
                return False
            if op == "neq" and actual == value:
                return False
            if op == "is" and not (
                (value in (None, "null") and actual is None)
                or (value not in (None, "null") and actual == value)
            ):
                return False
            if op == "in" and actual not in value:
                return False
            if op in ("gt", "gte", "lt", "lte"):
                if actual is None:
                    return False
                if op == "gt" and not actual > value:
                    return False
                if op == "gte" and not actual >= value:
                    return False
                if op == "lt" and not actual < value:
                    return False
                if op == "lte" and not actual <= value:
                    return False
            if op == "ilike":
                needle = str(value).lower().strip("%")
                if actual is None or needle not in str(actual).lower():
                    return False
        return True

    def _project(self, row: dict) -> dict:
        if self._columns is None:
            return row
        return {column: row.get(column) for column in self._columns}

    def execute(self) -> LocalResult:
        with self._store.lock:
            if self._action in ("insert", "upsert"):
                rows = self._payload if isinstance(self._payload, list) else [self._payload]
                written = [
                    self._store.write_new(
                        self._table,
                        row,
                        upsert=self._action == "upsert",
                        on_conflict=self._on_conflict,
                    )
                    for row in rows
                ]
                self._store.commit()
                return LocalResult([self._project(row) for row in written])

            rows = [row for row in self._store.read_all(self._table) if self._matches(row)]

            if self._action == "update":
                for row in rows:
                    row.update(self._payload)
                    if "updated_at" in row and "updated_at" not in self._payload:
                        row["updated_at"] = _now()
                    self._store.write_existing(self._table, row)
                self._store.commit()
            elif self._action == "delete":
                for row in rows:
                    self._store.remove(self._table, row)
                self._store.commit()

        for column, desc in reversed(self._orders):
            rows.sort(key=lambda row: (row.get(column) is None, row.get(column)), reverse=desc)

        total = len(rows)
        if self._offset:
            rows = rows[self._offset :]
        if self._limit is not None:
            rows = rows[: self._limit]
        return LocalResult(
            [self._project(row) for row in rows], count=total if self._count else None
        )


class LocalRpc:
    def __init__(self, store: "LocalStore", name: str, params: dict):
        self._store = store
        self._name = name
        self._params = params

    def execute(self) -> LocalResult:
        handler = getattr(self._store, f"_rpc_{self._name}", None)
        if handler is None:
            raise StoreError(f"Unknown RPC '{self._name}'")
        return LocalResult(handler(**self._params))


class LocalStore:
    """supabase-py compatible client persisted to a single SQLite file."""

    def __init__(self, path: str | Path = ":memory:"):
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        # The FastAPI app runs sync work in a threadpool; one connection
        # guarded by a re-entrant lock keeps writes serialised.
        self._conn = sqlite3.connect(self.path, check_same_thread=False)
        self._conn.execute("pragma journal_mode=wal")
        self._conn.execute(
            "create table if not exists records ("
            " tbl text not null, pk text not null, data text not null,"
            " primary key (tbl, pk))"
        )
        self._conn.commit()
        self.lock = threading.RLock()

    # -- supabase-py surface ---------------------------------------------
    def table(self, name: str) -> LocalQuery:
        return LocalQuery(self, name)

    def rpc(self, name: str, params: dict | None = None) -> LocalRpc:
        return LocalRpc(self, name, params or {})

    # -- storage primitives ----------------------------------------------
    def _pk(self, table: str, row: dict, columns: list[str] | None = None) -> str:
        key_columns = columns or PRIMARY_KEYS.get(table, ("id",))
        return "|".join(str(row.get(column)) for column in key_columns)

    def read_all(self, table: str) -> list[dict]:
        cursor = self._conn.execute("select data from records where tbl = ?", (table,))
        return [json.loads(data) for (data,) in cursor.fetchall()]

    def write_new(
        self, table: str, values: dict, upsert: bool = False, on_conflict: list[str] | None = None
    ) -> dict:
        if upsert:
            conflict_columns = on_conflict or list(PRIMARY_KEYS.get(table, ("id",)))
            for existing in self.read_all(table):
                if all(existing.get(column) == values.get(column) for column in conflict_columns):
                    existing.update(values)
                    self.write_existing(table, existing)
                    return existing

        now = _now()
        row = {**TABLE_DEFAULTS.get(table, {}), **values}
        row.setdefault("id", str(uuid.uuid4()))
        row.setdefault("created_at", now)
        for column in EXTRA_TIMESTAMPS.get(table, ()):
            row.setdefault(column, now)

        pk = self._pk(table, row)
        try:
            self._conn.execute(
                "insert into records (tbl, pk, data) values (?, ?, ?)", (table, pk, json.dumps(row))
            )
        except sqlite3.IntegrityError as exc:
            raise StoreError(f"duplicate key value violates unique constraint on {table}") from exc
        return row

    def write_existing(self, table: str, row: dict) -> None:
        self._conn.execute(
            "update records set data = ? where tbl = ? and pk = ?",
            (json.dumps(row), table, self._pk(table, row)),
        )

    def remove(self, table: str, row: dict) -> None:
        self._conn.execute(
            "delete from records where tbl = ? and pk = ?", (table, self._pk(table, row))
        )

    def commit(self) -> None:
        self._conn.commit()

    def is_empty(self, table: str) -> bool:
        cursor = self._conn.execute("select 1 from records where tbl = ? limit 1", (table,))
        return cursor.fetchone() is None

    # -- RPCs (Postgres functions in supabase/migrations) -----------------
    def _rpc_award_coins(
        self, p_user_id: str, p_amount: int, p_reason: str, p_reference_id: str | None = None
    ) -> None:
        """Ledger entry + balance update in one locked transaction, like the
        award_coins plpgsql function."""
        with self.lock:
            self.write_new(
                "coin_transactions",
                {
                    "user_id": p_user_id,
                    "amount": p_amount,
                    "reason": p_reason,
                    "reference_id": p_reference_id,
                },
            )
            for user in self.read_all("users"):
                if user["id"] == p_user_id:
                    user["coin_balance"] = (user.get("coin_balance") or 0) + p_amount
                    self.write_existing("users", user)
                    break
            self.commit()
        return None
