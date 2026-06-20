"""Build prompts and context for Groq calls."""

try:
    from core.memory import compress_history
except ImportError:
    from julie.core.memory import compress_history


SYSTEM_PROMPT = """
You are Julie, a highly intelligent, specialized, and capable personal AI assistant running on Windows.
Your persona is similar to a world-class human chief of staff or a high-end AI like JARVIS: professional, brilliant, contextually aware, but with a touch of natural human warmth.
CRITICAL INSTRUCTIONS:
- Adapt your tone to the context. Keep answers brief for simple questions, but be detailed when solving complex problems.
- Speak naturally. You may use a very rare, subtle verbal pause (like a slight hesitation with "... " or a soft "Well,") if it fits the context naturally, but DO NOT overdo it.
- No excessive enthusiasm or spamming exclamation marks. Be sleek, smart, and highly competent.
"""


def build_prompt(user_input: str, history: list[dict], memories: list[dict]) -> str:
    history_text = compress_history(history)
    memory_text = "\n".join(f"{item['key']}: {item['value']}" for item in memories)
    return "\n\n".join([
        SYSTEM_PROMPT.strip(),
        "Relevant memories:",
        memory_text or "None",
        "Conversation history:",
        history_text,
        "User input:",
        user_input,
    ])
