# CORVID-D-6-VERIFY — artifact verification of row D-6

Verifier: corvid-dsh, 2026-09-17 11:10 PDT. Author: kiln-flash (claimed 08:56,
closed 09:02). Artifact: `team/tools/check_external_cards.py`, the repaired
`team/EXTERNAL-CORPORA-RECOMMENDATION.md`, and the suite registration in
`team/tools/check_checker_exit_contracts.py`. Declared check:
`python3 team/tools/check_external_cards.py`. I am the named verifier; kiln
authored.

**Verdict: VERIFIED PASS. The registration claim is true as of kiln's run; two
drift findings from LATER work are recorded as actionable observations, and
one checker run today exits 1 by design — none of it D-6's to fix.**

## What was run

1. **Declared check rc 0** on the live team dir (2 cards:
   EXTERNAL-KNOWLEDGEDRIFT-20260916.md — the row's anointed template — and
   EXTERNAL-CORPORA-RECOMMENDATION.md).
2. **`--self-test` green**: clean card accepted; no-goal / no-trust / neither
   rejected by name; zero-cards dir reads "nothing to check yet", not a
   silent pass.
3. **Adversarial mutant (my construction):** a card with neither mandatory
   section, in a throwaway dir → both `[NO-GOAL-MAPPING]` and
   `[NO-DO-NOT-TRUST]` printed with filenames, `check: 2`, **rc 1**.
   Fail-closed confirmed empirically, not just by source read.
4. **Environment independence:** runs rc 0 from an unrelated cwd (absolute
   default path); zero-cards dir behavior exercised via its positional arg.
5. **The repair is real and disclosed.** CORPORA-RECOMMENDATION carried no
   do-not-trust section; the appended one contains four substantive trust
   boundaries (vendor-only score provenance per CLAIMS-LEDGER; the
   Open-SWE-Traces card-207,489-vs-report-511,668 discrepancy; SWE-chat's
   tier-1 status gated on authenticated `gated: "auto"`; the goal→source
   matrix is judgement, not measurement) and closes with a disclosure footer
   naming row D-6 and "no claim above was changed."
6. **Registration verified in the team/tools suite copy** (mtime 08:48:34,
   inside kiln's window): `check_external_cards` declared at lines
   358/365/423/452, good/bad fixtures wired, 21 names declared covered.

## Observations (drift from LATER work — actionable, not D-6 defects)

- **The suite run today exits 1 — correctly.** At kiln's run time (~09:02)
  the team/tools suite held 21/21 rc 0, matching the done note. At 09:46 —
  after D-6 closed — `check_no_pipes_in_seats.py` landed in team/tools/
  (mtime 09:46:04, D-5-era work), and the suite now reports
  `INCOMPLETE — 1 live guard(s) uncovered` rc 1. That is the meta-checker
  working as designed: the no-pipes guard needs registering in the covered
  set. Filed here so it does not get read as a D-6 failure; it belongs to
  D-5's follow-up.
- **Suite divergence:** the repo-root copy
  (`implementer/repo-glm-dsh3/scripts/check_checker_exit_contracts.py`,
  mtime 2026-09-15, 20 checks, no knowledge of check_external_cards) is a
  stale twin of the live team/tools copy. I ran the stale one first and got
  a clean 20/20 that knew nothing of the new checker — the cross-copy-drift
  class. One of the two should be reconciled or the stale one marked/deleted.
- **Card structure vs the row's four-part order:** KNOWLEDGEDRIFT (the
  template the row itself blesses) orders caveat before what-changes; the
  retrofitted CORPORA recommendation keeps its original 8-section shape with
  the mandatory do-not-trust appended last. The row's declared check —
  goal-mapping + do-not-trust — is what the machine enforces, and both cards
  carry both. The narrative order is prose guidance; noted, not enforced.
- **Stamps:** artifacts 08:47:42–08:48:37, claimed 08:56 (claim trails first
  artifact by ~8 min — within D-7G's 10-minute tolerance), done 09:02. No
  future stamps.
