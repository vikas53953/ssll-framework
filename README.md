# SSLL — Senior-Supervised Learning Loop

> A model-agnostic agent improvement harness that uses external rubric scoring, persistent policy memory, and failure-driven prompt updates to reduce repeat errors over time — without model retraining. Designed for bounded, reviewable operational workflows where improvement can be measured on held-out tasks.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Honest Positioning

SSLL is a **Reflexion-style agent harness** (Shinn et al., 2023) with external-reviewer scoring, atomic binary rubrics, and structural mitigation of self-scoring bias via middleware enforcement.

**What it is:** A prompt-and-policy improvement loop. The student agent adapts its behavior based on scored feedback. Policies persist across sessions. Repeat violations are blocked at pre-flight check.

**What it is not:** A learning agent in the strong RL sense. Policy updates are prompt edits, not weight updates. Improvement over N cycles on adjacent tasks shows local adaptation, not generalization. Proven generalization requires a held-out eval set and ablation — both on the roadmap, neither complete yet.

**Target use case:** Autonomous network-security intelligence lanes (CVE triage, CISA KEV tracking, threat briefings, vendor advisory extraction) where human review doesn't scale and bounded, auditable outputs are acceptable.

**Current state (2026-04-23):** 3 of 5 news lanes producing scored signal. Rubric v3 deployed. 3 cycles scored (89→97→97) on CVE analysis tasks. Eval layer (held-out set, ablation, judge calibration) in progress.

**Prior art to read:**
- Shinn et al. (2023), *Reflexion* — https://arxiv.org/abs/2303.11366 (closest architecture)
- Madaan et al. (2023), *Self-Refine* — https://arxiv.org/abs/2303.17651
- Khattab et al. (2023), *DSPy* — https://arxiv.org/abs/2310.03714
- Bai et al. (2022), *Constitutional AI* — https://arxiv.org/abs/2212.08073 (DNR rules = constitution)
- Zheng et al. (2023), *LLM-as-a-Judge* — https://arxiv.org/abs/2306.05685 (Biff reliability limits)

---

## The Problem This Solves

Most AI agents are stateless. They answer, forget, and repeat the same mistakes next session. At scale — 5 autonomous intelligence lanes running 24/7 — manual correction doesn't work.

SSLL gives an agent a structured feedback loop:
1. Attempt a task
2. Get scored by an **external** reviewer (not itself)
3. Calculate a reward from rubric scores
4. Write a policy update if score < 70
5. Carry policies forward across sessions via persistent memory

Over cycles, the agent reduces repeat failures on bounded task types. "Reduces" — not eliminates.

---

## Overview

SSLL is a prompt-engineering framework. The core idea: instead of one-shot prompting, a **Student agent** attempts tasks repeatedly, receives rubric-based scores from a separate **Senior reviewer**, calculates a reward score, and updates its own policies in a persistent knowledge base.

**Key properties:**
- No model fine-tuning — framework is model-agnostic; performance is model-dependent
- External review only — self-scoring is structurally prohibited and middleware-enforced
- Persistent memory via Obsidian — every episode, policy, and score stored on disk
- Autonomous operation — runs on cron schedule without human intervention
- DNR guardrails — specific failures tracked and blocked at pre-flight check

**Note on "works on any LLM":** The framework is model-agnostic. Actual performance varies by backbone. Memory provider benchmarks show substantial variation by model. Do not assume equal performance across LLMs without testing.

---

## Who Are the Agents?

SSLL uses two agent roles. You can name them anything — in this project they are called **Hermes** (student) and **Biff** (senior).

### Hermes — The Student Agent
The agent that attempts tasks, builds plans, writes evidence-backed answers, and updates its policies based on scored feedback.

### Biff — The Senior Reviewer
A **separate** AI session or human that scores Hermes's work using the rubric. Never the same session as Hermes.

**In practice, Biff can be:**
| Option | How |
|--------|-----|
| Claude (claude.ai or API) | Paste Hermes's output, ask Claude to score using the rubric |
| GPT-4o / GPT-4.1 | Same — paste output, apply rubric prompt |
| A human reviewer | Read the output, fill in the rubric manually |
| A second Hermes instance | Run a separate session with the senior-review prompt |

> The only rule: **Biff must never be the same session as Hermes.** Same-session self-scoring creates a bias loop. Demonstrated gap in cycle-001: self-estimate 95.0, external score 86.0 (9-point overestimate).

> **Note on external LLM judges:** Moving scoring from self to external reduces same-session self-preference bias. It does not eliminate evaluation bias. External LLM judges have documented reliability issues (Zheng et al., 2023). For critical workflows, supplement with periodic human spot-checks.

---

## Architecture

```
User gives task
      │
      ▼
 ┌─────────────────────────────────┐
 │       HERMES (Student)          │
 │                                 │
 │  1. Plan (≤ 6 lines — hard cap)│
 │  2. Draft with cited evidence  │
 │  3. Predict own score (ToM)    │
 │  4. Mark PENDING_REVIEW        │
 └─────────────┬───────────────────┘
               │
               ▼
 ┌─────────────────────────────────┐
 │       BIFF (Senior)             │
 │  (separate AI session / human)  │
 │                                 │
 │  Score rubric (0–5 per dim)    │
 │  Apply atomic sub-checks       │
 │  Give concrete fix per gap     │
 └─────────────┬───────────────────┘
               │
               ▼
        Reward Calculation
        (gated + weighted)
               │
               ▼
   Memory Write + Policy Update
               │
               ▼
          Next Cycle ↺
```

---

## Reward Formula (v3 — canonical)

```
Reward = (Accuracy × 0.30 + Evidence × 0.35 + Reasoning × 0.20 + Clarity × 0.10 + Efficiency × 0.05) × 20
```

Score range: **0–100**. Policy update triggered when reward < 70.

### Scoring Gates (applied before weighted formula)
| Gate | Condition | Cap |
|------|-----------|-----|
| Correctness | Accuracy < 3/5 | Score capped at 50 |
| Evidence floor | Evidence ≤ 2/5 | Score capped at 60 |
| DNR violation | Any DNR rule triggered | Score = 0 |

Gates are non-compensating controls — a strong Evidence score cannot offset a factually wrong answer. Applied in order; lowest cap wins.

### Efficiency Penalty (relative, anchored)
```
efficiency_penalty = max(0, (this_cycle_tool_calls - median_last_5_tool_calls) × 0.5)
Final_Reward = Raw_Reward - efficiency_penalty
```
Penalizes excess tool calls relative to Hermes's own 5-cycle baseline. Skipped if fewer than 5 prior cycles exist.

> **Note on formula consistency:** The v3 formula (weights 30/35/20/10/5) is the canonical version used in all scoring from 2026-04-23 onward. Earlier prompt files and the quickstart example reference a legacy formula (35/25/20/10/10) — those are outdated and being reconciled.

---

## Rubric (v2 — Atomic Sub-Checks)

Each dimension scored via binary sub-checks. Deterministic and reproducible across Biff sessions.

| Dimension | Weight | Sub-checks |
|-----------|--------|------------|
| Accuracy | 30% | Correct claims · No fabricated data · Valid causal chain |
| Evidence | 35% | Article-level URL · Verbatim quote · Quote matches claim |
| Reasoning | 20% | Counterfactual check · Belief revision block · Numeric comparison |
| Clarity | 10% | Structured output · No unexplained jargon |
| Efficiency | 5% | Plan ≤ 6 lines · No padding |

Sub-check scoring: 3/3 → 5, 2/3 → 3, 1/3 → 1, 0/3 → 0. See `prompts/02-19-all-prompts.md` Prompt 10 for full definitions.

**Plan cap — hard constraint:** ≤ 6 lines, no exceptions. Complexity lives in execution detail, not the plan skeleton. This is the Efficiency sub-check Ef1; violating it costs ~7 reward points per cycle.

---

## Core Policies

| Policy | Rule |
|--------|------|
| No self-scoring | All cycles without external review are `PENDING_REVIEW`. Self-estimates never update the Reward Board. |
| Evidence standard | Direct quotes from arXiv, CVEs, or official docs. Homepage links score Evidence = 0. |
| DNR enforcement | Pre-flight check before every cycle. Failed patterns in `policies.md` must not recur. Reduces repeat failures — does not guarantee elimination. |
| Causal framing | "Why it matters" must state domain impact, not just describe the event. |
| Plan cap | Plans must be ≤ 6 lines. Hard constraint. |

---

## Autonomous Operation

Hermes runs on a cron schedule:

- **Every 2 hours (9am–7pm):** Pull task from backlog → run SSLL cycle → mark `PENDING_REVIEW`
- **10:30pm daily:** Send Biff Queue report — all pending cycles for batch scoring

If the backlog is empty, Hermes auto-generates a VERIFIABLE task targeting its weakest rubric dimension.

---

## Memory Layout

```
~/obsidian_notes/
├── episode_log.txt        # Full trace of every cycle (plan → output → scores → reward)
├── Reward-Board.md        # Running scores, weekly moving average, best/worst runs
├── policies.md            # Active prompt policies and DNR list
├── task_backlog.txt       # Unsolved task queue (tagged VERIFIABLE or SOFT)
├── pending_reviews.txt    # Cycles awaiting Biff scoring
└── automations_built.txt  # Auto-built scripts log (Prompt 19)
```

---

## Quickstart — Implement in 5 Steps

### Step 1 — Copy vault template
```bash
cp -r vault-template/* ~/obsidian_notes/
```

### Step 2 — Set up your Student agent (Hermes)

Open your preferred AI agent or chat interface. Paste the contents of [`prompts/01-setup.md`](prompts/01-setup.md) to initialize.

Load all 20 prompts in order from the [`prompts/`](prompts/) folder. Each prompt is a self-contained instruction block.

### Step 3 — Set up your Senior reviewer (Biff)

Open a **separate** AI session (different tab, different account, or a human). This is Biff.

When Hermes marks a cycle `PENDING_REVIEW`, copy the output and paste it to Biff with this prompt:

```
You are Biff, a senior reviewer. Score the following output using this rubric:
- Accuracy (0–5): factual correctness
- Evidence (0–5): direct quotes and article-level citations only
- Reasoning (0–5): causal chain quality
- Clarity (0–5): structure and readability
- Efficiency (0–5): plan brevity (≤6 lines = pass)

For each dimension: give the score and one specific fix if below 5.
Then calculate: Reward = (Acc×0.30 + Ev×0.35 + Reas×0.20 + Clar×0.10 + Eff×0.05) × 20
Apply gates: if Accuracy < 3, cap at 50. If Evidence ≤ 2, cap at 60. If any DNR violation, score = 0.

Output to review:
[PASTE HERMES OUTPUT HERE]
```

### Step 4 — Return the score to Hermes

Copy Biff's scores back to Hermes and tell it to:
- Write the official reward to `Reward-Board.md`
- Update `episode_log.txt` with status: `REVIEWED`
- Apply any policy updates to `policies.md` if score < 70

### Step 5 — Set up autonomous cron jobs

```bash
# Run SSLL cycle every 2 hours from 9am to 7pm
0 9,11,13,15,17,19 * * * <your-hermes-trigger-command>

# Daily Biff Queue report at 10:30pm
30 22 * * * <your-hermes-report-command>
```

---

## Prompt Stack (20 prompts)

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
| 10 | Fixed Rubric | 0–5 scale + atomic sub-check definitions |
| 11 | Reward Formula | Canonical formula (v3) |
| 12 | Weekly Trend Tracking | Moving average maintenance |
| 13 | Output Contract | Mandatory fields per cycle |
| 14 | Global Policies | Causal links, NVD citations, plan caps |
| 15 | Reward Board Expansion | Weekly metrics |
| 16 | Artifact Locations | Canonical file paths |
| 17 | Theory of Mind | Predict scores before review, analyze gap after |
| 18 | Autonomous Sleep Mode | Cron-driven daytime self-improvement |
| 19 | Automation Scout | Auto-detect and build automatable tasks |
| 20 | Plan Approval Gate | Submit plan only, halt until Senior approves |

Full prompt text → [`prompts/`](prompts/)

---

## Key Concepts

| Term | Plain English |
|------|--------------|
| **SSLL** | The full loop: student attempts → senior scores → reward calculated → policy updated → repeat |
| **Student agent (Hermes)** | The AI that attempts tasks and updates policies based on scored feedback |
| **Senior reviewer (Biff)** | A separate AI or human that scores the student's output — never the same session |
| **Rubric** | 5-dimension scoring system (Accuracy, Evidence, Reasoning, Clarity, Efficiency) on a 0–5 scale |
| **Reward** | A single score 0–100 calculated from gated + weighted rubric scores |
| **Gate** | A non-compensating floor — correctness failures cannot be offset by other dimensions |
| **Policy** | A written rule Hermes follows in future cycles — stored in `policies.md` |
| **DNR (Do Not Repeat)** | Specific failures that trigger a pre-flight block before the next cycle |
| **PENDING_REVIEW** | Status assigned to any cycle not yet scored by Biff |
| **Biff Queue** | Nightly report listing all PENDING_REVIEW cycles for batch scoring |
| **Theory of Mind** | Hermes predicts its own score before Biff reviews, analyzes the gap afterward |
| **VERIFIABLE task** | Task with checkable ground truth (CVE analysis, paper comparison) |
| **SOFT task** | Task scored by rubric only, no ground truth (threat briefing, summary) |
| **Episode** | One complete SSLL cycle: plan + attempt + review + reward + memory write |

---

## Real Example

See [`examples/cycle-001.md`](examples/cycle-001.md) — Linear Attention bottleneck analysis.

| | Score |
|---|---|
| Self-estimate (Hermes, before review) | 95.0 |
| External score (Biff, after review) | **86.0** |
| Gap | 9 points |

This gap is why external review is structurally required. The self-preference bias is real and measurable in a single cycle.

---

## Hindsight Memory Integration

Hermes supports [Hindsight](https://github.com/vectorize-io/hindsight) as a memory provider for cross-session persistence of policies, DNR rules, and past cycle feedback.

**Setup:**
```bash
hermes memory setup
# Select option: hindsight

hermes memory status
# Verify: hindsight (long-term, searchable, declarative)
```

**Three operating modes:**
| Mode | Behavior |
|------|---------|
| `hybrid` | Auto-injection before every turn + explicit recall/retain/reflect tools |
| `context` | Auto-injection only |
| `tools` | Explicit tool calls only |

**Recommended mode:** `hybrid`

---

## Shared Backend Relay (Bot-to-Bot Communication)

Telegram blocks bots from reading each other's messages. SSLL uses a shared JSON file as the communication bus.

```
Hermes writes cycle → hive_state.json (PENDING_REVIEW)
                            │
                            ▼
                    Biff reads file directly
                    (WSL filesystem access)
                            │
                            ▼
                    Biff writes score back (REVIEWED)
                            │
                            ▼
              Hermes detects REVIEWED → updates Reward Board
```

**To start the watcher (auto-restarts on crash):**
```bash
python start_watchers.py &
```

---

## Changelog

### v3 — 2026-04-23
- Gated scoring: Accuracy < 3/5 caps at 50 (non-compensating correctness floor)
- Atomic rubric: each dimension decomposed into binary sub-checks
- Relative efficiency penalty: anchored to own 5-cycle baseline
- 90/10 task variance: VERIFIABLE/SOFT task tagging
- README rewritten: overclaims removed, prior art cited, honest positioning

### v2 — 2026-04
- Evidence weight raised to 0.35
- reward_guard.py middleware for self-score enforcement
- hive_state.json relay for bot-to-bot communication
- Hindsight memory integration

### v1 — Initial release
- 20-prompt SSLL stack, DNR enforcement, Reward Board, autonomous cron

---

## Built With

- Student agent: model-agnostic (tested with kimi-k2.6, Gemma, Claude)
- Memory: [Obsidian](https://obsidian.md) + Hindsight
- Scheduling: system cron
- Senior reviewer: Claude, GPT, or human
- Inter-agent relay: shared JSON file via WSL filesystem
- Bias guard: `reward_guard.py`

---

## Author

**Vikas Mittal** — Network Security / DC Engineer, Cisco Systems
GitHub: [@vikas53953](https://github.com/vikas53953)

---

## License

MIT — use freely, attribution appreciated.
