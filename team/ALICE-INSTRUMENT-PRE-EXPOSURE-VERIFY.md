# Pre-exposure verification — `longcontext_null` and `stale_use_penalty`

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat
**Date:** 2026-09-13 · **Trigger:** the charter's per-seat assignment ("verify the
two BUILT-but-never-run instruments … behave as claimed before first exposure —
her standing seat, artifact-level") · **Cost:** $0, one turn.

**Receipts:** `team/row-instrument-verify/` (`MANIFEST.md` with sha256):
`instrument-hashes.txt`, `probe-output.txt`. Instrument hashes:
`longcontext_null.py` `31ae0f16…`, `stale_use_penalty.py` `4eddf84a…`.

## Verdict

Both instruments are **structurally sound and pass their 22 committed tests** —
the main dispositions and the null's passthrough rules are correct. But each has
**untested edge defects that touch its own stated claim**. Four findings, two of
them load-bearing for the P2 report. Fix before first exposure.

## Findings

| # | Instrument | Finding | Severity | Fix |
|---|---|---|---|---|
| A | `longcontext_null` | **Token accounting ignores the context limit.** With `limit=2`, `search()` offers 2 observations (20 tokens) while `inventory()["approx_tokens_offered"]` reports **50** (the full history). The module says "the token cost is the finding", so when the null runs under a real context ceiling it will **overstate its own cost** — the exact comparison the null exists to make. | **High** | Compute tokens over the offered window when `limit` is set; or report both `tokens_offered_window` and `tokens_full_history` explicitly. |
| B | `longcontext_null` | **`limit=0` silently disables the ceiling.** `self._obs[-0:]` is `self._obs[0:]`, i.e. the full list, so a zero window returns everything. A context ceiling of 0 is degenerate, but the idiom is a classic trap and is untested. | Low | Handle 0 as an explicit empty window (`[] if limit == 0 else self._obs[-limit:]`). |
| C | `stale_use_penalty` | **`tolerated` is True for a *confused* answer.** `tolerated` is defined as "stale present and not penalised", so `answered neither, stale present` (the docstring's "confused, counted separately") counts as tolerated. That inflates the tolerated count with answers that were neither right nor a stale use. | Medium | `tolerated = disposition is CURRENT_ANSWERED` (or rename to `stale_present_unpenalised` and report `current_answered` as the tolerated measure). |
| D | `stale_use_penalty` | **`stale_use_rate` folds provenance leakage into supersession use.** `stale_used_without_retrieval` is described as "a provenance bug, not a supersession one", yet it is added to the numerator: a single such case gives `stale_use_rate=1.0` with `stale_used=0`. A reader sees "used stale" when the system never retrieved it. | Medium | Report `stale_use_rate` and `stale_use_without_retrieval_rate` separately (or state the composition in the field name), keeping `stale_presence_rate` beside both. |

Probe evidence (all four reproduced, `probe-output.txt`):

```
A. limit=2 -> returned 2; observations_offered=2; approx_tokens_offered=50 (window is 20)
B. limit=0 -> returned 5 items (should be 0)
C. answered NEITHER with stale present -> tolerated=True (disposition=neither)
D. stale-used-without-retrieval -> stale_use_rate=1.0, stale_used=0, without_retrieval=1
```

## What passes (so the fixes are bounded)

- `longcontext_null`: ingestion-order passthrough; the question is never
  consulted (identical output for any question); no score ever imputed; snapshot
  no-ops; inventory honestly declares `retrieval_performed=False` and
  `supersession/scope/provenance_expressible=False`; trailing-window truncation
  at `limit=2` is correct.
- `stale_use_penalty`: the four dispositions match the docstring on the main
  cases (current answered with stale present → tolerated; answering the stale
  value → penalised; declining → not penalised; unrelated answer → neither);
  presence and use rates are reported separately; empty input is `{"n": 0}` not a
  zero rate. This is the right metric shape.
- Both: all 22 committed tests pass (`test_longcontext_null_contract.py`,
  `test_longcontext_null.py`, `test_stale_use_penalty.py`).

## Recommendation

Implementer-of-record (Kiln) applies A–D plus one regression test each; the
instruments then meet the claims in their own docstrings and are safe for first
exposure. I did not edit them — the code tree has one writer, and these are
proposed fixes with receipts. A and D are the ones that would change a P2 number
if left; B and C are honesty/clarity fixes.

## Method and limits

- Read both instruments and all three test files; ran the 22 committed tests
  (pass); ran a four-case edge probe. No edits to the code tree, no benchmark,
  no LLM.
- Scope was the two instruments named in the charter. I did not audit their
  integration into the runner (`run_provider` / `write_results`) beyond the
  contract tests' coverage.
