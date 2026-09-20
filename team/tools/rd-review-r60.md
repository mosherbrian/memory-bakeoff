# Random tranche, seeded draw — stage one

60 documents, seed 20260919, drawn from the manifest excluding the 20 review files. All 60 processed cleanly: no rejected quotes, no errors, no unparsed replies.

Every quote below is verified present in its file. What needs your read is whether each ROLE is right for the passage supporting it.

## Role distribution across the tranche

- `verification` — 44
- `decision_record` — 21
- `proposal` — 15
- `implementation` — 13
- `measurement_report` — 10
- `protocol` — 8
- `research_intake` — 5
- `synthesis` — 5
- `operations` — 4
- `unknown` — 1

## ALICE-CHARTER-HARNESS-AUDIT.md
*A read-only audit of a charter draft against 10 harness guardrails, finding 7 met and proposing 3 additions to close the gap.*

- **verification** (L0) — "This is a read-only audit of a draft owned by Stratum; the additions are proposed, not applied."
- **proposal** (L70) — "Stratum (owner) adds A–C as three lines to §"Shared harness spec"; no number or criterion changes."

## ALICE-HINDSIGHT-THIRD-PARTY.md
*A verification/provenance investigation that checks Hindsight's 'independently reproduced' claim against the author list of the vendor's technical report and resolves it to co-authorship.*

- **verification** (L25) — "The README's *"independently reproduced by research collaborators at Virginia Tech [Sanghani Center] and The Washington Post"* refers to **co-authors of the vendor's own report** — not an external par"
- **decision_record** (L68) — "**`third-party` remains empty** — Hindsight was its only candidate, and it does not qualify."

## ALICE-INSTRUMENT-FIXES.md
*A document describing a verified patch (diff file) that fixes four pre-exposure findings in an instrument, with test and probe evidence that the patch resolves each defect.*

- **implementation** (L49) — "Built the patch by editing a scratch copy, generating the unified diff, then re-applying it to a *second* fresh copy and running the suite — so the receipt is the patch, not my working tree."
- **verification** (L27) — "After applying: **26 passed** — the **22 committed tests still pass** (the patch changes only untested edges) plus the 4 new regressions."

  uncertain: The document references a 'P2 number' and 'first exposure' whose broader context is not explained within this text.

## ALICE-META-COVERAGE-APPLIED-CHECK.md
*A second-seat verification check of the applied meta-guard completeness script, recording test-case outcomes and a PASS verdict with an explicit prohibition against applying the superseded patch.*

- **verification** (L18) — "Verified on the live file and in temp copies:"
- **decision_record** (L45) — "Assay's parallel `meta-coverage-completeness.diff` is genuinely superseded: do not apply it on top of `6cd289e7…`."

## ALICE-MUSE6-SECONDCHECK.md
*A second-seat verification document checking whether four ACCEPTs from Muse batch 6 are already covered by existing guards and whether two DUPLICATE classifications are correct.*

- **verification** (L14) — "Reproduced each gap with the live guards (`check_identifier_lifecycle.py` `f58a61c6…`, `check_cross_copy_drift.py` `f683903b…`):"

  uncertain: The section 'Two constraints I would bind before the probes are built' contains forward-looking recommendations that could be read as a proposal, but they are framed as caveats within the verification verdict rather than as a standalone proposal for change.

## ALICE-ORPHAN-EVIDENCE-GUARD-SECONDCHECK.md
*A second-seat verification check of the orphan-evidence guard script, reporting a PASS verdict with two findings about substring citation matching and missing allowlist handling.*

- **verification** (L13) — "PASS on the build — hash, self-test, the real census (52 orphans), the allowlist/plain-mention suppression, and the unreadable-results path all reproduce or hold."
- **proposal** (L60) — "The suite's convention elsewhere is a structured `missing prerequisite: <path>`; this should match it (and mention that `--fail` will then over-fire)."

## ASSAY-B3-CONTRACT-REGRESSION.md
*A verification report checking the B3 contract regression (23 cases) against the design document, recording F3c as closed, and proposing a minimal fix for a remaining wording ambiguity (F3c-x).*

- **verification** (L6) — "**Verdict: F3c CLOSED — PASS / AGREE.**"
- **proposal** (L0) — "Recommend it become the standing B3 regression guard; it exits 0 on the current contract."

  uncertain: The 23/23, 9/9, and 14/14 results could be read as a distinct quantitative observation (measurement_report), but they appear to be the verification evidence itself rather than a separate measurement.

## ASSAY-INVOCATION-B3-REVIEW.md
*An assay review of Addendum B3 to the invocation-benchmark design, testing its proposed predicate against synthetic event streams and proposing five fixes.*

- **verification** (L48) — "The literal predicate gives a perfect `FBMR_topic` to four behaviors the design explicitly wants at zero (dump, recency-only, explicit fallback, mere mention), plus a substring false positive."
- **proposal** (L10) — "One probe, five concrete failure modes, minimal fixes below."

  uncertain: It is not clear from the text whether the proposed fixes F1–F5 have been accepted or remain pending.

## ASSAY-POWERCHECK-S4-DELIVERED-CLASSIFIER.md
*A power check of the `verify_s4.py` delivered-level classifier that identifies a documented-vs-implemented regex mismatch and demonstrates false-positive paths using six synthetic cases.*

- **verification** (L28) — "Current: 4/6. Anchored `(?m)^\[project_perseus_recall\]\s+key=(\S+)`: **6/6**."
- **proposal** (L45) — "Adopt the anchored pattern (above) in the **next** revision of the verifier; do not silently edit the committed row-1 receipt mid-window."

## ASSAY-SECOND-DRIVER-READER-TRACE.md
*A verification record that recomputes per-provider reader trace counts from 56 per-case records and confirms they match the stored summary CSV and sidecar trace linkage.*

- **verification** (L11) — "Recomputed per-provider pass / prohibited / insufficient counts from the **56 per-case records** in `results/reader.json` (14 cases × 4 providers), compared them to `results/reader_summary.csv`, and c"

## ASSAY-U3-RECORD-TEXT-IDENTITY.md
*This document records a prototype assay (U3) that checks record-text identity across corpora, reports a census of three trees, and documents a correction to a reporting slip found by a second check.*

- **measurement_report** (L48) — "48 unique ids (528 id-per-file occurrences) cross-checked against the 50 canonical rows, **0 mismatches**; the 19 unindexed ids are stress distractors (M441–M499), expected."
- **verification** (L54) — "Alice's `ALICE-U3-RECORD-TEXT-SECONDCHECK.md` reproduced the census with its own extractor (67 ids, **48** checked, 0 forks/drift, 19 unindexed; case-sensitive and casefolded agree) and found a **repo"
- **implementation** (L58) — "Fixed to count the ids that actually match the canonical table; prototype now `5ae37253…`."

## ASSAY-VERIFICATION-COVERAGE.md
*A verification coverage index that maps protected findings and sprint anchor numbers to their independent re-derivation verdicts.*

- **verification** (L4) — "one page mapping every AGENTS.md "Existing findings to protect" (and the sprint's load-bearing numbers) to an independent Assay re-derivation, so the fleet can see at a glance that nothing cited is re"
- **synthesis** (L29) — "all protected-finding checks are **stored-artifact re-derivations** (recompute from per-case rows / raw lifecycle bytes) plus provenance pins."

## ASTRA-HUMAN-INTERFACE-DESIGN-20260917.md  *[PARTIAL INPUT: partial 40054/56124 chars]*
*A design proposal for a human-facing interface to a fleet of research agents, presenting architectural alternatives, design principles, and a staged implementation plan.*

- **proposal** (L9) — "This is a design proposal, not a complete audit; I made no project changes."
- **decision_record** (L85) — "Choose the middle approach."

## BILLING-CACHE-FINDINGS-20260915.md
*A findings document reporting cache lifetime measurements, a configuration comparison that closes item 6, a retraction of an earlier cost-saving estimate, and a recommendation to defer changes pending a clean measurement day.*

- **measurement_report** (L33) — "The cliff sits between 150s and 160s. It is a cliff, not a decay — 99.7% at 150, 0.5% at 160. Confirmed at both ends by separate runs."
- **decision_record** (L61) — "So item 6 cannot beat item 1. The hoped-for "keep the cache alive by configuration" route is closed."

  uncertain: It is unclear whether the keep-warm proxy discussed in §4 is a formal proposal from the author or remains an informal option attributed to Brian.

## BILLING-POSITION.md
*A billing position document that synthesizes multiple source documents into a unified recommendation for managing compute spend at full pace.*

- **synthesis** (L3) — "Builder filed no position; synthesis proceeds on two seats plus the conductor."
- **decision_record** (L23) — "Conductor's cool-pulse/shrink-context position is declined on cost grounds for Muse seats (slower = more misses) but serialization (one pulse per seat, no-trigger bumps off) is adopted."

  uncertain: It is unclear whether the recommendation section represents a formally accepted decision or a position still pending approval, though the language reads as definitive.

## BOARD.md  *[PARTIAL INPUT: partial 40055/271089 chars]*
*An append-only team message board (BOARD.md) serving as a non-task coordination space where multiple seats post status updates, decisions, findings, and verification results across a research campaign.*

- **operations** (L100) — "Rows 1,2,3,4,7 open with eligible seats idle. Row 2 (Assay) was gated on window-open — gate is now clear."
- **decision_record** (L75) — "RULES ADOPTED from your TEAM-1 answers (converged across 11 seats, near-verbatim): 1) No owner, no deadline, nothing to "do" — if it has those, it's a QUEUE row."
- **verification** (L107) — "Row 2 closed: capture→maintain non-promotion PASS on frozen `060d842` (receipt `implementer/repo-glm-dsh2/scripts/repro-20260912-assay-row2/`, commit `d12feb9`)."

  uncertain: The document spans many hours and dozens of posts covering distinct functions (proposals, measurement reports, synthesis); the three roles above are the most consistently evidenced across the full text, but individual posts within the board also serve as proposals and measurement reports in their own right.

## CANDIDATE-CARD-ALTK-EVOLVE.md
*This is a candidate card documenting the ALTK-Evolve guideline memory system and its Consistency Analyzer from IBM Research/AgentToolkit, with a disposition by corvid-dsh recording decisions on acquisition and method adoption.*

- **research_intake** (L0) — "The disposition is corvid's; this is the intake record and one seat's read."
- **decision_record** (L10) — "DISPOSITIONED by corvid-dsh 2026-09-19 01:11 PDT — full-system: do not acquire; Evolve Lite: acquire for controlled adapter measurement under binding conditions; Pass^k adopted with one finding; G4 pr"
- **verification** (L213) — "Verified in the harness: `passk()` (lines 113-130) scores usable = parses ∧ selftest rc 0 ∧ rejects the unbuilt artifact ∧ non-empty; `loop()` prints it at the end of every loop (155-157); the truncat"

## COLLECTION-LOG.md  *[PARTIAL INPUT: partial 40054/93212 chars]*
*An append-only collection log recording routine turn completions, artifact receipt checks, seat states, and anomaly escalations for a multi-seat research fleet.*

- **operations** (L3) — "Append-only. One line per finished lane turn. The collector (fsync) reads the last ~40 lines of this file before every collection; this header is the standing rule."
- **verification** (L16) — "Check every claimed artifact path exists; if a hash is claimed, check it matches."

  uncertain: The middle of the document is omitted, so additional roles may apply to the unshown portion.

## CORVID-BASELINE-PRODUCT-INGEST-FIX.md
*A validated diff document that sets product_ingest=False on four baseline configurations and verifies the fix passes tests and fails closed in product mode.*

- **implementation** (L0) — "Set `product_ingest=False` on `bm25`, `dense_lsa`, `tfidf_cosine`, `hybrid_rrf` (their classes already stay `baseline` in both modes), and add a regression assertion beside the habitus one in `tests/t"
- **verification** (L20) — "`PYTHONPATH=src:vendor/membukkit/src pytest -q tests/test_preflight_hardening.py` → **9 passed** (the new loop assertion included)."

## CORVID-CHECKER-COVERAGE-MAP.md
*A coverage map that maps defect classes to their corresponding evidence-integrity checker guards and identifies classes with no guard.*

- **synthesis** (L5) — "give the suite an inverse view — defect class → guard — and name the classes with **no guard**, so the next slice is chosen from a list instead of rediscovered."
- **measurement_report** (L408) — "Live: **18 cards, 0 findings** — the verifier-line gaps found in the census were filled by the card owner."
- **decision_record** (L0) — "Assay's parallel validated patch `meta-coverage-completeness.diff` (`c19e0589…`, guarded `7e289fdd…`, base `6a072f30…`) is superseded by the applied `6cd289e7…` — do not apply it."

  uncertain: The Handoff section assigns tasks to named seats; it is unclear whether this constitutes a proposal (work not yet in force) or is simply part of the synthesis/decision record.

## CORVID-CHECKER-SUITE-TRACKING-GAP.md
*A document by Corvid (worker-glm-dsh3) that censuses the git tracking status of the evidence-integrity checker suite across working trees, identifies the suite as having no durable home, and records the approval and application of a fix (S3-7).*

- **measurement_report** (L15) — "| `implementer/repo-glm-dsh3` | **19** | **0** | the live suite: 17 sibling guards + meta + map-hash |"
- **proposal** (L52) — "**Minimum now:** record this gap so the map/suite hashes are not read as durable until one of the above lands."
- **decision_record** (L67) — "CLOSED 2026-09-15 (S3-7 approved by GiLMore)"
- **verification** (L69) — "Verified from canonical: meta-guard **20/20 hold**, map-hash **0**."

## CORVID-DSH3-SRC-SYNC-VERIFY.md
*A document by Corvid (worker-glm-dsh3) verifying that Alice's instrument fix applies cleanly to dsh3 HEAD and reporting the resulting test and golden-parity outcomes.*

- **verification** (L8) — "Verified whether Alice's validated fix applies here."
- **measurement_report** (L21) — "the patched tree returns the canonical fixture exactly — `limit=0` offers nothing, `limit=1` → `o2`/`tokens_offered=2`, `limit=None` → both/4."
- **proposal** (L37) — "This is the same diff already landed on canonical (`80a6b08`) and dsh2 (`8fcaf5a`), so applying it makes dsh3's instrument semantics match and lets the cross-tree parity **golden half** become wireabl"

  uncertain: The handoff section could alternatively be read as an operations handoff (giving the implementer-of-record concrete commands) rather than a proposal; the distinction is unclear from the text alone.

## CORVID-GATE-SWEEP-20260914.md
*A record of a full P2 evidence-gate sweep run on 2026-09-14, executing 18 check invocations against a repository to confirm no drift after adding two new tools and renaming one.*

- **verification** (L0) — "re-ran the **complete** canonical gate list from `team/CORVID-P2-EVIDENCE-GATE-CARD.md` to confirm no drift and that the new artifacts did not break the suite."

## CORVID-LEDGER-PIN-STATUS-FIX.md
*A fix record describing corrections to pin-status entries in a claims ledger, with verification that the corrections were applied correctly.*

- **implementation** (L43) — "Edit-only: the snapshots themselves are Alice's receipts; this note does not re-fetch or re-hash them (her MANIFEST is the durable copy)."
- **verification** (L37) — "All four pin shas/dates cross-checked against `team/ALICE-MUTABLE-SOURCE-PINS.md` §Pins and `team/row-pin-receipts/MANIFEST.md`."

## CORVID-MAP-HASH-GUARD.md
*This document describes the implementation, verification, and adoption of a coverage-map hash-drift guard (guard 15) including two revisions that closed blind spots found by second-seat checks.*

- **implementation** (L0) — "Corvid applied it; the guard now checks **both directions**: map→live hash drift and live→map coverage."
- **verification** (L33) — "Ran Assay's prototype `439dd1e1…` independently → **0 findings** on the live map, matching his result."
- **protocol** (L47) — "Added to `team/CORVID-RD-CHECKER-SUITE.md` as **guard 15** and to the coverage map's Layer B as a maintenance row (`—`)."

## CORVID-MEMORYARENA-PINCHECK.md
*A pin check verifying bibliographic and license claims in a candidate card for the MemoryArena paper against arXiv, GitHub, and HuggingFace metadata.*

- **verification** (L33) — "So the CC-BY-4.0 claim is unsupported by the host metadata."
- **decision_record** (L0) — "Reuse should be treated as all-rights-reserved pending that."

## CORVID-READ-ESCAPE-FIX.md
*A fix record describing hardening changes to nine checker guards so that unreadable files produce structured findings rather than fail-open verdicts or tracebacks, authored by Corvid.*

- **implementation** (L40) — "Each changed guard's `--self-test` gains an explicit unreadable case, guarded by `if not os.access(p, R_OK)` so it is a no-op if the suite is ever run as root."
- **verification** (L45) — "All 10 self-tests PASS; compile clean."
- **protocol** (L21) — "A scan-based guard must **not** read an unreadable source as "no data": an unreadable `detail.csv`/index/prose becomes a finding, not a skipped dir/line."

## CORVID-S4-13-VERIFY.md
*A verification record for queue row S4-13, in which corvid-dsh independently recomputes values from primary sources and confirms the committed artifacts match, issuing a PASS verdict.*

- **verification** (L3) — "Verdict: PASS — 2026-09-16 13:46 PDT. kiln-flash authored; corvid-dsh verifies (independence holds)."

## CORVID-S7-2-VERIFY.md
*This document is a verification verdict on queue row S7-2, recording that the compose measurement artifact passed its declared checks.*

- **verification** (L3) — "**Verdict: VERIFIED PASS** (not-complementary is an honest negative; the row's deliverable was the compose measurement on the same frozen corpus, delivered)"

## CORVID-S8-2-VERIFY.md
*This document is a close-on-evidence receipt for row S8-2, recording its closure as a verbatim duplicate of S7-2 on existing verification evidence.*

- **verification** (L12) — "Declared check re-run at close: `python3 team/S7-COMPOSE/check.py --selftest` → rc 0"
- **decision_record** (L5) — "Per the re-measurement rule there is no expected difference from S7-2's not-complementary verdict, so there is nothing to re-run and no new verification to author."

  uncertain: It is unclear whether the 're-measurement rule' referenced is a formal protocol or an informal convention.

## CORVID-XOPENCODE-SESSION-CORRECTION.md
*A correction document that refutes a claim in an earlier findings document by demonstrating that the `x-opencode-session` header is present in the installed client binary.*

- **verification** (L0) — "For the client this fleet actually runs, that claim is false."

## D-7-timestamps/check.py
*A Python gate script for QUEUE row D-7 that re-derives timestamp comparisons from the board and filesystem to verify whether done-stamps are consistent with artifact modification times.*

- **verification** (L6) — "it does not trust report.md's account of the stamps, it re-derives the comparison from the board and the filesystem on every run."
- **implementation** (L4) — "Written FROM ROW D-7's TEXT ALONE, before any D-7 artifact existed (`team/D-7-timestamps/` was absent)."
- **protocol** (L58) — "Exit contract (team/tools/check_checker_exit_contracts.py): 0 clean, 1 with a named marker and the line `D-7 gate findings: N`, never a traceback."

## INVOCATION-CORPUS-SELFTEST-POWER.md
*A record of a power check in which three tampered copies of a corpus were used to confirm that a self-test script detects the faults.*

- **verification** (L13) — "Untampered corpus re-confirmed ALL GREEN 7/7 after the probes."

  uncertain: It is not clear whether the self-test script is governed by a frozen protocol or was run ad hoc.

## INVOCATION-CORPUS-V1-REDERIVE.md
*This document records a re-derivation of the invocation corpus v1 from its seed and script, comparing the output against committed hashes to confirm determinism.*

- **verification** (L5) — "Re-ran the row-36 generator (`seed 20260914`) into a scratch dir and compared against the committed `team/invocation-corpus-v1/hashes.json`:"

## KILN-D-13-VERIFY.md
*A verification receipt from kiln-flash recording the outcome of checking D-13 intel synthesis artifacts against their source feeds and handles across three dates (2026-09-17, 2026-09-18, 2026-09-19).*

- **verification** (L54) — "**PASS (re-confirmed).** The synthesis discharges D-13: every section answered, every handle genuinely cross-checked, cards D-6-complete, checker fix real, nothing imported, the outcome experiment unt"

## KILN-SWEEP-COVERAGE-20260912.md
*A coverage map reporting the collection health of a test suite (122 files, 1,625 tests) and recording a scope decision for a flake sweep.*

- **measurement_report** (L12) — "Total: **1,625 tests** collected in 0.87 s at HEAD `78cdd2d`."
- **decision_record** (L0) — "Until then, the sweep stays at its proven 9-suite boundary."

## OPS-RESULTS-TREE-20260918.md
*This document is an operator's report comparing two results trees on a local machine, documenting their byte-level consistency, and presenting three options for selecting a canonical tree.*

- **measurement_report** (L30) — "content differences .............. 0"
- **proposal** (L63) — "Neither tree is complete on its own, and they do not conflict. So the choice is between:"
- **decision_record** (L0) — "Rejected as not mine to decide."
- **verification** (L42) — "Every prerequisite the failing guards name is present in both and byte-identical where checked directly (`memconflict_gen38_full_release/scientific.json`, `claude_mem_compare_core/summary.csv`, `agent"

## R2H-REV3-RECEIPT.md
*A receipt recording a REV-3 code change to a deploy script that adds a `--pi-cmd` parameter and an unrunnable-binary guard, with verification results.*

- **implementation** (L9) — "`check` accepts `--pi-cmd` (default `"pi"`, mirrors `smoke`); probe uses it."
- **verification** (L20) — "`--pi-cmd /nonexistent` | `FAIL pi binary: /nonexistent: not found (resolved /nonexistent)`, no traceback"

  uncertain: It is unclear whether the re-ship noted in the Freeze section constitutes a formal decision or is merely a status note.

## RATER-HANDOFF.md
*A standing handoff document defining the operative protocol for a blind external reviewer to judge items in a blind package.*

- **protocol** (L18) — "For each item in the package: rule it against its stated criteria, using only the attached evidence. Record AGREE or DISAGREE plus a one-line basis for every DISAGREE."

  uncertain: The title says 'Standing' which implies the protocol is in force, but the text does not explicitly record an acceptance or freeze date.

## RD-TRACKS.md
*This document is a file named RD-TRACKS.md that contains no visible text content.*

- **unknown** (LNone) — "---"

  uncertain: The document appears to be empty or its content was not supplied, so its purpose and function cannot be determined.

## RESEARCH-HINDSIGHT-INDEPENDENCE-AUDIT.md
*This document is a provenance audit checking whether Hindsight's 'independently reproduced' benchmark claim is supported by the cited sources.*

- **verification** (L75) — "Independence claim: `contradicted`. We hold a reference (the ACL paper's author list) that disagrees with "independently reproduced.""
- **decision_record** (L77) — "94.6% LongMemEval headline: `contradicted`/unsourced. The vendor's own peer-reviewed paper reports 91.4% (Gemini-3 Pro) and 83.6% (20B OSS); the live page's 94.6% is not backed by it and names no spli"

## RESEARCH-VENDOR-CLAIM-CHECKLIST.md
*A vendor-claim integrity checklist that defines six checks derived from the Hindsight audit and maps portfolio engines against them using existing receipts.*

- **protocol** (L8) — "the checks that caught it should be a standing gate, not a one-off."
- **verification** (L43) — "**Hindsight** | ACL 2026 demo, **co-authored by the "independent" parties** | 94.6 (live) > 91.4 (paper) | **vendor (AMB)** | page: no; paper: LongMemEval-S | **3 fails** (§Addendum, ledger L-HS-01..0"
- **synthesis** (L4) — "**Cost:** $0, synthesis over existing ledger/survey receipts (no new fetches; provenance already on file)"

  uncertain: It is unclear whether the P2/P4 gate has been formally adopted or remains a proposal pending acceptance.

## RETRO-1-worker-codex.md
*A retrospective written by an outside/legacy seat about the team's coordination topology, seat management, and work-shape during a campaign.*

- **operations** (L7) — "The record shows strong work from a small active core, but the operating shape still carried more named seats than it could feed with bounded, useful work."
- **proposal** (L38) — "Run a "cold-seat recall drill" before Campaign-1 execution: give one parked or outside worker only `MISSION-20260912.md`, `SCOREBOARD-20260912.md`, and `CAMPAIGN-1.md`, then ask them to answer three o"
- **synthesis** (L24) — "The strongest parts of the record are the probe findings that narrowed the campaign: native capture non-serveable, `remember` demoting active records, row-6 blocked by missing data, delivery-level mea"

  uncertain: It is not clear from this text whether the proposed seat ledger or cold-seat recall drill were subsequently adopted or remain unaccepted.

## RETRO-3-cairn.md
*A personal daily retrospective written by a worker called Cairn, covering verification work completed, churn analysis, event-driven performance grading, keep/kill decisions, and blind spots.*

- **decision_record** (L19) — "Kill: two independent producers on one row — S3-1's collision cost an adjudication cycle; first-writer-wins with a claim check would have prevented it (BOARD ASY collision post)."
- **measurement_report** (L9) — "Roughly 4 work turns vs ~8 describe-only ticks today (≈1:2)."
- **operations** (L10) — "Largest churn source: repeated no-op poller ticks while S3-1 sat on Corvid's adjudication — each tick re-reads BOARD/QUEUE to confirm nothing changed."

## ROW30-EXTERNAL-CORPORA-ADAPTER-DESIGN.md
*This is a design note describing format-normalizer adapters for three external corpora (Wisp, SWE-chat, MindForge) that plug into a mining pipeline's operator_texts() function, including the completed implementation and real-data validation results.*

- **implementation** (L36) — "`mine.py` now carries the `--source {claude-code,wisp,swe-chat,mindforge-control}` switch; `operator_texts(record, source)` implements the voice rules above and `stats` records `source` + `source_oper"
- **measurement_report** (L45) — "wisp: 3 files / **3** operator turns / 1 env-fact"
- **verification** (L41) — "Tests: `tests/test_external_corpus_adapters.py` (wisp/swe-chat voice = user lines; tool-result excluded; mindforge-control empty; unknown source raises; end-to-end `scan` per source) — **29 passed** w"

## ROW41-PILOT-CARD-DELTA.md
*A note explaining why the pilot card reports 15 correction events while the committed pipeline yields 10, resolving a blocker on row 41.*

- **verification** (L23) — "The card row matches the **unmasked** variant exactly (all five classes). So the card is not a fabrication and not a different corpus; it is a **pre-`mask_quotes` snapshot**."
- **decision_record** (L43) — "row 41's blocker is **resolved by explanation**, and the export step is correct as shipped."

## S10-KD-CROSS/check.py
*A Python gate script for queue row S11-2 that checks a cross-system replay directory against a declared interface and records pass/fail findings with named markers.*

- **verification** (L53) — "Exit contract (team/tools/check_checker_exit_contracts.py): 0 clean, 1 with a named marker and the line `S11-2 gate findings: N`, never a traceback."
- **implementation** (L5) — "Written FROM ROW S11-2's TEXT ALONE, while `team/S10-KD-CROSS/` did not exist."
- **protocol** (L39) — "Declared interface (ROOT = team/S10-KD-CROSS): the S7-4 files and schema (declaration.json, items.jsonl, results.jsonl, verdict.json)"

  uncertain: Could not tell from the text whether this gate has been formally accepted into force or is still awaiting acceptance, though its selftest and exit contract suggest it is operative.

## S3-1-STANDARD-TIER-RECEIPT.md
*A receipt reporting quantitative results from an invocation benchmark run at the standard tier against a synthetic corpus of 60 scenarios.*

- **measurement_report** (L30) — "| **FBMR_topic** | **1.000 (30/30)** | 30 labeled topic moments | Wilson 95% CI **[0.886, 1.000]** |"
- **verification** (L51) — "Instrument-failure condition not met — the controls separate, so the system numbers above are publishable at this tier."

  uncertain: What the broader benchmark structure (e.g., the multi-engine tier) entails is not described here.

## S5-INTERPRETIVE-NOTES.md
*A file recording binding interpretive notes pinned during an S5 freeze, defining rules for metric-blind task assignment, classless turn handling, and the token field definition.*

- **decision_record** (L35) — "**`tokens` = `sum` — total per-call work.**"
- **protocol** (L15) — "Task-family assignment (including the "same calendar day on the same objective" fallback — "same objective" is the rule's only judgment term) is made from task text and timestamps *before* tokens/wall"

  uncertain: It is not clear from this text whether the referenced "window-close run" has been completed or is still pending.

## S6-CORRECTION/check.py
*A Python gate script for QUEUE row S6-1 that checks whether the S6-1 correction artifacts (note.md, numeric-claims.json, review.json, publication.json) meet defined criteria, and includes a selftest that verifies the gate can accept conforming fixtures and reject single-defect mutants.*

- **implementation** (L4) — "Written FROM ROW S6-1's TEXT ALONE, before any S6-1 artifact existed (`team/S6-CORRECTION/` was absent)."
- **verification** (L327) — "one defect each, so every check is shown to fail on its own"

## S6-ROADMAP/check.py
*A Python gate script for QUEUE row S6-3 that validates S6-ROADMAP artifacts against a declared interface, including a selftest that constructs single-defect mutants to prove the gate can fail and pass.*

- **implementation** (L5) — "plumb-fable, row S6-3G, 2026-09-17. Written FROM ROW S6-3's TEXT ALONE, before any S6-3 artifact existed (`team/S6-ROADMAP/` was absent)."

  uncertain: The selftest code performs verification activities (constructing mutants, recording their rejection) but the document does not record an actual execution outcome, so it is unclear whether a verification role applies to this document as a record rather than as code that would perform verification when run.

## S7-STATELAYER/design.md
*This document is a pre-registered experimental design for task S7-3, specifying frozen trials, arms, and a decision rule to compare false-supersession rates between pi-lcm native and a thin state layer.*

- **protocol** (L4) — "The binding declaration is `declaration.json`, written before any receipt and sha-bound into all of them; the trial list and the thin layer are frozen by sha256 inside it."

## SPARK-CONTRADICTION-SCAN-20260914.md
*A contradiction-term discovery pass (spark pulse 2026-09-14) that searched for negative evidence—critiques, replications, limitations—against five new candidates and identified one net-new external paper (MemDelta, arXiv:2606.29914).*

- **research_intake** (L5) — "Queries appended `limitations`, `criticism`, `replication`, `false positive`, `no improvement`, `contamination` to each candidate."
- **proposal** (L36) — "MemDelta is not a new score source — it is a controlled-baseline protocol we should fold into the citation/evidence rule before the next arm"
- **decision_record** (L0) — "The contradiction pass re-found it; it is **not** net-new, and still has no card."

  uncertain: It is unclear whether the proposal to fold MemDelta into the citation/evidence rule was subsequently accepted or remains pending.

## SPARK-DELTA2-PROVENANCE-LICENSE-20260915.md
*A provenance and license verification pass on 8 candidate papers from a watchlist delta, produced by muse-drafter (Spark) on 2026-09-15.*

- **research_intake** (L3) — "All 8 items verified at ID level (arXiv API + abs pages); paper licenses read off abs-page license links; artifact links grepped from abs pages."
- **verification** (L20) — "Re-verified via GitHub API: root has no LICENSE; `data/` holds only `.DS_Store` + `AgentProcessBench/` + `AnswerOnly/` (no LICENSE); nested data dir holds only 4 JSONL files; README contains **zero** "
- **decision_record** (L20) — "The MIT claim is unsupported — treat as ARR. Card owner to adjudicate before any download."

  uncertain: It is unclear whether the 'strongest fits' line (MemTX and HANDBOOK) records a selection decision or is merely an observational note deferred to the card owner.

## SPARK-HALUMEM-BODY-PASS-20260914.md
*This document is a body-read of the HaluMem paper (2511.03506v1) that extracts its extraction/updating/QA metric split as a proposed reporting shape for the project's own runs.*

- **research_intake** (L5) — "Body read of `2511.03506v1`. Grounding only — vendor rates stay **uncited, no score import.**"
- **proposal** (L47) — "For our own runs, report **three staged numbers + FMR** rather than one accuracy: extraction coverage (weighted), update accuracy/omission, QA accuracy, and distractor resistance — evaluated **per ses"

  uncertain: It is not clear whether the proposed metric split has been accepted into the project's reporting protocol or remains pending.

## SPARK-MEMSTRATA-ARTIFACT-20260914.md
*This document records a pass over arXiv paper 2606.26511 (Yadav) to assess its artifact availability and license status.*

- **research_intake** (L5) — "Paper `2606.26511` v1 2026-06-25 (Yadav), abstract-level only: deterministic (subject, relation, object) supersession in a bi-temporal ledger, no similarity threshold, no LLM call"
- **verification** (L6) — "comments field says "Code, prompts, and evaluation datasets included", but the arXiv abs page shows **no Code/Data/Media association** (toggle shells only, no linked repo/HF)."

## SPRINT-NEXT-PROPOSAL.dead-20260918-122712.md
*This document is a proposal for the next sprint's work, selecting two ranked items and defining goals, role assignments, and explicit exclusions.*

- **proposal** (L7) — "First build tests of whether workers follow checked, current instructions, then determine whether three source defects affect existing research findings."

## TEAM-1-Corvid.md
*A response from a worker seat called Corvid expressing conditional buy-in to a team concept, proposing board rules, and providing a persona install block.*

- **decision_record** (L205) — "Buy-in: yes, with a falsifier."
- **proposal** (L93) — "Rules that keep it from rotting into an obligation (proposed, not demanded):"
- **implementation** (L202) — "This turn's artifact is this file."

  uncertain: It is unclear whether the persona install block was actually installed into the system or remains a proposed artifact awaiting acceptance.

## VERITY-PULSE-ATTRIBUTION-NOTE.md
*A note by Verity auditing pulse-attribution integrity after a signing correction and recommending a lane-id signing convention.*

- **verification** (L15) — "No entry signed by this lane claims work it did not do."
- **proposal** (L21) — "One-line convention; the poller could even pre-stamp it."

  uncertain: The document references fsync's disclosure of misattribution as context; whether that disclosure itself constitutes a separate decision record is not determinable from this text alone.

## WINDOW-OPENING.md
*An append-only receipt log recording the window-opening actions for campaign-1, including a T0 config flip, pre-window checklist items (0–5), verification scans, a formal gate declaration, and subsequent corrections and additions.*

- **verification** (L0) — "acceptance is the behavioral proof the gate changed, not just the config byte."
- **decision_record** (L227) — "GiL declared **WINDOW OPEN at ~11:05** ("all six pre-window items receipted; evaluated cycles count from now")."

  uncertain: The broader research objective of campaign-1 is not stated in this document; it records only the operational window-opening process and its verification.

