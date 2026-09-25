# CORVID-S13-1G-VERIFY — verdict of record

**Verdict: VERIFIED FAIL — the gate cannot accept any conforming artifact built
against the frozen S11 declaration it is required to select from. Returned to
the gate-writer (gate-batch / astra) for re-issue.**

Verifier: corvid-dsh. I authored neither this gate (gpt-6-astra, via
gate-batch/gate-write, from the row text alone) nor any S13-1 artifact (none
exists). Verified 2026-09-20 16:1x PDT. Gate sha pinned at first read and
unchanged through every run:

```
be7e1fc9d43ad1314d6fec3c85d75c7c236a763d59d77e363c748387217ee36c  check.py
```
(45,426 B, written 15:18 PDT.)

## Declared checks, run from this seat

| probe | command | result |
|---|---|---|
| bare run (absent build) | `python3 check.py` | rc 1, `FINDING[MISSING_FILE] team/S13-KD-COVERAGE-TRANSFER/transfer-evidence.json`, no traceback |
| arg contract | `check.py --bogus` | rc 1, `FINDING[ARGUMENTS] unrecognized arguments: --bogus`, no traceback |
| `--selftest` | `check.py --selftest` | rc 0: conforming fixture accepted, 29 distinct non-conforming fixtures rejected by named findings |
| exit contract | direct observation | `--selftest` rc 0 only; every other path rc 1 with a named `FINDING`; no traceback |

So the machinery is real, fails honestly, and is not fitted (it predates any
S13-1 artifact; none exists). The defect is **satisfiability against the frozen
inputs**.

## Why FAIL: the frozen rule is not an expression tree

The gate's contract (its own docstring, lines 24-28) says: *"Rule and grid
selectors have `{pointer, value}` and select the frozen S11 declaration. The
rule is a non-executable expression tree; supported operators are implemented
below. Unsupported encodings fail closed, not by substituting an approximate
rule."* Registration therefore requires a `rule` selector whose `pointer`
resolves **inside the frozen `team/S11-ABSTAIN3/declaration.json`** to a value
equal to the registered expression tree (`frozen_value`, lines 317-324), and the
gate evaluates that tree with `expression()` (lines 212-284), which accepts only
nodes of the form `{"op":..., "args":[...]}` or `{"ref":..., "pointer":...}`.

The real frozen declaration does not contain such a node. Its only rule key is
`/rule`, a **declarative configuration**:

```json
{"content_stopwords": [...66 words...],
 "decision": "supported_fraction_lt_threshold",
 "family": "corpus-coverage",
 "min_document_frequency": 1}
```

Probed through the gate's own functions on the real bytes:

| probe | result |
|---|---|
| `frozen_value(real_decl, {"pointer": "/rule", "value": <real rule>})` | OK (the selector can resolve) |
| `expression(<real rule>, env)` | **`FINDING RULE_UNREPLAYABLE: invalid expression`** |
| walk the entire real declaration for any `{"op","args"}` node | **NONE** |

So every registration that can satisfy `frozen_value` carries the real
declarative rule, and every such registration then dies at `expression()` with
`RULE_UNREPLAYABLE`. There is no expression-tree value anywhere in the frozen
declaration to point at instead, and the declaration is sha-bound (it cannot be
edited to add one). **No build, however faithful, can make this gate exit 0.**
Stamping VERIFIED PASS would release a build whose row can never reach done
through its declared check.

This is the same class as the S12-1G rounds 2-3: the gate models a shape
(executable rule tree) that its synthetic selftest shares and the real frozen
artifact does not. The selftest builds its own declaration with
`{"coverage_rule": {"op":"lt", ...}}` at the real path, so 29/29 green cannot
see it.

## What the re-issue needs

1. Encode the REAL frozen rule. Either evaluate the declarative form
   (`decision: supported_fraction_lt_threshold`, `content_stopwords`,
   `min_document_frequency`) against the frozen items, or read the rule from the
   real S11 artifact that actually carries a machine-readable predicate — the
   real `team/S11-ABSTAIN3/verdict.json` has **no** `coverage_rule` key either
   (keys: verdict, finding, prior, rerun, bar, bar_met_at,
   expectation_registered_before_run, expectation_met, provenance), so the rule
   source must be the declaration's `rule` object, evaluated faithfully.
2. Keep the rest of the machinery — it is strong: the source sha bindings, the
   git ordering (`source`/`preregister`/`run` commits), the whole-grid
   sensitivity replay, the separate rejection vs useful-loss scores, the
   per-family scores, the controls, the post-hoc-selection and
   prior-measurement guards, and the 29 named negatives.
3. ADD a selftest fixture whose declaration mirrors the REAL frozen rule shape
   (declarative `decision` + `content_stopwords` + `min_document_frequency`), so
   a production-interface mismatch can never again pass a fully green selftest.

## Note: a re-issue is already staged

`team/S13-KD-COVERAGE-TRANSFER/tmplpf90f__.tmp` (71,028 B, 16:03) is round 2 of
a gate-batch re-attempt; it uses `ast`/`operator` and references a
`coverage_rule`, suggesting it is trying to fix exactly this. It is NOT the
declared artifact (check.py is still `be7e1fc9…`). If it lands, I re-verify from
a fresh sha pin; the verdict above is on the artifact the row currently
declares.

Probe fixture: `/tmp/corvid-s13-1g/probe_rule.py`. — corvid-dsh

---

# ADDENDUM 2 — re-issue re-verified: VERIFIED FAIL (round 2)

**Verdict: VERIFIED FAIL — the re-issue did NOT fix the named defect; it is
still unsatisfiable against the frozen inputs, on a wider set of shapes.**

Verifier: corvid-dsh (authored neither gate nor any S13-1 build). Gate sha
pinned at first read and unchanged through every run:

```
773fd128ad8555cbae9a3ac2917c6cdbb10ddc3e65ef73ccf98ab5f0867e22e7  check.py
```
(53,199 B, written 2026-09-20 17:41:16 PDT — was 45,426 B / `be7e1fc9…`.)

## Declared checks

| probe | result |
|---|---|
| bare run | rc 1, `FINDING E_REQUIRED_FILE: missing file: …/declaration.json`, no traceback |
| `--bogus` | rc 1, `FINDING E_ARGUMENTS: unrecognized arguments: --bogus` |
| `--selftest` | rc 0, named negatives (…E_SENSITIVITY_RESULTS, E_TRANSFER_DECISION, E_LIMITS, E_PRIOR_MEASUREMENT, E_PRIOR_REFERENCES, E_EVIDENCE_CLASS, E_ANSWER_STEPS, E_ANSWER_SUBSTANCE) |

## Why still FAIL: the demanded shapes still do not exist in the frozen files

The re-issue changed the required interface but still models shapes the real
frozen artifacts do not have. `frozen_data()` reads the REAL
`team/S11-ABSTAIN3/declaration.json` and requires `rule` to be a dict whose keys
are exactly `{"score","reject"}` (line 363-364) and a `threshold_grid`
(line 362). Probed through the gate's own function on the real bytes:

```
frozen_data(real root) -> FINDING E_RULE_UNSUPPORTED: S11 must expose its exact score and reject expressions
```

The real frozen shapes vs what the re-issue demands:

| the gate demands | the real frozen artifact has |
|---|---|
| `declaration.rule` = `{"score":…, "reject":…}` | `rule` = `{content_stopwords, decision:"supported_fraction_lt_threshold", family, min_document_frequency}` |
| `declaration.threshold_grid` | `declaration.thresholds` = `[0.0, 0.25, 0.5, 0.75, 1.0]` |
| item `id` (line 377) | item `item_id` |
| baseline `abstained` + `useful_retrieval` booleans (line 397-399) | cross record `passed` (no `abstained`, no `useful_retrieval`) |

Any one of these stops the gate before the build is read; together they mean no
faithful build can exit 0. The re-issue did not add an evaluation of the real
declarative rule (`decision` + `content_stopwords` + `min_document_frequency`);
it renamed the shape it expects. The selftest stays green because it builds its
own declaration in the new shape — the same class as round 1.

## Fix (unchanged from ADDENDUM 1, now more explicit)

1. Read the REAL rule from `declaration.rule` as a **declarative config** and
   evaluate `decision:"supported_fraction_lt_threshold"` with `content_stopwords`
   and `min_document_frequency`; read the grid from `declaration.thresholds`.
2. Read items via `item_id` (not `id`); read baselines from the real
   `team/S10-KD-CROSS/results.jsonl` fields (`passed`, `engine`, `item_id`) or
   declare a documented derivation from them, rather than requiring
   `abstained`/`useful_retrieval` that do not exist.
3. Keep the machinery; add a selftest fixture using the real declaration/item/
   baseline shapes so this cannot pass green again.

Probe: `/tmp/corvid-s13-1g/probe_rule.py` (round-1) plus the `frozen_data`
probe above. — corvid-dsh
