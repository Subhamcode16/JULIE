---
type: community
cohesion: 0.13
members: 25
---

# Community 6

**Cohesion:** 0.13 - loosely connected
**Members:** 25 nodes

## Members
- [[Any_2]] - code - julie/core/memory.py
- [[Build prompts and context for Groq calls.]] - rationale - julie/brain/prompt_builder.py
- [[Compress conversation history for context assembly.]] - rationale - julie/core/memory.py
- [[Connection_1]] - code - julie/core/memory.py
- [[Format conversation turns into a readable summary.]] - rationale - julie/core/memory.py
- [[Insert a conversation turn into the conversations table.]] - rationale - julie/core/memory.py
- [[Insert or update a memory keyed by 'key'.]] - rationale - julie/core/memory.py
- [[Memory engine for Julie.  Provides async helpers for storing and retrieving co]] - rationale - julie/core/memory.py
- [[Return a list of stored memories.]] - rationale - julie/core/memory.py
- [[Return the most recent conversation turns for a session as dicts.]] - rationale - julie/core/memory.py
- [[Return up to `limit` memories that match the user_input keywords.      Simple]] - rationale - julie/core/memory.py
- [[Summarize older turns using extractive first sentences.]] - rationale - julie/core/memory.py
- [[Use the full prompt path for informationconversation turns.]] - rationale - julie/core/main.py
- [[build_prompt()]] - code - julie/brain/prompt_builder.py
- [[call_full_brain()]] - code - julie/core/main.py
- [[compress_history()]] - code - julie/core/memory.py
- [[extractive_summarize()]] - code - julie/core/memory.py
- [[format_turns()]] - code - julie/core/memory.py
- [[get_recent_turns()]] - code - julie/core/memory.py
- [[get_relevant_memories()]] - code - julie/core/memory.py
- [[list_memories()]] - code - julie/core/memory.py
- [[memory.py]] - code - julie/core/memory.py
- [[prompt_builder.py]] - code - julie/brain/prompt_builder.py
- [[save_conversation_turn()]] - code - julie/core/memory.py
- [[upsert_memory()]] - code - julie/core/memory.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Community_6
SORT file.name ASC
```

## Connections to other communities
- 11 edges to [[_COMMUNITY_Community 22]]
- 5 edges to [[_COMMUNITY_Community 3]]
- 1 edge to [[_COMMUNITY_Community 8]]

## Top bridge nodes
- [[memory.py]] - degree 12, connects to 2 communities
- [[call_full_brain()]] - degree 7, connects to 2 communities
- [[get_recent_turns()]] - degree 7, connects to 1 community
- [[get_relevant_memories()]] - degree 6, connects to 1 community
- [[list_memories()]] - degree 6, connects to 1 community