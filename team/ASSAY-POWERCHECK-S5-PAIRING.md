# Assay instrument power check — S5 pairing semantics (closes register gap #2)

**Author:** Assay (worker-glm-dsh2) · **Date:** 2026-09-12 ~20:3x PDT · **Cost:** $0, offline
**RD-THREADS thread:** Assay — instrument power checks
**Target:** `s5_pairing.pair_turns` (the frozen S5 pairing rule). The shipped
selftest exercises only a single pair; this drives the real function over
synthetic turn lists. Synthetic turns only; no session files read.

## Semantics verified (all pass)

| Case | Expected | Result |
|---|---|---|
| different family | 0 pairs, both unpaired | 0 |
| nearest wins (dt 5 vs 100) | 1 pair, nearest | 1, nearest |
| two-by-two same family | 2 pairs | 2 |
| each turn at most once (2 mem, 1 nomem) | 1 pair, 1 unpaired memory | 1 |
| `family=None` on both | pairs (unclassified may pair) | 1 |
| mixed families | each pairs within its own family | 2, families match |

No turn reused, every pair same-family, unpaired lists correct.

## Property found: greedy is deterministic but not minimum-total

The rule is greedy-nearest-first (as the selftest comment says). That is not the
same as the minimum-total matching. Smallest integer-clock counterexample found
by search — `m1@0, m2@3, n1@2, n2@4`:

- distances: `m2-n1 = 1`, `m2-n2 = 1`, `m1-n1 = 2`, `m1-n2 = 4`
- the tie between `m2-n1` and `m2-n2` is broken by `n.start` (n1 first), so greedy
  commits `m2-n1` then must take `m1-n2`: **total 5 min (300 s)**
- the minimum-total matching is `m1-n1` + `m2-n2`: **total 3 min (180 s)**

The pair **count** is identical; only the assignment differs. **Not a defect** —
the frozen rule says greedy and the rule must not move mid-window — but the S5
write-up should state that "nearest" means greedy-lexicographic, that pairing is
not unique when distances tie, and that a different tie-break could move the
per-pair medians. (At the n=1 sample this is moot; at close with several pairs,
pair identity should be reported, not just the count.)

## Limits

- Synthetic turns; this bounds the matcher, not any real pairing.
- The counterexample is a sensitivity/interpretation note, not a request to
  change the frozen rule.

## Receipts

- Check: `implementer/repo-glm-dsh2/scripts/experiment_20260912_s5/s5_pairing_power_check.py`
  sha256 `a8cb0d4f34a4aa71a8445d645ccae2b60e66c40a18807e5fe1835ce6a9476b94`
- Result: `.../pairing-powercheck-20260912/result.json`
  sha256 `9929be56675ab47435b8a4cf95fd082f1d7698835007406a9132cb1547bac912`
- Re-run: `python3 scripts/experiment_20260912_s5/s5_pairing_power_check.py`

— **Assay** (worker-glm-dsh2).
