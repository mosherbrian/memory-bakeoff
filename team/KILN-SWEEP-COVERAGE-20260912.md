# Kiln R&D pulse — sweep coverage map (2026-09-12)

Thread: "build hardening / flaky-adapter sweep" — closes the "out of scope"
caveat in `team/KILN-FLAKE-SWEEP-20260912.md` with an explicit inventory.
One turn, $0, read-only (collection only; nothing executed beyond imports).

## Finding 1: the suite is collection-healthy end to end

**122/122 test files collect cleanly in this lane** (fresh pytest process
each, 15 s timeout cap, zero failures, zero hangs): no import rot, no
missing-dependency collection errors anywhere in the historical suite.
Total: **1,625 tests** collected in 0.87 s at HEAD `78cdd2d`.

## Finding 2: collection ≠ sweepable — runtime classes are the real gate

The flake sweep's 9-suite / 82-test subset was selected on RUNTIME safety
(no network, no metered lanes, no live experiment state), and that remains
the sweep's honest boundary. Collection health says nothing about whether a
suite's runtime needs a service, a metered lane, a materialized external
dataset, or a live store — per-suite runtime classes live in historical
knowledge (dispatch docs, receipts, KNOWN_FAILURES.json), not in the tree.

Carried, not self-adopted: label each suite's runtime class (in-lane /
service-gated / metered / live-state) when that suite is next touched for
any reason — incremental, no bulk labeling programme (reset-plan §7
discipline: no new reporting infrastructure). Until then, the sweep stays
at its proven 9-suite boundary.

## Explicit non-goals

- **No full-suite run was performed** — deliberately. The reset's scoped
  verification policy replaced whole-suite reruns, some suites carry
  known-failure baselines (`known_failures_baseline`,
  `retracted_claims_stay_retracted`), and runtime gates are unlabeled.
  This map is a health inventory, not a mandate to execute 1,625 tests.
- Collection receipts are re-derivable in ~35 s (the whole inventory above
  is one loop of `pytest --collect-only -q` per file).

— Kiln, R&D pulse 2026-09-12, ~15 min, $0.
