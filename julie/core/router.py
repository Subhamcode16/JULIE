"""Intent classification system."""

import re
from enum import Enum
from dataclasses import dataclass
from typing import Optional

class SecurityZone(Enum):
    """Security classification for intents."""
    GREEN = "green"    # Safe, auto-execute
    YELLOW = "yellow"  # Requires confirmation
    RED = "red"        # Hard-blocked



class IntentType(Enum):
    """Intent classification types."""
    SYSTEM_ACTION = "system_action"
    BROWSER_ACTION = "browser_action"
    AGENT_HANDOFF = "agent_handoff"
    SCREEN_ACTION = "screen_action"
    INFORMATION = "information"
    SCHEDULE = "schedule"
    MEMORY = "memory"
    CONVERSATION = "conversation"
    CONTEXTUAL_ACTION = "contextual_action"
    AUTONOMOUS_ACTION = "autonomous_action"


@dataclass
class ClassifiedIntent:
    """Result of intent classification."""
    intent_type: IntentType
    confidence: float
    params: dict
    raw_input: str
    security_zone: SecurityZone = SecurityZone.GREEN
    used_llm: bool = False


# Filler prefixes to strip before matching (handles natural speech)
_FILLER_PREFIXES = re.compile(
    r"^(?:can you|could you|please|hey sixteen|sixteen|"
    r"would you|will you|i need you to|i want you to|"
    r"go ahead and|just)\s+",
    re.IGNORECASE,
)

# Filler suffixes to strip after matching (e.g. "open chrome for me?")
_FILLER_SUFFIXES = re.compile(
    r"\s+(?:for me|please|now|right now|quickly|asap)[.?!]?$",
    re.IGNORECASE,
)


def _strip_fillers(text: str) -> str:
    """Remove polite/filler words at start and end of a command."""
    prev = None
    while prev != text:
        prev = text
        text = _FILLER_PREFIXES.sub("", text).strip()
    text = _FILLER_SUFFIXES.sub("", text).strip()
    return text


# Zero-cost rule patterns (no LLM needed)
DIRECT_PATTERNS = [
    (r"^(?:open|launch|start)\s+(.+?)(?:\s+and.*)?$", IntentType.SYSTEM_ACTION, {"action": "open"}),
    (r"^take\s+(?:a\s+)?screenshot", IntentType.SCREEN_ACTION, {"action": "screenshot"}),
    (r"^(?:go to|navigate to|open browser to)\s+(.+)$", IntentType.BROWSER_ACTION, {"action": "navigate"}),
    (r"^run\s+(.+?)\s+in\s+(?:the\s+)?terminal$", IntentType.SYSTEM_ACTION, {"action": "terminal"}),
    (r"^remember\s+that\s+(.+)$", IntentType.MEMORY, {"action": "save"}),
    (r"^(?:recall|show|list)\s+(?:memories|memory)$", IntentType.MEMORY, {"action": "list"}),
    (r"^remind\s+me\s+(.+)$", IntentType.SCHEDULE, {"action": "create"}),
    (r"^list\s+(?:files|directory|folder)(?:\s+(.+))?$", IntentType.SYSTEM_ACTION, {"action": "list"}),
    (r"^read\s+(?:file|content)\s+(.+)$", IntentType.SYSTEM_ACTION, {"action": "read"}),
    (r"^write\s+file\s+(.+?)(?:\s+with\s+(.+))?$", IntentType.SYSTEM_ACTION, {"action": "write"}),
    (r"^search\s+(?:for\s+)?(.+?)(?:\s+on\s+(.+))?$", IntentType.BROWSER_ACTION, {"action": "search"}),
    (r"^(?:show\s+)?(?:tokens|token usage|api usage|sixteen stats).*$", IntentType.INFORMATION, {"action": "token_summary"}),
    (r"^type\s+(.+?)\s+(?:in\s+here|here)$", IntentType.CONTEXTUAL_ACTION, {"action": "type"}),
    (r"^(?:book|buy|find)\s+(.+?)$", IntentType.AUTONOMOUS_ACTION, {"action": "autonomous_web"}),
]


def classify_intent(text: str) -> ClassifiedIntent:
    """
    Classify user input into an intent type.

    Returns high-confidence classification for rule-matched patterns.
    Returns low-confidence (requires LLM) for ambiguous inputs.
    """
    text_lower = text.lower().strip()
    # Pre-process: strip polite/filler words so "can you open chrome" -> "open chrome"
    text_clean = _strip_fillers(text_lower)

    # Try rule-based patterns on both cleaned and original text
    for candidate in ([text_clean] if text_clean != text_lower else []) + [text_lower]:
        for pattern, intent_type, base_params in DIRECT_PATTERNS:
            match = re.match(pattern, candidate)
            if match:
                params = {**base_params}

                if match.groups():
                    action = params.get("action")
                    if intent_type == IntentType.SYSTEM_ACTION:
                        params["target"] = match.group(1).strip()
                        if action == "write" and len(match.groups()) > 1:
                            params["content"] = match.group(2) or ""
                    elif intent_type == IntentType.BROWSER_ACTION:
                        params["url_or_query"] = match.group(1).strip()
                        if action == "search" and len(match.groups()) > 1 and match.group(2):
                            params["platform"] = match.group(2).strip()
                    elif intent_type == IntentType.MEMORY and action == "save":
                        params["fact"] = match.group(1).strip()
                    elif intent_type == IntentType.SCHEDULE:
                        params["schedule_desc"] = match.group(1).strip()
                    elif intent_type == IntentType.CONTEXTUAL_ACTION and action == "type":
                        params["text"] = match.group(1).strip()
                    elif intent_type == IntentType.AUTONOMOUS_ACTION:
                        params["goal"] = match.group(0).strip()
                        
                # Determine security zone based on intent and action
                zone = SecurityZone.GREEN
                if intent_type == IntentType.SYSTEM_ACTION:
                    if action == "terminal" or action == "delete":
                        zone = SecurityZone.RED
                    elif action == "write":
                        zone = SecurityZone.YELLOW
                elif intent_type == IntentType.AGENT_HANDOFF:
                    zone = SecurityZone.YELLOW

                return ClassifiedIntent(
                    intent_type=intent_type,
                    confidence=0.95,
                    params=params,
                    raw_input=text,
                    security_zone=zone,
                    used_llm=False,
                )

    # No rule match — return low confidence (requires LLM)
    return ClassifiedIntent(
        intent_type=IntentType.CONVERSATION,
        confidence=0.3,
        params={"query": text},
        raw_input=text,
        security_zone=SecurityZone.GREEN,
        used_llm=False,
    )


def extract_app_name(text: str) -> Optional[str]:
    """Extract app name from text like 'open chrome' or 'launch vs code'."""
    match = re.match(r"^(?:open|launch|start)\s+(.+?)(?:\s+and.*)?$", text.lower())
    if match:
        return match.group(1).strip()
    return None


def extract_url(text: str) -> Optional[str]:
    """Extract URL from text like 'go to gmail' or 'navigate to github.com'."""
    match = re.match(r"^(?:go to|navigate to)\s+(.+)$", text.lower())
    if match:
        return match.group(1).strip()
    return None
