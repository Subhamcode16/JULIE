# Milestone A Progress

**Goal:** Make Julie's Phase 1 core reliable: package/test setup, security enforcement, memory actions, token tracking, rule-first LLM routing, and end-to-end verification.

## TODO

- [x] Audit the current Milestone A code paths and tests.
- [x] Add `julie` as a Python package.
- [x] Add root pytest configuration for `julie/tests` and `julie` imports.
- [x] Create a project-local `.venv`.
- [x] Update Phase 1 requirements for Python 3.13 compatibility.
- [x] Install the corrected Phase 1 dependencies in `.venv`.
- [x] Stop configuration loading from terminating rule-only/offline startup when no LLM key is present.
- [x] Add concrete action-name mapping for security classification.
- [x] Enforce blocked paths inside file and directory tools.
- [x] Enforce RED/YELLOW policy inside the tool executor.
- [x] Add confirmed execution support for YELLOW actions.
- [x] Add confirmation expiry handling.
- [x] Implement memory save/list execution through SQLite.
- [x] Implement SQLite token usage logging and summaries.
- [x] Add rule-based token summary and memory-list intents.
- [x] Replace the old Groq completion wrapper with an async chat-completions provider interface.
- [x] Add cheap LLM classification for ambiguous requests.
- [x] Add full-brain responses for information/conversation requests.
- [x] Keep rule-based operation available when no LLM key is configured.
- [ ] Add/adjust tests for new memory, token, provider, and security behavior.
- [ ] Run the complete pytest suite and fix all failures.
- [ ] Run targeted SQLite memory/token smoke tests.
- [ ] Run FastAPI/WebSocket end-to-end smoke tests.
- [ ] Run final compile/import checks.
- [ ] Update this tracker with final results and mark Milestone A complete.

## Activity Log

### 2026-06-16

- Audited Julie's PRD, TRD, brain design, implementation plan, core modules, and tests.
- Added `JULIE_HERMES_CAPABILITY_MAP.md` with the approved milestone roadmap.
- Identified Milestone A gaps: imports, missing runtime dependencies, incomplete security enforcement, placeholder memory/token actions, and an outdated Groq wrapper.
- Implemented the initial Milestone A code changes.
- Created `.venv`; initial dependency install was blocked by sandbox networking.

### 2026-06-20

- Resumed from the dependency-install blocker.
- Initial full requirements install failed because Pillow 10.3 and Pydantic 2.7 predate Python 3.13 wheels.
- Split `requirements-phase1.txt` into the actual core/test dependency set.
- Updated core dependency ranges to Python 3.13-compatible versions.
- Installed the corrected requirements successfully into `.venv`.
- Next action: run pytest, repair failures, and add coverage for all new Milestone A paths.

## Verification Results

- Static compilation before dependency installation: passed, with a harmless `.pytest_cache` listing warning.
- Dependency installation: passed on 2026-06-20.
- Pytest suite: not run yet after installation.
- End-to-end WebSocket smoke test: not run yet.

