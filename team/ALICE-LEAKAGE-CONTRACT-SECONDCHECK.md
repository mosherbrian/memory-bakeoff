# Second seat: leakage-field contract + guard-14 schema delta

**Seat:** Alice (`worker-glm-dsh` / lane `alice-dsh`) · **Date:** 2026-09-14 02:57Z · **Cost:** $0, static
**Reviews:** `team/CORVID-LEAKAGE-FIELD-CONTRACT.md` (Corvid, 2026-09-14) and its probe.
**Serves:** that doc's "Next step" item 1 (Alice/Assay second seat on the contract + schema delta).

## Verdict

**The contract direction is SOUND and the census is CONFIRMED. The guard-14 schema
delta is NOT YET SIGNABLE** — three small, named semantic blockers (all in the
delta, none in the design) each let a declared leakage-bearing run pass or fail
for the wrong reason. Fix them and this seat signs.

| check | claimed | re-derived | verdict |
|---|---|---|---|
| probe sha256 | `23a640c8…` | `23a640c83797dfcc3fe21199a6a0f922e4c948555996568d3e4ebbf5fd550735` | ✔ |
| guard-14 sha256 | `3ae6cf05…` | `3ae6cf05632ea8c47b1b56d46afe8539971d84dc3b48e72a74fe7e732bed98ab` | ✔ |
| probe `--self-test` | PASS | PASS (5 controls) | ✔ |
| three-tree census | 102/106/102, 0 declared, 0 findings | 102/106/102, 0 declared, 0 findings | ✔ |
| aggregate not stored | `wrong_scope_context_case_rate` computed by `frozen_reader.py` | `repo-glm-dsh3/src/memory_bakeoff/frozen_reader.py:144` computes it; absent from every `summary.csv` (present only in one reader `manifest.json`) | ✔ (caveat holds at summary level) |

Census command (reproducible): `cd implementer/repo-glm-dsh3/scripts && python3
probe_leakage_field_contract.py ../../<tree>/results`.

## Adversarial controls (real `scan()` path, synthetic dirs, nothing committed)

Corvid's five controls reproduce. I added seven shapes the self-test never
covers; column set was `hit@5,prohibited@5,mean_context_chars` in every case.

| # | case | observed | should be |
|---|---|---|---|
| c7 | declaration `{"leakage_required": false}` | **flagged** required-absent | legacy floor |
| c8 | waiver `{"waived":["hit@5"],"reason":"…leakage in corpus…"}` | **clean** | still flagged (wrong metric waived) |
| c9 | declared, column `not_leakage` | **clean** | still flagged (no metric) |
| c10 | declared, column `leakage_notes` | **clean** | still flagged (no metric) |
| c11 | declared, column `leakage` (no `@k`) | **clean** | flagged (contract says `leakage@<int>`) |
| c12 | declaration `[]` (parseable, not an object) | required-absent, no malformed finding | fail-closed; either shape is defensible |
| c13 | declared, column `leakage@10` | clean | clean ✔ |
| c6 | declaration `{not json` | malformed **and** required-absent | flagged ✔ (untested by self-test) |

## Blockers before the schema delta can be signed

**B1 — waiver semantics undefined; probe's waiver test is not guard-14's.**
Guard 14 waives by exact membership in `{"waived":[<column>,…]}`. `leakage@k` is
a *family* (`leakage@5`, `leakage@10`, …), so "waiver lookup unchanged" has no
fixed token to match. The probe sidesteps this with `"leakage" in
json.dumps(waiver).lower()`, which c8 defeats: a waiver for an unrelated metric
suppresses the leakage finding if its reason text says "leakage".
*Fix (pick one and write it in the delta):* define the waiver token as the
literal `"leakage"` with prefix matching (`metric.startswith(token)`), or add a
dedicated `"leakage_waived": true` field. Do not waive on substring.

**B2 — trigger is file presence, not `leakage_required`.** c7 shows a
declaration carrying `"leakage_required": false` still imposes the requirement;
c12 shows a bare `[]` is accepted as a declaration. The field name promises a
boolean.
*Fix:* pin the rule. Recommend `decl.get("leakage_required") is True` triggers;
non-object or `false` = legacy floor; unparseable = finding. If presence is
meant to be the trigger, delete the boolean or document it as informational.

**B3 — matcher strictness not pinned; probe and delta disagree.** The delta
proposes `leakage_column_pattern: "leakage@\\d+"`; the probe uses
`re.compile(r"leakage(@\d+)?", re.IGNORECASE).search`, which accepts `not_leakage`,
`leakage_notes`, and bare `leakage` (c9–c11). A declared run can therefore
"satisfy" the requirement with a column that carries no leakage number — the
same selective-omission class guard 14 exists to catch, one field over.
*Fix:* put the matcher in one function used by both the probe and the guard;
recommend `re.fullmatch(r"leakage@\d+", col, re.IGNORECASE)` (plus any declared
sub-type whitelist), or state that a documented sub-type prefix is the unit.

## Non-blocking gaps (fix with the delta, don't gate the signature)

- **G1 — malformed rule has no power-check control.** The self-test asserts a
  global `len(got) == 2` and never exercises c6, c7, or c12. The contract's rule
  table has six rows; the power-check table has five. Add controls and assert
  per-case, not globally.
- **G2 — guard-14 integration edge.** The existing loop skips a summary with
  none of `recognized_columns` (`check_required_metrics.py:134`) *before* any
  per-run requirement logic. A declared run whose summary omits all recognized
  columns is silently skipped, so "required iff marker present" is not enforced
  for that shape. Make the marker check precede the recognized-skip.
- **G3 — new schema keys unvalidated.** `_validate_schema` type-checks only
  `required_columns`/`recognized_columns`/`waiver_file`/`glob`; a malformed
  `leakage_marker`/`leakage_column_pattern` would change behavior silently.
  Extend the validation with the delta.
- **G4 (doc only).** Probe docstring says "drives all four" controls while the
  body creates five; the RD entry says five. Stale docstring.

## Sign-off

Second seat **conditional**: I sign the *contract* (declared trigger, legacy
floor, advisory symmetric direction, malformed = finding) and I confirm the
probe fires on the five stated controls and the three-tree zero census. I do
**not** sign the guard-14 schema delta until B1–B3 are pinned in the delta text
and the probe shares the guard's matcher and waiver test.

**Not done:** no guard wired, no tree modified, no live/blinding instrument
re-run, no hash of any result changed. The adversarial harness was written to a
scratch dir and is not committed; the table above is the receipt.

— **Alice**. $0, one turn.
