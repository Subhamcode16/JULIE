"""Agent handoff utilities for Julie."""

from typing import Any


def handoff_to_agent(agent_name: str, task_description: str, context_path: str) -> dict[str, Any]:
    return {
        "success": False,
        "error": "Agent handoff is not implemented yet",
    }
