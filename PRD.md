# Julie — Product Requirements Document (PRD)
**Version:** 1.0.0  
**Author:** Subham Rath  
**Status:** Active  
**Last Updated:** June 2026

---

## 1. Vision

Julie is a persistent, always-on desktop AI operating layer for Windows. She is not a chatbot. She is not a coding assistant. She is the **intent-aware orchestration headroom** that sits between the user and every AI tool, system resource, and autonomous workflow on the machine.

When you need something done, you tell Julie. Julie decides whether to do it herself (system actions) or hand it off to the right agent (Claude Code, Cursor, browser bots). She understands context, tracks token usage across all agents, enforces security, and learns your patterns over time.

The mental model: **Julie is the operating system layer above Windows, purpose-built for AI-native workflows.**

---

## 2. Problem Statement

Power users working with AI tools today face three compounding problems:

**Problem 1 — Context switching tax**  
Switching between Claude, Cursor, browser, terminal, and Notion to accomplish one task costs 5–15 minutes of mental overhead per task. There is no single intent layer that routes correctly.

**Problem 2 — Token waste**  
Users re-explain context to every agent separately. The same project background, file paths, and preferences get typed into Claude Code, then ChatGPT, then a browser agent. This is pure waste.

**Problem 3 — No system-level orchestration**  
No existing AI tool can simultaneously open an application, fill a form in the browser, run a terminal command, and hand off a coding task to the right IDE agent — from a single voice or text command.

---

## 3. Target User

**Primary:** Solo bootstrapped AI systems builders (Subham's archetype)  
- Runs multiple AI agents simultaneously  
- Heavy terminal and browser automation user  
- Optimizes obsessively for token efficiency  
- Works across FastAPI, Python, MongoDB, AWS/Hetzner stacks  
- Needs phone/desktop parity for remote control  

**Secondary:** Power developers, AI researchers, indie hackers  

---

## 4. Core Principles

| Principle | What it means in practice |
|---|---|
| **Julie routes, not solves** | She never becomes the coding agent. She hands off. |
| **Token efficiency first** | Every action is classified before LLM is called. Cheap actions skip the LLM entirely. |
| **Security by default** | No action executes without zone classification. RED zone requires explicit user unlock. |
| **Local first** | STT, TTS, wake word, memory all run locally. Only the LLM call goes to Groq API. |
| **Intent over instruction** | Julie infers what you mean, not just what you say. |

---

## 5. Feature Requirements

### 5.1 Core Features (MVP — Phase 1 & 2)

#### F-01: Voice Interface
- **Wake word detection** — always-listening, local, zero latency ("Hey Julie")
- **Speech-to-text** — Whisper tiny model, local, CPU-capable, <2s transcription
- **Text-to-speech** — edge-tts with `en-US-AriaNeural`, <300ms first audio
- **Text fallback** — keyboard input always available, same pipeline

#### F-02: Intent Router
- Classifies every input into: SYSTEM_ACTION / AGENT_HANDOFF / INFORMATION / CONVERSATION
- SYSTEM_ACTION: execute directly, no LLM call if intent is unambiguous
- AGENT_HANDOFF: spawn correct agent with pre-packaged context
- Uses lightweight Groq API call (Llama 3.1 70B) for ambiguous intents only

#### F-03: System Control
- **App launcher** — open any installed Windows application by name
- **Browser control** — Playwright-driven Chrome: navigate, click, fill forms, scrape
- **File operations** — read, write, move, delete with path sanitization
- **Terminal execution** — run commands via subprocess with output capture
- **Screenshot + vision** — capture screen, send to LLM vision for context

#### F-04: Security Guardrail Layer
- Three-zone classification on every action (GREEN / YELLOW / RED)
- YELLOW actions require 5-second confirmation window
- RED actions hard-blocked by default, require session unlock command
- Prompt injection detection on all external content (browser, files)
- Julie runs as standard Windows user — never holds admin privileges
- Blocked path registry (System32, registry, program files without whitelist)

#### F-05: Agent Handoff
- Detect coding/AI intent → spawn correct agent CLI with context package
- Supported handoff targets: Claude Code, Cursor, any CLI-based agent
- Context package: current file, project path, recent conversation summary
- Token usage logged per handoff session

#### F-06: Memory Layer
- SQLite local database
- Stores: conversation history, learned shortcuts, user preferences, token usage log
- Session context window: last 20 exchanges compressed before each Groq call
- Long-term memory: user-tagged facts persist across restarts

#### F-07: Token Usage Tracker
- Logs every Groq API call: tokens in / tokens out / model / timestamp / intent type
- Daily/weekly summary on request
- Alerts when approaching free tier limits

### 5.2 Extended Features (Phase 3 & 4)

#### F-08: Desktop Overlay HUD
- Tauri frameless window, always-on-top
- Waveform animation when Julie is listening/speaking
- Minimal dark UI — matte black, electric accent
- Drag to reposition, collapse to icon

#### F-09: Background Task Scheduler
- APScheduler-based cron engine
- "Julie, remind me to check deployments every morning at 9"
- Task queue with status visibility in HUD

#### F-10: Telegram Bridge
- Remote control Julie from phone via Telegram bot
- Same security zones apply to Telegram commands
- Receive screenshots, task results on phone

---

## 6. Non-Requirements (Explicit Exclusions)

- Julie will NOT be a coding assistant. She hands off to agents.
- Julie will NOT store data in the cloud. Everything is local SQLite.
- Julie will NOT run as admin. Ever.
- Julie will NOT process audio from other applications (legal/privacy reasons).
- Julie will NOT use OpenAI or Claude APIs as primary LLM (cost constraint).

---

## 7. Success Metrics

| Metric | Target |
|---|---|
| Wake word to first response | < 3 seconds |
| Intent classification accuracy | > 90% on common commands |
| Groq API calls per session | < 20 (smart routing reduces calls) |
| Token usage vs naive chatbot | 60% reduction |
| System action execution time | < 2 seconds for GREEN actions |
| False RED zone blocks | < 2% of legitimate commands |

---

## 8. Phased Delivery

| Phase | Scope | Target |
|---|---|---|
| Phase 1 | Core brain, text interface, system tools, security | Week 1 |
| Phase 2 | Voice layer, wake word, TTS | Week 2 |
| Phase 3 | Tauri HUD overlay, background scheduler | Week 3 |
| Phase 4 | Agent handoff, token tracker, Telegram bridge | Week 4 |

---

## 9. Out of Scope for v1.0

- Multi-user support
- Cross-machine sync
- Mobile app
- Plugin marketplace
- Self-updating skills (planned for v2.0)
