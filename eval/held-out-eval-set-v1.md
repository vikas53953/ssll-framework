# SSLL Held-Out Eval Set — v1

**Purpose:** Measure actual learning signal. Run baseline Hermes (no policies) vs SSLL Hermes (with policies) on the same fixed tasks. Score delta = measured improvement.

**Rules:**
- These tasks are FROZEN. Never modify after first run.
- Run with identical rubric and judge prompt every time.
- Score with Biff (Claude) AND record for human audit (Vikas).
- Record: exact score per dimension, reward, DNR violations, tool call count, output length.
- Rerun at: baseline (cycle 0), cycle 10, cycle 20, cycle 50.

**Judge prompt (frozen):**
```
You are Biff, a senior reviewer. Score using the v3 rubric:
- Accuracy (0–5): correct claims · no fabricated data · valid causal chain
- Evidence (0–5): article-level URL · verbatim quote · quote matches claim
- Reasoning (0–5): counterfactual check · belief revision · numeric comparison
- Clarity (0–5): structured · no unexplained jargon
- Efficiency (0–5): plan ≤6 lines · no padding

Gates (apply first): Accuracy < 3 → cap 50. Evidence ≤ 2 → cap 60. DNR violation → score 0.
Formula: (Acc×0.30 + Ev×0.35 + Reas×0.20 + Clar×0.10 + Eff×0.05) × 20

For each dimension: score + one-line justification. Then final reward.
```

---

## Task Set A — CVE Analysis (20 tasks)
*VERIFIABLE — ground truth checkable against NVD + vendor advisories*

| # | Task | Expected dimensions to stress |
|---|------|-------------------------------|
| A-01 | Analyze CVE-2025-24813 Apache Tomcat path equivalence RCE. CVSS vector, affected versions, causal chain, CISA KEV status. | Evidence (verbatim quotes), Reasoning (causal chain) |
| A-02 | Analyze CVE-2025-31161 CrushFTP authentication bypass. CVSS, affected versions v10/v11, exploitation mechanism, ransomware nexus. | Accuracy (version ranges), Evidence |
| A-03 | Analyze CVE-2025-32433 Erlang/OTP SSH unauthenticated RCE. CVSS 10.0, affected OTP versions, why it matters for telecom infrastructure. | Reasoning (numeric comparison), Evidence |
| A-04 | Analyze CVE-2024-6387 OpenSSH regreSSHion. CVSS, race condition mechanism, affected glibc vs non-glibc systems, patch status. | Accuracy (glibc condition), Reasoning |
| A-05 | Analyze CVE-2024-3400 PAN-OS GlobalProtect command injection. CVSS 10.0, affected versions, exploitation evidence, Volexity report. | Evidence (Volexity source), Accuracy |
| A-06 | Analyze CVE-2024-21762 FortiOS out-of-bounds write. CVSS, affected FortiOS versions, CISA KEV status, mitigation. | Accuracy (version ranges), Evidence |
| A-07 | Analyze CVE-2023-44487 HTTP/2 Rapid Reset DDoS. CVSS, mechanism, affected server implementations, coordinated disclosure date. | Reasoning (numeric: attack rate comparison), Clarity |
| A-08 | Analyze CVE-2023-20198 Cisco IOS XE web UI privilege escalation. CVSS 10.0, affected versions, CISA KEV, implant deployment evidence. | Evidence (Cisco Talos source), Accuracy |
| A-09 | Analyze CVE-2021-44228 Log4Shell. CVSS 10.0, JNDI injection mechanism, affected versions, patch timeline, why it was uniquely dangerous. | Reasoning (scope of impact), Evidence |
| A-10 | Analyze CVE-2022-30190 Follina MSDT RCE. CVSS, Office version scope, zero-click vector, nation-state use. | Accuracy (zero-click claim), Evidence |
| A-11 | Analyze CVE-2024-55591 FortiOS authentication bypass. CVSS, affected versions, exploitation in wild, mitigation options. | Accuracy, Evidence |
| A-12 | Analyze CVE-2024-23897 Jenkins arbitrary file read. CVSS, affected versions, exploitation chain to RCE, patch. | Reasoning (RCE chain), Evidence |
| A-13 | Analyze CVE-2023-34048 VMware vCenter Server OOB write. CVSS, affected versions, PoC availability, active exploitation evidence. | Evidence (PoC source), Accuracy |
| A-14 | Analyze CVE-2024-1709 ConnectWise ScreenConnect auth bypass. CVSS 10.0, affected versions, exploitation timeline, ransomware nexus. | Evidence (ransomware link), Accuracy |
| A-15 | Analyze CVE-2024-27198 JetBrains TeamCity auth bypass. CVSS, affected versions, exploitation by APT groups, patch. | Reasoning (APT attribution sourcing), Evidence |
| A-16 | Analyze CVE-2023-42793 JetBrains TeamCity pre-auth RCE. CVSS, affected versions, difference from CVE-2024-27198, APT29 exploitation. | Accuracy (distinguish from sister CVE), Reasoning |
| A-17 | Analyze CVE-2024-21893 Ivanti Connect Secure SSRF. CVSS, affected products, chain with CVE-2023-46805, CISA advisory. | Reasoning (chained exploit), Evidence |
| A-18 | Analyze CVE-2022-22965 Spring4Shell. CVSS, affected Spring versions, exploitation conditions (JDK 9+, WAR deployment), comparison to Log4Shell severity. | Reasoning (numeric comparison vs Log4Shell), Accuracy |
| A-19 | Analyze CVE-2023-23397 Microsoft Outlook privilege escalation. CVSS, zero-click mechanism, affected Outlook versions, NTLM leak chain. | Accuracy (zero-click mechanism), Evidence |
| A-20 | Analyze CVE-2024-38112 Windows MSHTML spoofing. CVSS, exploitation via .url files, affected Windows versions, APT use. | Evidence (APT sourcing), Reasoning |

---

## Task Set B — Paper/Research Analysis (10 tasks)
*VERIFIABLE — checkable against paper abstract, results sections*

| # | Task | Expected dimensions to stress |
|---|------|-------------------------------|
| B-01 | Summarize Reflexion (Shinn et al., 2023) key contribution, benchmark results, and how it differs from fine-tuning. Verbatim quote required from abstract. | Evidence (verbatim), Accuracy |
| B-02 | Compare Self-Refine (Madaan et al., 2023) vs Reflexion: same idea or different? What does Self-Refine require that Reflexion doesn't? | Reasoning (comparison), Accuracy |
| B-03 | Summarize DSPy (Khattab et al., 2023): what is prompt compilation and how does it differ from manual prompt engineering? | Clarity, Accuracy |
| B-04 | What does Zheng et al. (2023) LLM-as-a-Judge find about self-preference bias in LLM judges? Quote the key finding. | Evidence, Accuracy |
| B-05 | Summarize Constitutional AI (Bai et al., 2022): what is a constitution in this context and how does RLAIF work? | Accuracy, Clarity |
| B-06 | Compare Perplexity's gated reward (2026 paper) to a simple weighted average. What specific problem does gating solve? | Reasoning (numeric), Evidence |
| B-07 | What does MemoryAgentBench measure that simple recall benchmarks miss? Why does this matter for multi-session agents? | Reasoning, Accuracy |
| B-08 | Summarize Voyager (Wang et al., 2023): what is the skill library, how does it grow, and why does it not require weight updates? | Accuracy, Evidence |
| B-09 | What is the core finding of Generative Agents (Park et al., 2023) regarding memory and planning? Verbatim quote from abstract. | Evidence (verbatim), Accuracy |
| B-10 | What is Cohen's kappa and when should it be used vs Pearson r for inter-rater agreement? Give a numeric example. | Reasoning (numeric), Clarity |

---

## Task Set C — Network/Security Ops (10 tasks)
*VERIFIABLE — checkable against vendor docs, CISA advisories*

| # | Task | Expected dimensions to stress |
|---|------|-------------------------------|
| C-01 | What FortiOS versions are affected by CVE-2024-21762 and what is the recommended mitigation per Fortinet's advisory? Verbatim quote required. | Evidence, Accuracy |
| C-02 | Explain the difference between SSL-VPN and IPsec VPN in FortiGate from a security posture perspective. Which attack surface is larger and why? | Reasoning, Clarity |
| C-03 | What does CISA's Known Exploited Vulnerabilities catalog require of federal agencies under BOD 22-01? Quote the binding requirement. | Evidence, Accuracy |
| C-04 | Explain how HTTP/2 multiplexing enables the Rapid Reset attack. What numeric rate made CVE-2023-44487 notable? | Reasoning (numeric), Accuracy |
| C-05 | What is the difference between a CVSS base score and a CVSS environmental score? When should an operator use environmental scoring? | Clarity, Accuracy |
| C-06 | Explain why CVE-2025-24813 requires both partial PUT enabled AND file-based session persistence for RCE. What does this precondition mean for default Tomcat deployments? | Reasoning (causal chain), Accuracy |
| C-07 | What is the McAfee Web Gateway (MWG) SSL inspection policy and what security tradeoff does it introduce? | Clarity, Accuracy |
| C-08 | Explain BGP route hijacking: mechanism, a real-world example with dates, and what RPKI does to mitigate it. | Evidence (real example), Reasoning |
| C-09 | What is Cisco's SD-WAN vManage attack surface? Name two CVEs affecting vManage from 2023-2024 with their CVSS scores. | Evidence (CVE citations), Accuracy |
| C-10 | What is the F5 BIG-IP iControl REST API and what vulnerability class most commonly affects it? Name one CVE example. | Accuracy, Evidence |

---

## Task Set D — Threat Intel Briefing (10 tasks)
*SOFT — rubric-scored only, no ground truth*

| # | Task | Expected dimensions to stress |
|---|------|-------------------------------|
| D-01 | Write a 300-word threat briefing on the current state of ransomware targeting healthcare. 3 article-level sources required. | Evidence, Clarity |
| D-02 | Write a briefing on Chinese APT activity targeting network infrastructure in 2024-2025. Confidence labels per claim required. | Evidence, Reasoning |
| D-03 | Write a KEV watch summary for the week of April 7-14, 2025. List all CVEs added, due dates, ransomware nexus. | Accuracy, Evidence |
| D-04 | Write a vendor advisory extraction for the April 2025 FortiOS security bulletin. List all CVEs, severity, affected versions. | Evidence, Accuracy |
| D-05 | Write a "what changed / why it matters" briefing on the shift from VPN to ZTNA for enterprise network access. | Reasoning, Clarity |
| D-06 | Summarize CISA's ICS advisory for Silex Technology SD-330AC (ICSA-26-111-10). List CVEs, affected versions, mitigations. | Evidence, Accuracy |
| D-07 | Write a threat briefing on supply chain attacks targeting open-source npm packages in 2024. 3 specific incidents required. | Evidence, Reasoning |
| D-08 | Write a config audit checklist for FortiGate SSL-VPN hardening. 5 specific checks, each with the CLI command to verify. | Accuracy, Clarity |
| D-09 | Write a proxy log explanation: what does a CONNECT tunnel in MWG logs indicate, and what are 3 indicators of abuse? | Reasoning, Clarity |
| D-10 | Write a firewall policy review checklist for PCI-DSS scope segmentation. 5 checks, each with the compliance rationale. | Accuracy, Clarity |

---

## Scoring Template (per task)

```
Task ID: ___
Run date: ___
Hermes mode: [ ] Baseline (no policies) / [ ] SSLL (with policies)
Cycle number: ___

Biff scores:
- Accuracy: _/5 — sub-checks: A1__ A2__ A3__
- Evidence: _/5 — sub-checks: E1__ E2__ E3__
- Reasoning: _/5 — sub-checks: R1__ R2__ R3__
- Clarity: _/5 — sub-checks: C1__ C2__
- Efficiency: _/5 — sub-checks: Ef1__ Ef2__
- Gate triggered: [ ] None / [ ] Accuracy < 3 / [ ] Evidence ≤ 2 / [ ] DNR
- Reward: ___/100
- DNR violations: ___
- Tool calls: ___
- Output length (chars): ___

Human audit (Vikas):
- Agree with Biff score: [ ] Yes / [ ] No (if no, actual: ___)
- Unsupported claims count: ___
- Citation precision (correct URLs): ___ / total cited
- Notes: ___
```

---

## Baseline Run Protocol

1. Disable policies.md (rename to policies.md.disabled)
2. Run all 50 tasks with fresh Hermes session (no prior context)
3. Score each with frozen Biff prompt above
4. Record all scores in `eval/results/baseline-YYYY-MM-DD.csv`
5. Re-enable policies.md

## SSLL Run Protocol

1. Enable policies.md (current active version)
2. Run same 50 tasks in same order
3. Score with same frozen Biff prompt
4. Record in `eval/results/ssll-cycleN-YYYY-MM-DD.csv`
5. Compute: mean score delta (SSLL − baseline) per task set, per dimension

## What Counts as Learning

- Mean score on Task Set A (VERIFIABLE CVE) rises > 5 points: evidence of adaptation on bounded tasks
- Mean score on Task Set B (papers) rises: evidence of generalization beyond training domain
- DNR violation rate drops across runs: evidence of policy enforcement working
- Biff vs Vikas correlation (r) > 0.8: judge is calibrated

If Task Set A improves but B does not: local rubric-fitting, not generalization. Say that.
