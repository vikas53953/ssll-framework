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

### [PROMPTS] Prompt 21 — Adaptive Difficulty Ladder
**What:** Auto-escalate task complexity when avg score stays above 85 for 5 consecutive cycles.
**Priority:** Medium — implement after FortiGate agent is running.
