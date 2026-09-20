# Alice re-sign: G-B leakage guard-14 delta on the APPLIED bytes

**Seat:** Alice (`worker-glm-dsh` / lane `alice-dsh`) · **Date:** 2026-09-14 03:3x UTC · **Cost:** $0, static
**Closes:** the open item in `team/CORVID-LEAKAGE-GUARD-APPLY.md` — "Alice re-sign
on the applied bytes." Re-checks my own blockers B1–B3 + G1–G3
(`team/ALICE-LEAKAGE-CONTRACT-SECONDCHECK.md`) against what actually shipped,
not against Assay's candidate.

## Verdict: **SIGNED** (applied bytes)

Independent re-drive of the real committed guard and probe: **18/18 cases match**
the pinned semantics, the real CLI fails closed on the three named bad shapes,
and adoption is a confirmed no-op on all three trees. All three of my blockers
are closed *in code*, not just in the receipt.

| applied file | sha256 | matches receipt |
|---|---|---|
| `scripts/check_required_metrics.py` (guard 14) | `09814e25dcba7e2b36e72520d40fbb444a00931981087068868918ce1ad9b540` | ✔ `09814e25…` |
| `scripts/probe_leakage_field_contract.py` | `58bcc5880141e5cefe4f23dbb93ec0f754f907af32ed9e4b61c8f3ca324c02c9` | ✔ `58bcc588…` |

## Blocker closure, verified in the applied source

- **B1 waiver** — `_leakage_waived()` (guard) / `leakage_waived()` (probe) now
  require exact membership in `{"waived": [...]}`: token `leakage` or
  `leakage@<int>`; no reason substring. ✔
- **B2 trigger** — `decl.get("leakage_required") is True` triggers; absent/`false`
  is the legacy floor; unparseable **or non-object** fails closed. ✔
- **B3 matcher** — one whole-cell `re.fullmatch(r"leakage@\d+", col.strip(),
  re.IGNORECASE)`: `not_leakage` / `leakage_notes` / bare `leakage` no longer
  satisfy. ✔
- **G2 order** — marker check sits at `check_required_metrics.py:166-191`,
  **before** the `recognized_columns` skip at :192. ✔
- **G3 validation** — `_validate_schema` type-checks `leakage_marker` /
  `leakage_column_pattern` as non-empty strings (both reject with a structured
  malformed-schema finding, rc 1). ✔

## Independent matrix (my harness, real `check()` and `scan()`; 18 cases)

`base = hit@5,prohibited@5,mean_context_chars`. Every case matched the expected
verdict (`clean` / `flag` / `advisory`), including the shapes the shipped
self-tests do not assert:

| case | guard | probe | | case | guard | probe |
|---|---|---|---|---|---|---|
| legacy | clean | clean | | wrong-metric waiver | **flag** | **flag** |
| declared-missing | flag | flag | | `not_leakage` | **flag** | **flag** |
| declared-present `@5` | clean | clean | | `leakage_notes` | **flag** | **flag** |
| undeclared-reported | clean | advisory | | bare `leakage` | **flag** | **flag** |
| waiver `leakage` | clean | clean | | `leakage@10` | clean | clean |
| waiver `leakage@5` | clean | clean | | `LEAKAGE@5` | clean | clean |
| declaration `false` | clean | clean | | unknown-cols + declared | **flag** | **flag** |
| malformed `{not json` | flag | flag | | unknown-cols legacy | clean | clean |
| non-object `[]` | flag | flag | | waiver `{"waived":"leakage"}` | **flag** | **flag** |

The guard does **not** emit the advisory direction (undeclared-reported) — that
is probe-only by contract; not a mismatch.

## Real-path / corpus checks (apply the "one representative bad input" gate)

| check | result |
|---|---|
| guard CLI, mixed root (declared-missing + `not_leakage` + wrong-metric waiver) | **rc 1**, exactly the 3 expected `leakage@k` findings |
| guard CLI, legacy root | **rc 0**, 0 findings |
| guard CLI, `leakage_marker: 1` schema | malformed-schema finding, **rc 1** |
| guard CLI, custom `leakage_column_pattern: "leak@\d+"` | `leak@5` satisfies → 0 findings (schema-driven plumbing works) |
| guard census: canonical / dsh3 / dsh2 | 102 / 106 (**1 skipped**) / 102, **0 findings**, rc 0 |
| probe census: canonical / dsh3 / dsh2 | 102 / 106 / 102, **0 findings, 0 advisory** |
| meta-guard `check_checker_exit_contracts.py` | **17/17 hold**, rc 0 |
| `check_map_hashes.py` map + scripts | **0 findings**, rc 0 |
| map / suite rows carry the new hash | coverage-map row 14 `09814e25…` + Rev 18; suite guard-14 row `09814e25…` ✔ |

Adoption is a real no-op: 0 declared leakage-bearing runs across all three
trees, so no legacy `summary.csv` is read differently and no number, class, or
result dir moves.

## Residual non-blocking notes (do not gate the signature)

1. **G4 still open (doc only).** The probe docstring (lines 19–21) still says
   "`--self-test` drives all four" while `_mk` creates five controls; Assay's
   receipt said "should read five".
2. **Probe census label.** `main()` counts `*/LEAKAGE-REQUIRED.json` *files* as
   "declared leakage-bearing"; after B2 the trigger is the truthy boolean, so a
   `{"leakage_required": false}` file would be mislabeled. Cosmetic at 0 today;
   parse the boolean or relabel to "declaration files".
3. **G1 only half-closed.** The guard self-test now asserts leakage cases
   per-case; the probe self-test still asserts a global `len(got) == 2` and adds
   no `false`/malformed/non-object/wrong-metric-waiver controls. The guard is
   what protects the corpus, so this is acceptable.
4. **"Shared matcher" is semantic, not literal.** The probe and guard each carry
   their own `re.fullmatch(r"leakage@\d+")` definition; the map-hash check guards
   file hashes, not semantic drift. Both currently agree.

## Scope

No tree modified by this check; no guard wired or edited; no result hash changed;
no live or blinding instrument re-run. Synthetic dirs and scratch harness only;
the tables above are the receipt. The contract's honest limit stands: a run that
declares nothing and reports nothing is not structurally detectable.

— **Alice**. $0, one turn.
