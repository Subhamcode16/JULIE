"""SQLite database schema and initialization."""

import aiosqlite
from pathlib import Path


SCHEMA = """
-- Conversation history
CREATE TABLE IF NOT EXISTS conversations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  TEXT NOT NULL,
    role        TEXT NOT NULL,
    content     TEXT NOT NULL,
    intent_type TEXT,
    tokens_used INTEGER DEFAULT 0,
    timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Long-term memory (user-tagged facts)
CREATE TABLE IF NOT EXISTS memories (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    key         TEXT UNIQUE NOT NULL,
    value       TEXT NOT NULL,
    source      TEXT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Token usage log
CREATE TABLE IF NOT EXISTS token_usage (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    model       TEXT NOT NULL,
    provider    TEXT NOT NULL,
    intent_type TEXT,
    tokens_in   INTEGER NOT NULL,
    tokens_out  INTEGER NOT NULL,
    latency_ms  INTEGER,
    timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Scheduled tasks
CREATE TABLE IF NOT EXISTS scheduled_tasks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    cron_expr   TEXT NOT NULL,
    action      TEXT NOT NULL,
    enabled     BOOLEAN DEFAULT TRUE,
    last_run    DATETIME,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- App shortcuts learned
CREATE TABLE IF NOT EXISTS learned_shortcuts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    trigger     TEXT UNIQUE NOT NULL,
    resolved_to TEXT NOT NULL,
    use_count   INTEGER DEFAULT 1,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for fast lookups
CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp);
CREATE INDEX IF NOT EXISTS idx_memories_key ON memories(key);
CREATE INDEX IF NOT EXISTS idx_token_usage_timestamp ON token_usage(timestamp);
CREATE INDEX IF NOT EXISTS idx_scheduled_tasks_enabled ON scheduled_tasks(enabled);
"""


async def init_db(db_path: Path) -> aiosqlite.Connection:
    """Initialize database and create schema."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    db = await aiosqlite.connect(str(db_path))
    await db.executescript(SCHEMA)
    await db.commit()
    return db


async def close_db(db: aiosqlite.Connection) -> None:
    """Close database connection."""
    await db.close()
