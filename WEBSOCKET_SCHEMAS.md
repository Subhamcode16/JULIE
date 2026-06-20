# Julie — WebSocket Message Schemas
**Version:** 1.0.0  
**Last Updated:** June 2026

---

## Overview

All communication between the UI (Tauri), Voice process, and Core happens via WebSocket at `ws://127.0.0.1:8765`.

Every message is a JSON object with this envelope:

```json
{
  "type": "MESSAGE_TYPE",
  "id": "uuid-v4",
  "timestamp": "2026-06-15T09:00:00.000Z",
  "payload": { ... }
}
```

`id` is used to correlate requests with responses. The sender generates it. The responder echoes it.

---

## 1. Client → Core Messages

### 1.1 USER_INPUT_TEXT
User typed a message via HUD or terminal.

```json
{
  "type": "USER_INPUT_TEXT",
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "timestamp": "2026-06-15T09:00:00.000Z",
  "payload": {
    "text": "open chrome and go to gmail",
    "source": "hud"
  }
}
```

| Field | Type | Values | Description |
|---|---|---|---|
| text | string | any | Raw user input |
| source | enum | `hud` \| `terminal` \| `telegram` | Input origin |

---

### 1.2 USER_INPUT_VOICE
Transcribed voice input from the voice process.

```json
{
  "type": "USER_INPUT_VOICE",
  "id": "b2c3d4e5-f6a7-8901-bcde-f12345678901",
  "timestamp": "2026-06-15T09:00:01.200Z",
  "payload": {
    "text": "hey julie open my project in vs code",
    "confidence": 0.94,
    "audio_duration_ms": 2800,
    "transcription_ms": 1450
  }
}
```

| Field | Type | Description |
|---|---|---|
| text | string | Whisper transcription |
| confidence | float 0–1 | Whisper confidence score |
| audio_duration_ms | int | Length of recorded audio |
| transcription_ms | int | Time taken to transcribe |

---

### 1.3 CONFIRM_ACTION
User confirmed a YELLOW zone action.

```json
{
  "type": "CONFIRM_ACTION",
  "id": "c3d4e5f6-a7b8-9012-cdef-123456789012",
  "timestamp": "2026-06-15T09:00:05.100Z",
  "payload": {
    "action_id": "d4e5f6a7-b8c9-0123-defa-234567890123",
    "decision": "confirm"
  }
}
```

| Field | Type | Values | Description |
|---|---|---|---|
| action_id | uuid | — | ID of the pending YELLOW action |
| decision | enum | `confirm` \| `cancel` | User's choice |

---

### 1.4 UNLOCK_RED_ZONE
User explicitly unlocks a RED zone action for this session.

```json
{
  "type": "UNLOCK_RED_ZONE",
  "id": "e5f6a7b8-c9d0-1234-efab-345678901234",
  "timestamp": "2026-06-15T09:00:10.000Z",
  "payload": {
    "action_type": "modify_registry",
    "scope": "session",
    "user_confirmation_phrase": "julie unlock modify_registry for this session"
  }
}
```

| Field | Type | Values | Description |
|---|---|---|---|
| action_type | string | RED action name | Which RED action to unlock |
| scope | enum | `session` \| `once` | Duration of unlock |
| user_confirmation_phrase | string | — | Echoed for audit log |

---

### 1.5 HEARTBEAT (Client)
Sent by UI and Voice every 5 seconds to signal they're alive.

```json
{
  "type": "HEARTBEAT",
  "id": "f6a7b8c9-d0e1-2345-fabc-456789012345",
  "timestamp": "2026-06-15T09:00:15.000Z",
  "payload": {
    "client": "voice_process",
    "status": "healthy",
    "whisper_loaded": true,
    "wake_word_active": true
  }
}
```

---

## 2. Core → Client Messages

### 2.1 JULIE_RESPONSE
Main response message. Sent after every processed input.

```json
{
  "type": "JULIE_RESPONSE",
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "timestamp": "2026-06-15T09:00:01.800Z",
  "payload": {
    "text": "Chrome is open and I've navigated to Gmail.",
    "speak": true,
    "intent_classified": "BROWSER_ACTION",
    "actions_taken": [
      {
        "tool": "open_application",
        "params": { "app": "chrome" },
        "result": "success",
        "zone": "GREEN"
      },
      {
        "tool": "navigate_browser",
        "params": { "url": "https://gmail.com" },
        "result": "success",
        "zone": "GREEN"
      }
    ],
    "tokens_used": {
      "prompt": 847,
      "completion": 112,
      "provider": "groq",
      "model": "llama-3.1-70b-versatile",
      "latency_ms": 623
    },
    "llm_called": true
  }
}
```

| Field | Type | Description |
|---|---|---|
| text | string | Julie's response text |
| speak | bool | Whether voice should speak this |
| intent_classified | string | Detected intent type |
| actions_taken | array | List of tools executed |
| tokens_used | object | API usage metrics (null if no LLM called) |
| llm_called | bool | Whether Groq API was invoked |

---

### 2.2 STATE_UPDATE
Julie's internal state changed. HUD uses this to update visuals.

```json
{
  "type": "STATE_UPDATE",
  "id": "b2c3d4e5-f6a7-8901-bcde-f12345678902",
  "timestamp": "2026-06-15T09:00:01.200Z",
  "payload": {
    "state": "THINKING",
    "previous_state": "LISTENING",
    "message": "Classifying your intent..."
  }
}
```

| Field | Type | Values | Description |
|---|---|---|---|
| state | enum | `IDLE` \| `LISTENING` \| `THINKING` \| `SPEAKING` \| `CONFIRMING` \| `EXECUTING` \| `ERROR` \| `BLOCKED` | Current state |
| previous_state | enum | same | Previous state |
| message | string | optional | Display message for HUD |

---

### 2.3 CONFIRMATION_REQUEST
A YELLOW zone action needs user approval.

```json
{
  "type": "CONFIRMATION_REQUEST",
  "id": "c3d4e5f6-a7b8-9012-cdef-123456789013",
  "timestamp": "2026-06-15T09:00:02.100Z",
  "payload": {
    "action_id": "d4e5f6a7-b8c9-0123-defa-234567890124",
    "zone": "YELLOW",
    "tool": "write_file",
    "description": "Write 47 lines to D:\\projects\\julie\\config.toml",
    "preview": "[tool]\nname = \"julie\"\nversion = \"1.0.0\"\n...",
    "timeout_seconds": 5,
    "auto_cancel": true
  }
}
```

| Field | Type | Description |
|---|---|---|
| action_id | uuid | ID to echo back in CONFIRM_ACTION |
| zone | string | Always "YELLOW" for this message |
| tool | string | Tool being requested |
| description | string | Human-readable summary |
| preview | string | Content preview (truncated to 200 chars) |
| timeout_seconds | int | Seconds before auto-cancel |
| auto_cancel | bool | Whether to cancel on timeout |

---

### 2.4 SECURITY_BLOCK
A RED zone action was attempted and blocked.

```json
{
  "type": "SECURITY_BLOCK",
  "id": "e5f6a7b8-c9d0-1234-efab-345678901235",
  "timestamp": "2026-06-15T09:00:03.000Z",
  "payload": {
    "blocked_action": "modify_registry",
    "reason": "Registry modification is a RED zone action.",
    "attempted_path": "HKEY_LOCAL_MACHINE\\SOFTWARE\\...",
    "unlock_phrase": "julie unlock modify_registry for this session",
    "injection_detected": false
  }
}
```

| Field | Type | Description |
|---|---|---|
| blocked_action | string | Action that was blocked |
| reason | string | Human-readable reason |
| attempted_path | string | Specific path/target (sanitized) |
| unlock_phrase | string | Exact phrase to unlock if legitimate |
| injection_detected | bool | Whether prompt injection triggered this |

---

### 2.5 INJECTION_WARNING
Prompt injection was detected in external content.

```json
{
  "type": "INJECTION_WARNING",
  "id": "f6a7b8c9-d0e1-2345-fabc-456789012346",
  "timestamp": "2026-06-15T09:00:04.200Z",
  "payload": {
    "source": "browser_page",
    "url": "https://example.com/malicious",
    "pattern_matched": "ignore previous instructions",
    "content_sanitized": true,
    "action": "content stripped, user alerted"
  }
}
```

---

### 2.6 AGENT_HANDOFF_STATUS
Status update when an external agent is spawned.

```json
{
  "type": "AGENT_HANDOFF_STATUS",
  "id": "a7b8c9d0-e1f2-3456-abcd-567890123457",
  "timestamp": "2026-06-15T09:00:05.000Z",
  "payload": {
    "agent": "claude_code",
    "status": "spawned",
    "pid": 5678,
    "context_package": {
      "task": "Fix the WebSocket reconnection bug in core/main.py",
      "project_path": "D:\\projects\\julie",
      "relevant_files": ["core/main.py", "core/router.py"],
      "conversation_summary": "User asked Julie to fix a bug where..."
    },
    "tokens_delegated": 0,
    "message": "Handed off to Claude Code. Check your terminal."
  }
}
```

---

### 2.7 TOKEN_USAGE_SUMMARY
Periodic token usage report (sent every 30 min or on request).

```json
{
  "type": "TOKEN_USAGE_SUMMARY",
  "id": "b8c9d0e1-f2a3-4567-bcde-678901234568",
  "timestamp": "2026-06-15T09:30:00.000Z",
  "payload": {
    "period": "today",
    "groq": {
      "calls": 23,
      "tokens_in": 18450,
      "tokens_out": 3210,
      "estimated_cost_usd": 0.00,
      "free_tier_remaining_pct": 74
    },
    "cerebras": {
      "calls": 2,
      "tokens_in": 1200,
      "tokens_out": 340,
      "estimated_cost_usd": 0.00
    },
    "llm_calls_avoided": 41,
    "efficiency_pct": 64
  }
}
```

---

### 2.8 SCHEDULED_TASK_RESULT
Background task completed and has a result.

```json
{
  "type": "SCHEDULED_TASK_RESULT",
  "id": "c9d0e1f2-a3b4-5678-cdef-789012345679",
  "timestamp": "2026-06-15T09:00:01.000Z",
  "payload": {
    "task_id": 7,
    "task_name": "morning_email_summary",
    "status": "success",
    "result_text": "You have 4 new emails. 2 from clients, 1 from GitHub, 1 from Groq.",
    "speak": true,
    "execution_ms": 4230
  }
}
```

---

### 2.9 HEARTBEAT_ACK (Core)
Core acknowledges a client heartbeat.

```json
{
  "type": "HEARTBEAT_ACK",
  "id": "f6a7b8c9-d0e1-2345-fabc-456789012345",
  "timestamp": "2026-06-15T09:00:15.050Z",
  "payload": {
    "core_status": "healthy",
    "active_clients": ["hud", "voice_process"],
    "active_tasks": 2,
    "groq_available": true,
    "cerebras_available": true
  }
}
```

---

## 3. Voice Process ↔ Core Messages

### 3.1 WAKE_WORD_DETECTED
Wake word fired. Core should prepare for incoming transcription.

```json
{
  "type": "WAKE_WORD_DETECTED",
  "id": "a1b2c3d4-1111-2222-3333-444444444444",
  "timestamp": "2026-06-15T09:00:00.050Z",
  "payload": {
    "wake_word": "hey julie",
    "confidence": 0.97
  }
}
```

---

### 3.2 SPEAK_REQUEST
Core tells the voice process to speak a response.

```json
{
  "type": "SPEAK_REQUEST",
  "id": "b2c3d4e5-2222-3333-4444-555555555555",
  "timestamp": "2026-06-15T09:00:02.000Z",
  "payload": {
    "text": "Chrome is open and I've navigated to Gmail.",
    "voice": "en-US-AriaNeural",
    "speed": 1.0,
    "priority": "normal"
  }
}
```

| Field | Type | Values | Description |
|---|---|---|---|
| voice | string | edge-tts voice name | TTS voice to use |
| speed | float | 0.5–2.0 | Playback speed |
| priority | enum | `normal` \| `urgent` \| `interrupt` | `interrupt` stops current speech |

---

### 3.3 SPEAK_COMPLETE
Voice process signals TTS audio finished playing.

```json
{
  "type": "SPEAK_COMPLETE",
  "id": "b2c3d4e5-2222-3333-4444-555555555555",
  "timestamp": "2026-06-15T09:00:04.100Z",
  "payload": {
    "text_spoken": "Chrome is open and I've navigated to Gmail.",
    "duration_ms": 2100
  }
}
```

---

## 4. Tool Call Schema (LLM Function Calling)

These are the tool definitions sent to Groq's API. The LLM returns calls to these tools which Julie executes.

### 4.1 open_application
```json
{
  "name": "open_application",
  "description": "Open an installed Windows application by name",
  "parameters": {
    "type": "object",
    "properties": {
      "app_name": {
        "type": "string",
        "description": "Name of the application e.g. 'chrome', 'notepad', 'vscode'"
      },
      "args": {
        "type": "array",
        "items": { "type": "string" },
        "description": "Optional command line arguments"
      }
    },
    "required": ["app_name"]
  }
}
```

### 4.2 navigate_browser
```json
{
  "name": "navigate_browser",
  "description": "Navigate the browser to a URL",
  "parameters": {
    "type": "object",
    "properties": {
      "url": {
        "type": "string",
        "description": "Full URL to navigate to"
      },
      "new_tab": {
        "type": "boolean",
        "description": "Open in new tab (default: false)"
      }
    },
    "required": ["url"]
  }
}
```

### 4.3 browser_action
```json
{
  "name": "browser_action",
  "description": "Perform an action in the browser: click, fill, or read",
  "parameters": {
    "type": "object",
    "properties": {
      "action": {
        "type": "string",
        "enum": ["click", "fill", "read_text", "scroll", "screenshot"]
      },
      "selector": {
        "type": "string",
        "description": "CSS selector or descriptive label e.g. 'search input', 'submit button'"
      },
      "value": {
        "type": "string",
        "description": "Value to fill (only for fill action)"
      }
    },
    "required": ["action"]
  }
}
```

### 4.4 run_terminal_command
```json
{
  "name": "run_terminal_command",
  "description": "Run a command in Windows terminal (cmd or PowerShell). YELLOW zone.",
  "parameters": {
    "type": "object",
    "properties": {
      "command": {
        "type": "string",
        "description": "The command to execute"
      },
      "shell": {
        "type": "string",
        "enum": ["cmd", "powershell"],
        "default": "powershell"
      },
      "timeout_seconds": {
        "type": "integer",
        "default": 30
      }
    },
    "required": ["command"]
  }
}
```

### 4.5 read_file
```json
{
  "name": "read_file",
  "description": "Read the contents of a file",
  "parameters": {
    "type": "object",
    "properties": {
      "path": {
        "type": "string",
        "description": "Absolute or relative file path"
      },
      "max_lines": {
        "type": "integer",
        "description": "Maximum lines to return (default: 100)",
        "default": 100
      }
    },
    "required": ["path"]
  }
}
```

### 4.6 write_file
```json
{
  "name": "write_file",
  "description": "Write content to a file. YELLOW zone — requires confirmation.",
  "parameters": {
    "type": "object",
    "properties": {
      "path": {
        "type": "string",
        "description": "Absolute or relative file path"
      },
      "content": {
        "type": "string",
        "description": "Content to write"
      },
      "mode": {
        "type": "string",
        "enum": ["write", "append"],
        "default": "write"
      }
    },
    "required": ["path", "content"]
  }
}
```

### 4.7 take_screenshot
```json
{
  "name": "take_screenshot",
  "description": "Take a screenshot of the screen or a specific window",
  "parameters": {
    "type": "object",
    "properties": {
      "target": {
        "type": "string",
        "enum": ["fullscreen", "active_window"],
        "default": "fullscreen"
      },
      "analyze": {
        "type": "boolean",
        "description": "Whether to send to LLM vision for analysis",
        "default": false
      },
      "question": {
        "type": "string",
        "description": "Question to ask the vision model about the screenshot"
      }
    }
  }
}
```

### 4.8 handoff_to_agent
```json
{
  "name": "handoff_to_agent",
  "description": "Delegate a task to an external AI coding agent",
  "parameters": {
    "type": "object",
    "properties": {
      "agent": {
        "type": "string",
        "enum": ["claude_code", "cursor", "aider"],
        "description": "Which agent to spawn"
      },
      "task": {
        "type": "string",
        "description": "Clear description of the task for the agent"
      },
      "context_files": {
        "type": "array",
        "items": { "type": "string" },
        "description": "File paths to include in context"
      }
    },
    "required": ["agent", "task"]
  }
}
```

### 4.9 save_memory
```json
{
  "name": "save_memory",
  "description": "Save a fact to long-term memory",
  "parameters": {
    "type": "object",
    "properties": {
      "key": {
        "type": "string",
        "description": "Identifier for this memory e.g. 'project_path'"
      },
      "value": {
        "type": "string",
        "description": "The value to remember"
      }
    },
    "required": ["key", "value"]
  }
}
```

### 4.10 schedule_task
```json
{
  "name": "schedule_task",
  "description": "Create a recurring background task",
  "parameters": {
    "type": "object",
    "properties": {
      "name": {
        "type": "string",
        "description": "Human-readable task name"
      },
      "cron": {
        "type": "string",
        "description": "Cron expression e.g. '0 9 * * *' for 9 AM daily"
      },
      "action": {
        "type": "object",
        "description": "Action payload matching any other tool schema"
      }
    },
    "required": ["name", "cron", "action"]
  }
}
```

---

## 5. Error Response Schema

Any message from core can include an error instead of a normal payload.

```json
{
  "type": "ERROR",
  "id": "echoed-request-id",
  "timestamp": "2026-06-15T09:00:01.000Z",
  "payload": {
    "code": "TOOL_EXECUTION_FAILED",
    "message": "Could not find application 'chome' — did you mean 'chrome'?",
    "tool": "open_application",
    "recoverable": true,
    "suggestion": "Try: 'open chrome'"
  }
}
```

| Error Code | Description |
|---|---|
| `TOOL_EXECUTION_FAILED` | Tool ran but produced an error |
| `SECURITY_BLOCKED` | RED zone block |
| `INJECTION_DETECTED` | Prompt injection in external content |
| `LLM_UNAVAILABLE` | Both Groq and Cerebras down |
| `INVALID_PATH` | File path blocked or invalid |
| `TIMEOUT` | Action exceeded time limit |
| `CONFIRMATION_TIMEOUT` | YELLOW action timed out without confirm |
| `AGENT_SPAWN_FAILED` | Could not launch external agent |
