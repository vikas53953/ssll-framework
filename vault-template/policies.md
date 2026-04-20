# SSLL Global Learning Policies

## Active Policies

- Always utilize cross-lane evidence before finalizing synthesis.
- Reasoning synthesis must include at least one numeric comparison (e.g., accuracy %, memory ratio) between the methods being contrasted.
- Prioritize primary sources over summaries. Mandatory: pull direct quotes from arXiv papers when comparing architectural mechanisms.
- Any lane output without at least one article-level URL (not a homepage) is automatically scored 0 and marked NEEDS_REWORK.
- Every claim must link to the specific article, post, or advisory — never link to a homepage.
- Insert Causal Link pass after evidence aggregation.
- Mandatory NVD citation for every CVE.
- Plan length capped at 6 lines.
- Mandatory Counterfactual Check before final answer on analytical/news outputs.
- Mandatory Belief Revision mini-block (exactly one Before → After with why).
- Mandatory episode recall: retrieve top 3 similar episodes from episode_log.txt before drafting lane output.
- **Hermes does not hold the reward formula. Reward calculation is Biff's exclusive function.**

---

## Do Not Repeat (DNR Table)

| mistake_id | pattern | example | prevention_rule | status |
|------------|---------|---------|-----------------|--------|
| DNR-001 | Lack of causal probe | Reporting CVE and OPS anomaly as separate events | Mandatory causal_link_check after evidence aggregation | active |
| DNR-002 | Fluffy planning | Plans exceeding 8 lines | Strict length cap (max 6 lines) | active |
| DNR-003 | Overconfidence without falsification | Final report has no explicit failure condition | Add Counterfactual Check with 1–2 concrete conditions | active |
| DNR-004 | No explicit belief update | Report presents conclusions without updated model | Add Belief Revision: Before → After (why) mini-block | active |
| DNR-005 | Past mistakes not reused | Same failure repeats across cycles | Inject top-3 similar episodes from episode_log as few-shot context | active |
| DNR-006 | Self-scoring bias | Assigning a final Reward Score without Senior review | Mark as PENDING_REVIEW; only external scores update Reward Board | active |
