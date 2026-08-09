import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

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

def lookup_caller(user_id: str) -> Optional[Dict[str, Any]]:
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
            "last_interaction": row[4]
        }
    return None

def save_caller_info(user_id: str, name: str, language_preference: str, facts: Dict[str, Any]):
    """Inserts or updates the record and sets last_interaction to the current timestamp."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    timestamp = datetime.now().isoformat()
    facts_json = json.dumps(facts)
    
    cursor.execute("""
        INSERT INTO caller_records (user_id, name, language_preference, facts, last_interaction)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            name = excluded.name,
            language_preference = excluded.language_preference,
            facts = excluded.facts,
            last_interaction = excluded.last_interaction
    """, (user_id, name, language_preference, facts_json, timestamp))
    
    conn.commit()
    conn.close()
    logger.info(f"Saved caller info for {user_id}")

# Initialize on import
init_db()
