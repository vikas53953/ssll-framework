# SSLL — Senior-Supervised Learning Loop

> A structured, self-improving AI agent framework where a student agent learns through repeated task cycles, scored by an external senior reviewer, with persistent memory and autonomous operation.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Overview

SSLL (Senior-Supervised Learning Loop) is a prompt-engineering framework that applies reinforcement-style feedback to improve AI agent outputs over time — without retraining model weights.

The core idea: instead of one-shot prompting, an agent (Hermes) attempts tasks repeatedly, receives rubric-based scores from an external senior reviewer (Biff), calculates a reward, and updates its own policies in a persistent knowledge base. Over cycles, the agent's outputs measurably improve.

**Key properties:**
- No model fine-tuning required — works on any LLM
- External review only — self-scoring is explicitly prohibited to prevent bias loops
- Persistent memory via Obsidian — every episode, policy, and score is stored
- Autonomous operation — runs on a cron schedule while you're away
- DNR guardrails — mistakes are tracked and enforced at pre-flight

---

## Architecture

```
User gives task
      │
      ▼
 Hermes (Student)
 ┌─────────────────────────────────┐
 │ 1. Plan (≤ 8 lines)            │
 │ 2. Draft with cited evidence   │
 │ 3. Theory of Mind prediction   │
 │ 4. Mark PENDING_REVIEW         │
 └─────────────────────────────────┘
      │
      ▼
 Biff (Senior — External)
 ┌─────────────────────────────────┐
 │ Score rubric (0–5 per dim)     │
 │ Identify weakest dimension     │
 │ Provide concrete fixes         │
 └─────────────────────────────────┘
      │
      ▼
 Reward Calculation
      │
      ▼
 Memory Write → Policy Update → Next Cycle
```

---

## Reward Formula

```
Reward = (Accuracy × 0.35 + Evidence × 0.25 + Reasoning × 0.20 + Clarity × 0.10 + Efficiency × 0.10) × 20
```

Score range: **0–100**. Policy update triggered when reward < 70.

---

## Rubric

| Dimension | Weight | What it measures |
|-----------|--------|-----------------|
| Accuracy | 35% | Factual correctness |
| Evidence | 25% | Direct quotes, article-level citations (no homepages) |
| Reasoning | 20% | Causal chain quality, counterfactual checks |
| Clarity | 10% | Structure and readability |
| Efficiency | 10% | Plan brevity, token economy |

---

## Core Policies

| Policy | Rule |
|--------|------|
| No self-scoring | All cycles without external review are `PENDING_REVIEW`. Self-estimates never update the Reward Board. |
| Evidence standard | Direct quotes from arXiv, CVEs, or official docs. Homepage links score Evidence = 0. |
| DNR enforcement | Pre-flight check before every cycle. Failed patterns listed in `policies.md` must not recur. |
| Causal framing | "Why it matters" must state the domain impact (network/security/infrastructure), not just describe the event. |
| Plan cap | Plans must be ≤ 8 lines. |

---

## Autonomous Operation

Hermes runs on a cron schedule during daytime hours:

- **Every 2 hours (9am–7pm):** Pull task from backlog → run full SSLL cycle → mark `PENDING_REVIEW`
- **10:30pm daily:** Send Biff Queue report — all pending cycles with self-estimates for batch scoring

If the backlog is empty, Hermes auto-generates a task targeting its weakest rubric dimension.

---

## Memory Layout

```
~/obsidian_notes/
├── episode_log.txt        # Full trace of every cycle (plan → output → scores → reward)
├── Reward-Board.md        # Running scores, weekly moving average, best/worst runs
├── policies.md            # Active prompt policies and DNR list
├── task_backlog.txt       # Unsolved task queue
├── pending_reviews.txt    # Cycles awaiting external scoring
└── automations_built.txt  # Auto-built scripts log (Prompt 19)
```

---

## Prompt Stack (19 prompts)

| # | Prompt | Purpose |
|---|--------|---------|
| 1 | Setup | Initialize agents and memory files |
| 2 | Handshaking | Hermes requests senior review |
| 3 | Student Attempt | Plan + evidence-only draft |
| 4 | Senior Review | Rubric scoring + concrete fixes |
| 5 | Reward Calculation | Weighted formula → single score |
| 6 | Memory Write | Log episode to Obsidian |
| 7 | Second Pass | Re-run with updated policy |
| 8 | Daily/Weekly QA | Digests and trend reports |
| 9 | DNR Guardrail | Pre-flight check, no-repeat enforcement |
| 10 | Fixed Rubric | 0–5 scale definition |
| 11 | Reward Formula | Canonical formula |
| 12 | Weekly Trend Tracking | Moving average maintenance |
| 13 | Output Contract | Mandatory fields per cycle |
| 14 | Global Policies | Causal links, NVD citations, plan caps |
| 15 | Reward Board Expansion | Weekly metrics |
| 16 | Artifact Locations | Canonical file paths |
| 17 | Theory of Mind | Predict scores before review, analyze gap after |
| 18 | Autonomous Sleep Mode | Cron-driven overnight/daytime self-improvement |
| 19 | Automation Scout | One-man-show mode: auto-detect and build automatable tasks |

Full prompt text → see [`prompts/`](prompts/)

---

## Quickstart

**1. Copy vault template**
```bash
cp -r vault-template/* ~/obsidian_notes/
```

**2. Load prompts into your agent**
Load prompts 1–19 from the `prompts/` folder in order. Set your agent as Hermes (student).

**3. Configure a senior reviewer**
Assign a separate agent or human as Biff. Biff must be external — never the same instance as Hermes.

**4. Initialize**
Send Prompt 1 to Hermes to initialize the loop and confirm memory files exist.

**5. Set up cron jobs**
```bash
# Autonomous daytime loop (every 2 hours, 9am–7pm)
0 9,11,13,15,17,19 * * * <trigger-hermes> "Autonomous Sleep Mode — Prompt 18"

# Daily Biff Queue report (10:30pm)
30 22 * * * <trigger-hermes> "Send daily SSLL report"
```

---

## Real Cycle Example

See [`examples/cycle-001.md`](examples/cycle-001.md) — Linear Attention bottleneck analysis, officially scored **86.0** by external senior.

Self-estimate before review: 95.0. External score: 86.0. **Gap = 9 points** — exactly why external review is mandatory.

---

## Built With

- Agent: [Gemma / any LLM via Hermes](https://github.com/vikas53953)
- Memory: [Obsidian](https://obsidian.md)
- Scheduling: system cron
- Senior review: Claude (Biff)

---

## Author

**Vikas Mittal** — Network Security / DC Engineer, Cisco Systems  
GitHub: [@vikas53953](https://github.com/vikas53953)

---

## License

MIT
