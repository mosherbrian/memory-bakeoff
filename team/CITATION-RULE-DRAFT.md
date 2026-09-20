# Citation rule for P3/P4 — consolidated draft for Verity's rule check

**Author:** Corvid (`worker-glm-dsh3`), merging proposals by **Stratum**, **Alice**,
and me. **Status:** **Rev 2** — DRAFT for Verity's rule pass + GiLMore nod at P2
entry; fields 7–8 marked proposed 2026-09-14. Does **not** replace Stratum's
`DESIGN-CORNERS-1.md` Corners 7b/8 (those govern scorer *design*) or Alice's
`ALICE-VENDOR-DATA-TRANSPARENCY.md` (the per-system evidence table).
**Cost:** $0, synthesis.

**Plain English (for Brian):** today's claim audits kept finding the same
failure — a benchmark number quoted without enough to reproduce or even compare
it. Instead of three separate rules, this is the single gate P3/P4 should apply
before a number reaches a report.

## The rule

An upstream (not-our-own-run) benchmark number may appear in a Brian-facing
artifact only if the citation carries **all** of:

1. **Source + date + pin** — the exact page/artifact, its date, and a
   commit/version pin (or an explicit `unpinned/mutable` marker).
2. **Operator** — who ran the harness: vendor / independent / vendor-operated.
3. **Split / version** — e.g. LongMemEval-S vs oracle vs V2; for pre-2026
   LoCoMo per-category numbers, the **numeric id** (1–5), never the prose name.
4. **Metric + reader + judge** — the answerer model, the grader, and the
   aggregation choice (question-weighted vs category mean).
5. **Reproduction status** — a command, or an explicit `not shipped`.
6. **Class** — `vendor-only` / `third-party-measured` /
   `third-party-attributed`; the last **never** moves the number off
   `vendor-only`.
7. **Evidence grade + confidence** (Rev 2) — `A/B/C/D/S` and `High/Med/Low`,
   per `RESEARCH-INTELLIGENCE-DIRECTIVE.md` §14. **The grade is authored, not
   derived from Class**: the census `team/CORVID-CITATION-GRADE-CENSUS.md` shows
   the ledger's current schema decides 9 of 16 headline rows and cannot promote
   any above `D`/`S` — the B-vs-C boundary needs code/data/ablation/replication
   facts we do not store.
8. **`REVISIT TRIGGER`** (Rev 2) — one line naming the evidence that would
   reopen the claim (benchmark version bump, independent measurement,
   contradiction hit, pin change). A number cited as evidence with an empty
   trigger is **incomplete**, not merely old. No current ledger cell carries
   this; it is a new authored field.

**Failure branches:**
- Cannot give source + date + pin → **do not cite it.**
- Operator is the vendor and no independent measurement exists → label it
  **"vendor-marketing, not evidence."**
- A live headline exceeds the vendor's own peer-reviewed number → same label
  until reconciled.

## Component credit (nothing here is new policy by me)

| Component | Owner | Receipt |
|---|---|---|
| source + date + pin, or no citation | Stratum | `ECOSYSTEM-MAP.md` §5; board 40x |
| operator + marketing-vs-paper + field set; "vendor-marketing, not evidence" | Corvid | Awaiting L1353; `RESEARCH-VENDOR-CLAIM-CHECKLIST.md` |
| `third-party-measured` vs `third-party-attributed`; LoCoMo numeric-id rule; name the grader | Alice | `CLAIMS-LEDGER.md` class refinement; `ALICE-OMNIMEMEVAL-JUDGE-CHECK.md`; `ALICE-VENDOR-DATA-TRANSPARENCY.md` |
| PASS/FAIL/INCONCLUSIVE + power check; arbitrary choices pinned before data | Stratum (Corners 8, 7b) | `DESIGN-CORNERS-1.md` — adjacent, **not** merged |
| A/B/C/D/S grade + `REVISIT TRIGGER` (fields 7–8); "grade is authored" finding | Corvid (advisory input from the directive) | `CORVID-CITATION-GRADE-CENSUS.md`; `probe_citation_grade.py` `86b4027f…`; `RESEARCH-INTELLIGENCE-DIRECTIVE.md` §14 |

## Why it matters — the receipts that motivated it

| System | Failure the field set catches |
|---|---|
| Hindsight | 94.6 is a **vendor-operated** AMB run (operator); the vendor's own paper says 91.4; "highest" `not established` (L-HS-02a/02b) |
| MemOS | self 89.20 vs TiMem **69.24 / 73.07** (`third-party-measured`), cross-protocol |
| Mem0 | 92.5 headline **traces to no shipped artifact**; four configurations across pages |
| Zep | **six** published numbers across four benchmarks; source must be named |
| Memobase | rival rows **pasted from Mem0's paper** — one origin, not corroboration |

## Handoff

- **Verity:** rule check — is the **eight-field** gate operational and testable,
  and does it conflict with Corners 7b/8 or the charter? For fields 7–8
  specifically: is "grade authored, Class not a grade" the right split, and is
  `REVISIT TRIGGER` enforceable as a non-empty line?
- **GiLMore:** nod at P2 entry; then it rides the P2 pre-registration.
- No ledger class changes; this is a citation gate, not a scoring rule.

— **Corvid** (`worker-glm-dsh3`). One gate from three seats' findings, for the
rule owner to accept or amend.
