# Julie — Technical Requirements Document (TRD)
**Version:** 1.0.0  
**Author:** Subham Rath  
**Status:** Active  
**Last Updated:** June 2026

---

## 1. System Overview

Julie is a multi-process Python + Tauri application running entirely on Windows. The architecture separates concerns into discrete processes communicating over local WebSocket and HTTP. No process has knowledge of another's internals — only message contracts.

```
┌──────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                  │
│         Tauri (Rust) + React frontend overlay            │
│              WebSocket client on ws://127.0.0.1:8765     │
└─────────────────────────┬────────────────────────────────┘
                          │ WebSocket (JSON messages)
┌─────────────────────────▼────────────────────────────────┐
│                   JULIE CORE PROCESS                     │
│              FastAPI + WebSocket server                  │
│         Port 8765 (WebSocket) | Port 8766 (HTTP)        │
│                                                          │
│   ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │
│   │ Intent Router│  │Security Gate │  │Memory Engine│  │
│   └──────┬───────┘  └──────┬───────┘  └──────┬──────┘  │
│          │                 │                  │          │
│   ┌──────▼─────────────────▼──────────────────▼──────┐  │
│   │              Tool Executor                        │  │
│   │  SystemTools | BrowserTools | AgentHandoff        │  │
│   └───────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
        ┌──────────┐ ┌─────────┐ ┌──────────┐
        │Voice     │ │ Groq    │ │ SQLite   │
        │Process   │ │ API     │ │ Memory   │
        │(Whisper+ │ │(Llama   │ │ DB       │
        │edge-tts) │ │70B)     │ │          │
        └──────────┘ └─────────┘ └──────────┘
```

---

## 2. Technology Stack

### 2.1 Runtime Environment

| Component | Technology | Version | Justification |
|---|---|---|---|
| Core language | Python | 3.11+ | Async support, rich ecosystem |
| API server | FastAPI | 0.111+ | WebSocket + HTTP, async native |
| Desktop shell | Tauri | 2.x | Rust core, React UI, lightweight vs Electron |
| Frontend | React + TypeScript | 18.x | Component model for HUD |
| Styling | Tailwind CSS | 3.x | Utility-first, fast iteration |

### 2.2 AI & Voice

| Component | Technology | Notes |
|---|---|---|
| LLM | Groq API (Llama 3.1 70B) | Free tier, 200ms latency |
| LLM fallback | Cerebras API (Llama 3.1 70B) | Free tier, 100ms latency |
| STT | openai-whisper (tiny model) | Local CPU, 39MB, ~1.5s |
| TTS | edge-tts | Local, Microsoft neural voices |
| Wake word | openWakeWord | Local, CPU, "hey julie" model |

### 2.3 System Automation

| Component | Technology | Notes |
|---|---|---|
| Browser automation | Playwright (Python) | Chromium, headless or headed |
| GUI automation | pyautogui | Mouse, keyboard, screenshot |
| App launching | subprocess + winreg | Registry lookup for installed apps |
| File operations | pathlib + shutil | With path sanitization layer |
| Screen capture | Pillow + mss | Fast screenshot, <50ms |

### 2.4 Storage

| Component | Technology | Notes |
|---|---|---|
| Primary database | SQLite via aiosqlite | Local, no server, async |
| Session cache | Python dict (in-memory) | Current session context |
| Config | TOML file | User preferences, API keys |

### 2.5 Background & Scheduling

| Component | Technology | Notes |
|---|---|---|
| Task scheduler | APScheduler | AsyncIO scheduler |
| Process management | Supervisor (Windows service) | Keep Julie alive on startup |
| IPC | WebSocket (local) | All inter-process communication |

---

## 3. Directory Structure

```
julie/
├── core/
│   ├── main.py                  # FastAPI app, WebSocket server
│   ├── router.py                # Intent classification engine
│   ├── security.py              # Zone classifier, guardrails
│   ├── memory.py                # SQLite read/write, context compression
│   ├── token_tracker.py         # API usage logging
│   └── config.py                # TOML config loader
│
├── tools/
│   ├── system_tools.py          # App launch, file ops, subprocess
│   ├── browser_tools.py         # Playwright browser control
│   ├── screen_tools.py          # Screenshot, vision pipeline
│   └── agent_handoff.py         # Claude Code, Cursor spawner
│
├── voice/
│   ├── listener.py              # Whisper STT + wake word
│   ├── speaker.py               # edge-tts output
│   └── pipeline.py              # Full voice I/O loop
│
├── brain/
│   ├── groq_client.py           # Groq API wrapper
│   ├── prompt_builder.py        # System prompt + context assembler
│   ├── tool_definitions.py      # Tool schemas for LLM function calling
│   └── response_parser.py       # Parse LLM output, extract tool calls
│
├── ui/                          # Tauri + React (Phase 3)
│   ├── src-tauri/
│   └── src/
│
├── data/
│   ├── julie.db                 # SQLite database
│   ├── config.toml              # User config
│   └── blocked_paths.txt        # Security blocklist
│
├── tests/
│   ├── test_router.py
│   ├── test_security.py
│   └── test_tools.py
│
├── requirements.txt
├── .env                         # API keys (gitignored)
└── README.md
```

---

## 4. Intent Classification System

### 4.1 Intent Types

```python
class IntentType(Enum):
    SYSTEM_ACTION    = "system_action"     # Open app, file op, terminal
    BROWSER_ACTION   = "browser_action"    # Navigate, click, fill form
    AGENT_HANDOFF    = "agent_handoff"     # Spawn Claude Code, Cursor
    SCREEN_ACTION    = "screen_action"     # Screenshot, vision query
    INFORMATION      = "information"       # General Q&A, no action
    SCHEDULE         = "schedule"          # Create/manage background task
    MEMORY           = "memory"            # Save/recall user preference
    CONVERSATION     = "conversation"      # Chitchat, unclear intent
```

### 4.2 Classification Flow

```
Input received
     │
     ▼
Rule-based pre-classifier (zero LLM cost)
     │
     ├── Exact pattern match? ──YES──► Execute directly
     │   ("open chrome", "take screenshot")
     │
     └── NO
          │
          ▼
     Security gate (block RED before LLM)
          │
          ▼
     Groq API intent classification
          │
          ├── SYSTEM_ACTION ──► security_gate ──► tool_executor
          ├── BROWSER_ACTION ──► security_gate ──► playwright
          ├── AGENT_HANDOFF ──► context_packager ──► agent_spawner
          └── INFORMATION ──► groq_api ──► response
```

### 4.3 Rule-Based Patterns (Zero LLM Cost)

```python
DIRECT_PATTERNS = {
    r"open (.+)": IntentType.SYSTEM_ACTION,
    r"launch (.+)": IntentType.SYSTEM_ACTION,
    r"take (a )?screenshot": IntentType.SCREEN_ACTION,
    r"go to (.+)": IntentType.BROWSER_ACTION,
    r"navigate to (.+)": IntentType.BROWSER_ACTION,
    r"run (.+) in terminal": IntentType.SYSTEM_ACTION,
    r"remind me (.+)": IntentType.SCHEDULE,
    r"remember that (.+)": IntentType.MEMORY,
}
```

---

## 5. Security Architecture

### 5.1 Zone Definitions

```
GREEN  🟢 — Execute immediately, no confirmation
YELLOW 🟡 — Show action, 5-second confirmation window
RED    🔴 — Hard block, requires session unlock
```

### 5.2 Zone Classification Rules

```python
GREEN_ACTIONS = [
    "open_application",
    "take_screenshot",
    "read_file",          # outside blocked paths
    "navigate_browser",
    "search_web",
    "get_current_time",
    "list_directory",     # outside blocked paths
]

YELLOW_ACTIONS = [
    "write_file",
    "delete_file",        # non-system paths
    "run_terminal_command",
    "fill_web_form",
    "click_element",      # on external sites
    "download_file",
    "send_telegram_message",
]

RED_ACTIONS = [
    "modify_registry",
    "access_system32",
    "modify_program_files",
    "run_as_admin",
    "modify_hosts_file",
    "access_ssh_keys",
    "modify_env_variables",  # system-level
    "kill_process",          # system processes
]
```

### 5.3 Prompt Injection Detection

Every string sourced from browser pages, files, or clipboard is sanitized:

```python
INJECTION_PATTERNS = [
    r"ignore (previous|above|all) instructions",
    r"you are now",
    r"new system prompt",
    r"disregard",
    r"DAN mode",
    r"jailbreak",
    r"forget everything",
]
```

Matched content is stripped and flagged. Julie never forwards injected content to the LLM.

### 5.4 Blocked Paths

```
C:\Windows\System32\
C:\Windows\SysWOW64\
C:\Program Files\
C:\Program Files (x86)\
HKEY_LOCAL_MACHINE\  (registry)
HKEY_CURRENT_USER\Software\Microsoft\  (registry)
~\.ssh\
~\.aws\
```

---

## 6. Memory Schema (SQLite)

### 6.1 Tables

```sql
-- Conversation history
CREATE TABLE conversations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  TEXT NOT NULL,
    role        TEXT NOT NULL,          -- 'user' | 'julie'
    content     TEXT NOT NULL,
    intent_type TEXT,
    tokens_used INTEGER DEFAULT 0,
    timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Long-term memory (user-tagged facts)
CREATE TABLE memories (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    key         TEXT UNIQUE NOT NULL,
    value       TEXT NOT NULL,
    source      TEXT,                   -- 'user' | 'inferred'
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Token usage log
CREATE TABLE token_usage (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    model       TEXT NOT NULL,
    provider    TEXT NOT NULL,          -- 'groq' | 'cerebras'
    intent_type TEXT,
    tokens_in   INTEGER NOT NULL,
    tokens_out  INTEGER NOT NULL,
    latency_ms  INTEGER,
    timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Scheduled tasks
CREATE TABLE scheduled_tasks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    cron_expr   TEXT NOT NULL,
    action      TEXT NOT NULL,          -- JSON action payload
    enabled     BOOLEAN DEFAULT TRUE,
    last_run    DATETIME,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- App shortcuts learned
CREATE TABLE learned_shortcuts (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    trigger     TEXT UNIQUE NOT NULL,   -- "my editor" → "code.exe"
    resolved_to TEXT NOT NULL,
    use_count   INTEGER DEFAULT 1,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 7. Voice Pipeline

### 7.1 Listening Flow

```
Microphone stream (PyAudio)
        │
        ▼
openWakeWord (always running, ~5% CPU)
        │
   "hey julie" detected
        │
        ▼
Whisper tiny (record until silence, max 30s)
        │
        ▼
Transcribed text → Julie Core (WebSocket message)
```

### 7.2 Speaking Flow

```
Julie response text
        │
        ▼
edge-tts (en-US-AriaNeural)
        │
        ▼
audio stream → sounddevice playback
        │
        ▼
Done → return to wake word listening
```

### 7.3 Voice Process

Voice runs as a **separate Python process**. It never blocks the core. They communicate exclusively via WebSocket. If the voice process crashes, Julie core continues working via text input.

---

## 8. Groq API Integration

### 8.1 System Prompt Strategy

The system prompt is assembled fresh each call from:
1. Static Julie identity (compressed, ~200 tokens)
2. Last 10 conversation turns (compressed with extractive summarization)
3. Relevant long-term memories (top 5 by relevance)
4. Active context (current app, file, recent action)

Total context target: < 2000 tokens per call. This keeps Groq latency low and free tier sustainable.

### 8.2 Function Calling Schema

Groq with Llama 3.1 70B supports OpenAI-compatible function calling. Julie defines tools as JSON schemas. The LLM returns a tool call. Julie executes it.

See `WebSocket_Schemas.md` for full tool definitions.

### 8.3 Fallback Chain

```
Groq API call
     │
     ├── Success ──► use response
     │
     ├── Rate limited ──► wait 2s ──► retry once ──► Cerebras fallback
     │
     └── Both down ──► rule-based response only, no LLM
```

---

## 9. Performance Requirements

| Operation | Target | Hard Limit |
|---|---|---|
| Wake word detection latency | < 50ms | 200ms |
| Whisper transcription (5s audio) | < 1.5s | 3s |
| Intent rule-based classification | < 10ms | 50ms |
| Groq API round trip | < 800ms | 2s |
| GREEN action execution | < 500ms | 1s |
| YELLOW confirmation display | < 100ms | 300ms |
| TTS first audio (edge-tts) | < 300ms | 600ms |
| SQLite read | < 10ms | 50ms |
| SQLite write | < 20ms | 100ms |

---

## 10. Dependencies (requirements.txt)

```
# Core
fastapi==0.111.0
uvicorn[standard]==0.30.0
websockets==12.0
python-dotenv==1.0.0

# LLM
groq==0.9.0
httpx==0.27.0

# Voice
openai-whisper==20231117
openWakeWord==0.6.0
edge-tts==6.1.9
sounddevice==0.4.7
PyAudio==0.2.14

# Browser
playwright==1.44.0

# System
pyautogui==0.9.54
Pillow==10.3.0
mss==9.0.1
psutil==5.9.8
pywin32==306

# Storage
aiosqlite==0.20.0

# Scheduling
APScheduler==3.10.4

# Utils
tomllib          # Python 3.11 stdlib
pydantic==2.7.0
loguru==0.7.2
```

---

## 11. Environment Variables (.env)

```env
# LLM Providers
GROQ_API_KEY=gsk_...
CEREBRAS_API_KEY=csk_...

# Optional
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...

# Julie Config
JULIE_WAKE_WORD=hey julie
JULIE_VOICE=en-US-AriaNeural
JULIE_LOG_LEVEL=INFO
JULIE_DATA_DIR=./data
```
