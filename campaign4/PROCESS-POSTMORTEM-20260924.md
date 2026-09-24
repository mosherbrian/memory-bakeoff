# Campaign 4 build post-mortem and proportional-proof proposal

2026-09-24. Written by Claude at Brian's request. Brian's instruction: "I would like to operationalize
these for the future. Can we socialize this with the fleet and get the necessary agreements/buy-in?"
Brian's view, in his words: "we have been applying a maximalist one-size-fits-all approach up until now.
The actual memory-bakeoff project likely needs a higher bar than a 'research dashboard build-out' does."

Status: PROPOSAL. Nothing here changes the charter until Tern adopts it (section 6). Finder and category
counts are a hand classification and approximate; allocated minutes are ceilings, not time spent.
Brian's copy with the same content: Claude doc "Campaign 4 Build Post-Mortem" (two tabs).

## 1. Verdict

The build delivered what it set out to: a single Go loop in production since 2026-09-24 that turns every
stall into progress or one owned escalation, proven by live tests. It cost about 78 hours, about 39 package
revisions and about 7,660 allocated minutes, and the research it serves has not moved since 2026-09-21.
The main lesson: one maximal burden of proof was applied to everything. The research deserves it; most
machinery and all tooling do not.

## 2. Timeline and numbers

| Phase | Packages | Window (UTC) | Result |
| --- | --- | --- | --- |
| Specify and Python core | P1-P5 (11 revisions) | 09-21 14:44 - 23:49 | Core accepted (P5-r2) |
| Host and live recovery | P6 (20 revisions) | 09-21 23:49 - 09-23 03:41 | Live-positive handoff (P6-r9); about 28 h |
| Go port, view, first qualification | P7-P9 | 09-23 03:41 - 06:32 | Supervised preview only; P8 NOT READY |
| Requalify, timeouts, cutover | P10-P12 | 09-23 13:58 - 09-24 03:53 | Go loop in production (P12) |
| Director decisions | P13 | 09-24 04:17 - 20:29 | Promoted; about 9.5 h waiting on Claude's usage reset |

| Measure | Value |
| --- | --- |
| Package revisions | about 39: 15 accepted, about 20 exhausted or not ready, 3 superseded |
| Corvid review verdicts | 104: 66 PASS, 25 FAIL, 9 INCOMPLETE, 4 other; plus 34 admissions |
| Live and prep runs | about 16; P13 needed 4 live runs |
| Findings logged | about 230 |
| Allocated ceilings | about 7,660 minutes (P12 grew 260 to 1,430 in 14 steps; P13 180 to 865 in 17 steps) |
| Ledger rows | 769 (233 dispatches) |
| Model spend | small where recorded (controller about $0.06/h); total not recorded |

## 3. Where the failures came from

| Found by | P1-P6 | P7-P12 | P13 | Total |
| --- | --- | --- | --- | --- |
| Corvid independent review | ~45 | ~23 | ~15 | ~92 |
| Tern reading code or probing | ~50 | ~3 | ~12 | ~65 |
| Controller process faults (lost wakes, ledger slips) | ~23 | ~9 | 0 | ~32 |
| Live and prep runs | ~7 | ~6 | 3 | ~16 |
| Author self-report and planted faults | ~5 | ~6 | ~4 | ~13 |
| Brian | ~11 | 1 | 0 | ~12 |

- Early (P1-P6) the process found real product defects: false REST states (P3), trusted caller
  attribution (P5), double verifier wakes (P6-r4), a fail-open hash check (P6-r7).
- Live runs found what nothing else could: real handoff latency (P6-r8), the hardcoded trusted-seat list
  (P8), idle-cancel settlement (P11), AI fixture directors deciding early (P13).
- Late (P10-P13) most findings were in the process's own tests, plans and evidence formats.
- About 14 of 39 non-PASS verdicts were about evidence format, not substance (stale manifests, truncated
  hashes, wrong freeze citations, an empty conformance file).
- About 9 rounds ended only because the time box was shorter than the work.

Representative findings with sources: P3 `packages/P3-core-validator/acceptance-withheld.json`;
P5 `packages/P5-clock-ingress/director-repair-decision.md`; P6-r4
`packages/P6-r4-notify-timer-drain/director-readiness-findings.json`; P6-r7
`packages/P6-r7-real-host-path/candidate-review.md`; P6-r8 `packages/P6-r8-case-execution/live-review.md`;
P6-r18 `packages/P6-r18-runtime-source-time/candidate-review.md`; P8
`packages/P8-go-unattended-qualification/live-director-findings-1.json`; P10
`packages/P10-go-requalification-cutover/director-plan-repair-reproducer.json`; P11
`packages/P11-live-driver-qualification/live-timeout-idle-finding.json`; P12
`packages/P12-timeout-ownership-live-closure/real-process-defect-ruling.json`; lost wakes
`LOST-WAKE-CAUSE-20260922.md`. Product-side guards per failure kind: agent-loop README, "Failure modes,
and where each is guarded".

## 4. Process inventory

| Practice | Gave us | Cost us | Proposal |
| --- | --- | --- | --- |
| Worker, independent verifier, director as separate seats | Caught self-verification and author blind spots | One review per author round, even for plans and docs | Keep for product code and research; one reviewer for docs and plans |
| Contract reader admission before work | Stopped bad contracts before spend | 10-15 min gate before every round, incl. small repairs | Keep for new packages; skip for a repair inside an admitted package |
| Frozen contracts, hash pins, manifests, receipts | Every claim checkable to the byte | Many rounds failed on a stale manifest or hash | Keep hashes for released binaries and research data; drop manifest ceremony for plans and docs |
| Short absolute time boxes, no extension, honest INCOMPLETE | Honest status | Many INCOMPLETE rounds only because the box was shorter than one test run | Size boxes from measured run times; allow one owned extension |
| One attempt plus at most one repair | Stopped endless patching | New packages and amendments for normal iteration | Keep for research runs; machinery may iterate until green inside one box |
| Python reference + conformance + Go port | Go core proven equal to the reference | Two implementations; reference faults copied | Keep; retire the Python reference once Go is the reference |
| Planted-fault (mutation) tests | Proved the tests can fail; found test gaps | 30 min serial, 5 min parallel | Keep for core and loop; parallel by default |
| Real-process witnesses | Found what stubs could not (daemon-reload, local-time timers) | Setup per witness | Keep for timers, services, processes |
| Offline rehearsal with stand-ins | Cheap early signal | Stand-ins unlike reality caused most late rounds | Only with a test that the stand-in behaves like the real thing |
| Live runs with fresh fixtures, signatures, wall timers | The only whole-chain proof | 4 live runs for P13 | One live qualification per product change; deterministic fixtures from the start |
| Staged promotion with snapshot and exact rollback | Safe install; sandbox found a real bug | Three rounds | Keep; P13 plan is the template |
| Escalation ledger (E-numbers), wakes | Nothing waited silently | Many notices for routine events | Routine progress as status, not escalations |
| Tern decides and signs every boundary | One accountable owner | Every small step waited for a signature | Tern signs research and production changes; delegate plan and doc approvals |
| Append-only history, keep every failed attempt | Full audit trail | 15 GB repo, hundreds of temp folders | Keep for ledgers and research evidence; add retention rules for test runs |

## 5. Proposed rule: proportional burden of proof

Set the bar by one question: **what happens if this is wrong and nobody notices?**

| Tier | Kind of work | If wrong and unnoticed | Required proof | Not required |
| --- | --- | --- | --- | --- |
| 1 | Research claims (bake-off results; anything reported to Brian as a finding) | Wrong conclusions steer the project | Criteria registered before the run (commit ancestry); pinned data, code, environment; independent reproduction, blind first; one attempt plus one repair; negative results kept | - |
| 2 | Unattended machinery (loop core, timers, escalation, anything that can go silent) | The fleet stalls or pages nobody | Planted-fault tests; real-process witness for timers and services; one live qualification with deterministic fixtures; staged install with exact rollback | Manifest ceremony for plans; a new package per iteration inside the box |
| 3 | Operational scripts and adapters (install plans, fleet scripts) | A bad install, caught by its own checks | Sandbox run with real binaries plus failure cases; one reviewer; rollback | Live qualification; frozen-byte rounds |
| 4 | Read-only tools (dashboards, research view, status, reports) | A wrong number, visible and fixable | Runs on real data; one reviewer look | Independent reproduction, hashes, live runs, signatures |
| 5 | Docs, plans, notes | A confusing page | Author writes; reader optional | Everything else |

Operating rules that go with the tiers:

1. Tern assigns the tier at admission, in one line. The tier sets rounds, reviews and signatures.
2. Any reviewer may move a package UP a tier by showing a concrete blast radius. Moving down needs Tern.
3. Time boxes are sized from measured run times plus margin; one owned extension per round is allowed.
4. Tier 2-5 work may iterate until green inside its box; tier 1 keeps one attempt plus one repair.
5. A stand-in counts only with a check that it behaves like the real service.
6. Routine progress goes out as status; escalations are for things that need someone to act.
7. Tern signs tier 1 and production changes (tier 2 installs). Tiers 3-5 are approved by the reviewer.
8. Unchanged: author is not verifier (tiers 1-3); honest COMPLETE/INCOMPLETE; append-only ledgers; the
   charter's two hard stops.

## 6. What is asked of each seat

- **Tern (director):** adopt, amend or reject this as a charter amendment; record the disposition in
  `PROCESS-POSTMORTEM-DISPOSITION-20260924.md`; answer or route the open questions below; collect the
  other seats' responses.
- **Corvid (reviewer):** one bounded review: does any tier drop a check that caught a real defect in
  campaign 4? Cite the finding if so. Also: are the tier 1 research requirements sufficient?
- **Kiln (worker) and Cairn (controller/duty):** one short response each: can you work under rules 3-6,
  and what would you change?

## 7. Open questions

- Brian: accept the five tiers? Who assigns a tier when Tern is unsure?
- Brian: is the machinery phase closed, so research resumes through the live loop?
- Tern: first research package = the 2026-09-20 research synthesis, as a tier 1 judgment package?
- Tern: which parts of the 15 GB package archive are research evidence to keep, and which test runs can
  expire? (Brian's original goal 5: storage and retention rules.)
- Both: retire the Python reference now that the Go binary is in production?
- Also open from Brian's original five goals: goal 3, the research and roadmap view.
