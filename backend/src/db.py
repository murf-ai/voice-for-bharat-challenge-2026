import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Define the database file path within the backend/src directory
DB_PATH = Path(__file__).parent / "agent_memory.db"

logger = logging.getLogger("db")


def init_db():
    """Initializes the database and creates the caller_records table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS caller_records (
            user_id TEXT PRIMARY KEY,
            name TEXT,
            language_preference TEXT,
            facts TEXT,
            last_interaction TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    logger.info("Database initialized.")


def lookup_caller(user_id: str) -> Optional[dict[str, Any]]:
    """Returns the saved record as a dict if it exists, else None."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM caller_records WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "user_id": row[0],
            "name": row[1],
            "language_preference": row[2],
            "facts": json.loads(row[3]),
            "last_interaction": row[4],
        }
    return None


def save_caller_info(
    user_id: str, name: str, language_preference: str, facts: dict[str, Any]
):
    """Inserts or updates the record and sets last_interaction to the current timestamp."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    timestamp = datetime.now().isoformat()
    facts_json = json.dumps(facts)

    cursor.execute(
        """
        INSERT INTO caller_records (user_id, name, language_preference, facts, last_interaction)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            name = excluded.name,
            language_preference = excluded.language_preference,
            facts = excluded.facts,
            last_interaction = excluded.last_interaction
    """,
        (user_id, name, language_preference, facts_json, timestamp),
    )

    conn.commit()
    conn.close()
    logger.info(f"Saved caller info for {user_id}")


def init_orders_db():
    """Initializes the database and creates the orders table if it doesn't exist."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                item TEXT,
                quantity TEXT,
                price TEXT,
                timestamp TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
        logger.info("Orders database initialized.")
    except Exception as e:
        logger.error(f"Error initializing orders database: {e}")
        raise

def save_order(user_id: str, item: str, quantity: str, price: str):
    """Inserts a new order into the orders table."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        timestamp = datetime.now().isoformat()
        cursor.execute(
            """
            INSERT INTO orders (user_id, item, quantity, price, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """,
            (user_id, item, quantity, price, timestamp),
        )
        conn.commit()
        conn.close()
        logger.info(f"Saved order for {user_id}: {item} x {quantity}")
    except Exception as e:
        logger.error(f"Error saving order for {user_id}: {e}")
        raise


def create_call_record(call_sid: str, channel: str):
    """Inserts a new call record with outcome='in_progress' and started_at=now."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    started_at = datetime.now().isoformat()
    cursor.execute(
        """
        INSERT INTO calls (call_sid, channel, started_at, outcome)
        VALUES (?, ?, ?, ?)
    """,
        (call_sid, channel, started_at, "in_progress"),
    )
    conn.commit()
    conn.close()
    logger.info(f"Created call record for {call_sid} on {channel}")


def update_call_outcome(
    call_sid: str, outcome: str, failure_reason: Optional[str] = None
):
    """Updates the call record: sets outcome, failure_reason, ended_at=now, and calculates duration_seconds."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Retrieve the latest in_progress call record with this call_sid
    cursor.execute(
        """
        SELECT id, started_at FROM calls
        WHERE call_sid = ? AND outcome = 'in_progress'
        ORDER BY id DESC LIMIT 1
    """,
        (call_sid,),
    )
    row = cursor.fetchone()

    if not row:
        # Fall back to the latest record regardless of outcome if none are in_progress
        cursor.execute(
            """
            SELECT id, started_at FROM calls
            WHERE call_sid = ?
            ORDER BY id DESC LIMIT 1
        """,
            (call_sid,),
        )
        row = cursor.fetchone()

    if not row:
        conn.close()
        logger.warning(f"No call record found for call_sid {call_sid}")
        return

    call_id, started_at_str = row
    ended_at = datetime.now()
    ended_at_str = ended_at.isoformat()

    duration_seconds = None
    try:
        started_at = datetime.fromisoformat(started_at_str)
        duration_seconds = int((ended_at - started_at).total_seconds())
    except Exception as e:
        logger.error(f"Error calculating call duration for {call_sid}: {e}")

    cursor.execute(
        """
        UPDATE calls
        SET outcome = ?,
            failure_reason = ?,
            ended_at = ?,
            duration_seconds = ?
        WHERE id = ?
    """,
        (outcome, failure_reason, ended_at_str, duration_seconds, call_id),
    )

    conn.commit()
    conn.close()
    logger.info(f"Updated call outcome for {call_sid} to {outcome}")


def get_call_stats() -> dict[str, int]:
    """Returns a dict with total_calls, successful_calls, failed_calls counts."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            COUNT(*),
            SUM(CASE WHEN outcome = 'success' THEN 1 ELSE 0 END),
            SUM(CASE WHEN outcome = 'failed' THEN 1 ELSE 0 END)
        FROM calls
    """)
    row = cursor.fetchone()
    conn.close()

    total_calls = row[0] if row else 0
    successful_calls = row[1] if row and row[1] is not None else 0
    failed_calls = row[2] if row and row[2] is not None else 0

    return {
        "total_calls": total_calls,
        "successful_calls": successful_calls,
        "failed_calls": failed_calls,
    }


def init_calls_db():
    """Initializes the database and creates the calls table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            call_sid TEXT,
            channel TEXT,
            started_at TIMESTAMP,
            ended_at TIMESTAMP,
            outcome TEXT,
            failure_reason TEXT,
            duration_seconds INTEGER
        )
    """)
    conn.commit()
    conn.close()
    logger.info("Calls database initialized.")


init_db()
# init_orders_db()
init_calls_db()
