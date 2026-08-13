import sqlite3

import pytest

from db import (
    DB_PATH,
    create_call_record,
    get_call_stats,
    update_call_outcome,
    save_order,
)


@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Ensure a clean state for testing calls and orders table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Back up existing call stats / count if needed, or simply clean up test-inserted records
    # For maximum safety, we will delete only our specific test SIDs and orders
    cursor.execute("DELETE FROM calls WHERE call_sid LIKE 'test_call_%'")
    cursor.execute("DELETE FROM orders WHERE user_id LIKE 'test_user_%'")
    conn.commit()
    conn.close()

    yield

    # Clean up again after test runs
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM calls WHERE call_sid LIKE 'test_call_%'")
    cursor.execute("DELETE FROM orders WHERE user_id LIKE 'test_user_%'")
    conn.commit()
    conn.close()

# ... existing tests ...

def test_save_order():
    user_id = "test_user_1"
    item = "Rice"
    quantity = "5kg"
    price = "500"

    save_order(user_id, item, quantity, price)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT user_id, item, quantity, price FROM orders WHERE user_id = ?",
        (user_id,),
    )
    row = cursor.fetchone()
    conn.close()

    assert row is not None
    assert row[0] == user_id
    assert row[1] == item
    assert row[2] == quantity
    assert row[3] == price


def test_create_and_update_call_record():
    call_sid = "test_call_abc123"
    channel = "sip"

    # 1. Create a record
    create_call_record(call_sid, channel)

    # Verify insertion
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT call_sid, channel, outcome, started_at, ended_at, duration_seconds FROM calls WHERE call_sid = ?",
        (call_sid,),
    )
    row = cursor.fetchone()
    conn.close()

    assert row is not None
    assert row[0] == call_sid
    assert row[1] == channel
    assert row[2] == "in_progress"
    assert row[3] is not None  # started_at
    assert row[4] is None  # ended_at
    assert row[5] is None  # duration_seconds

    # 2. Update record outcome to success
    update_call_outcome(call_sid, "success")

    # Verify update
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT outcome, ended_at, duration_seconds, failure_reason FROM calls WHERE call_sid = ?",
        (call_sid,),
    )
    row = cursor.fetchone()
    conn.close()

    assert row is not None
    assert row[0] == "success"
    assert row[1] is not None  # ended_at
    assert row[2] is not None  # duration_seconds should be calculated
    assert row[3] is None  # failure_reason

    # 3. Create another call and update to failed with failure_reason
    fail_sid = "test_call_fail789"
    create_call_record(fail_sid, "browser")
    update_call_outcome(fail_sid, "failed", failure_reason="connection timeout")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT outcome, failure_reason FROM calls WHERE call_sid = ?", (fail_sid,)
    )
    row = cursor.fetchone()
    conn.close()

    assert row is not None
    assert row[0] == "failed"
    assert row[1] == "connection timeout"


def test_get_call_stats():
    # Record initial stats to handle existing DB entries
    initial_stats = get_call_stats()

    # Create and update temporary test calls
    create_call_record("test_call_s1", "browser")
    update_call_outcome("test_call_s1", "success")

    create_call_record("test_call_f1", "sip")
    update_call_outcome("test_call_f1", "failed", "user busy")

    create_call_record("test_call_ip1", "browser")  # keeps in_progress

    new_stats = get_call_stats()

    assert new_stats["total_calls"] == initial_stats["total_calls"] + 3
    assert new_stats["successful_calls"] == initial_stats["successful_calls"] + 1
    assert new_stats["failed_calls"] == initial_stats["failed_calls"] + 1
