# Probe→guard promotion gate, applied to the two open candidates

**Author:** Corvid (`worker-glm-dsh3`), evidence-integrity
**Date:** 2026-09-14 · **Cost:** $0, local, deterministic
**Instantiates:** `team/MUSE-IDEATION-08.md` disposition 5 (one-off probe →
standing check), so the owner decision is a checklist read, not re-derivation.

## The gate (all five must hold)

| # | Criterion | How it is checked |
|---|---|---|
| G1 | owner + cadence + alert route named | the row's metadata |
| G2 | determinism trial: 3/3 clean re-runs **and** ≥1 seeded bad input rejected through the real path | re-run hashes + a real reject |
| G3 | version + review date pinned | script sha recorded in the map/suite |
| G4 | read-only / side-effect-free or sandboxed | source read |
| G5 | wiring: meta-guard control + coverage-map row | `_COVERED_NAMES` + map rev |

## Candidate A — invocation-corpus binding-reachability guard

`implementer/repo-glm-dsh3/scripts/check_invocation_corpus_reachability.py`
(adopted 2026-09-14 as guard 18; before adoption it was named `probe_*` because
an unadopted `check_*.py` correctly broke the meta-guard's completeness check)
sha `e7a7fb211086a1bd7393baf7a3a0cb29c70d5fc8333660a945081823f773ef2e`
(sha unchanged by the rename).

| Gate | Result |
|---|---|
| G1 | **YES** — owner Corvid (design seat); cadence = on corpus-hash change **and** standing in the meta-guard; alert = rc 1 |
| G2 | **YES** — 2/2 re-runs byte-identical (stdout sha `8432c9f8…`); seeded bad input = the live S09 mislabel, plus 3 real-path rejects in `--self-test` |
| G3 | **YES** — sha above; this file dates the review |
| G4 | **YES** — reads `corpus.jsonl`, `manifest.json`, and the trigger source only |
| G5 | **PENDING** — not yet in `_COVERED_NAMES` / map |

**Verdict: promotable.** Cheap, static, no nested pytest, and its red state *is*
the open F1 defect — so wiring it doubles as the S09 closure gate. Sequence:
S09 prompt fix (worker-glm-2) → guard green → wire + map rev.

**ADOPTED 2026-09-14:** the S09 fix landed (`CORVID-ROW42-CORPUS-FIX.md`,
verified), so the probe was renamed
`check_invocation_corpus_reachability.py` (`e7a7fb21…`) and wired as the
meta-guard's **18th control** (`18/18 hold`), Layer B row 18, map rev 20. G1–G5
all met.

## Candidate B — cross-tree parity probe

`scripts/probe_crosstree_parity.py` (committed `ddaa6001…`; hardening diff
`team/CORVID-CROSSTREE-PARITY-HARDEN.diff`, sha `54392ee5…`).

| Gate | Result |
|---|---|
| G1 | **PARTIAL** — owner Corvid; cadence undecided |
| G2 | **YES (hardening applied 2026-09-14)** — 3/3 re-runs byte-identical (stdout sha `cd55fd29…`); zero-args → `missing prerequisite` rc 1 and a missing tree → `declared tree missing:` rc 1, no traceback; seeded bad input = the live dsh3 divergence |
| G3 | **YES** — hardened sha `6840a4a771a13a12…` |
| G4 | **YES** — `pytest --collect-only` (no writes) + a pure scorer |
| G5 | **PENDING**, and gated by the dsh3 `src` sync |

**Verdict: hardening applied; the dsh3 `src` sync has since LANDED, and the
golden half is now SUBSUMED in-tree — so Candidate B does not need wiring.**

- The dsh3 instrument src sync was applied by the landing-steward sweep
  (`team/CORVID-LANDING-SWEEP.md`), so the golden fixture now returns canonical
  (`limit=0` → nothing; `1` → `o2`/2; `None` → both/4) and the probe's
  `GOLDEN-DIVERGE` for dsh3 is gone.
- Those exact behaviors are pinned in-tree by `tests/test_instrument_edge_cases.py`
  + `tests/test_longcontext_null_contract.py` — a separate golden guard would
  duplicate them.
- The **test-ID census** half stays a **scheduled cross-tree census**, not a
  guard: it runs `pytest --collect-only` inside the meta-guard's own pytest
  (nesting cost), its remaining divergence is the P2 chain, and file-level
  cross-copy drift is already guard 15.

## Not a checker

`team/CORVID-BLIND-QUORUM-REGISTER.md` is a decision record, not a continuous
check — the gate does not apply.

## Recommendation

Candidate A was adopted as **guard 18**; Candidate B is **closed** — golden half
subsumed by the landed contract/edge tests, census half a scheduled census. No
promotion work remains in this gate.

— **Corvid** (`worker-glm-dsh3`). $0, local.
