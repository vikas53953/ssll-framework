# Cycle 001 — Linear Attention Bottlenecks

**Date:** 2026-04-20  
**Task:** Research the current state of the Linear-Attention mechanism in transformers and identify 3 primary bottlenecks that prevent it from fully replacing Softmax attention in large-scale LLMs.  
**Status:** REVIEWED  
**Senior:** Biff

---

## Plan

1. Research Linear Attention vs Softmax bottlenecks via arXiv and technical blogs
2. Extract architectural differences (rank, stability, convergence)
3. Identify the top 3 bottlenecks
4. Synthesize results and perform self-critique

---

## Output

Based on research (including arXiv:2507.23632), the primary bottlenecks are:

**1. Expressivity & Rank Approximation**
Softmax attention creates a "sharp" focus on specific tokens. Linear attention approximates the kernel, effectively creating a lower-rank representation that cannot replicate this "spike," resulting in lower retrieval precision for specific tokens.

**2. Numerical Stability & Scaling**
Unlike the naturally normalized softmax, linear attention cumulative sums in associative memory can grow unbounded or vanish, requiring complex normalization (e.g., scaling by the sum of keys) which introduces overhead and instability.

**3. Training Convergence & Perplexity**
Linear attention models often demonstrate slower convergence and higher final perplexity. The lack of the exponential term prevents effective "noise filtering" during early training, making them less robust at the scale of modern LLMs.

---

## Rubric Scores (Biff — External Senior)

| Dimension | Score | Notes |
|-----------|-------|-------|
| Accuracy | 5/5 | Three bottlenecks technically correct |
| Evidence | 3/5 | arXiv cited but no direct quotes pulled |
| Reasoning | 4/5 | Good causal structure; retrieval problem needed more depth |
| Clarity | 5/5 | Clean structure |
| Efficiency | 4/5 | Plan appropriate length |

**Reward: (5×0.35 + 3×0.25 + 4×0.20 + 5×0.10 + 4×0.10) × 20 = 86.0**

---

## Policy Update

Mandatory: pull direct quotes from arXiv papers when comparing architectural mechanisms. Evidence score 3/5 → target 5/5 next cycle.

---

## Self-Estimate (before review)

self_estimate: 95.0 — *Note: inflated due to self-scoring bias, illustrating why external review is mandatory.*
