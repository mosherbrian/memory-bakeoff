# Assay instrument power check — blind_pack.py scorer refusal guard

**Author:** Assay (worker-glm-dsh2) · **Date:** 2026-09-12 ~18:4x PDT · **Cost:** $0, offline
**RD-THREADS thread:** Assay — instrument power checks
**Instrument:** `team/blind_pack.py` (QUEUE row 9, fsync) — **pending adoption**;
this check is offered to its owner and to GiLMore/Verity, not a self-adopted change.
**Content scope:** synthetic sealed pack only. No live session, no packet, no
fire-log content.

## Question

`score` is the half of the blind harness that joins ratings to the sealed key.
Its guard is supposed to **refuse** (exit 2) any ratings sheet that is
incomplete, unknown, duplicate, off-vocabulary, or non-JSON
(`blind_pack.py:305-327`). Does it refuse on every malformed input, or can any
shape get past/around the guard?

## Method

Built a minimal synthetic s3 sealed dir (`packet/MANIFEST.json`,
`sealed/KEY.json`, two items) and drove the real `cmd_score` over nine rating
sheets plus a tampered key. Synthetic only.

## Result

| Input | Expected | Actual |
|---|---|---|
| valid baseline | rc 0 | rc 0 |
| duplicate item | refuse (2) | refuse (2) |
| unknown/extra item | refuse (2) | refuse (2) |
| label off-vocabulary | refuse (2) | refuse (2) |
| guess off-vocabulary | refuse (2) | refuse (2) |
| missing item | refuse (2) | refuse (2) |
| non-JSON line (`{oops`) | refuse (2) | refuse (2) |
| **JSON string line (`"just a string"`)** | **refuse (2)** | **CRASH: `AttributeError: 'str' object has no attribute 'get'`** |
| **JSON number line (`42`)** | **refuse (2)** | **CRASH: `TypeError: argument of type 'int' is not a container or iterable`** |
| tampered key | refuse (2) | refuse (2) |

## Defect (low severity, real)

`cmd_score` accepts a ratings line that is **valid JSON but not an object** and
then calls `.get()` on it. The `JSONDecodeError` handler catches malformed JSON
but not wrong-type JSON, so the guard **crashes instead of refusing**. It fails
loudly and does not accept bad input, so this is not a blinding hole; it is a
guard-robustness hole in an instrument that is about to be adopted.

**Proposed fix (one type check, in the parse loop after
`r = json.loads(line)`):**

```python
if not isinstance(r, dict):
    bad.append(f"line {n}: not a JSON object")
    continue
```

## Coverage gap in the shipped self-test (16/16)

The self-test asserts only **missing item** and **tampered key** among the
scorer refusals (plus the build leak gate). The duplicate, unknown/extra,
off-vocabulary (label and guess), and non-JSON paths **fire correctly but are
not asserted**. Cheap additions: one malformed sheet per path, folded into the
existing `quiet(cmd_score, ...) == 2` pattern. (A self-test that only covers the
paths that happen to be exercised is how the two crash paths above stayed
invisible.)

## Limits

- Synthetic inputs; this bounds the guard's behavior, not any live scoring run.
- Severity is low: the failure is loud and pre-acceptance, not silent.

## Receipts

- Check: `implementer/repo-glm-dsh2/scripts/verify-20260912-assay-row1/blind_pack_scorer_power_check.py`
  sha256 `ad56cf5d6b9d0451b267b72a66f5f61e7a4a29022f7b6fc8c88b6dcc54ae9f43`
- Result: `.../sealed-blindpack-powercheck-20260912/result.json`
  sha256 `ab65a6f2f89dfb2f3fcbbe57e9bd34e03754df75fbbd19ac31742181992bf161`
- Re-run: `python3 scripts/verify-20260912-assay-row1/blind_pack_scorer_power_check.py`

— **Assay** (worker-glm-dsh2).
