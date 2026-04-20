# SSLL — Senior-Supervised Learning Loop

> A structured, self-improving AI agent framework where a student agent learns through repeated task cycles, scored by an external senior reviewer, with persistent memory and autonomous operation.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## The Problem This Solves

Most AI agents give you one answer and move on. If the answer is wrong or shallow, you fix it manually. Next time, the agent makes the same mistake again — it has no memory of what went wrong.

SSLL fixes this. It gives an AI agent the ability to:
1. Attempt a task
2. Get scored by an external reviewer
3. Calculate a reward from the score
4. Write a policy update based on what went wrong
5. Do better next time — automatically

Over 10–20 cycles, measurable improvement appears in the scores. The agent doesn't just answer questions — it **learns how to answer better**.

---

## Overview

SSLL (Senior-Supervised Learning Loop) is a prompt-engineering framework that applies reinforcement-style feedback to improve AI agent outputs over time — without retraining model weights.

The core idea: instead of one-shot prompting, a **Student agent** attempts tasks repeatedly, receives rubric-based scores from an external **Senior reviewer**, calculates a reward score, and updates its own policies in a persistent knowledge base. Over cycles, the agent's outputs measurably improve.

**Key properties:**
- No model fine-tuning required — works on any LLM (Claude, GPT, Gemini, Gemma, etc.)
- External review only — self-scoring is explicitly prohibited to prevent bias loops
- Persistent memory via Obsidian — every episode, policy, and score is stored on disk
- Autonomous operation — runs on a cron schedule without human intervention
- DNR guardrails — mistakes are tracked and blocked at pre-flight check

---

## Who Are the Agents?

SSLL uses two agent roles. You can name them anything — in this project they are called **Hermes** (student) and **Biff** (senior).

### Hermes — The Student Agent
The agent that attempts tasks, builds plans, writes evidence-backed answers, and improves its policies over time. In this project, Hermes runs on a local LLM (Gemma via Ollama) but can be any agent: Claude, GPT, or a custom setup.

### Biff — The Senior Reviewer
Biff is the **external reviewer** that scores Hermes's work. Biff is NOT a separate product — it is simply a second AI session (or a human) that reads the output and applies the rubric.

**In practice, Biff can be:**
| Option | How |
|--------|-----|
| Claude (claude.ai or API) | Paste Hermes's output, ask Claude to score using the rubric |
| GPT-4o / GPT-5 | Same — paste output, apply rubric prompt |
| A human reviewer | Read the output, fill in the rubric manually |
| A second Hermes instance | Run a separate session with the senior-review prompt |

> The only rule: **Biff must never be the same session as Hermes.** Self-scoring creates a bias loop — agents consistently overrate their own work (demonstrated in cycle-001: self-estimate 95.0, external score 86.0).

---

## Architecture

```
User gives task
      │
      ▼
 ┌─────────────────────────────────┐
 │       HERMES (Student)          │
 │                                 │
 │  1. Plan (≤ 8 lines)           │
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
 │  Identify weakest dimension    │
 │  Give concrete fix per gap     │
 └─────────────┬───────────────────┘
               │
               ▼
        Reward Calculation
               │
               ▼
   Memory Write + Policy Update
               │
               ▼
          Next Cycle ↺
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
| DNR enforcement | Pre-flight check before every cycle. Failed patterns in `policies.md` must not recur. |
| Causal framing | "Why it matters" must state domain impact, not just describe the event. |
| Plan cap | Plans must be ≤ 8 lines. |

---

## Autonomous Operation

Hermes runs on a cron schedule:

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

Load prompts 1–19 in order from the [`prompts/`](prompts/) folder. Each prompt is a self-contained instruction block.

### Step 3 — Set up your Senior reviewer (Biff)

Open a **separate** AI session (different tab, different account, or a human). This is Biff.

When Hermes marks a cycle `PENDING_REVIEW`, copy the output and paste it to Biff with this prompt:

```
You are Biff, a senior reviewer. Score the following output using this rubric:
- Accuracy (0–5): factual correctness
- Evidence (0–5): direct quotes and article-level citations only
- Reasoning (0–5): causal chain quality
- Clarity (0–5): structure and readability
- Efficiency (0–5): plan brevity

For each dimension: give the score and one specific fix if below 5.
Then calculate: Reward = (Acc×0.35 + Ev×0.25 + Reas×0.20 + Clar×0.10 + Eff×0.10) × 20

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
| 18 | Autonomous Sleep Mode | Cron-driven daytime self-improvement |
| 19 | Automation Scout | Auto-detect and build automatable tasks |
| 20 | Plan Approval Gate | Hermes submits plan only, halts until Senior approves before executing |

Full prompt text → [`prompts/`](prompts/)

---

## Key Concepts Explained

| Term | Plain English |
|------|--------------|
| **SSLL** | The full loop: student attempts → senior scores → reward calculated → policy updated → repeat |
| **Student agent (Hermes)** | The AI that does the work and learns from feedback |
| **Senior reviewer (Biff)** | A separate AI or human that scores the student's output — never the same session |
| **Rubric** | A fixed 5-dimension scoring system (Accuracy, Evidence, Reasoning, Clarity, Efficiency) on a 0–5 scale |
| **Reward** | A single score 0–100 calculated from the weighted rubric scores |
| **Policy** | A written rule Hermes follows in future cycles — stored in `policies.md` |
| **DNR (Do Not Repeat)** | A list of specific mistakes that must never happen again. Pre-flight check runs before every cycle. |
| **PENDING_REVIEW** | Status assigned to any cycle not yet scored by Biff. Self-estimates are never accepted. |
| **Biff Queue** | The nightly report listing all PENDING_REVIEW cycles so the senior can batch-score efficiently |
| **Theory of Mind** | Hermes predicts its own score *before* Biff reviews, then analyzes the gap afterward — builds self-awareness |
| **Reward Board** | A markdown file tracking all scores, moving average, best/worst runs, and weekly trends |
| **Task Backlog** | A queue of unsolved problems Hermes pulls from during autonomous cycles |
| **Automation Scout** | Prompt 19 — Hermes automatically detects repetitive tasks and builds code to automate them |
| **Episode** | One complete SSLL cycle: plan + attempt + review + reward + memory write |

---

## Real Example

See [`examples/cycle-001.md`](examples/cycle-001.md) — Linear Attention bottleneck analysis.

| | Score |
|---|---|
| Self-estimate (Hermes, before review) | 95.0 |
| External score (Biff, after review) | **86.0** |
| Gap | 9 points |

This 9-point gap is why external review is mandatory. The bias loop is real and measurable.

---

## Hindsight Memory Integration

Hermes supports [Hindsight](https://github.com/vectorize-io/hindsight) as a native memory provider — a structured memory backend with 91.4% recall accuracy on long-horizon benchmarks.

**Why it matters for SSLL:** By default, each cron trigger gives Hermes a fresh context with no memory of past policy violations. Hindsight gives Hermes persistent cross-session memory so it actually remembers its constraints, DNR rules, and past cycle feedback between runs.

**Setup:**
```bash
hermes memory setup
# Select option: hindsight
# Choose: local or API key mode

hermes memory status
# Verify: hindsight (long-term, searchable, declarative)
```

**Three operating modes:**
| Mode | Behavior |
|------|---------|
| `hybrid` | Auto-injection before every turn + explicit recall/retain/reflect tools |
| `context` | Auto-injection only |
| `tools` | Explicit tool calls only (hindsight_recall, hindsight_retain, hindsight_reflect) |

**Recommended mode:** `hybrid` — Hermes automatically loads relevant memories (policies, past failures) before each cycle.

---

## Shared Backend Relay (Bot-to-Bot Communication)

Telegram blocks bots from reading each other's messages. SSLL solves this with a shared JSON file as the communication bus.

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

**Files:**
- `vault-template/hive_state.json` — shared state template
- `hive_watcher.py` — runs on the Biff machine, polls for PENDING_REVIEW and sends Telegram notification

**To start the watcher:**
```bash
# Set your bot token
export TELEGRAM_BOT_TOKEN=your_token_here
export TELEGRAM_CHAT_ID=your_chat_id

python hive_watcher.py
```

If Hermes runs in WSL and Biff runs on the Windows host, the watcher reads `\\wsl$\Ubuntu\home\<user>\obsidian_notes\hive_state.json` directly — no network required.

---

## Built With

- Student agent: any LLM (Gemma, Claude, GPT, etc.)
- Memory: [Obsidian](https://obsidian.md) + Hindsight (persistent cross-session memory)
- Scheduling: system cron
- Senior reviewer: Claude, GPT, or human
- Inter-agent relay: shared JSON file via WSL filesystem
- Bias guard: `reward_guard.py` — auto-sanitizes unauthorized self-scored entries

---

## Author

**Vikas Mittal** — Network Security / DC Engineer, Cisco Systems
GitHub: [@vikas53953](https://github.com/vikas53953)

---

## License

MIT — use freely, attribution appreciated.
