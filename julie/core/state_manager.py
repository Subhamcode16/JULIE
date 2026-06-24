"""State Manager for System Modes."""

from enum import Enum
from typing import Dict, Any

class SystemMode(Enum):
    NORMAL = "normal"
    ENGINEERING = "engineering"
    RESEARCH = "research"
    CREATOR = "creator"

_current_mode = SystemMode.NORMAL

def get_current_mode() -> SystemMode:
    """Get the current system mode."""
    return _current_mode

def set_mode(mode_name: str) -> Dict[str, Any]:
    """Switch the system mode to tailor agent behavior."""
    global _current_mode
    mode_name = mode_name.lower().strip()
    
    try:
        _current_mode = SystemMode(mode_name)
        return {"success": True, "message": f"Switched system mode to: {_current_mode.value.upper()}"}
    except ValueError:
        return {"success": False, "error": f"Unknown mode: {mode_name}. Valid modes are: {[m.value for m in SystemMode]}"}

def get_mode_prompt_injection() -> str:
    """Return a system prompt addition based on the current mode."""
    if _current_mode == SystemMode.ENGINEERING:
        return (
            "You are currently in ENGINEERING MODE. Focus on deep technical analysis, "
            "code generation, architecture design, and precise terminal/system commands. "
            "Minimize casual conversation."
        )
    elif _current_mode == SystemMode.RESEARCH:
        return (
            "You are currently in RESEARCH MODE. Focus on comprehensive web scraping, "
            "cross-referencing data, and synthesizing large amounts of information. "
            "Be extremely factual and cite sources."
        )
    elif _current_mode == SystemMode.CREATOR:
        return (
            "You are currently in CREATOR MODE. Focus on creative writing, asset generation, "
            "and brainstorming. Offer multiple stylistic options when requested."
        )
    else:
        return ""
