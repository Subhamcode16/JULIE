"""Memory engine for Julie.

Provides async helpers for storing and retrieving conversation turns
and long-term memories from the SQLite database.
"""

import re
import os
import yaml
from datetime import datetime
from typing import Any, List, Dict, Optional
import aiosqlite

OBSIDIAN_VAULT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "obsidian_vault")


def format_turns(turns: List[Dict[str, Any]]) -> str:
    """Format conversation turns into a readable summary."""
    lines = []
    for turn in turns:
        role = turn.get("role", "user")
        content = turn.get("content", "")
        lines.append(f"{role}: {content}")
    return "\n".join(lines)


def extractive_summarize(turns: List[Dict[str, Any]]) -> str:
    """Summarize older turns using extractive first sentences."""
    sentences: List[str] = []
    for turn in turns:
        content = turn.get("content", "")
        match = re.search(r"([^.?!]+[.?!])", content.strip())
        if match:
            sentences.append(match.group(1).strip())
        elif content:
            sentences.append(content.strip())
    return " ".join(sentences)


def compress_history(turns: List[Dict[str, Any]]) -> str:
    """Compress conversation history for context assembly."""
    if len(turns) <= 4:
        return format_turns(turns)

    recent = turns[-4:]
    older = turns[:-4]
    summary = extractive_summarize(older)
    return f"[Earlier: {summary}]\n\n{format_turns(recent)}"


# Async DB helpers
async def save_conversation_turn(db: aiosqlite.Connection, session_id: str, role: str, content: str, intent_type: Optional[str] = None, tokens_used: int = 0) -> None:
    """Insert a conversation turn into the conversations table."""
    await db.execute(
        """
        INSERT INTO conversations (session_id, role, content, intent_type, tokens_used)
        VALUES (?, ?, ?, ?, ?)
        """,
        (session_id, role, content, intent_type, tokens_used),
    )
    await db.commit()


async def get_recent_turns(db: aiosqlite.Connection, session_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """Return the most recent conversation turns for a session as dicts."""
    cursor = await db.execute(
        "SELECT id, session_id, role, content, intent_type, tokens_used, timestamp FROM conversations WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
        (session_id, limit),
    )
    rows = await cursor.fetchall()
    await cursor.close()
    # rows are tuples; map to dict
    keys = ["id", "session_id", "role", "content", "intent_type", "tokens_used", "timestamp"]
    return [dict(zip(keys, row)) for row in rows][::-1]  # return oldest->newest


async def upsert_memory(db: aiosqlite.Connection, key: str, value: str, source: str = "user") -> None:
    """Insert or update a memory keyed by 'key' and sync to Obsidian Vault."""
    await db.execute(
        """
        INSERT INTO memories (key, value, source)
        VALUES (?, ?, ?)
        ON CONFLICT(key) DO UPDATE SET
            value = excluded.value,
            source = excluded.source,
            updated_at = CURRENT_TIMESTAMP
        """,
        (key, value, source),
    )
    await db.commit()

    # Sync to Obsidian vault
    if not os.path.exists(OBSIDIAN_VAULT_DIR):
        os.makedirs(OBSIDIAN_VAULT_DIR, exist_ok=True)
    
    safe_filename = "".join([c for c in key if c.isalpha() or c.isdigit() or c == ' ']).rstrip()
    if not safe_filename:
        safe_filename = f"memory_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    file_path = os.path.join(OBSIDIAN_VAULT_DIR, f"{safe_filename.replace(' ', '_')}.md")
    
    frontmatter = {
        "tags": ["julie-memory", source],
        "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "key": key
    }
    
    content = f"---\n{yaml.dump(frontmatter)}---\n\n# {key}\n\n{value}\n"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


async def get_relevant_memories(db: aiosqlite.Connection, user_input: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Return up to `limit` memories that match the user_input using TurboQuant Vector Search."""
    try:
        from brain.turboquant_indexer import search_memory
    except ImportError:
        from julie.brain.turboquant_indexer import search_memory
        
    results = search_memory(user_input, top_k=limit)
    
    # Format the results to match what the old SQLite code returned
    formatted = []
    for score, meta in results:
        # Extract the key/title from the first line or file name
        key = meta.get("file", "memory").replace(".md", "")
        # The content has frontmatter, so let's just return the raw markdown for now
        formatted.append({
            "key": key,
            "value": meta.get("content", ""),
            "score": float(score)
        })
        
    return formatted


async def list_memories(db: aiosqlite.Connection, limit: int = 100) -> List[Dict[str, Any]]:
    """Return a list of stored memories."""
    cursor = await db.execute("SELECT key, value, source, created_at, updated_at FROM memories ORDER BY updated_at DESC LIMIT ?", (limit,))
    rows = await cursor.fetchall()
    await cursor.close()
    keys = ["key", "value", "source", "created_at", "updated_at"]
    return [dict(zip(keys, row)) for row in rows]
