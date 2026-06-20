---
type: community
cohesion: 0.10
members: 30
---

# Community 5

**Cohesion:** 0.10 - loosely connected
**Members:** 30 nodes

## Members
- [[.test_confirm_action_executes_or_cancels()]] - code - julie/tests/test_confirmation_flow.py
- [[.test_confirm_action_executes_pending_intent()]] - code - julie/tests/test_confirmation_flow.py
- [[.test_launch_application_fails_without_binary()]] - code - julie/tests/test_tool_executor.py
- [[.test_navigate_intent()]] - code - julie/tests/test_router.py
- [[.test_open_application_intent()]] - code - julie/tests/test_router.py
- [[.test_terminal_command_runs()]] - code - julie/tests/test_tool_executor.py
- [[.test_unknown_intent_defaults_to_conversation()]] - code - julie/tests/test_router.py
- [[.test_yellow_action_creates_pending()]] - code - julie/tests/test_confirmation_flow.py
- [[ClassifiedIntent_1]] - code - julie/core/router.py
- [[ClassifiedIntent]] - code - julie/core/main.py
- [[Classify user input into an intent type.          Returns high-confidence clas]] - rationale - julie/core/router.py
- [[ConfirmationFlowTestCase]] - code - julie/tests/test_confirmation_flow.py
- [[Enum]] - code
- [[Extract URL from text like 'go to gmail' or 'navigate to github.com'.]] - rationale - julie/core/router.py
- [[Extract app name from text like 'open chrome' or 'launch vs code'.]] - rationale - julie/core/router.py
- [[Intent classification system.]] - rationale - julie/core/router.py
- [[Intent classification types.]] - rationale - julie/core/router.py
- [[IntentType]] - code - julie/core/router.py
- [[Result of intent classification.]] - rationale - julie/core/router.py
- [[RouterTestCase]] - code - julie/tests/test_router.py
- [[Run rule-first classification with optional cheap LLM fallback.]] - rationale - julie/core/main.py
- [[ToolExecutorTestCase]] - code - julie/tests/test_tool_executor.py
- [[classify_intent()]] - code - julie/core/router.py
- [[classify_user_input()]] - code - julie/core/main.py
- [[extract_app_name()]] - code - julie/core/router.py
- [[extract_url()]] - code - julie/core/router.py
- [[router.py]] - code - julie/core/router.py
- [[test_confirmation_flow.py]] - code - julie/tests/test_confirmation_flow.py
- [[test_router.py]] - code - julie/tests/test_router.py
- [[test_tool_executor.py]] - code - julie/tests/test_tool_executor.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Community_5
SORT file.name ASC
```

## Connections to other communities
- 10 edges to [[_COMMUNITY_Community 3]]
- 9 edges to [[_COMMUNITY_Community 22]]
- 3 edges to [[_COMMUNITY_Community 15]]
- 2 edges to [[_COMMUNITY_Community 8]]

## Top bridge nodes
- [[IntentType]] - degree 13, connects to 2 communities
- [[router.py]] - degree 12, connects to 2 communities
- [[ClassifiedIntent_1]] - degree 12, connects to 2 communities
- [[classify_user_input()]] - degree 9, connects to 2 communities
- [[classify_intent()]] - degree 8, connects to 1 community