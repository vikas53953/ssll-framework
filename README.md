# SSLL — Senior-Supervised Learning Loop

A structured, self-improving agent framework where a student agent (Hermes) learns through repeated task cycles reviewed by a senior agent (Biff), scored via a fixed rubric, and stored in a persistent memory system.

## What is SSLL?

SSLL is a reinforcement-style learning loop for AI agents. Instead of training model weights, it iteratively improves the agent's **prompt policies** through:

- Structured attempts at tasks
- External rubric-based scoring (not self-scored)
- Reward calculation from weighted scores
- Policy updates written to a persistent knowledge base
- DNR (Do Not Repeat) guardrails to prevent recurring failures

## Architecture

```
User gives task → Hermes (Student) attempts → Senior (Biff) reviews
     ↑                                                    ↓
Policy updated ← Memory written ← Reward calculated ← Score returned
```

## Reward Formula

```
Reward = (Accuracy×0.35 + Evidence×0.25 + Reasoning×0.20 + Clarity×0.10 + Efficiency×0.10) × 20
```

Scores are on a 0–5 scale per dimension.

## Rubric

| Dimension | Weight | What it measures |
|-----------|--------|-----------------|
| Accuracy | 35% | Factual correctness of the answer |
| Evidence | 25% | Quality and specificity of citations (direct quotes, article-level URLs) |
| Reasoning | 20% | Causal chain quality, counterfactual checks |
| Clarity | 10% | Structure, readability |
| Efficiency | 10% | Plan length, token economy |

## Key Policies

- **No self-scoring**: All cycles without an external senior review are marked `PENDING_REVIEW`. Self-estimates are logged separately and never update the Reward Board.
- **Evidence mandatory**: Direct quotes from arXiv papers, CVE advisories, or official documentation. Homepage-only links score 0.
- **DNR enforced**: Mistakes tracked in a pre-flight checklist. Failed patterns must never recur.
- **Causal-link probes**: "Why it matters" sections must explain network/security impact, not just describe the event.

## Autonomous Loop

Hermes runs every 2 hours during daytime via cron:
- Pulls tasks from `task_backlog.txt`
- Generates novel tasks if backlog is empty (targeting weakest rubric category)
- Marks cycles `PENDING_REVIEW`
- Sends a daily 10:30pm Biff Queue report listing all pending cycles for batch scoring

## Memory Layout (Obsidian)

```
~/obsidian_notes/
├── episode_log.txt       # Full trace of every SSLL cycle
├── Reward-Board.md       # Running scores, moving average, best/worst
├── policies.md           # Current active prompt policies
├── task_backlog.txt      # Queue of unsolved tasks
├── automations_built.txt # Log of auto-built scripts (Prompt 19)
└── pending_reviews.txt   # Cycles awaiting Biff scoring
```

## Quickstart

1. Copy the `vault-template/` folder to `~/obsidian_notes/`
2. Load the prompts from `prompts/` into your agent in order (1 → 19)
3. Set your agent as Hermes (student) and configure a senior reviewer
4. Run Prompt 1 to initialize the loop
5. Set up cron jobs for autonomous daytime cycles (see Prompt 18)

## Prompt Timeline

See `prompts/` directory for all 19 prompts in order.

## Example Run

See `examples/cycle-001.md` for a real scored cycle (Linear Attention, reward: 86.0).

## Author

Built by [@vikas53953](https://github.com/vikas53953) — Network Security / DC Engineer at Cisco Systems.
