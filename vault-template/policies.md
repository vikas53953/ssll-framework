# SSLL Active Policies

## Evidence
- Mandatory: pull direct quotes from arXiv papers when comparing architectural mechanisms
- All lane outputs must include article-level URLs (not homepages). Homepage-only links score 0.
- For ALERTS: must link to individual advisory page (e.g., /advisories/aa24-xxx), not the advisory directory

## Review Integrity
- Senior Review must never be self-scored
- If no external senior is available, mark cycle PENDING_REVIEW
- Self-review scores logged as self_estimate only — never update Reward Board

## Reasoning
- Every "why it matters" section must state the network/security implication, not just describe the event
- Causal-link probes required: explicitly state the mechanism from cause to effect

## Planning
- Plans must be ≤ 8 lines
- NVD/CVE claims require article-level advisory URL

## DNR (Do Not Repeat)
- Do not submit homepage URLs as evidence
- Do not self-score and write to Reward Board without external review
