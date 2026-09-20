ANSWER:
| Research question | Current answer | Limitation | Next discriminating step |
|---|---|---|---|
| Does memory improve real work? | **Not established. This interval produced no new evidence that memory improves real work.** The supplied measurements concern retrieval, evidence delivery and stored-state behavior, not completed-task outcomes (`S7-COMPOSE/verdict.json`, `S7-STATELAYER/verdict.json`, `S7-KD-WORLDS/verdict.json`, `S8-DOOR/verdict.json`, `S9-DOOR-RUNG2/verdict.json`). | No demonstrated reduction in errors or repeated discovery; no demonstrated daily-workflow winner. | Run the pre-registered matched outcome comparison against no memory once private-data authorization and the budget/date requirements are satisfied. |
| Can the existing stopword filter make BM25 decline irrelevant queries? | **No on the ten tested cases:** correct abstentions stayed at 0/5, while correct retrievals fell from 5/5 to 4/5 (`S7-BM25-PREFILTER/verdict.json`). | Rejects this filter, not every possible abstention mechanism. | Pre-register a score-margin abstention rule; measure both irrelevant queries rejected and useful retrievals lost. |
| Does combining BM25 with pi-lcm improve retrieval? | **The tested combination adds no benefit:** mean set-F1 stayed at 0.60, with only 1/5 retrieval cases correct and 5/5 abstentions correct. Requiring pi-lcm to permit retrieval discarded BM25’s additional coverage (`S7-COMPOSE/verdict.json`). | Ten cases and one construction; this does not reject all combinations. | Require a separately declared construction and corpus with plausible complementary coverage before another composition experiment. |
| Does pi-lcm need an added state layer to prevent false supersession? | **The tested layer fixes no observed problem:** native pi-lcm and the layer each falsely superseded 0/32 distractors and correctly handled 12/12 updates (`S7-STATELAYER/verdict.json`). | Controlled trials do not establish reliability across longer histories or rarer failure types. | Measure native pi-lcm on pre-declared broader histories before proposing a corrective layer. |
| Does BM25’s weakness recur on an externally authored benchmark? | **Yes on the sampled KnowledgeDrift families:** retrieval passed 21/40, abstention 0/40 and rationale 5/40. Lexical and paraphrase retrieval each passed 10/10; oblique passed 1/10 and crossed phrasing 0/10 (`S7-KD-WORLDS/verdict.json`). | Two frozen worlds, 120 probes, three families. The benchmark’s author has a system in its own ranking, and it wins. These are benchmark results, not real-work outcomes. | Compare additional pinned systems on the same frozen sample, reporting each family separately. |
| Does competing text prevent useful evidence reaching the model? | **Yes under constructed query-adjacent pressure on five items:** at a 600-character limit, useful-evidence presence fell from 100% to 20% for BM25, 20% to 0% for pi-lcm, and 100% to 60% for the tested claude-mem adapter. The earlier pressure caused no presence loss (`S8-DOOR/verdict.json`, `S9-DOOR-RUNG2/verdict.json`). | Establishes a delivery failure under this pressure, not its frequency or task-level cost in daily work. Evidence presence and irrelevant delivered bytes remain separate measurements. | Measure whether lost evidence produces additional errors or repeated discovery in matched tasks. |

CHANGED SINCE LAST TIME: nothing - no new evidence since the last answer. No supplied verdict file is new relative to that answer; it already incorporated `S9-DOOR-RUNG2/verdict.json`. Checker construction and fleet repairs do not change the research answers.

DECISION-READY: Reject the tested composition and state-layer justifications for building: the combination adds no retrieval benefit, and the layer fixes no observed native supersession failure (`S7-COMPOSE/verdict.json`, `S7-STATELAYER/verdict.json`). Retain the Phase G build restriction; the broader adopt/compose/build choice remains unresolved. The roadmap’s first externally anchored scored lane already exists: KnowledgeDrift, with separately reported family results and its author-conflict caveat (`S7-KD-WORLDS/verdict.json`).

EVIDENCE: `S7-BM25-PREFILTER/verdict.json`; `S7-COMPOSE/verdict.json`; `S7-STATELAYER/verdict.json`; `S7-KD-WORLDS/verdict.json`; `S8-DOOR/verdict.json`; `S9-DOOR-RUNG2/verdict.json`.

SELECT: 13, 14, 15
SPRINT-GOAL: Produce three pre-registered, independently checked comparisons that narrow the abstention, external-benchmark and native-state questions, without claiming they establish real-work benefit.
WHY: These candidates directly test three remaining uncertainties, have no unmet dependencies and require $0 local execution. Preserve their ranking and budget approximately 30, 50 and 40 implementer minutes respectively; these are planning estimates for substantive experiments, not three trivial maintenance tasks. Defer 16 and 17 explicitly because reporting repairs do not discriminate among memory approaches and would displace the measurement work. Skip private outcome execution pending explicit data/scope authorization and the applicable spending date, full SWE-chat acquisition pending storage and co-sign conditions, and the watch and keep-warm work pending their time triggers; technical choices incorrectly parked on the sponsor are reassigned below.

OUTLINE:

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
