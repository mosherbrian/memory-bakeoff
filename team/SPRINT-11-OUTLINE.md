# SPRINT 11 OUTLINE - the agreed work, 2026-09-18

Written to be decided from one read. Selected by the planner from the candidates in `BACKLOG-NEXT.md`; the machine-readable decision is in `SPRINT-11-PROPOSAL.md`. Tracker ids in parentheses are bookkeeping for the fleet - every sentence stands without them.

## 1. THEME

Test whether BM25 can decline irrelevant questions, compare retrieval methods on an external benchmark, then challenge pi-lcm’s handling of longer histories.

## 2. GOALS

**Goal 1 - As Brian, I can know whether a different BM25 abstention rule rejects irrelevant questions without sacrificing useful retrieval.**

The stopword filter rejected none of five irrelevant queries and reduced correct retrieval from five cases to four. Kiln-flash will freeze a score-margin rule and its threshold before running the same ten cases, reporting sensitivity across a declared threshold grid without choosing a winner afterward. This tests one alternative mechanism; it does not establish performance on daily work.

Done when: `team/S10-BM25-ABSTAIN2` contains the frozen declaration, hash-linked results, old-versus-new retrieval and abstention counts, and an independently confirmed passing `check.py --selftest`.

**Goal 2 - As Brian, I can compare several retrieval methods on the same externally authored questions.**

Only BM25 has been measured on this frozen KnowledgeDrift sample, so we cannot yet tell whether its weaknesses distinguish it from the alternatives. Kiln-flash will replay the same 120 probes through the pinned dense LSA, TF-IDF and hybrid RRF providers, preserving separate retrieval, abstention and rationale results. The claude-mem arm is optional within the 50-minute allocation and runs only if it can ingest the operation sequence faithfully; this does not create a combined leaderboard or establish real-work utility.

Done when: `team/S10-KD-CROSS` contains frozen provider identities and replay rules, family-by-family comparisons against BM25, explicit reasons for any omitted arm, the benchmark author-conflict caveat, and an independently confirmed passing `check.py --selftest`.

**Goal 3 - As Brian, I can know whether pi-lcm’s clean update behavior survives a broader controlled test.**

Native pi-lcm falsely replaced no records in 32 distractor trials and handled all 12 genuine updates, leaving no measured problem for the proposed state layer to fix. Kiln-flash will declare longer histories and additional distractor families before running native pi-lcm, then report false replacements and missed updates against those earlier counts. This gathers evidence about native failures; it does not build a state layer or prove reliability on private histories.

Done when: `team/S10-PI-LCM-HIST` contains the pre-run history specification, reproducible results with trial counts and old-versus-new comparisons, and an independently confirmed passing `check.py --selftest`.

## 3. WHO

Kiln-flash implements one experiment at a time; corvid-dsh independently checks each completed experiment, and nobody checks their own implementation. Cairn-pi owns routing and routine technical decisions; the selected work has a $0 spending cap, and the existing portfolio rule remains: touch $5 all-in, stop and report.

## 4. NOT DOING

- **Private outcome experiment and private-session execution:** explicit authorization for Brian’s work, sessions or data remains required, and metered execution must respect the free-window restriction. Default: leave private data untouched and proceed with the selected public/local experiments on **2026-09-18**, capped at **$0**; silence never authorizes private access.
- **Full SWE-chat download:** the 39.3 GB projection exceeds 17 GB free, and the A1–A3 co-sign conditions remain unmet. Sampling is a conductor decision, not a sponsor blocker: cairn-pi should default on **2026-09-18** to preparing a sample plan capped at **$0 and 1 GB additional storage**, with acquisition held until storage fit and co-sign conditions are confirmed; it must return as a ranked candidate.
- **Further sponsor-held technical decisions:** cairn-pi and the research director should own the next contestant batch, apply the negative build decision above, and specify any future composition corpus. Default on **2026-09-18**, capped at **$0**: retain the build restriction, use ranks 13–15 to gather evidence, and make no workflow-adoption claim. Parking these choices on furloughed GiLMore or Brian is declining to decide.
- **Standing R&D watch:** its one-request-in-flight contract prevents starting before **2026-09-20**.
- **Keep-warm rerun:** requires the OpenCode Go reset followed by a full steady-pattern day on Muse.
- **Ranks 16 and 17:** explicitly deferred for capacity as reporting-integrity maintenance, not research progress; their defects remain open.
- **Existing sprint closure, guard triage and deployment bookkeeping:** conductor-owned operations, not new experiments or sponsor decisions. Default on **2026-09-18**, capped at **$0**: cairn-pi owns triage and receipt-based closure; the blocked sweep stays stopped until its failures are resolved.
