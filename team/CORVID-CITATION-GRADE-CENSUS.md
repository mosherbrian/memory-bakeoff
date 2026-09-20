# Citation-grade census — can A/B/C/D/S be derived from our ledger?

**Author:** Corvid (`worker-glm-dsh3`), R&D + evidence-integrity · **Date:** 2026-09-14
**Cost:** $0, static · **Serves:** directive assessment §4 item 4 (fold the
evidence grade + `REVISIT TRIGGER` into the citation rule).
**Probe:** `implementer/repo-glm-dsh3/scripts/probe_citation_grade.py`
sha256 `86b4027f5e1de409…`; `--self-test` PASS.

## The question, and why it is worth answering before adopting

The directive (`team/RESEARCH-INTELLIGENCE-DIRECTIVE.md` §14) defines Grade
**A** (replicated), **B** (strong primary: code/data, baselines, ablations,
realistic workload), **C** (credible but incomplete), **D** (self-reported),
**S** (signal), and requires every finding to carry a **`REVISIT TRIGGER`**.
Assessment §4 item 4 says "fold it into the citation rule / ledger."

Before adopting a field, check whether we can populate it. If the grade is
**authored** it is a per-claim judgment (fine, but then the rule needs a
reviewer and a place to record it). If it is **derivable** from fields we
already keep, the ledger can compute it and the reviewer only audits. This
probe answers that mechanically, and the answer changes what the citation rule
should say.

## Method

Parse the primary headline table of `team/CLAIMS-LEDGER.md` (the table with
`Source kind` + `Class`), apply a documented draft mapping, and count. Rows the
mapping cannot decide are reported `UNDERIVABLE` **with the missing field named**
— that list is the actual finding.

Mapping (draft, in the probe):

| Class / Source kind | Draft grade | Basis |
|---|---|---|
| `verified-by-us` | A | our receipt |
| `third-party-measured` | B | independent measurement, not our reproduction |
| `third-party-attributed` | D | rule keeps it vendor-only |
| `unsourced` / search-summary / issue | S | signal-only |
| blog / README / competitor page / vendor doc | D | owner-controlled self-report |
| paper / arXiv / NeurIPS / body | **UNDERIVABLE** | B-vs-C turns on code/data/ablation/replication facts with **no ledger column** |
| `no-claim` / `UNCLAIMED` | n/a | nothing to grade |

## Result (live ledger, 16 headline rows)

| Grade | Rows |
|---|---:|
| A | 0 |
| B | 0 |
| C | 0 |
| D | 8 |
| S | 1 |
| n/a | 1 |
| **UNDERIVABLE** | **6** |

**The schema decides 9 of 16; it cannot promote a single row above D/S.** All
six underivable rows are primary-source claims (letta paper v2; a_mem v11/v1;
MemOS v4; Zep v1 ×2) — precisely the rows a reader would want graded B or C.

## Finding (three parts)

1. **The grade is authored, not derived — on our current schema.** The B/C
   boundary is exactly the information the ledger does not keep: whether the
   paper ships code/data, whether the baselines are meaningful, whether
   ablations exist, and whether the workload is realistic. So the citation rule
   must say **who assigns the grade and where it lives**, not imply it falls out
   of `Class`.
2. **`REVISIT TRIGGER` is entirely absent.** No table cell in the headline table
   carries "what would make this wrong." The directive's requirement therefore
   needs a **new ledger column** (and a citation-rule field), not a re-use of
   existing cells.
3. **Cheap schema change, not a re-scan.** Two authored sub-fields
   (`artifact_backed`, `independent_replication`) would make B-vs-C decidable;
   one authored field (`revisit_trigger`) satisfies the directive. Existing rows
   can default to `underivable`/`none recorded` and be filled on next touch — no
   number changes.

## Scope limit (stated so the census is not over-read)

- Only the **headline table** is parsed. The `L-HS-*` rows and `L-S16-02b`
  (TiMem independent values) live in other tables and are **not** in this
  census; a full-ledger version is a follow-up, not a bigger claim here.
- The probe is **advisory**, not a guard; it exits 0 and is deliberately not
  named `check_*` (a new gating guard would need a self-test, a meta-guard
  control, and a second seat first).
- The mapping is a **draft**, offered for amendment; the durable finding is the
  underivable set and the missing columns, not the particular letters.

## Proposed citation-rule change (Rev 2, pending Verity)

Add to the six-field gate:

7. **Evidence grade + confidence** — `A/B/C/D/S` plus `High/Med/Low`, with the
   class→grade mapping above. **Authored** from the source when B/C depend on
   artifact/ablation facts; `Class` alone must not be read as a grade.
8. **`REVISIT TRIGGER`** — one line naming the evidence that would reopen the
   claim (a benchmark version bump, an independent measurement, a contradiction
   hit, a pin change). A row cited as evidence with an empty trigger is
   **incomplete**, not merely old.

## Next step (bounded)

1. Extend the probe to the attribution + reproduction tables (full-ledger
   census) — one turn, static.
2. Fold fields 7–8 into `team/CITATION-RULE-DRAFT.md` (done in the same edit;
   marked proposed for Verity's rule pass).
3. If the ledger grows the three authored fields, the probe's `UNDERIVABLE`
   count is the before/after metric for the schema change.

— **Corvid** (`worker-glm-dsh3`). $0, static; no claim or number changed.
