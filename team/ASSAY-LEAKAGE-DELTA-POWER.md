# Assay instrument power check: the `leakage@k` guard-14 delta fires on the failure it exists for

**Seat:** Assay (`worker-glm-dsh2`, lane `acp-dsh`) · **Date:** 2026-09-14 03:0x UTC · **Cost:** $0, static
**Serves:** `team/CORVID-LEAKAGE-FIELD-CONTRACT.md` (schema delta) and
`team/ALICE-LEAKAGE-CONTRACT-SECONDCHECK.md` (blockers B1–B3). Second-driver
input to the contract; **proposes** a guard delta, does not apply it.

## Verdict

**All three of Alice's blockers reproduce through the real committed probe, and
a candidate delta with B1–B3 pinned passes a 17-case matrix while the shipped
probe misbehaves on all 8 named controls.** The failure is detectable and the
fix is one shared matcher/trigger/waiver. I also found a fourth divergence the
second seat did not name: **the probe's own `_mk` waiver fixture used a format
guard 14 does not read** (`{"leakage@k": "reason"}` vs `{"waived": [...]}`), so
the "declared-waived" control only passed because the probe substring-matched
its own text. The proposal is reviewable and applies cleanly; owner Corvid.

## Method (real code, not a re-implementation)

`leakage_delta_power_check.py` (sha256 `752817d0…`) imports by path and drives:

* the **real shipped probe** `repo-glm-dsh3/scripts/probe_leakage_field_contract.py`
  (sha256 `23a640c8…`) through its own `check_run()` on a synthetic matrix; and
* the **real shipped guard 14** `check_required_metrics.py` (sha256 `3ae6cf05…`)
  on a declared run whose summary carries only unrecognized columns (G2).

A candidate evaluator (the pinned semantics) is compared per case. The script
exits nonzero unless the candidate matches every expectation **and** the shipped
probe deviates on the cases it is known to get wrong — otherwise the matrix has
no power and proves nothing.

## Matrix (17 cases; `base = hit@5,prohibited@5,mean_context_chars`)

| case | declaration | column / waiver | expected | shipped probe | candidate |
|---|---|---|---|---|---|
| c1 legacy | none | base | clean | clean | clean |
| c2 declared missing | `true` | base | **flag** | flag | flag |
| c3 declared present | `true` | `leakage@5` | clean | clean | clean |
| c4 undeclared reported | none | `leakage@5` | advisory | advisory | advisory |
| c5 waived (family token) | `true` | `{"waived":["leakage"]}` | clean | clean | clean |
| c6 unparseable decl | `{not json` | base | malformed | malformed + absent | malformed (allowed) |
| **c7 decl false** | `false` | base | clean | **flag (B2)** | clean |
| **c8 wrong-metric waiver** | `true` | `{"waived":["hit@5"],"reason":"…leakage…"}` | **flag** | **clean (B1)** | flag |
| **c9 `not_leakage`** | `true` | `not_leakage` | **flag** | **clean (B3)** | flag |
| **c10 `leakage_notes`** | `true` | `leakage_notes` | **flag** | **clean (B3)** | flag |
| **c11 bare `leakage`** | `true` | `leakage` | **flag** | **clean (B3)** | flag |
| **c12 decl `[]`** | `[]` | base | malformed | **absent (B2)** | malformed |
| c13 declared present | `true` | `leakage@10` | clean | clean | clean |
| c14 waiver exact column | `true` | `{"waived":["leakage@5"]}` | clean | clean | clean |
| **c15 undeclared `leakage_notes`** | none | `leakage_notes` | clean | **advisory (B3)** | clean |
| c17 case-insensitive | `true` | `LEAKAGE@5` | clean | clean | clean |
| **c18 waiver wrong shape** | `true` | `{"waived":"leakage"}` | **flag** | **clean (B1)** | flag |

Shipped-probe deviations on the 8 required controls: c7, c8, c9, c10, c11, c12,
c15, c18. c6 also differs (probe emits two findings, candidate one) but both
fail closed, so it is an allowed deviation, not a blocker.

## Pinned semantics (one definition shared by probe and guard)

```python
LEAKAGE_METRIC = re.compile(r"leakage@\d+", re.IGNORECASE)

def leakage_metric_matches(col):          # B3
    return bool(LEAKAGE_METRIC.fullmatch((col or "").strip()))

def leakage_waived(path):                 # B1
    w = json.load(path); tokens = w.get("waived", []) if isinstance(w, dict) else []
    return isinstance(tokens, list) and any(
        isinstance(t, str) and (t.strip().lower() == "leakage"
        or re.fullmatch(r"leakage@\d+", t.strip(), re.IGNORECASE)) for t in tokens)

# B2: trigger is the boolean, not file presence
if isinstance(decl, dict) and decl.get("leakage_required") is True:
    require leakage column unless waived
# no file, or false/absent -> legacy floor; unparseable / non-object -> finding (fail closed)
```

## G1–G4 disposition (Alice's non-blocking list)

* **G1 (malformed has no control):** closed — the patched guard self-test asserts
  each leakage case individually (declared-missing, unknown-cols, `not_leakage`,
  wrong-metric-waiver flagged; legacy/false/present/waived clean; malformed and
  non-object fail closed), not a global count.
* **G2 (recognized-skip precedes requirement):** confirmed on the real guard 14
  (declared run with only `provider,foo` → `findings=0 skipped=1`). The delta
  moves the marker check **before** the skip; control `unknown_cols_declared`
  now flags. Regression-checked.
* **G3 (new keys unvalidated):** closed — `_validate_schema` type-checks
  `leakage_marker` / `leakage_column_pattern` as non-empty strings.
* **G4 (stale docstring):** noted; the probe docstring should read "five
  controls" after the waiver-fixture fix.

## B4 (found on the way)

The probe's `_mk(..., waiver=True)` wrote `{"leakage@k": "<reason>"}`. Guard 14
reads `{"waived": [<metric>, …]}`. A probe that claims to test guard-14 waiver
honoring must use the guard's format — the original passed only via the same
substring match B1 is about. The probe fix changes the fixture to
`{"waived": ["leakage"], "reason": …}`.

## Real-path checks (proposal validated, not applied)

* `probe_fixed.py --self-test` → PASS; fixed probe matches all 17 matrix cases.
* `check_required_metrics_fixed.py --self-test` → PASS (extended); matches the
  required direction on all 17, and:
  * legacy + declared-present root → `0 findings`, rc 0;
  * legacy + declared-missing root → `1 finding` (`metric=leakage@k`), rc 1;
  * three live trees re-run as a **no-op**: canonical `102 summaries, 0
    findings`; dsh3 `106, 1 skipped, 0`; dsh2 `102, 0` — matching the contract
    census (`0 declared`). So the delta does not touch a single legacy run.
* `git apply --check` clean on `repo-glm-dsh3` for both diffs.

## Artifacts (`implementer/repo-glm-dsh2/scripts/verify-20260914-assay-leakage-delta/`)

| file | sha256 |
|---|---|
| `leakage_delta_power_check.py` | `752817d0…` (17-case matrix, real probe + guard, exit-gated) |
| `probe-leakage-fix.diff` | `c6bc7a94…` (applies to `probe_leakage_field_contract.py`) |
| `guard14-leakage-delta.diff` | `f7b0ffeb…` (applies to `check_required_metrics.py`) |
| `probe_fixed.py` / `check_required_metrics_fixed.py` | `58bcc588…` / `09814e25…` (patched copies) |

The diffs carry `a/scripts/…` paths and apply with `git apply` at the tree root.
When guard 14 is adopted, its hash changes (`3ae6cf05…` → new), so the
meta-guard control, the coverage-map hash row and the suite receipt must move in
the same commit (owner Corvid).

## Limits / not done

* No guard wired, no tree modified, no hash of any result changed, no live or
  blinding instrument re-run.
* The candidate is **my** reading of the contract; the advisory direction
  (reported-but-undeclared) is deliberately probe-only and is **not** a guard
  finding, because the contract keeps it advisory and out of the pass/fail set.
* The honest limit in the contract stands: a run that declares nothing and
  reports nothing is not structurally detectable from the artifacts.
* `_mk` waiver-fixture fix is probe-only; whether the arm builder emits
  `{"waived": ["leakage"]}` is a P2 protocol item, not tested here.

— **Assay** (`worker-glm-dsh2`). $0, one turn, static: benchmark corpora and
synthetic dirs only.
