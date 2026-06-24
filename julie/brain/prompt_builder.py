"""Build prompts and context for Groq calls."""

try:
    from core.memory import compress_history
except ImportError:
    from julie.core.memory import compress_history


try:
    from core.state_manager import get_mode_prompt_injection
except ImportError:
    from julie.core.state_manager import get_mode_prompt_injection

import os

def get_system_prompt() -> str:
    # Attempt to read from the project root system_prompt.md
    # We fallback to a default if not found
    prompt_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "system_prompt.md"))
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return "You are Sixteen, a highly intelligent personal AI assistant running on Windows."



def build_prompt(user_input: str, history: list[dict], memories: list[dict]) -> str:
    history_text = compress_history(history)
    memory_text = "\n".join(f"{item['key']}: {item['value']}" for item in memories)
    return "\n\n".join([
        get_system_prompt().strip(),
        get_mode_prompt_injection(),
        "Relevant memories:",
        memory_text or "None",
        "Conversation history:",
        history_text,
        "User input:",
        user_input,
    ])
