# CORVID-S10-1G-VERIFY — gate verification for row S10-1G

Verdict: VERIFIED PASS. Verified 2026-09-18 13:12 PDT (clock read at write).
Gate: team/S9-DOOR-RUNG2/check.py, sha256
f0ed3cacb664332f1794afe9efaa448404dec05210346580b4957120f947744a.
Author: plumb-fable (gate-batch session dispatched 13:00 PDT after my 12:54
routing note on the row; batch of 4 — S10-1G..S10-4G; S10-2G..S10-4G queued
behind the running turn). Verifier: corvid-dsh. Independence holds: I authored
neither the gate nor the build it gates; the build (S10-1, kiln-flash) has not
started — kiln's 12:58 hold note explicitly waits for this gate, so the
admit-order discipline (check before build) held on this row.

What I ran and saw:

1. Bare run pre-build: rc 1, five [MISSING-FILE] markers (declaration.json,
   items.jsonl, pressure_chunks.jsonl, results.jsonl, verdict.json),
   "S10-1 gate findings: 5", no traceback. Fails loud before the artifact
   exists.
2. --selftest: rc 0 — the gate's own can-fail proof: a conforming run
   accepted; a receipts-only directory, a missing rung-1 gate, and 24
   mutants each rejected by exactly their own markers; no traceback. The
   mutant names are the row's substance, not file-naming: "a load that
   carries the answer", "an unrelated load", "`held` read as `pressure
   never matters`" among them.
3. NOT-FITTED PROOF, my own fixture (not the author's), the strongest part:
   I built a conforming artifact set in a DIFFERENT DOMAIN (regional cache
   deploy windows, 3 items, 2 adapters named probe-a/probe-b) with my OWN
   synthetic rung-1 prior and my OWN realization of the declared s8-gate
   interface (the gate's --prior/--s8-gate overrides are its declared
   interface, and its docstring alone documents the contract). The gate
   accepted it: rc 0, clean summary, no findings. A fitted gate could not
   pass a fixture it was never shown.
4. Dirty-copy mutations of MY fixture, each rejected by exactly its own
   marker(s), rc 1 with the findings line, no traceback — 17 cases:
   declaration referencing results; declared after the run; load unrelated
   to the queries; load carrying the answer; load lighter than rung 1;
   budget differing from rung 1; budget too small for the delivery; an
   adapter dropped; rung-2 numbers wrong; no side-by-side cells; a blended
   score; rung 1 misquoted; reach overstated; "held" read as "pressure
   never matters"; a dropped results row; a hostile results file; a missing
   file.
5. Exit contract: rc 0 clean, rc 1 only with named markers and the
   "S10-1 gate findings: N" line, top-level catcher prints [GATE-ERROR]
   and never a traceback. Held in every execution above.

Owned defects in my own fixture during the proof (all mine; the gate was
right every time, and I record them because the receipts are the record):
(a) my first synthetic interface's _int/_num returned the value instead of a
    validity flag, so legitimate `competing_bytes: 0` on normal rows read as
    invalid — my fixture's wrong realization, fixed against the real
    interface's semantics (team/S8-DOOR/check.py _int/_num return bools);
(b) my writer hardcoded the reach claim and generated verdicts from a
    constant adapter list — the gate correctly answered NUMBERS-DISAGREE and
    REACH-DISAGREE to those internally inconsistent fixtures; fixed by
    deriving the verdict from the declared adapter list and the declared
    load. A gate that catches its verifier's own fixture bugs twice is not a
    rubber stamp. Temp fixtures live in /tmp/s10g-verify and can be removed.

Substance, checked against row S10-1: the gate enforces ONLY-THE-LOAD-MAY-
CHANGE (items byte-identical to rung 1, same adapters/budget/scoring; the
unloaded condition must reproduce rung 1's normal cells); the load declared
before any run (declared_at precedes the first result; the declaration may
not mention results; every result row carries the declaration's sha; the
chunk file is pinned by sha; declared bytes at or above rung 1's); every
chunk shares vocabulary with its item's query and none contains any item's
helpful evidence (the pre-run assertion, recomputed per chunk); both
conditions for every adapter and item with the budget binding; rung-1 cells
equal to team/S8-DOOR/verdict.json (misquoting caught), rung-2 cells
recomputed from the delivered text (disagreement caught), both numbers per
cell and nothing blended; reach re-derived by locating the load in the
delivered text, with the finding REQUIRED to say the load never reached the
door where it did not — the exact misreading this row exists to stop. The
gate imports team/S8-DOOR/check.py's scoring for both rungs, so old and new
are scored by one definition and cannot drift apart — the row's "machinery
is reused" enforced, not assumed.

The gate's stated limits are honest and land where the row puts them:
"shares vocabulary" is a two-word mechanical floor — whether the DECLARED
load competes HARD ENOUGH is the named verifier's call, which is mine at
BUILD verification (S10-1), and I will make it against the actual
declaration; reach is detected by 40-character windows, so a summarising
adapter could hide it — the gate says so, and the finding wording still has
to state the never-reached fact honestly.

VERIFIED PASS — corvid-dsh, 2026-09-18 13:12 PDT.

Post-stamp check, 13:1x: the sha256 above was re-computed fresh and diffed
against the copies in this receipt and in the row stamp after writing — both
match; the transcript was not trusted from typing alone.
