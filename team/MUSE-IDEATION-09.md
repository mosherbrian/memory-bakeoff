# Muse ideation batch 9 — patch handoff, apply-verification, registry sync, canonical-only declarations

**Tag:** `batch9` · **Prompt sha256:** `665770802ca598026e774131a84b2dce1e6b756bef57f3c10bc5698756ddd457` (`PROMPT9.txt`, recorded before send) · **Date:** 2026-09-14
**Authorization:** standing Muse cadence (Corvid thread, `RD-THREADS.md`; original
Brian/GiLMore approval 2026-09-12, `scripts/experiment_20260912_muse_ideation/PROTOCOL.md`).
**Fitted cause:** today produced several validated diffs awaiting an owner whose
tree keeps moving (`CORVID-PENDING-DIFF-APPLICABILITY.md`), and two guards adopted
by hand-editing the meta-guard registry + coverage map (guards 18/19). Both are
live instances of the general problems below.
**Content policy:** public methodology only; no project detail, paths, results, or
strategy.

## Prompt (verbatim, preregistered)

See `PROMPT9.txt`: four public questions — (1) handoff-drift failure modes when a
validated patch meets a moving target; (2) verifying a handed-off patch was
applied exactly as reviewed; (3) keeping a check-suite registry/manifest in sync
when each new check needs hand-edited metadata; (4) declaring a file
canonical-only so expected absence is not repeatedly reported as drift.

## Receipt

One tagged call, `ready=true`, `end_seen=true`, latency 25.68 s, 5,646 assistant
chars, no block signals. Meter `spent $0.0261` before and after; `openrouter
$0.00 today` — cost ≈ $0.00. Receipts:
`scripts/experiment_20260912_muse_ideation/receipts/batch9-*`.

## Dispositions (Muse proposes, Corvid disposes)

1. **Handoff triple `base_commit + patch_sha256 + validation_log`, no-fuzz
   apply, re-validate on the landed result** — **ACCEPT** `[I]`. Today's pending
   diffs are exactly this problem (`CORVID-PENDING-DIFF-APPLICABILITY.md`).
   Bounded probe: a handoff-receipt format pinning the base commit + patch sha +
   validation command, plus a rule that validation is re-run **after** landing
   (not reused from the base). Our diffs already carry a sha; the missing piece
   is the base-commit pin and the post-apply re-run.
2. **`git patch-id` (normalized-diff identity) at review vs after landing** —
   **ACCEPT** `[I]`, new and cheap. Compares the *artifact*, not the commit
   message: record `git diff base..landed | git patch-id` after apply and require
   it to equal the authored patch's id. Catches re-typing, bundling, and silent
   edits. Bounded probe: add the patch-id to each handoff receipt.
3. **Auto-discovered checks with a generated registry; CI asserts
   `discovered == registered`** — **DUPLICATE**. The meta-guard's `_COVERED_NAMES`
   completeness check (`check_checker_exit_contracts.py`, rev 10) already asserts
   both directions (`NO CONTROL` / `CONTROL WITHOUT A LIVE GUARD`) — which is why
   an unadopted `check_*.py` correctly broke it today. Residual noted, not
   re-proposed: full generation is limited because each control needs its own
   fixture builders; the promotion-gate checklist already covers the "add a
   guard" path.
4. **Per-copy presence manifest (`expected_in_A/B`, reason, expiry) consumed by
   the drift checker, with a two-assertion power check** — **ACCEPT** `[I]`.
   This is the concrete form of the declaration dry-run recommendation
   (`CORVID-CROSSTREE-DECLARATION-DRYRUN.md`): a `canonical-only:`/absent-by-design
   category so the P2 chain's expected absence is not permanent `missing in a
   tree:` noise. Bounded probe: (a) exempt-absent file → **0** findings;
   (b) remove one non-exempt file → **exactly 1** finding; plus an expiry lint.

**Net:** 3 ACCEPT / 1 DUPLICATE. No ACCEPT is a finding until its probe runs.
Second seat open (Alice/Assay).

**Probe status (2026-09-14, Corvid):** ACCEPT 1+2 are built as
`team/CORVID-PATCH-HANDOFF-RECEIPTS.md` (base + patch sha + expected post-apply
hashes + reverse-check); ACCEPT 4 is **built into guard 15** —
`check_cross_copy_drift.py` now supports the `canonical-only:` category with the
two-assertion power check (map rev 22). ACCEPT 3 was a DUPLICATE.
