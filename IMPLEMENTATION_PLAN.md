# Julie AI Assistant — Implementation Plan
**Status:** Ready for execution  
**Last Updated:** June 15, 2026  
**Phases:** 4 (4 weeks estimated)

---

## 🎯 FINAL GOAL

Build Julie — a persistent, always-on Windows AI operating layer that routes user intent to the right tool without context switching. Julie orchestrates system actions, browser automation, and agent handoff. She sits between the user and all AI tools, enforcing security, tracking tokens, and learning patterns.

**Success = Single voice/text input → correct tool execution + context preserved + tokens optimized.**

---

## Phase 1: Core Brain & Security (Week 1)

### P1-01: Project Setup
- [ ] Initialize Python 3.11 project structure
- [ ] Create `requirements.txt` with FastAPI, uvicorn, websockets, pydantic, loguru
- [ ] Setup `.env` file template for API keys
- [ ] Initialize SQLite database + migration scripts
- [ ] Create `config.toml` loader for user preferences

**Deliverable:** Project boots, FastAPI server starts on port 8766 (HTTP) + 8765 (WS)

### P1-02: Intent Router Core
- [ ] Build `core/router.py` — rule-based pattern matcher (DIRECT_PATTERNS dict)
- [ ] Implement IntentType enum (SYSTEM_ACTION, BROWSER_ACTION, AGENT_HANDOFF, SCREEN_ACTION, INFO, SCHEDULE, MEMORY, CONVERSATION)
- [ ] Build Groq API wrapper (`brain/groq_client.py`) with retry + fallback to Cerebras
- [ ] Implement zero-LLM patterns: "open X", "navigate to Y", "take screenshot", "remember that Z"

**Deliverable:** Input classification works. Rule-based commands skip LLM.

### P1-03: Security Layer
- [ ] Build `core/security.py` — zone classifier (GREEN / YELLOW / RED)
- [ ] Implement blocked paths registry + permission checks
- [ ] Build prompt injection scanner (regex patterns for jailbreak attempts)
- [ ] Implement confirmation UX for YELLOW actions
- [ ] Block RED actions until explicit unlock

**Deliverable:** All actions classified. RED zone hard-blocks. YELLOW asks for confirmation.

### P1-04: Memory Engine
- [ ] Create SQLite schema (conversations, memories, token_usage, scheduled_tasks, learned_shortcuts)
- [ ] Build `core/memory.py` — read/write/upsert to SQLite
- [ ] Implement context assembly: load last 10 turns + top 5 relevant memories + session state
- [ ] Build conversation compression (keep last 4 turns verbatim, summarize older)
- [ ] Implement token_usage logging per API call

**Deliverable:** Database operational. Context assembled <1100 tokens. Compression works.

### P1-05: Tool Executor Base
- [ ] Build `tools/system_tools.py` — app launcher (Windows registry lookup)
- [ ] Build subprocess runner with output capture + error handling
- [ ] Build file I/O: read, write (with path sanitization), delete
- [ ] Build terminal command execution (marked as YELLOW)

**Deliverable:** Can open apps, run commands, read/write files with security checks.

### P1-06: Text Interface
- [ ] Build terminal input loop (read from stdin → WebSocket to core)
- [ ] Implement WebSocket server that accepts USER_INPUT_TEXT messages
- [ ] Build response formatter (one-liner for actions, bullets for info)
- [ ] Implement error messages + clarification questions

**Deliverable:** Type command in terminal → Julie responds → action executed.

---

## Phase 2: Voice Layer (Week 2)

### P2-01: Voice Process Architecture
- [ ] Create separate `voice/listener.py` process
- [ ] Implement Whisper tiny model loader (~39MB, CPU inference)
- [ ] Implement PyAudio microphone stream capture
- [ ] Build silence detection (auto-stop recording after 1.5s silence)
- [ ] Implement max 30s timeout on recording

**Deliverable:** Can record audio, transcribe with Whisper, send text to core.

### P2-02: Wake Word Detection
- [ ] Load openWakeWord model ("hey julie")
- [ ] Implement always-listening background loop
- [ ] Optimize CPU usage (<5% idle)
- [ ] Build event fire → start recording → send USER_INPUT_VOICE to core

**Deliverable:** Say "hey julie" → recording starts automatically.

### P2-03: Text-to-Speech
- [ ] Build `voice/speaker.py` using edge-tts (en-US-AriaNeural)
- [ ] Implement streaming audio playback via sounddevice
- [ ] Target <300ms first audio latency
- [ ] Add response queue (if Julie is speaking, queue next message)

**Deliverable:** Julie speaks all responses. <300ms time to first audio.

### P2-04: Voice Process IPC
- [ ] Implement WebSocket client in voice process
- [ ] Connect voice → core on startup
- [ ] Send USER_INPUT_VOICE messages with confidence + timing metadata
- [ ] Handle voice process crashes (core detects dead connection, restarts)
- [ ] Implement heartbeat mechanism (5s timeout → auto-restart)

**Deliverable:** Voice process and core communicate. Crashes auto-recover.

### P2-05: Voice Pipeline Integration
- [ ] Wire voice process startup into main.py
- [ ] Test full voice loop: wake word → record → transcribe → route → execute
- [ ] Implement error handling (LLM down → rule-based only, voice down → text fallback)

**Deliverable:** End-to-end voice works. "Hey Julie, open Chrome" → Chrome opens.

---

## Phase 3: HUD Overlay & Scheduler (Week 3)

### P3-01: Tauri Project Init
- [ ] Initialize Tauri 2.x project
- [ ] Setup React + TypeScript frontend
- [ ] Configure Tailwind CSS for styling
- [ ] Create WebSocket client to connect to core

**Deliverable:** Tauri window opens, connects to core via WebSocket.

### P3-02: HUD UI States
- [ ] Build component states: BOOTING, READY, LISTENING, THINKING, SPEAKING, CONFIRMING, EXECUTING, ERROR, BLOCKED
- [ ] Implement waveform animation (CSS) for LISTENING / SPEAKING states
- [ ] Build dark UI with electric accent (matte black + bright cyan/lime)
- [ ] Make window frameless, always-on-top, drag-to-reposition

**Deliverable:** HUD shows all states with animations. Minimally distracting overlay.

### P3-03: Confirmation Dialog
- [ ] Build YELLOW zone confirmation card component
- [ ] Show action summary + preview (e.g., "Write to D:\projects\x.py — [preview]")
- [ ] Auto-cancel timer (5 seconds)
- [ ] Send CONFIRM_ACTION message back to core on user choice

**Deliverable:** YELLOW actions show confirmation. Timer cancels if ignored.

### P3-04: Background Task Scheduler
- [ ] Build `core/scheduler.py` using APScheduler (AsyncIO)
- [ ] Parse natural language cron: "every morning at 9 AM" → "0 9 * * *"
- [ ] Store scheduled_tasks in SQLite
- [ ] Execute tasks on schedule, send results to HUD + Telegram (optional Phase 4)

**Deliverable:** "Remind me every morning at 9 to check email" works.

### P3-05: Status Line Badge
- [ ] Build statusline component showing `[JULIE]` with icon
- [ ] Display token counter after first `/julie-stats` call
- [ ] Update in real-time (WebSocket messages → status update)

**Deliverable:** Bottom of HUD shows status + token usage.

---

## Phase 4: Agent Handoff & Polish (Week 4)

### P4-01: Agent Handoff System
- [ ] Build `tools/agent_handoff.py`
- [ ] Detect coding intent → spawn Claude Code or Cursor with context
- [ ] Package context: project path + recent files + task description + conversation summary
- [ ] Implement agent CLI spawner (subprocess + argument passing)
- [ ] Log token delegation in token_tracker

**Deliverable:** "Build a function that converts X to Y" → spawns Claude Code with full context.

### P4-02: Token Tracker
- [ ] Implement token_usage table queries
- [ ] Build daily/weekly summary on `/julie-stats`
- [ ] Add alerts when approaching free tier limits (80% threshold)
- [ ] Dashboard view: tokens by day / by intent type / by provider

**Deliverable:** `/julie-stats` shows detailed token usage with trends.

### P4-03: Browser Automation Tools
- [ ] Build `tools/browser_tools.py` using **Camoufox** (https://github.com/daijro/camoufox.git) instead of Playwright
- [ ] Implement: navigate, click, fill, screenshot, scrape
- [ ] Add content sanitization (block injection patterns from scraped text)
- [ ] Implement vision pipeline (screenshot + Groq vision API for context)

**Deliverable:** Browser automation works. Can fill forms, scrape pages, analyze screenshots.

### P4-04: Screen Vision
- [ ] Implement `tools/screen_tools.py`
- [ ] Screenshot capture via mss (~<50ms)
- [ ] Image compression (max 1280px wide) + Base64 encoding
- [ ] Groq vision API call with image + question
- [ ] Parse visual response

**Deliverable:** "What's on screen?" → Julie analyzes screenshot and answers.

### P4-05: Telegram Bridge (Optional)
- [ ] Build Telegram bot receiver
- [ ] Implement same security zones (commands via Telegram are YELLOW/RED restricted)
- [ ] Send task results + screenshots to Telegram
- [ ] Allow remote control of Julie from phone

**Deliverable:** Control Julie from Telegram. Receive results on phone.

### P4-06: Polish & Testing
- [ ] Integration test: voice → intent → tool execution (all phases)
- [ ] Error handling audit (LLM down, voice down, network timeout)
- [ ] Performance profiling (startup <8s, wake word <50ms latency, GREEN action <500ms)
- [ ] Documentation + README
- [ ] Create Windows installer (.exe) via PyInstaller + Tauri bundler

**Deliverable:** Shippable, polished, tested end-to-end.

---

## 📊 Dependency Map

```
Phase 1 (Core) ──┐
                 ├─► Phase 2 (Voice) ──┐
                 │                      ├─► Phase 3 (UI/Scheduler) ──┐
                 │                      │                            ├─► Phase 4 (Polish)
                 ├─ SQLite DB ◄────────┴────────────────────────────┤
                 │                                                    │
                 └─► Phase 4 (Agent Handoff) ◄──────────────────────┘
```

**Critical path:** P1-01 → P1-02 → P1-03 → P1-04 → P1-05 → P1-06 → Phase 2+ (parallel after P1)

---

## ✅ Success Criteria

| Metric | Target |
|---|---|
| Phase 1 complete | Text input → intent classification + tool execution |
| Wake word latency | < 50ms after "hey julie" |
| Whisper transcription | < 1.5s for 5s audio |
| Intent accuracy | > 90% on common commands |
| GREEN action time | < 500ms |
| YELLOW confirmation | < 100ms display + 5s timeout |
| Startup time | < 8s (boot to "Julie ready") |
| Groq API latency | < 800ms round trip |
| Token usage | < 20 calls/session typical |
| False RED blocks | < 2% of legitimate commands |

---

## 🛠️ Next Immediate Actions

1. **Create project structure** — mkdir core/ tools/ voice/ brain/ ui/ data/ tests/
2. **Install dependencies** — `pip install -r requirements.txt`
3. **Initialize FastAPI app** — Start with P1-01 (main.py + config loader)
4. **Build router** — Implement P1-02 (pattern matching + Groq wrapper)
5. **Implement security** — P1-03 (zone classifier + injection scanner)
6. **Wire SQLite** — P1-04 (schema + context assembly)
7. **Test loop** — Execute one command end-to-end (text input → app launch)

**Estimated pace:** 4-6 tasks per day across phases. Full MVP by end of Week 4.

---

## 📝 Key Assumptions

- Groq free tier stays available (200ms latency acceptable)
- Windows registry lookup works for app discovery
- Playwright Chromium install succeeds
- User has Whisper tiny model disk space (~39MB)
- fastapi + uvicorn + websockets combo is production-ready for this scale
- SQLite handles 200k+ rows without performance issues

**Risk mitigations:**
- Cerebras API fallback if Groq down
- Rule-based responses if all LLM APIs fail
- Voice gracefully degrades to text if process crashes
- No admin privileges required — run as standard user
