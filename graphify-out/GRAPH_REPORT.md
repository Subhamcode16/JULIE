# Graph Report - .  (2026-06-20)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 859 nodes · 1321 edges · 83 communities (66 shown, 17 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 35 edges (avg confidence: 0.62)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 64|Community 64]]
- [[_COMMUNITY_Community 65|Community 65]]
- [[_COMMUNITY_Community 66|Community 66]]
- [[_COMMUNITY_Community 67|Community 67]]
- [[_COMMUNITY_Community 68|Community 68]]
- [[_COMMUNITY_Community 69|Community 69]]
- [[_COMMUNITY_Community 70|Community 70]]

## God Nodes (most connected - your core abstractions)
1. `execute_intent()` - 19 edges
2. `main()` - 18 edges
3. `main()` - 15 edges
4. `IntentType` - 13 edges
5. `handle_user_input()` - 12 edges
6. `ClassifiedIntent` - 12 edges
7. `SecurityZone` - 12 edges
8. `validate()` - 10 edges
9. `validate()` - 10 edges
10. `main()` - 10 edges

## Surprising Connections (you probably didn't know these)
- `parseModeChange()` --calls--> `getDefaultMode()`  [INFERRED]
  caveman/src/plugins/opencode/plugin.js → caveman/src/hooks/caveman-config.js
- `downloadTo()` --calls--> `require`  [INFERRED]
  caveman/bin/install.js → caveman/tests/installer/unit.settings.test.mjs
- `handleSessionCreated()` --calls--> `getDefaultMode()`  [INFERRED]
  caveman/src/plugins/opencode/plugin.js → caveman/src/hooks/caveman-config.js
- `applyModeChange()` --calls--> `safeWriteFlag()`  [INFERRED]
  caveman/src/plugins/opencode/plugin.js → caveman/src/hooks/caveman-config.js
- `WebSocket` --uses--> `ClassifiedIntent`  [INFERRED]
  julie/core/main.py → julie/core/router.py

## Import Cycles
- None detected.

## Communities (83 total, 17 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.07
Nodes (55): absoluteNodePath(), captureSpawn(), checkNodeVersion(), checkWslWindowsNode(), child_process, copyDirRecursive(), crypto, cursorExtPresent() (+47 more)

### Community 1 - "Community 1"
Cohesion: 0.10
Nodes (20): Path, count_bullets(), extract_code_blocks(), extract_headings(), extract_inline_codes(), extract_paths(), extract_urls(), Line-based fenced code block extractor.      Handles ``` and ~~~ fences with v (+12 more)

### Community 2 - "Community 2"
Cohesion: 0.10
Nodes (29): Path, backup_dir_for(), build_compress_prompt(), build_fix_prompt(), call_claude(), compress_file(), is_sensitive_path(), Strip outer ```markdown ... ``` fence when it wraps the entire output. (+21 more)

### Community 3 - "Community 3"
Cohesion: 0.12
Nodes (29): action_name_for_params(), is_path_blocked(), Check if path is in blocked registry., Return the concrete security action name for a classified intent., execute_intent(), _memory_key_from_fact(), Execute classified intents for Julie., Return a blocking result when an intent is not allowed to execute. (+21 more)

### Community 4 - "Community 4"
Cohesion: 0.09
Nodes (25): require, SETTINGS, addCommandHook(), claudeConfigDir(), crypto, fs, hasCavemanHook(), MANAGED_HOOK_BASENAMES (+17 more)

### Community 5 - "Community 5"
Cohesion: 0.10
Nodes (18): classify_user_input(), Run rule-first classification with optional cheap LLM fallback., ClassifiedIntent, classify_intent(), extract_app_name(), extract_url(), IntentType, Intent classification system. (+10 more)

### Community 6 - "Community 6"
Cohesion: 0.13
Nodes (23): build_prompt(), Build prompts and context for Groq calls., call_full_brain(), Use the full prompt path for information/conversation turns., compress_history(), extractive_summarize(), format_turns(), get_recent_turns() (+15 more)

### Community 7 - "Community 7"
Cohesion: 0.16
Nodes (22): appendFlag(), readHistory(), aggregateHistory(), COMPRESSION, deriveSavings(), findCompressedPairs(), findRecentSession(), formatHistory() (+14 more)

### Community 8 - "Community 8"
Cohesion: 0.13
Nodes (17): answer_with_llm(), classify_with_llm(), GroqClient, LLMResult, parse_classifier_json(), Async Groq chat-completions client for Julie., Classify ambiguous input with a cheap JSON-only LLM call., Generate a concise Julie response for information/conversation turns. (+9 more)

### Community 9 - "Community 9"
Cohesion: 0.20
Nodes (17): Path, count_bullets(), extract_code_blocks(), extract_headings(), extract_inline_codes(), extract_paths(), extract_urls(), Line-based fenced code block extractor.      Handles ``` and ~~~ fences with v (+9 more)

### Community 10 - "Community 10"
Cohesion: 0.20
Nodes (17): Path, count_bullets(), extract_code_blocks(), extract_headings(), extract_inline_codes(), extract_paths(), extract_urls(), Line-based fenced code block extractor.      Handles ``` and ~~~ fences with v (+9 more)

### Community 11 - "Community 11"
Cohesion: 0.13
Nodes (16): compress(), compressDescriptionsInPlace(), FILLERS, HEDGES, LEADERS, PLEASANTRIES, PROTECTED_PATTERNS, withProtectedSegments() (+8 more)

### Community 12 - "Community 12"
Cohesion: 0.20
Nodes (17): Path, count_bullets(), extract_code_blocks(), extract_headings(), extract_inline_codes(), extract_paths(), extract_urls(), Line-based fenced code block extractor.      Handles ``` and ~~~ fences with v (+9 more)

### Community 13 - "Community 13"
Cohesion: 0.11
Nodes (18): author, bin, caveman, bugs, url, description, engines, node (+10 more)

### Community 14 - "Community 14"
Cohesion: 0.27
Nodes (17): Path, CompletedProcess, CheckFailure, ensure(), _frontmatter_description(), load_compress_modules(), read_json(), run() (+9 more)

### Community 15 - "Community 15"
Cohesion: 0.17
Nodes (12): classify_zone(), describe_zone(), Security zone classifier and guardrails., Action security zone., Scan content for prompt injection patterns. Return matched pattern or None., Sanitize content from external sources (web pages, files).          Returns: (, Get human description of zone., Classify action into security zone.      Normalizes action names so callers ma (+4 more)

### Community 16 - "Community 16"
Cohesion: 0.16
Nodes (14): findRepoConfigPath(), fs, getConfigDir(), getConfigPath(), getDefaultMode(), os, path, readModeFromConfigFile() (+6 more)

### Community 17 - "Community 17"
Cohesion: 0.12
Nodes (14): readFlag(), VALID_MODES, { execFileSync }, flagPath, fs, { getDefaultMode, safeWriteFlag, readFlag, VALID_MODES }, INDEPENDENT_MODES, os (+6 more)

### Community 18 - "Community 18"
Cohesion: 0.12
Nodes (15): author, bin, caveman-shrink, description, files, homepage, keywords, license (+7 more)

### Community 19 - "Community 19"
Cohesion: 0.23
Nodes (14): appendBootstrapToSoul(), frontmatterHasKey(), fs, installOpenclaw(), loadBootstrapSnippet(), loadSkillBody(), mergeOpenclawFrontmatter(), os (+6 more)

### Community 20 - "Community 20"
Cohesion: 0.22
Nodes (14): Path, backup_dir_for(), build_compress_prompt(), build_fix_prompt(), call_claude(), compress_file(), is_sensitive_path(), Strip outer ```markdown ... ``` fence when it wraps the entire output. (+6 more)

### Community 21 - "Community 21"
Cohesion: 0.22
Nodes (14): Path, backup_dir_for(), build_compress_prompt(), build_fix_prompt(), call_claude(), compress_file(), is_sensitive_path(), Strip outer ```markdown ... ``` fence when it wraps the entire output. (+6 more)

### Community 22 - "Community 22"
Cohesion: 0.19
Nodes (12): format_execution_response(), get_app_config(), handle_confirmation(), handle_user_input(), Julie core FastAPI application., WebSocket endpoint for UI, voice, and terminal clients., Confirm or cancel a pending YELLOW action., Handle user input from text or voice. (+4 more)

### Community 23 - "Community 23"
Cohesion: 0.23
Nodes (8): build_confirm_action_message(), build_user_input_message(), format_response(), interact(), main(), parse_args(), Namespace, TerminalClientTestCase

### Community 24 - "Community 24"
Cohesion: 0.19
Nodes (9): BaseSettings, JulieConfig, load_config(), SQLite database path., Blocked paths registry., Check required config is present., Load and validate config., Load config from .env and environment variables. (+1 more)

### Community 25 - "Community 25"
Cohesion: 0.29
Nodes (12): call_api(), compute_stats(), dry_run(), format_prompt_label(), format_table(), load_caveman_system(), load_prompts(), main() (+4 more)

### Community 26 - "Community 26"
Cohesion: 0.18
Nodes (9): safeWriteFlag(), applyModeChange(), CavemanPlugin(), config, flagPath, handleSessionCreated(), here, INDEPENDENT_MODES (+1 more)

### Community 27 - "Community 27"
Cohesion: 0.15
Nodes (6): HERE, INSTALLER, REPO_ROOT, requireCjs, SETTINGS, SKILL_BODY_SRC

### Community 28 - "Community 28"
Cohesion: 0.24
Nodes (11): Path, detect_file_type(), _is_code_line(), _is_json_content(), _is_yaml_content(), Return True if the file is natural language and should be compressed., Check if a line looks like code., Check if content is valid JSON. (+3 more)

### Community 29 - "Community 29"
Cohesion: 0.24
Nodes (11): Path, detect_file_type(), _is_code_line(), _is_json_content(), _is_yaml_content(), Return True if the file is natural language and should be compressed., Check if a line looks like code., Check if content is valid JSON. (+3 more)

### Community 30 - "Community 30"
Cohesion: 0.24
Nodes (11): Path, detect_file_type(), _is_code_line(), _is_json_content(), _is_yaml_content(), Return True if the file is natural language and should be compressed., Check if a line looks like code., Check if content is valid JSON. (+3 more)

### Community 31 - "Community 31"
Cohesion: 0.24
Nodes (11): Path, detect_file_type(), _is_code_line(), _is_json_content(), _is_yaml_content(), Return True if the file is natural language and should be compressed., Check if a line looks like code., Check if content is valid JSON. (+3 more)

### Community 32 - "Community 32"
Cohesion: 0.20
Nodes (10): close_db(), init_db(), SQLite database schema and initialization., Initialize database and create schema., Close database connection., Initialize database and log startup., shutdown_event(), startup_event() (+2 more)

### Community 33 - "Community 33"
Cohesion: 0.18
Nodes (8): assert, { execFileSync }, fs, os, path, ROOT, STATS, TRACKER

### Community 34 - "Community 34"
Cohesion: 0.42
Nodes (3): Path, CompressSafetyTests, Tests for the data-loss guards in `compress_file` (issue #237).  The compress

### Community 35 - "Community 35"
Cohesion: 0.20
Nodes (5): HERE, INSTALLER, REPO_ROOT, requireCjs, SETTINGS

### Community 36 - "Community 36"
Cohesion: 0.20
Nodes (7): assert, { execFileSync }, fs, INIT, os, path, ROOT

### Community 37 - "Community 37"
Cohesion: 0.22
Nodes (8): flagPath, fs, { getDefaultMode, safeWriteFlag }, INDEPENDENT_MODES, mode, os, path, settingsPath

### Community 38 - "Community 38"
Cohesion: 0.25
Nodes (7): description, name, owner, name, url, plugins, $schema

### Community 39 - "Community 39"
Cohesion: 0.29
Nodes (5): HERE, REPO_ROOT, requireCjs, SHIPPED_AGENT_FILES, { stripOpencodeAgentTools }

### Community 40 - "Community 40"
Cohesion: 0.29
Nodes (6): description, main, name, private, type, version

### Community 42 - "Community 42"
Cohesion: 0.29
Nodes (5): assert, { compress, compressDescriptionsInPlace }, { getSpawnOptions }, path, ROOT

### Community 43 - "Community 43"
Cohesion: 0.60
Nodes (5): Path, benchmark_pair(), count_tokens(), main(), print_table()

### Community 44 - "Community 44"
Cohesion: 0.60
Nodes (5): Path, benchmark_pair(), count_tokens(), main(), print_table()

### Community 45 - "Community 45"
Cohesion: 0.60
Nodes (5): Path, benchmark_pair(), count_tokens(), main(), print_table()

### Community 46 - "Community 46"
Cohesion: 0.60
Nodes (5): Path, benchmark_pair(), count_tokens(), main(), print_table()

### Community 47 - "Community 47"
Cohesion: 0.53
Nodes (5): count(), fmt_pct(), main(), Read evals/snapshots/results.json (produced by llm_run.py) and report real toke, stats()

### Community 48 - "Community 48"
Cohesion: 0.47
Nodes (5): Any, click(), fill(), navigate(), Browser automation wrappers.

### Community 49 - "Community 49"
Cohesion: 0.60
Nodes (4): claude_version(), main(), Run each prompt through Claude Code in three conditions and snapshot the real L, run_claude()

### Community 50 - "Community 50"
Cohesion: 0.50
Nodes (3): handoff_to_agent(), Agent handoff utilities for Julie., Any

### Community 51 - "Community 51"
Cohesion: 0.50
Nodes (3): Task scheduling placeholder for Julie., schedule_task(), Any

### Community 52 - "Community 52"
Cohesion: 0.67
Nodes (3): count(), main(), Generate a boxplot showing the distribution of token compression per skill, com

### Community 55 - "Community 55"
Cohesion: 0.50
Nodes (3): Voice listener using openWakeWord and Whisper., Start the wake word listener., start_listening()

### Community 56 - "Community 56"
Cohesion: 0.50
Nodes (3): Text-to-speech integration for Julie., Speak text via edge-tts., speak()

## Knowledge Gaps
- **166 isolated node(s):** `$schema`, `name`, `description`, `name`, `url` (+161 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `execute_intent()` connect `Community 3` to `Community 5`, `Community 22`, `Community 6`?**
  _High betweenness centrality (0.004) - this node is a cross-community bridge._
- **Why does `JulieConfig` connect `Community 24` to `Community 8`?**
  _High betweenness centrality (0.004) - this node is a cross-community bridge._
- **Why does `get_config()` connect `Community 8` to `Community 24`, `Community 22`?**
  _High betweenness centrality (0.003) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `IntentType` (e.g. with `ClassifiedIntent` and `Any`) actually correct?**
  _`IntentType` has 7 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Caveman compress scripts.  This package provides tools to compress natural lan`, `Split YAML frontmatter from body. Returns (frontmatter, body).      Memory fil`, `Resolve the out-of-tree backup directory for a given source file.      Backups` to the rest of the system?**
  _288 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.07199032062915911 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.09915966386554621 - nodes in this community are weakly interconnected._