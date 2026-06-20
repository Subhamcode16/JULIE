"""Security zone classifier and guardrails."""

import re
from enum import Enum
from pathlib import Path
from typing import Optional


class SecurityZone(Enum):
    """Action security zone."""
    GREEN = "green"   # Execute immediately
    YELLOW = "yellow"  # Show confirmation, 5s timeout
    RED = "red"       # Hard block, requires unlock


GREEN_ACTIONS = {
    "open_application",
    "take_screenshot",
    "read_file",
    "navigate_browser",
    "search_web",
    "get_current_time",
    "list_directory",
    "view_clipboard",
}

YELLOW_ACTIONS = {
    "write_file",
    "delete_file",
    "run_terminal_command",
    "fill_web_form",
    "click_element",
    "download_file",
    "send_telegram_message",
    "modify_memory",
    "create_schedule",
}

RED_ACTIONS = {
    "modify_registry",
    "access_system32",
    "modify_program_files",
    "run_as_admin",
    "modify_hosts_file",
    "access_ssh_keys",
    "modify_env_variables",
    "kill_process",
    "format_drive",
    "uninstall_app",
}


BLOCKED_PATHS = [
    r"C:\\Windows\\System32",
    r"C:\\Windows\\SysWOW64",
    r"C:\\Program Files",
    r"C:\\Program Files \(x86\)",
    r"~\\.ssh",
    r"~\\.aws",
    r"HKEY_LOCAL_MACHINE",
    r"HKEY_CURRENT_USER\\Software\\Microsoft",
]

INJECTION_PATTERNS = [
    r"ignore\s+(?:previous|above|all)\s+instructions",
    r"you\s+are\s+now",
    r"new\s+system\s+prompt",
    r"disregard",
    r"DAN\s+mode",
    r"jailbreak",
    r"forget\s+everything",
    r"prompt\s+injection",
    r"code\s+injection",
]


def classify_zone(action_name: str) -> SecurityZone:
    """Classify action into security zone.

    Normalizes action names so callers may pass values like "write_file_action" or
    "write_file" interchangeably.
    """
    name = action_name.lower()
    if name.endswith("_action"):
        name = name[: -len("_action")]

    # Map common verb forms (e.g., "write" -> "write_file") if obvious
    if name == "write":
        name = "write_file"
    if name == "modify_registry":
        name = "modify_registry"

    if name in RED_ACTIONS:
        return SecurityZone.RED
    elif name in YELLOW_ACTIONS:
        return SecurityZone.YELLOW
    else:
        return SecurityZone.GREEN


def is_path_blocked(path: str) -> bool:
    """Check if path is in blocked registry."""
    expanded = str(Path(path).expanduser())
    path_normalized = expanded.upper()
    
    for blocked in BLOCKED_PATHS:
        blocked_path = str(Path(blocked).expanduser()) if not blocked.startswith("HKEY_") else blocked
        pattern = blocked_path.replace("\\", "\\\\")
        if re.match(f"^{pattern}", path_normalized, re.IGNORECASE):
            return True
    
    return False


def action_name_for_params(intent_type: str, params: dict) -> str:
    """Return the concrete security action name for a classified intent."""
    if intent_type == "system_action":
        action = (params or {}).get("action", "").lower()
        if action == "open":
            return "open_application"
        if action == "terminal":
            return "run_terminal_command"
        if action == "list":
            return "list_directory"
        if action == "read":
            return "read_file"
        if action == "write":
            return "write_file"
        if action == "delete":
            return "delete_file"
        if action:
            return action
    if intent_type == "browser_action":
        action = (params or {}).get("action", "").lower()
        if action == "navigate":
            return "navigate_browser"
        if action == "search":
            return "search_web"
        return action or "browser_action"
    if intent_type == "screen_action":
        return "take_screenshot"
    if intent_type == "memory":
        return "modify_memory" if (params or {}).get("action") == "save" else "read_memory"
    if intent_type == "schedule":
        return "create_schedule"
    return f"{intent_type}_action"


def scan_for_injection(content: str) -> Optional[str]:
    """Scan content for prompt injection patterns. Return matched pattern or None."""
    content_lower = content.lower()
    
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, content_lower, re.IGNORECASE):
            return pattern
    
    return None


def sanitize_external_content(content: str) -> tuple[str, bool]:
    """
    Sanitize content from external sources (web pages, files).
    
    Returns: (sanitized_content, was_injected)
    """
    injection = scan_for_injection(content)
    
    if injection:
        return "", True
    
    return content, False


def describe_zone(zone: SecurityZone) -> str:
    """Get human description of zone."""
    if zone == SecurityZone.GREEN:
        return "✓ Execute immediately"
    elif zone == SecurityZone.YELLOW:
        return "⚠️ Requires 5-second confirmation"
    else:
        return "🔴 Blocked — touches protected system areas"
