"""Async Groq chat-completions client for Julie."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any

import httpx

try:
    from core.config import get_config
except ImportError:
    from julie.core.config import get_config


DEFAULT_MODEL = "llama-3.3-70b-versatile"


@dataclass
class LLMResult:
    """Normalized LLM response."""

    success: bool
    content: str = ""
    provider: str = "groq"
    model: str = DEFAULT_MODEL
    tokens_in: int = 0
    tokens_out: int = 0
    latency_ms: int = 0
    error: str | None = None
    raw: dict[str, Any] | None = None


class GroqClient:
    """Small provider wrapper around Groq's OpenAI-compatible chat API."""

    def __init__(self, api_key: str | None = None, model: str = DEFAULT_MODEL):
        config = get_config()
        self.api_key = api_key if api_key is not None else config.groq_api_key
        self.model = model
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.timeout = 20

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    async def chat(
        self,
        messages: list[dict[str, str]],
        *,
        max_tokens: int = 500,
        temperature: float = 0.2,
        response_format: dict[str, str] | None = None,
    ) -> LLMResult:
        """Call Groq and normalize response/errors."""
        if not self.available:
            return LLMResult(success=False, error="No GROQ_API_KEY configured")

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if response_format:
            payload["response_format"] = response_format

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        started = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(self.base_url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
        except Exception as exc:
            return LLMResult(
                success=False,
                latency_ms=int((time.perf_counter() - started) * 1000),
                error=str(exc),
            )

        choice = (data.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        usage = data.get("usage") or {}
        return LLMResult(
            success=True,
            content=message.get("content") or "",
            provider="groq",
            model=data.get("model") or self.model,
            tokens_in=usage.get("prompt_tokens") or 0,
            tokens_out=usage.get("completion_tokens") or 0,
            latency_ms=int((time.perf_counter() - started) * 1000),
            raw=data,
        )


CLASSIFIER_PROMPT = """Classify this user request into exactly one Julie intent.
Return JSON only with keys: intent, confidence, extracted_params, needs_clarification, clarification_question.

Intent values:
- system_action: open/close apps, file read/write/list, terminal commands
- browser_action: navigate web, search web, click, fill forms, scrape
- agent_handoff: coding tasks, debugging, implementation work for Claude Code or Cursor
- screen_action: screenshot or visual screen questions
- information: questions, token usage, explanations, no direct system action
- schedule: reminders or recurring tasks
- memory: save or recall user facts
- conversation: chitchat or unclear input

Use extracted_params.action when obvious, such as open, terminal, read, write, list, save, token_summary."""


async def classify_with_llm(text: str, client: GroqClient | None = None) -> LLMResult:
    """Classify ambiguous input with a cheap JSON-only LLM call."""
    client = client or GroqClient()
    return await client.chat(
        [
            {"role": "system", "content": CLASSIFIER_PROMPT},
            {"role": "user", "content": text},
        ],
        max_tokens=180,
        temperature=0,
        response_format={"type": "json_object"},
    )


async def answer_with_llm(prompt: str, client: GroqClient | None = None) -> LLMResult:
    """Generate a concise Julie response for information/conversation turns."""
    client = client or GroqClient()
    return await client.chat(
        [
            {
                "role": "system",
                "content": "You are Julie, a highly intelligent, specialized Windows AI assistant. You speak aloud. Keep your answers brief, professional, and contextually aware, with just a touch of warmth.",
            },
            {"role": "user", "content": prompt},
        ],
        model=DEFAULT_MODEL,
        max_tokens=500,
        temperature=0.3,
    )


async def answer_with_vision(prompt: str, base64_image: str) -> LLMResult:
    """Send a vision prompt to Groq."""
    client = GroqClient()
    return await client.chat(
        [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        model="llama-3.2-90b-vision-preview",
        max_tokens=1024,
    )


def parse_classifier_json(content: str) -> dict[str, Any] | None:
    """Parse classifier JSON safely."""
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None
