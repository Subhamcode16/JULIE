# Julie — App Flow Document
**Version:** 1.0.0  
**Last Updated:** June 2026

---

## 1. System Startup Flow

```
Windows Boot / Julie.exe launched
              │
              ▼
     Load config.toml
     Validate API keys (.env)
              │
              ▼
     Initialize SQLite DB
     Run migrations if needed
              │
              ▼
     Start FastAPI core (port 8765 WS / 8766 HTTP)
              │
              ▼
     Start Voice Process (separate PID)
       ├── Load Whisper tiny model (~2s)
       ├── Load openWakeWord model (~1s)
       └── Connect to core via WebSocket
              │
              ▼
     Launch Tauri HUD overlay (Phase 3+)
       └── Connect to core via WebSocket
              │
              ▼
     ┌─────────────────────────┐
     │   JULIE IS ACTIVE       │
     │   Listening for input   │
     └─────────────────────────┘
```

**Startup target: < 8 seconds from launch to "Julie is ready"**

---

## 2. Primary Input Flow (Voice)

```
[IDLE STATE — wake word listening]
              │
    User says "Hey Julie"
              │
              ▼
    openWakeWord fires event
    HUD pulses: LISTENING state
              │
              ▼
    PyAudio records until:
      ├── 1.5s silence detected
      └── 30s max timeout
              │
              ▼
    Whisper tiny transcribes
    Text sent to core via WebSocket
    (message type: USER_INPUT_VOICE)
              │
              ▼
    ┌─────────────────────────┐
    │   INTENT PROCESSING     │
    └─────────────────────────┘
              │
    [Continue to Flow 4: Intent Processing]
```

---

## 3. Primary Input Flow (Text)

```
User types in HUD text field
or types in terminal (Phase 1)
              │
              ▼
    Input sent directly to core
    (message type: USER_INPUT_TEXT)
              │
              ▼
    ┌─────────────────────────┐
    │   INTENT PROCESSING     │
    └─────────────────────────┘
              │
    [Continue to Flow 4: Intent Processing]
```

---

## 4. Intent Processing Flow

```
Input received (text)
              │
              ▼
    ┌─────────────────────────────┐
    │  SECURITY GATE — PRE-CHECK  │
    │                             │
    │  Scan for injection patterns│
    │  If matched → BLOCK + alert │
    └──────────────┬──────────────┘
                   │ Clean
                   ▼
    ┌─────────────────────────────┐
    │  RULE-BASED CLASSIFIER      │
    │                             │
    │  Pattern match against      │
    │  DIRECT_PATTERNS dict       │
    └──────────────┬──────────────┘
                   │
          ┌────────┴────────┐
          │                 │
        MATCH            NO MATCH
          │                 │
          ▼                 ▼
    Extract params    GROQ API CALL
    Skip LLM          (intent + params)
          │                 │
          └────────┬────────┘
                   │
                   ▼
    ┌─────────────────────────────┐
    │  SECURITY GATE — ACTION     │
    │                             │
    │  Classify action zone       │
    │  GREEN / YELLOW / RED       │
    └──────────────┬──────────────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
      GREEN      YELLOW      RED
        │          │          │
        ▼          ▼          ▼
    Execute    Show in HUD  BLOCK
    directly   5s confirm   alert user
        │          │
        │      User confirms?
        │       YES │  NO
        │          │   │
        │       Execute Cancel
        │          │
        └──────────┘
                   │
                   ▼
    ┌─────────────────────────────┐
    │       TOOL EXECUTOR         │
    └──────────────┬──────────────┘
                   │
    [Continue to Flow 5: Tool Execution]
```

---

## 5. Tool Execution Flows

### 5A: System Action

```
IntentType: SYSTEM_ACTION
              │
              ▼
    Parse extracted params:
      ├── app_name: "chrome"
      ├── action: "open"
      └── args: []
              │
              ▼
    system_tools.py:
      ├── Look up app in Windows registry
      ├── Resolve path: "chrome" → "C:\...\chrome.exe"
      └── subprocess.Popen(path, args)
              │
              ▼
    Result: {success: true, app: "chrome", pid: 1234}
              │
              ▼
    Julie responds: "Chrome is open"
    TTS speaks response
    HUD updates to IDLE
```

### 5B: Browser Action

```
IntentType: BROWSER_ACTION
              │
              ▼
    Playwright: get or create browser context
              │
              ▼
    Parse action:
      ├── navigate → page.goto(url)
      ├── click → page.click(selector)
      ├── fill → page.fill(selector, value)  [YELLOW]
      ├── screenshot → page.screenshot()
      └── scrape → page.inner_text(selector)
              │
              ▼
    Execute Playwright command
              │
    If page content returned:
      └── Sanitize for injection
          └── Pass clean content to LLM if needed
              │
              ▼
    Result returned to core
    Julie responds with outcome
```

### 5C: Agent Handoff

```
IntentType: AGENT_HANDOFF
              │
              ▼
    Detect target agent:
      ├── coding task → Claude Code / Cursor
      ├── search task → browser agent
      └── custom → user-defined agent
              │
              ▼
    Build context package:
      ├── current_directory (from memory)
      ├── recent_files (last 3 accessed)
      ├── task_description (from intent)
      └── conversation_summary (last 5 turns)
              │
              ▼
    Spawn agent CLI:
      subprocess.Popen([
        "claude",          # or "cursor"
        "--context", context_package_path,
        "--task", task_description
      ])
              │
              ▼
    Log token delegation in token_tracker
    Julie responds: "Handed off to Claude Code.
                     Here's what I told it: [summary]"
              │
              ▼
    Monitor agent process
    Report completion to user
```

### 5D: Screen Vision

```
IntentType: SCREEN_ACTION
              │
              ▼
    mss.screenshot() → PIL Image
              │
              ▼
    Compress image (max 1280px wide)
    Base64 encode
              │
              ▼
    Groq API call with vision:
      [image + "What do you see? 
       Answer user question: {query}"]
              │
              ▼
    Response returned
    Julie speaks / displays answer
```

---

## 6. Memory Read/Write Flow

### 6A: Saving a Memory

```
User: "Remember that my project path is D:\projects\julie"
              │
              ▼
    IntentType: MEMORY
              │
              ▼
    Extract key-value:
      key: "project_path"
      value: "D:\projects\julie"
              │
              ▼
    UPSERT into memories table
              │
              ▼
    Julie: "Got it. I'll remember your project path."
```

### 6B: Context Assembly Before Groq Call

```
Groq call triggered
              │
              ▼
    memory.py: build_context()
              │
              ├── Load last 10 conversation turns
              │     └── Compress if > 1500 tokens
              │
              ├── Load top 5 relevant memories
              │     └── Ranked by keyword match to current intent
              │
              └── Load current session state:
                    ├── active_app
                    ├── last_browser_url
                    └── recent_files
              │
              ▼
    Assembled context → prompt_builder.py
    Final prompt → Groq API
```

---

## 7. YELLOW Zone Confirmation Flow

```
Action classified as YELLOW
              │
              ▼
    HUD displays confirmation card:
    ┌─────────────────────────────┐
    │  ⚠️  Julie wants to:        │
    │  Write to: D:\projects\x.py │
    │  Content: [preview...]      │
    │                             │
    │  [CONFIRM ✓]  [CANCEL ✗]   │
    │  Auto-cancels in: 5s        │
    └─────────────────────────────┘
              │
         User action
              │
    ┌─────────┴─────────┐
    │                   │
  Confirm            Cancel / Timeout
    │                   │
  Execute            Log cancelled action
    │                   │
  Report result      Julie: "Cancelled."
```

---

## 8. Scheduled Task Flow

```
User: "Every morning at 9 AM, open my email and summarize new messages"
              │
              ▼
    IntentType: SCHEDULE
              │
              ▼
    Parse cron expression:
      trigger: "every morning at 9 AM" → "0 9 * * *"
      action: {
        type: "browser_action",
        steps: ["navigate gmail", "scrape inbox", "summarize"]
      }
              │
              ▼
    Insert into scheduled_tasks table
    Register with APScheduler
              │
              ▼
    Julie: "Done. I'll check your email every morning at 9 AM
            and give you a summary."
              │
              ▼
    [9:00 AM next day]
              │
    APScheduler fires task
    Execute browser_action steps
    Send result to:
      ├── HUD notification
      └── Telegram message (if enabled)
```

---

## 9. Token Usage Tracking Flow

```
Every Groq/Cerebras API call:
              │
              ▼
    Record before call:
      start_time = now()
              │
              ▼
    API call executes
              │
              ▼
    On response:
      tokens_in  = response.usage.prompt_tokens
      tokens_out = response.usage.completion_tokens
      latency_ms = (now() - start_time).ms
              │
              ▼
    INSERT into token_usage table
              │
              ▼
    Check daily total:
      if daily_tokens > WARNING_THRESHOLD (80% of free tier):
        Julie: "Heads up — you've used 80% of today's 
                Groq token allowance. I'll route more 
                commands without LLM calls."
```

---

## 10. Startup States (HUD)

```
BOOTING   → Tauri window visible, spinner
READY     → Idle, mic icon visible
LISTENING → Blue pulse, waveform active
THINKING  → Yellow pulse, "Julie is thinking..."
SPEAKING  → Green pulse, TTS audio playing
CONFIRMING → Yellow card, YELLOW zone action
EXECUTING → Progress indicator
ERROR     → Red flash, error message
BLOCKED   → Red solid, security block message
```

---

## 11. Error Handling Flows

### LLM API Down
```
Groq call fails
      │
      ▼
Retry once after 2s
      │
  Still fails
      │
      ▼
Switch to Cerebras
      │
  Still fails
      │
      ▼
Rule-based response only
Julie: "My reasoning engine is offline right now.
        I can still handle direct commands like 
        opening apps and browser navigation."
```

### Voice Process Crash
```
Voice process sends no heartbeat for 5s
      │
      ▼
Core detects dead voice process
      │
      ▼
Restart voice process automatically
HUD shows: "Voice restarting..."
      │
      ▼
Voice reconnects via WebSocket
HUD returns to READY
```

### Security Block
```
RED zone action detected
      │
      ▼
Hard block — do NOT call LLM
      │
      ▼
Log attempt to security_log table
      │
      ▼
Julie: "I can't do that. [action] touches 
        protected system areas. 
        If you really need this, type: 
        'julie unlock [action] for this session'"
```
