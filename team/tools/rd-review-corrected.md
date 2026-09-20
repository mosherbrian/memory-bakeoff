# Entries you corrected, regenerated under the revised prompt

All 60 tranche documents are now ok: no rejected quotes, no errors.

## Role distribution, recomputed from the current records

- `verification` — 42
- `decision_record` — 19
- `proposal` — 15
- `implementation` — 12
- `measurement_report` — 9
- `protocol` — 9
- `synthesis` — 6
- `research_intake` — 5
- `operations` — 4
- `unknown` — 1

---

## ASTRA-HUMAN-INTERFACE-DESIGN-20260917.md
*A design proposal for a human interface for a multi-agent research fleet, covering architectural alternatives, a machine-to-human translation contract, evaluation metrics, and a staged implementation plan.*

- **proposal** (L9) — "This is a design proposal, not a complete audit; I made no project changes."
- **synthesis** (L228) — "Those are supported by the inspected experiment records and proposed outcome design; they are not claims that I independently reran the experiments."

## CORVID-DSH3-SRC-SYNC-VERIFY.md
*A verification report by Corvid (worker-glm-dsh3) checking whether Alice's instrument fix diff applies cleanly to dsh3 HEAD and whether the resulting tree passes focused tests and clears the golden parity probe.*

- **verification** (L21) — "**Golden parity clears:** the patched tree returns the canonical fixture exactly — `limit=0` offers nothing, `limit=1` → `o2`/`tokens_offered=2`, `limit=None` → both/4."

## TEAM-1-Corvid.md
*A response from the evaluation/probe seat (Corvid) to a team culture question, recording its buy-in decision and proposing rules for a shared board.*

- **decision_record** (L21) — "buy-in is yes, with a falsifier attached"
- **proposal** (L93) — "Rules that keep it from rotting into an obligation (proposed, not demanded):"

## SPARK-CONTRADICTION-SCAN-20260914.md
*A contradiction-term fan-out scan by muse-drafter (Spark) against five candidate papers, checking for external critiques, replications, and self-declared limitations.*

- **research_intake** (L5) — "Queries appended `limitations`, `criticism`, `replication`, `false positive`, `no improvement`, `contamination` to each candidate."
- **verification** (L0) — "The contradiction pass re-found it; it is **not** net-new, and still has no card."
- **proposal** (L36) — "**MemDelta is not a new score source — it is a controlled-baseline protocol we should fold into the citation/evidence rule before the next arm**"

## COLLECTION-LOG.md
*This is an append-only collection log that records routine turn collections, artifact path and hash checks, and seat status for a multi-agent research fleet.*

- **operations** (L3) — "Append-only. One line per finished lane turn. The collector (fsync) reads the last ~40 lines of this file before every collection; this header is the standing rule."
- **verification** (L16) — "Check every claimed artifact path exists; if a hash is claimed, check it matches."

## CORVID-MAP-HASH-GUARD.md
*A document describing the implementation, verification, and integration of a hash-drift guard (guard 15) that checks coverage-map table cells against live guard file hashes.*

- **implementation** (L23) — "Parses the coverage map's Layer B table rows (numbered or `—` rows naming a `check_*.py` and an 8-char hash prefix)."
- **verification** (L33) — "Ran Assay's prototype `439dd1e1…` independently → **0 findings** on the live map, matching his result."
- **protocol** (L47) — "Added to `team/CORVID-RD-CHECKER-SUITE.md` as **guard 15** and to the coverage map's Layer B as a maintenance row (`—`)."

## RESEARCH-VENDOR-CLAIM-CHECKLIST.md
*A checklist document by Corvid that lists six integrity checks derived from the Hindsight audit, maps portfolio engines against them using existing receipts, and proposes a standing gate for P2/P4.*

- **proposal** (L55) — "Any headline number entering the P4 close report must carry, in-line: **paper-or-none · operator · split · metric · reader · judge · reproduction command**."
- **synthesis** (L4) — "**Cost:** $0, synthesis over existing ledger/survey receipts (no new fetches; provenance already on file)"
- **verification** (L43) — "| **Hindsight** | ACL 2026 demo, **co-authored by the "independent" parties** | 94.6 (live) > 91.4 (paper) | **vendor (AMB)** | page: no; paper: LongMemEval-S | **3 fails** (§Addendum, ledger L-HS-01..03) |"

## S10-KD-CROSS/check.py
*A Python gate script for queue row S11-2 that checks a cross-system replay directory against a prior single-system run's frozen sample and declared parameters.*

- **implementation** (L2) — "Gate for QUEUE row S11-2 (KnowledgeDrift cross-system replay: more systems on the SAME frozen sample, family scores kept separate, old beside new)."
- **protocol** (L39) — "Declared interface (ROOT = team/S10-KD-CROSS): the S7-4 files and schema (declaration.json, items.jsonl, results.jsonl, verdict.json), with   results.jsonl  engines return-nothing, oracle, then bm25, dense_lsa,          "

## S6-CORRECTION/check.py
*A Python gate script that declares and implements checks for the S6-1 correction document (the publishable correction to the S4-12 zeros), including a selftest that exercises its own failure modes.*

- **implementation** (L2) — "Gate for QUEUE row S6-1 (the publishable correction to the S4-12 zeros)."
- **protocol** (L0) — "The interface below is therefore declared by the gate, not fitted to a document; every finding names what it wants, so the author can conform without reading this source."

## D-7-timestamps/check.py
*A Python script implementing a verification gate for QUEUE row D-7 that re-derives timestamp comparisons from the board and filesystem on every run.*

- **implementation** (L2) — "Gate for QUEUE row D-7 (the board's own timestamps are not evidence)."
- **protocol** (L58) — "Exit contract (team/tools/check_checker_exit_contracts.py): 0 clean, 1 with a named marker and the line `D-7 gate findings: N`, never a traceback."

## S6-ROADMAP/check.py
*This document is a Python gate script for QUEUE row S6-3 that checks whether a set of files (map.md, evidence.json, next-experiment.json, review.json) conform to a declared interface, and includes a selftest that verifies the gate can accept conforming fixtures and reject single-defect mutants.*

- **implementation** (L64) — "python3 check.py [ROOT]      # ROOT defaults to this directory"
- **protocol** (L0) — "The interface below is declared by the gate, not fitted to a document; every finding names what it wants, so the author can conform without reading this source."

