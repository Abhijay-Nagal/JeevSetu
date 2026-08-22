"""In-memory stand-in for the supabase-py Client, scoped to the query shapes
the services actually use. Not a general-purpose fake -- extend it if a new
service needs a query shape it doesn't support yet.
"""

import uuid
from datetime import datetime, timezone


class FakeResult:
    def __init__(self, data):
        self.data = data


class FakeTable:
    def __init__(self):
        self.rows: list[dict] = []
        self.default_row: dict = {}

    def new_row(self, values: dict) -> dict:
        row = {**self.default_row, **values}
        row.setdefault("id", str(uuid.uuid4()))
        row.setdefault("created_at", datetime.now(timezone.utc).isoformat())
        row.setdefault("updated_at", row["created_at"])
        # community_members' timestamp column is named joined_at, not created_at --
        # harmless to set on every table, Pydantic response models ignore extra keys.
        row.setdefault("joined_at", row["created_at"])
        self.rows.append(row)
        return row


class FakeQuery:
    def __init__(self, table: FakeTable):
        self._table = table
        self._filters: dict[str, object] = {}
        self._order_column: str | None = None
        self._order_desc = False
        self._pending_insert: dict | None = None
        self._pending_update: dict | None = None
        self._pending_delete = False
        self._is_null_columns: list[str] = []
        self._limit: int | None = None

    def insert(self, values: dict) -> "FakeQuery":
        self._pending_insert = values
        return self

    def update(self, values: dict) -> "FakeQuery":
        self._pending_update = values
        return self

    def delete(self) -> "FakeQuery":
        self._pending_delete = True
        return self

    def select(self, *_columns: str) -> "FakeQuery":
        return self

    def eq(self, column: str, value: object) -> "FakeQuery":
        self._filters[column] = value
        return self

    def is_(self, column: str, _value: str) -> "FakeQuery":
        self._is_null_columns.append(column)
        return self

    def limit(self, count: int) -> "FakeQuery":
        self._limit = count
        return self

    def order(self, column: str, desc: bool = False) -> "FakeQuery":
        self._order_column = column
        self._order_desc = desc
        return self

    def execute(self) -> FakeResult:
        if self._pending_insert is not None:
            row = self._table.new_row(self._pending_insert)
            return FakeResult([row])

        rows = list(self._table.rows)
        for column, value in self._filters.items():
            rows = [row for row in rows if row.get(column) == value]
        for column in self._is_null_columns:
            rows = [row for row in rows if row.get(column) is None]

        if self._pending_update is not None:
            for row in rows:
                row.update(self._pending_update)

        if self._pending_delete:
            self._table.rows = [row for row in self._table.rows if row not in rows]

        if self._order_column:
            rows = sorted(rows, key=lambda row: row[self._order_column], reverse=self._order_desc)

        if self._limit is not None:
            rows = rows[: self._limit]

        return FakeResult(rows)


class FakeRpc:
    """Only understands the RPCs this codebase actually calls -- extend the
    dispatch in execute() if a service starts calling a new one.
    """

    def __init__(self, client: "FakeSupabaseClient", name: str, params: dict):
        self._client = client
        self._name = name
        self._params = params

    def execute(self) -> FakeResult:
        if self._name == "award_coins":
            self._client._award_coins(**self._params)
            return FakeResult(None)
        raise NotImplementedError(f"FakeRpc does not implement '{self._name}'")


class FakeSupabaseClient:
    def __init__(self):
        self._tables: dict[str, FakeTable] = {}

    def set_defaults(self, table_name: str, defaults: dict) -> None:
        self._get_table(table_name).default_row = defaults

    def table(self, name: str) -> FakeQuery:
        return FakeQuery(self._get_table(name))

    def rpc(self, name: str, params: dict) -> FakeRpc:
        return FakeRpc(self, name, params)

    def _award_coins(
        self, p_user_id: str, p_amount: int, p_reason: str, p_reference_id: str | None = None
    ) -> None:
        self.table("coin_transactions").insert(
            {
                "user_id": p_user_id,
                "amount": p_amount,
                "reason": p_reason,
                "reference_id": p_reference_id,
            }
        ).execute()

        users_table = self._get_table("users")
        for row in users_table.rows:
            if row.get("id") == p_user_id:
                row["coin_balance"] = row.get("coin_balance", 0) + p_amount
                return

        # Real Postgres always has a users row for an authenticated caller
        # (the signup trigger creates it) -- test fixtures often use ad-hoc
        # ids like "user-1" without bothering to seed one, so self-heal here
        # instead of requiring every fixture to pre-create a users row.
        users_table.rows.append({"id": p_user_id, "coin_balance": p_amount})

    def _get_table(self, name: str) -> FakeTable:
        if name not in self._tables:
            self._tables[name] = FakeTable()
        return self._tables[name]
