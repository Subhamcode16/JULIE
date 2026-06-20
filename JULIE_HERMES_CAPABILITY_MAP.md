# Julie x Hermes Capability Map

**Purpose:** Use Hermes Agent as an architectural reference while keeping Julie focused on her own product identity: a local-first Windows AI operating layer with voice, HUD, security zones, and agent handoff.

Julie should not become a clone of Hermes. Hermes is a mature general personal agent that runs across CLI, messaging gateways, desktop, cloud backends, skills, plugins, and scheduled jobs. Julie's sharper niche is Windows-native orchestration: understand intent, protect the machine, route work to the right tool or agent, preserve context, and stay lightweight enough to feel always present.

---

## 1. Current Julie Baseline

### Already Implemented

| Area | Current State |
|---|---|
| Product docs | PRD, TRD, brain architecture, app flow, implementation plan |
| Core API | FastAPI app with WebSocket endpoint |
| Terminal client | WebSocket terminal client with confirmation flow |
| Intent router | Rule-based classifier for common commands |
| Security layer | GREEN / YELLOW / RED classifier and injection scanner |
| Database | SQLite schema for conversations, memories, token usage, scheduled tasks, learned shortcuts |
| Memory helpers | Conversation turn persistence, simple history compression, memory upsert/list helpers |
| System tools | App resolution/launch, terminal command execution, file read/write, directory listing |
| Tests | Initial router, security, tool executor, terminal client, confirmation flow tests |

### Partially Implemented

| Area | Gap |
|---|---|
| Groq client | Basic wrapper exists but does not match the current chat-completions/tool-calling architecture |
| Tool executor | Executes only a subset of system actions |
| Memory | Storage exists, but memory intent does not yet execute through the tool pipeline |
| Security | Path blocking exists as helper logic, but file/tool execution does not consistently enforce it |
| Confirmation | Terminal confirmation exists, but no expiry loop or HUD integration yet |
| Browser tools | File exists, but browser action execution is not wired end-to-end |
| Voice | Listener/speaker modules exist, but the full wake word -> STT -> WebSocket -> TTS loop is not complete |

### Not Yet Implemented

| Area | Needed |
|---|---|
| LLM fallback routing | Cheap classifier, full brain call, tool-call parsing, provider fallback |
| Scheduler | APScheduler-backed task creation, persistence, execution, and notification |
| Agent handoff | Context package builder and Claude/Cursor/CLI agent launcher |
| Screen tools | Screenshot capture and vision analysis |
| HUD | Tauri/React overlay with state, confirmations, and token stats |
| Telegram bridge | Remote control, delivery, security-zone enforcement |
| Skills | Reusable procedural capabilities and self-improvement loop |
| Subagents | Parallel workstreams for research/build/review style tasks |

---

## 2. Hermes Ideas Worth Borrowing

| Hermes Capability | Julie Adaptation |
|---|---|
| Narrow core, capability at edges | Keep Julie core limited to routing, state, security, memory, and execution contracts |
| Skills system | Add `julie/skills/` later for reusable procedures, not as Phase 1 core complexity |
| Messaging gateway | Build Telegram first as a gateway client over Julie's existing WebSocket/API layer |
| Cron automations | Build a local APScheduler service with SQLite persistence and optional delivery targets |
| Session search/memory | Add SQLite FTS before considering embeddings/vector DB |
| Subagent delegation | Treat Claude Code/Cursor/other CLIs as external workers with packaged context |
| Model/provider flexibility | Keep Groq primary, but design an LLM provider interface early |
| Tool gating | Expose tools only when configured and permitted by security zone |
| Command approval | Extend Julie's YELLOW confirmation into a reusable approval contract |
| Context files | Support project-level context packs for handoff and repeated work |

---

## 3. Hermes Ideas To Avoid For Now

| Avoid | Why |
|---|---|
| Full plugin marketplace | Too much surface before Julie's core loop is stable |
| Many messaging platforms at once | Telegram is enough to validate gateway architecture |
| Cloud terminal backends | Julie is intentionally local-first on Windows |
| Large model-tool schema | Every always-present tool increases token cost and routing confusion |
| Autonomous self-modification | Useful later, risky before security and test coverage are mature |
| Heavy memory providers | Start with SQLite and FTS; avoid premature vector/memory infrastructure |
| Multi-user profiles | Out of scope for the personal assistant v1 |

---

## 4. Recommended Architecture Direction

Julie should be shaped around a small set of stable contracts:

1. **Input clients**
   - Terminal
   - Voice process
   - HUD
   - Telegram gateway

2. **Julie core**
   - Intent router
   - Security gate
   - State machine
   - Memory/context assembler
   - Tool executor
   - Event broadcaster

3. **Capability modules**
   - System tools
   - Browser tools
   - Screen tools
   - Scheduler
   - Agent handoff
   - Memory actions
   - Token tracker

4. **Future extension layer**
   - Skills
   - Plugins
   - MCP servers
   - Subagents

The core should route and enforce policy. Capability modules should do work. Skills should teach Julie procedures without forcing new core tools.

---

## 5. Implementation Roadmap

### Milestone A: Make Phase 1 Actually Solid

Goal: Text input can reliably classify, secure, execute, persist, and report.

Priority tasks:

- Fix import/package ergonomics so tests and app startup work consistently.
- Install/standardize test runner dependencies.
- Enforce security path checks inside file operations and tool execution.
- Wire memory intents into `upsert_memory` and `list_memories`.
- Wire token summary intent into token tracker.
- Replace the Groq wrapper with a chat-completions provider interface.
- Add cheap LLM classification for ambiguous intents.
- Add full brain path for INFORMATION and CONVERSATION.
- Add structured tool-call parsing only after direct execution is stable.

Definition of done:

- `python -m pytest julie/tests -q` passes.
- `open chrome`, `list files`, `read file`, `remember that`, and a YELLOW terminal command work from the terminal client.
- RED paths/actions are blocked before execution.

### Milestone B: Browser, Screen, And Scheduler

Goal: Julie can operate beyond local commands.

Priority tasks:

- Implement Playwright browser session manager.
- Add browser actions: navigate, search, scrape, click, fill.
- Sanitize external browser/file content before LLM use.
- Implement screenshot capture with `mss`.
- Add `what is on my screen` as a screen action.
- Implement scheduler persistence and APScheduler execution.
- Add natural-language schedule parsing for common cases first.

Definition of done:

- Browser navigation works from terminal.
- Screenshot capture works.
- A scheduled reminder persists across restart.

### Milestone C: Agent Handoff

Goal: Julie delegates coding and research work without becoming the coding agent.

Priority tasks:

- Create `HandoffContext` model.
- Build context package: task, project path, recent turns, relevant memories, current files.
- Support configurable preferred agent.
- Start with CLI handoff target before Cursor GUI automation.
- Log handoff events and token/cost estimates.

Definition of done:

- "Ask Claude Code to implement X in this project" creates a concise context package and launches the configured agent.

### Milestone D: Voice And HUD

Goal: Julie starts feeling alive on the desktop.

Priority tasks:

- Complete voice process loop: wake word -> record -> Whisper -> WebSocket.
- Complete TTS response queue.
- Build HUD state display over WebSocket.
- Add YELLOW confirmation UI.
- Add token/status badge.

Definition of done:

- "Hey Julie, open Chrome" works end-to-end.
- YELLOW actions are confirmed or canceled through the HUD.

### Milestone E: Telegram Gateway And Automations

Goal: Julie becomes reachable from the phone and useful while unattended.

Priority tasks:

- Build Telegram bot as a gateway client, not a second brain.
- Apply the same security zones to remote commands.
- Deliver task results and screenshots.
- Add scheduler delivery targets.

Definition of done:

- User can send Julie a Telegram command, receive the result, and approve YELLOW actions safely.

### Milestone F: Skills And Learning Loop

Goal: Julie starts gaining procedural memory.

Priority tasks:

- Add a simple `julie/skills/` folder format.
- Let skills define instructions, required tools, and examples.
- Add skill search/list/run commands.
- Add "suggest skill creation" after repeated multi-step workflows.
- Add explicit user approval before saving or modifying a skill.

Definition of done:

- Julie can run a saved procedure like "daily startup check" without expanding the core tool schema.

---

## 6. Immediate Next Build Slice

The next best slice is **Milestone A**. It is the foundation everything else rests on.

Suggested order:

1. Fix test execution and package imports.
2. Harden security enforcement in actual tool execution.
3. Implement memory actions.
4. Implement token tracker summary.
5. Replace Groq client with a proper provider interface.
6. Add LLM classifier only after tests cover rule-first behavior.

This keeps Julie disciplined: local actions first, security always, LLM only when rules cannot decide.

