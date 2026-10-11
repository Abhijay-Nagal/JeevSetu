import pytest

from app.core.local_store import LocalStore, StoreError


@pytest.fixture
def store() -> LocalStore:
    return LocalStore(":memory:")


def test_insert_applies_table_defaults_and_timestamps(store):
    row = (
        store.table("observations").insert({"user_id": "u1", "species": "Tiger"}).execute().data[0]
    )

    assert row["status"] == "submitted"
    assert row["like_count"] == 0
    assert row["community_id"] is None
    assert row["id"] and row["created_at"] and row["updated_at"]


def test_filters_order_and_limit(store):
    for name, age in [("a", 3), ("b", 1), ("c", 2)]:
        store.table("things").insert(
            {"name": name, "age": age, "group": None if name == "c" else "x"}
        ).execute()

    ordered = store.table("things").select("name").order("age", desc=True).execute().data
    assert [row["name"] for row in ordered] == ["a", "c", "b"]
    assert store.table("things").select("*").eq("name", "b").execute().data[0]["age"] == 1
    assert [
        r["name"] for r in store.table("things").select("*").is_("group", "null").execute().data
    ] == ["c"]
    assert len(store.table("things").select("*").in_("name", ["a", "b"]).execute().data) == 2
    assert len(store.table("things").select("*").order("age").limit(2).execute().data) == 2
    assert store.table("things").select("*", count="exact").gte("age", 2).execute().count == 2


def test_select_projects_columns(store):
    store.table("users").insert({"id": "u1", "name": "Asha", "email": "a@example.com"}).execute()

    row = store.table("users").select("id, name").eq("id", "u1").execute().data[0]

    assert row == {"id": "u1", "name": "Asha"}


def test_update_and_delete(store):
    store.table("things").insert({"id": "t1", "n": 1}).execute()
    store.table("things").insert({"id": "t2", "n": 2}).execute()

    updated = store.table("things").update({"n": 10}).eq("id", "t1").execute().data
    store.table("things").delete().eq("id", "t2").execute()

    assert updated[0]["n"] == 10
    assert [row["id"] for row in store.table("things").select("*").execute().data] == ["t1"]


def test_composite_primary_key_rejects_duplicates(store):
    store.table("observation_likes").insert({"observation_id": "o1", "user_id": "u1"}).execute()

    with pytest.raises(StoreError):
        store.table("observation_likes").insert({"observation_id": "o1", "user_id": "u1"}).execute()


def test_upsert_updates_existing_row(store):
    store.table("documents").upsert(
        {"source_type": "blog", "external_id": 1, "title": "Old"},
        on_conflict="source_type,external_id",
    ).execute()
    store.table("documents").upsert(
        {"source_type": "blog", "external_id": 1, "title": "New"},
        on_conflict="source_type,external_id",
    ).execute()

    rows = store.table("documents").select("*").execute().data
    assert [row["title"] for row in rows] == ["New"]


def test_award_coins_rpc_updates_ledger_and_balance(store):
    store.table("users").insert({"id": "u1"}).execute()

    store.rpc("award_coins", {"p_user_id": "u1", "p_amount": 25, "p_reason": "test"}).execute()
    store.rpc("award_coins", {"p_user_id": "u1", "p_amount": -5, "p_reason": "spend"}).execute()

    assert store.table("users").select("*").eq("id", "u1").execute().data[0]["coin_balance"] == 20
    assert len(store.table("coin_transactions").select("*").eq("user_id", "u1").execute().data) == 2


def test_data_persists_across_connections(tmp_path):
    path = tmp_path / "store.db"
    LocalStore(path).table("users").insert({"id": "u1", "name": "Persisted"}).execute()

    reopened = LocalStore(path)

    assert (
        reopened.table("users").select("*").eq("id", "u1").execute().data[0]["name"] == "Persisted"
    )
