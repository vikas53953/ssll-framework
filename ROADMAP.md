# SSLL Roadmap

## Future Upgrades

### [MEMORY] Replace flat episode_log.txt with SQLite FTS5 backend
**Source:** agentic-stack (https://github.com/codejunkie99/agentic-stack) — v0.8.0, 1.4k stars
**What it solves:** episode_log.txt is a flat file — slow to search, no structured recall. SQLite FTS5 gives fast full-text search across all episodes, structured episodic/semantic/working memory layers, and query-aware retrieval.
**What to borrow:** Their SQLite memory layer + query-aware retrieval pattern.
**What NOT to borrow:** Their review protocol (SSLL's rubric scoring + DNR enforcement is more rigorous). Their multi-adapter support (only relevant if moving off Claude Code).
**Effort:** Medium — requires migrating episode_log.txt ingestion and Hindsight retrieval calls.
**Priority:** Low — current flat file works; upgrade when episode_log grows beyond ~500 entries.

---

### [AGENTS] FortiGate Ops Agent
**What:** Domain-specific SSLL agent for FortiGate firewall ops (policy audits, BGP/OSPF analysis, CVE triage).
**Needs:** soul.md + policies.md for FortiGate domain, separate Telegram channel in Ninja group.
**Priority:** High — next build after Hermes benchmark confirms 85+ avg over full day.

### [AGENTS] MWG Proxy Agent
**What:** Domain-specific SSLL agent for McAfee Web Gateway proxy ops.
**Priority:** Medium.

### [AGENTS] F5 LTM Agent
**What:** Domain-specific SSLL agent for F5 load balancer ops.
**Priority:** Medium.

---

### [INFRA] fcntl.flock() concurrent-access safety on hive_state.json
**What:** File locking to prevent race conditions when multiple agents read/write hive_state.json simultaneously.
**Priority:** Low — only matters when running 2+ domain agents concurrently.

### [INFRA] Cycle quarantine mechanism
**What:** episode_log_quarantine.txt for sub-60 scores excluded from Hindsight retrieval — prevents bad episodes from polluting future context.
**Priority:** Medium.

### [PROMPTS] Prompt 21 — Adaptive Difficulty Ladder (Fail-Improve Loop)
**Source:** GBrain (https://github.com/garrytan/gbrain) — fail-improve loop pattern (intent classifier: 40% → 87% deterministic in 1 week)
**What:** When any atomic sub-check fails 3+ consecutive cycles, auto-generate a VERIFIABLE task targeting that exact sub-check. Also auto-escalate task complexity when avg score stays above 85 for 5 consecutive cycles.
**How it works:**
1. After each cycle, Biff writes failed sub-checks to a `subcheck_failures.json` counter file
2. If any sub-check hits streak ≥ 3, Hermes generates a task: "Fix [sub-check X]: produce output where [specific criterion] passes"
3. Task is tagged VERIFIABLE and inserted at top of task_backlog.txt
4. If all sub-checks passing and avg_score > 85 for 5 cycles → escalate to harder task class
**Why GBrain confirms this works:** Their fail-improve loop took intent classifier from 40% → 87% deterministic in 1 week using the same pattern — log failure → generate targeted fix → measure improvement.
**Effort:** Medium — requires subcheck_failures.json tracking + task generation logic in Hermes startup prompt.
**Priority:** Medium — implement after FortiGate agent is running.

---

### [MEMORY] DNR Knowledge Graph (SQLite)
**Source:** GBrain (https://github.com/garrytan/gbrain) — auto-wired knowledge graph with typed relationships, graph-only F1: 86.6% vs grep's 57.8%
**What:** Lightweight SQLite graph on top of episode_log.txt mapping: task_type → dimension_failed → dnr_rule_triggered → cycle_id. Enables structured queries Hindsight can't answer.
**Example queries this enables:**
- "Which CVE task types trigger DNR-007 most?"
- "Which sub-check fails most on SOFT tasks vs VERIFIABLE tasks?"
- "Show all cycles where Accuracy gate fired (< 3/5)"
**What NOT to borrow:** GBrain's full Postgres/PGLite stack, 26 skills, Supabase/S3 — overkill for SSLL.
**Implementation:** Single Python script `episode_graph.py` — reads episode_log.txt, extracts entities, writes to SQLite. No external dependencies beyond sqlite3 (stdlib).
**Effort:** Medium — parsing episode_log.txt + schema design. Hindsight retrieval unchanged.
**Priority:** Low — implement when episode_log grows beyond ~500 entries or when "which DNR fires most?" becomes a recurring question.
