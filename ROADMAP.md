# SSLL Roadmap

## Honest Current State (2026-04-23)
- 3 of 5 lanes producing signal (TECH+SEC 42, X TRENDS 78, ALERTS 62)
- 2 lanes non-functional (AI NEWS 0, DAILY NEWS 0) — prompt fixes deployed, pending next cron
- Rubric v3 deployed (gated scoring, atomic sub-checks, 90/10 task variance)
- 3 cycles scored: 89 → 97 → 97. Not a learning curve yet — 3 data points on different tasks is noise.
- No held-out eval set. No ablation. No reviewer agreement metric. No DNR compliance rate.

## Priority 1 — Evidence Layer (before any domain agents)

### [EVAL] Held-out eval set (20 fixed tasks)
**Why:** Without this, score changes measure task variance, not learning. Same 20 tasks must be run at cycle 1, 10, 20, 50. If scores on the fixed set rise over time, that's evidence of learning. Otherwise it's prompt iteration.
**Design:** 10 CVE analysis tasks + 5 paper comparison tasks + 5 threat briefings. Fixed inputs, never changed.
**Metric:** Mean score on held-out set ± std. Run before and after every major rubric/policy change.
**Priority:** CRITICAL — implement before claiming improvement.

### [EVAL] Gold-standard human scoring (20 cycles)
**Why:** When Biff scores 97, how do we know 97 is correct? Need Vikas to manually score 20 outputs, compute Pearson r with Biff. Target r > 0.8. If r < 0.8, Biff's rubric interpretation is drifting.
**Method:** Pick 20 diverse cycles. Score independently. Compare. Rerun quarterly.
**Priority:** CRITICAL — without this, reward signal has unknown validity.

### [EVAL] Ablation study
**Why:** Run 1 week with policy updates enabled, 1 week disabled (control arm). Score delta = actual learning signal. If experimental doesn't beat control by > noise, "learning" is just prompt tuning.
**Method:** Disable policies.md writes for 1 week. Compare avg scores. Publish delta.
**Priority:** High — confirms whether SSLL's core loop actually works.

### [EVAL] Second-reviewer audit (10% of cycles)
**Why:** Biff is Claude grading Claude. Reward signal ceiling = Claude's ability to judge. Need independent reviewer to detect systematic bias.
**Method:** Every 10th cycle, score with GPT-4.1 or Gemini 2.5. Compute Cohen's kappa with Biff. If kappa < 0.7, rubric needs redesign.
**Priority:** High — especially for novel security reasoning where Claude may be blind-leading-blind.

### [TELEMETRY] DNR compliance rate
**Why:** "DNR rules persist and block violations" is unverified. What's the measured compliance rate across 50+ cycles?
**Method:** Parse reward_guard_violations.txt + episode_log.txt. Compute per-rule trigger rate, bypass rate, false-positive rate.
**Priority:** High — if DNR compliance rate is unknown, DNR layer is aspirational not functional.

---

## Priority 2 — Academic Grounding

### [DOCS] Cite prior art properly
SSLL is a Reflexion-style loop (Shinn et al., 2023) with external-reviewer scoring and policy persistence. Not novel RL. Cite:
- **Reflexion** (Shinn et al., 2023) — closest prior art. https://arxiv.org/abs/2303.11366
- **Self-Refine** (Madaan et al., 2023) — where self-critique works and where it doesn't. https://arxiv.org/abs/2303.17651
- **DSPy** (Khattab et al., 2023) — formal treatment of prompt optimization. https://arxiv.org/abs/2310.03714
- **Constitutional AI** (Bai et al., 2022) — DNR rules are a constitution; read how Anthropic handles gaming. https://arxiv.org/abs/2212.08073
- **LLM-as-a-Judge** (Zheng et al., 2023) — directly relevant to Biff-as-reviewer question. https://arxiv.org/abs/2306.05685

### Honest one-paragraph pitch (approved 2026-04-23)
"SSLL is a Reflexion-style agent harness with external-reviewer scoring, atomic binary rubrics, and structural mitigation of self-scoring bias via middleware enforcement. It operates on prompt/policy updates rather than model retraining. Contributions: gated scoring with Accuracy as a non-compensating floor, VERIFIABLE/SOFT task tagging to prevent score inflation across task types, and relative efficiency baselines. Target domain: autonomous network-security intelligence lanes where human review doesn't scale. Current state: 3 lanes producing signal, 2 lanes failing, rubric v3 deployed. Next milestone: held-out eval set + ablation to measure actual learning."

---

## Priority 3 — Lane Agent Fixes

### [LANES] AI NEWS + DAILY NEWS (0/100 → target 40+)
SSLL feedback injected into lane prompts (2026-04-23). Takes effect next 9am cron.
Root cause: [SILENT] output = zero article-level URLs found. Fix: minimum 3 article-level URLs required.

### [LANES] TECH+SEC (42/100 → target 65+)
Fix: remove speculation language from prompt. Deployed.

### [LANES] ALERTS (62/100 → target 80+)
Fix: mandatory Confidence: High/Medium/Low per item. Deployed.

---

## Priority 4 — Infra

### [PROMPTS] Prompt 21 — Adaptive Difficulty Ladder (Fail-Improve Loop)
**Source:** GBrain fail-improve loop pattern
**What:** When any atomic sub-check fails 3+ consecutive cycles → auto-generate VERIFIABLE task targeting that sub-check. Escalate difficulty when avg > 85 for 5 cycles.
**Priority:** Medium — after eval layer is in place.

### [MEMORY] DNR Knowledge Graph (SQLite)
**Source:** GBrain knowledge graph pattern
**What:** SQLite graph over episode_log.txt: task_type → dimension_failed → dnr_rule_triggered. Enables structured queries across cycles.
**Priority:** Low — when episode_log > 500 entries.

### [MEMORY] Replace episode_log.txt with SQLite FTS5
**Source:** agentic-stack
**Priority:** Low — when episode_log > 500 entries.

### [INFRA] fcntl.flock() on hive_state.json
**Priority:** Low — only matters with 2+ concurrent agents.

### [INFRA] Cycle quarantine mechanism
**What:** episode_log_quarantine.txt for sub-60 scores, excluded from Hindsight retrieval.
**Priority:** Medium.

---

## Priority 5 — Domain Agents (after eval layer confirmed)

### [AGENTS] FortiGate Ops Agent
**Priority:** High — but only after ablation confirms SSLL learning signal is real.

### [AGENTS] MWG Proxy Agent
**Priority:** Medium.

### [AGENTS] F5 LTM Agent
**Priority:** Medium.
