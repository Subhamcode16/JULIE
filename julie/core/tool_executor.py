"""Execute classified intents for Julie."""

from typing import Any

try:
    from core.security import SecurityZone, check_command_security, is_path_blocked
    from core.router import ClassifiedIntent, IntentType
    from data.memory import upsert_memory, list_memories
    from tools.system_tools import (
        resolve_app_path,
        launch_application,
        run_terminal_command,
        list_directory,
        read_file,
        write_file,
    )
    from tools.browser_tools import google_search, scrape_url
    from tools.screen_tools import analyze_screen
    from tools.agent_handoff import handoff_to_antigravity
    from core.token_tracker import get_token_summary
except ImportError:
    from julie.core.security import SecurityZone, check_command_security, is_path_blocked
    from julie.core.router import ClassifiedIntent, IntentType
    from julie.data.memory import upsert_memory, list_memories
    from julie.tools.system_tools import (
        resolve_app_path,
        launch_application,
        run_terminal_command,
        list_directory,
        read_file,
        write_file,
    )
    from julie.tools.browser_tools import google_search, scrape_url
    from julie.tools.screen_tools import analyze_screen
    from julie.tools.agent_handoff import handoff_to_antigravity
    from julie.core.token_tracker import get_token_summary


def _security_check(intent: ClassifiedIntent, confirmed: bool) -> dict[str, Any] | None:
    """Return a blocking result when an intent is not allowed to execute."""
    # Assuming new check_command_security interface
    return check_command_security(intent, confirmed)


def _memory_key_from_fact(fact: str) -> str:
    """Create a stable, human-readable key for a remembered fact."""
    lowered = fact.strip().lower()
    for prefix in ("my ", "the "):
        if lowered.startswith(prefix):
            lowered = lowered[len(prefix):]
    if " is " in lowered:
        lowered = lowered.split(" is ", 1)[0]
    return "_".join(lowered.split())[:64] or "memory"


async def execute_intent(intent: ClassifiedIntent, db: Any = None, confirmed: bool = False) -> dict[str, Any]:
    """Execute or prepare execution for a classified intent."""
    security_result = _security_check(intent, confirmed=confirmed)
    if security_result:
        return security_result

    if intent.intent_type == IntentType.SYSTEM_ACTION:
        action = intent.params.get("action")
        target = intent.params.get("target")
        if action == "open" and target:
            app_path = resolve_app_path(target)
            if app_path:
                result = launch_application(app_path)
                return {
                    "success": result["success"],
                    "tool": "launch_application",
                    "detail": result,
                }
            return {
                "success": False,
                "error": f"Could not locate application '{target}'",
            }

        if action == "terminal" and target:
            result = run_terminal_command(target)
            return {
                "success": result["success"],
                "tool": "run_terminal_command",
                "detail": result,
            }

        if action == "list":
            path = intent.params.get("target") or "."
            result = list_directory(path)
            return {
                "success": result["success"],
                "tool": "list_directory",
                "detail": result,
            }

        if action == "read" and target:
            result = read_file(target)
            return {
                "success": result["success"],
                "tool": "read_file",
                "detail": result,
            }

        if action == "write" and target:
            result = write_file(target, intent.params.get("content", ""))
            return {
                "success": result["success"],
                "tool": "write_file",
                "detail": result,
            }

        return {
            "success": False,
            "error": "Unsupported system action",
        }

    if intent.intent_type == IntentType.BROWSER_ACTION:
        action = intent.params.get("action")
        target = intent.params.get("url_or_query")
        
        if action == "search" and target:
            result = await google_search(target)
            return {
                "success": result["success"],
                "tool": "google_search",
                "detail": result,
            }
        
        if action == "navigate" and target:
            result = await scrape_url(target)
            return {
                "success": result["success"],
                "tool": "scrape_url",
                "detail": result,
            }
            
        return {
            "success": False,
            "error": "Unsupported browser action",
        }

    if intent.intent_type == IntentType.SCREEN_ACTION:
        # e.g., action == "screenshot"
        prompt = intent.params.get("prompt", "What's on the screen?")
        result = await analyze_screen(prompt)
        return {
            "success": result["success"],
            "tool": "analyze_screen",
            "detail": result,
        }

    if intent.intent_type == IntentType.AGENT_HANDOFF:
        task = intent.params.get("task", intent.raw_input)
        result = handoff_to_antigravity(task)
        return {
            "success": result["success"],
            "tool": "agent_handoff",
            "detail": result,
        }

    if intent.intent_type == IntentType.INFORMATION:
        action = intent.params.get("action")
        if action == "token_summary":
            if db:
                summary = await get_token_summary(db)
                msg = f"Token Usage Summary:\nTotal Tokens: {summary['total']}\nPrompt: {summary['prompt']}\nCompletion: {summary['completion']}"
                return {"success": True, "tool": "token_summary", "detail": msg}
            return {"success": False, "error": "Database not available"}

    if intent.intent_type == IntentType.MEMORY:
        if db is None:
            return {
                "success": False,
                "error": "Memory actions require a database connection",
            }
        action = intent.params.get("action")
        if action == "save":
            fact = intent.params.get("fact", "").strip()
            if not fact:
                return {"success": False, "error": "No memory fact provided"}
            key = intent.params.get("key") or _memory_key_from_fact(fact)
            await upsert_memory(db, key=key, value=fact, source="user")
            return {
                "success": True,
                "tool": "save_memory",
                "detail": {"key": key, "value": fact},
            }
        if action == "list":
            memories = await list_memories(db)
            return {
                "success": True,
                "tool": "list_memories",
                "detail": {"memories": memories},
            }
        return {
            "success": False,
            "error": "Unsupported memory action",
        }

    if intent.intent_type == IntentType.SCHEDULE:
        return {
            "success": False,
            "error": "Scheduling is not implemented yet",
        }

    if intent.intent_type == IntentType.SCREEN_ACTION:
        return {
            "success": False,
            "error": "Screen actions are not implemented yet",
        }

    if intent.intent_type == IntentType.INFORMATION and intent.params.get("action") == "token_summary":
        if db is None:
            return {
                "success": False,
                "error": "Token summary requires a database connection",
            }
        summary = await get_token_summary(db)
        return {
            "success": True,
            "tool": "get_token_summary",
            "detail": summary,
        }

    return {
        "success": False,
        "error": "Intent requires LLM routing or has no direct execution path yet",
    }
