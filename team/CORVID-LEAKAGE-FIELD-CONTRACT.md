# Leakage-field contract (`leakage@k`) — declared trigger, legacy floor

**Author:** Corvid (`worker-glm-dsh3`), R&D + evidence-integrity · **Date:** 2026-09-14 · **Cost:** $0, static
**Status:** **ADOPTED (2026-09-14)** — the design was second-seated by Assay's
census (`team/ASSAY-LEAKAGE-FIELD-CENSUS.md`) and Alice's independent recount
(`team/ALICE-LEAKAGE-CENSUS-SECONDDRIVER.md`); Alice's B1–B3 blockers are pinned
by Assay's power-checked delta (`team/ASSAY-LEAKAGE-DELTA-POWER.md`, real-path
matrix 17/17, Corvid-reproduced), and the delta is **applied** to
`check_required_metrics.py` (`3ae6cf05…` → **`09814e25…`**) and
`probe_leakage_field_contract.py` (`23a640c8…` → **`58bcc588…`**). Alice's
re-sign on the applied bytes is the only open seat item.
**Serves:** `CORVID-SCOPE-LEAKAGE-GATE-ADDENDUM.md` §6 step 1 / Gap **G-B**.

## The problem this closes

My addendum proposed requiring `leakage@k` on runs whose cases carry
cross-scope or retracted items. Assay's census and Alice's independent recount
agree that a **`detail.csv`-derived trigger is non-discriminating**: 0 of 102
canonical details carry a scope/leak column, while `prohibited_ids` is universal
(102/102). A fail-closed guard keyed on detail would red all 102/105/102 legacy
runs — an instrument that cries wolf on the whole corpus. The requirement needs
a **declaration**, not a derivation.

## The contract

| Element | Rule |
|---|---|
| **Declaration** | `results/<run>/LEAKAGE-REQUIRED.json` — `{"leakage_required": true, "classes": ["wrong_scope","post_retraction","future"], "fixture": "..."}`. Emitted by the arm builder, not inferred. |
| **Satisfaction** | `summary.csv` exposes a `leakage@k` column (any `leakage@<int>` header; sub-type columns optional). Required **iff** declared. |
| **Legacy floor** | A run with **no declaration** is not required to report the column. **Absence alone is never a finding** — so no edit to the 102/105/102 legacy dirs is needed. |
| **Waiver** | A declared run that cannot report the field ships `METRIC-WAIVER.json` naming `leakage` with a reason — the same mechanism guard 14 already honors. |
| **Symmetric direction** | A summary that *carries* a leakage column with **no declaration** is reported (advisory): a runner cannot quietly start reporting the field and let the declaration drift. |
| **Malformed declaration** | A present-but-unparseable `LEAKAGE-REQUIRED.json` is a finding (fail closed), never a silent skip. |

**Refinement over the census's recommendation:** Assay proposed a blanket legacy
waiver; with a declaration file the floor is simply *no declaration*, so the
legacy set needs no waiver at all (a waiver only for a declared arm that cannot
yet report). If the harness cannot emit the declaration, Assay's waiver-first
floor is the correct fallback — both are consistent with "declare the trigger."

**Alice's caveat, honored:** `wrong_scope_context_case_rate` is **computed by
`frozen_reader.py` (`4f4649d7…`), not stored**, so the guard must read a column
the runner **persists** — it cannot read the aggregate straight from the reader
JSON. The contract requires the persisted column for that reason.

## Power check (the contract fires on the failure it exists for)

`implementer/repo-glm-dsh3/scripts/probe_leakage_field_contract.py`
sha256 `23a640c83797dfcc…` (pre-adoption; now **`58bcc588…`**);
`--self-test` **PASS**, five controls through the real `scan()` path:

| control | expected | result |
|---|---|---|
| legacy run (no declaration, no column) | clean | clean |
| declared leakage-bearing, no column, no waiver | **flagged** `leakage@k required but absent` | flagged |
| declared leakage-bearing, column present | clean | clean |
| undeclared run that carries the column | advisory | advisory |
| declared, no column, valid waiver | clean | clean |

**Adoption power check:** Assay's 17-case real-path matrix
(`ASSAY-LEAKAGE-DELTA-POWER.md`, `leakage_delta_power_check.py` `752817d0…`)
reports the shipped probe deviating on all 8 named controls (B1/B2/B3/B4) and the
candidate matching every expectation; Corvid re-ran it pre-apply (**PASS**) and
confirmed the applied bytes are byte-identical to Assay's seals. The guard's
extended self-test asserts each leakage case per-case, and the real CLI rejects
a synthetic declared-missing tree (rc 1) while clearing legacy / `false` /
present.

**Live census (three trees, static):**

| tree | runs scanned | declared leakage-bearing | findings |
|---|---:|---:|---:|
| `implementer/repo` (canonical) | 102 | 0 | 0 |
| `repo-glm-dsh3` | 106 | 0 | 0 |
| `repo-glm-dsh2` | 102 | 0 | 0 |

So adoption is a **no-op today** — the guard would be green on all three trees
and would bite only a new arm that declares itself leakage-bearing and then
omits the field.

## Guard-14 schema delta (APPLIED 2026-09-14)

The delta adopted in `check_required_metrics.py` (`3ae6cf05…` → **`09814e25…`**):

- `kinds.run_summary` gains `leakage_marker: "LEAKAGE-REQUIRED.json"` and
  `leakage_column_pattern: "leakage@\\d+"` (both type-validated);
- trigger is the boolean `leakage_required: true` (not file presence); absent /
  `false` = legacy floor; unparseable / non-object = finding (fail closed);
- matcher is a whole-cell `re.fullmatch(r"leakage@\d+", col, re.IGNORECASE)`
  **shared with the probe**, so `not_leakage` / `leakage_notes` / bare
  `leakage` do not satisfy it (pins B3);
- waiver is exact token membership in `{"waived": [...]}` — the literal
  `leakage` family token or an exact `leakage@<int>` — never a reason substring
  (pins B1);
- the marker check runs **before** the unknown-schema skip (pins G2);
- the self-test asserts each case per-case (pins G1), and the real CLI rejects a
  declared-missing run while clearing legacy/`false`/present.

Probe `probe_leakage_field_contract.py` (`23a640c8…` → **`58bcc588…`**) now
shares the matcher and waiver test and uses guard 14's `{"waived": [...]}` waiver
fixture (B4).

## Honest limit

A leakage-bearing run that declares **nothing** and reports **nothing** is not
structurally detectable from the artifacts — the declaration is on the arm
builder's honour. The contract catches the two drift directions it can
(declared-but-unreported, reported-but-undeclared); it does not manufacture a
signal where the artifacts are silent. Stated so a green census is not read as
"no leakage anywhere."

## Next step (bounded)

1. Alice re-signs the **applied bytes** (B1–B3 pinned; Assay power check
   reproduced by Corvid; three-tree census a no-op).
2. Fold the field into `CORVID-P2-EVIDENCE-GATE-CARD.md` publication-gate prose
   (still not a seventh pass/fail check — it rides guard 14).

— **Corvid** (`worker-glm-dsh3`). $0, static; no number changed, no guard wired.
