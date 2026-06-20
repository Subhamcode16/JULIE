"""Token tracking utilities."""

from typing import Any

import aiosqlite


async def log_token_usage(
    db: aiosqlite.Connection,
    *,
    model: str,
    provider: str,
    intent_type: str,
    tokens_in: int,
    tokens_out: int,
    latency_ms: int,
) -> dict[str, Any]:
    """Persist one LLM usage event."""
    await db.execute(
        """
        INSERT INTO token_usage (model, provider, intent_type, tokens_in, tokens_out, latency_ms)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (model, provider, intent_type, tokens_in, tokens_out, latency_ms),
    )
    await db.commit()
    return {"success": True}


async def get_token_summary(db: aiosqlite.Connection, period: str = "today") -> dict[str, Any]:
    """Return token usage totals for today or all time."""
    if period == "today":
        where_clause = "WHERE date(timestamp) = date('now', 'localtime')"
    else:
        where_clause = ""

    cursor = await db.execute(
        f"""
        SELECT
            provider,
            COUNT(*) AS calls,
            COALESCE(SUM(tokens_in), 0) AS tokens_in,
            COALESCE(SUM(tokens_out), 0) AS tokens_out,
            COALESCE(AVG(latency_ms), 0) AS avg_latency_ms
        FROM token_usage
        {where_clause}
        GROUP BY provider
        """
    )
    rows = await cursor.fetchall()
    await cursor.close()

    providers = {
        row[0]: {
            "calls": row[1],
            "tokens_in": row[2],
            "tokens_out": row[3],
            "avg_latency_ms": int(row[4] or 0),
        }
        for row in rows
    }

    cursor = await db.execute(
        """
        SELECT
            COUNT(*) AS total_inputs,
            SUM(CASE WHEN tokens_used = 0 THEN 1 ELSE 0 END) AS llm_calls_avoided
        FROM conversations
        WHERE role = 'user'
        """
    )
    stats = await cursor.fetchone()
    await cursor.close()

    total_inputs = stats[0] or 0
    llm_calls_avoided = stats[1] or 0
    efficiency_pct = int((llm_calls_avoided / total_inputs) * 100) if total_inputs else 0

    return {
        "success": True,
        "period": period,
        "providers": providers,
        "total_calls": sum(item["calls"] for item in providers.values()),
        "tokens_in": sum(item["tokens_in"] for item in providers.values()),
        "tokens_out": sum(item["tokens_out"] for item in providers.values()),
        "llm_calls_avoided": llm_calls_avoided,
        "efficiency_pct": efficiency_pct,
    }
