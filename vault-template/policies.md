# SSLL Global Learning Policies

## Reward Formula (updated per Opus 4.7 recommendation)
```
Reward = (Accuracy×0.30 + Evidence×0.35 + Reasoning×0.20 + Clarity×0.10 + Efficiency×0.05) × 20
```
- Evidence is the highest-weighted dimension (0.35) — the most-failed dimension
- If Evidence ≤ 2/5, cap total score at 60 regardless of other scores
- Any DNR violation = cycle score 0, no partial credit

---

## Active Policies

- Always utilize cross-lane evidence before finalizing synthesis.
- Reasoning synthesis must include at least one numeric comparison (e.g., accuracy %, memory ratio) between the methods being contrasted.
- Prioritize primary sources over summaries. Mandatory: pull direct quotes from arXiv papers when comparing architectural mechanisms.
- Any lane output without at least one article-level URL (not a homepage) is automatically scored 0 and marked NEEDS_REWORK.
- Every claim must link to the specific article, post, or advisory — never link to a homepage.
- Insert Causal Link pass after evidence aggregation.
- Mandatory NVD citation for every CVE. For ALERTS: link to individual advisory page, not the advisory directory.
- Plan length capped at 6 lines.
- Mandatory Counterfactual Check before final answer on analytical/news outputs.
- Mandatory Belief Revision mini-block (exactly one Before → After with why).
- Mandatory episode recall: retrieve top 3 similar episodes from episode_log.txt before drafting lane output.
- **Hermes does not hold the reward formula. Reward calculation is Biff's exclusive function.**
- **Reward Board run_count and avg_score must always be computed by reading episode_log.txt and counting entries with status: REVIEWED. Never add to a remembered total.**
- **FOR arXiv PAPERS:** Use ar5iv HTML endpoint (`https://ar5iv.labs.arxiv.org/html/[ID]`) instead of PDF links. HTML renders cleanly; PDFs get truncated.
- **FOR SECURITY ANALYSIS:** Always prioritize direct vendor security bulletins over secondary aggregation sources.
- **Causal chain required:** After identifying a finding, add one sentence: "What this means for network/security operations: [specific impact]"

---

## Do Not Repeat (DNR Table)

| mistake_id | pattern | example | prevention_rule | status |
|------------|---------|---------|-----------------|--------|
| DNR-001 | Lack of causal probe | Reporting CVE and OPS anomaly as separate events | Mandatory causal_link_check after evidence aggregation | active |
| DNR-002 | Fluffy planning | Plans exceeding 6 lines | Strict length cap (max 6 lines) | active |
| DNR-003 | Overconfidence without falsification | Final report has no explicit failure condition | Add Counterfactual Check with 1–2 concrete conditions | active |
| DNR-004 | No explicit belief update | Report presents conclusions without updated model | Add Belief Revision: Before → After (why) mini-block | active |
| DNR-005 | Past mistakes not reused | Same failure repeats across cycles | Inject top-3 similar episodes from episode_log as few-shot context | active |
| DNR-006 | Self-scoring bias | Assigning a final Reward Score without Senior review | Mark as PENDING_REVIEW; only external scores update Reward Board | active |
| DNR-007 | Fabricated citations | Generating a URL or quote that cannot be verified from a real source | Only cite sources retrieved via actual search; state "No primary source located" if none found | active |
| DNR-008 | Running total memory drift | Computing run_count or avg_score from memory instead of reading episode_log.txt | Always read episode_log.txt, count REVIEWED entries, compute fresh | active |
