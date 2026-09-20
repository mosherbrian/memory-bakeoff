# KILN-D-8-VERIFY — substantive verification of row D-8

Verifier: kiln-flash, 2026-09-17 13:03 PDT (clock read at write). Author:
corvid-dsh (BACKLOG-NEXT.md, first 10:09, rebuilt ~12:3x); gate author:
plumb-fable (team/D-8-backlog/check.py, written blind from row D-8's text
alone, VERIFIED PASS 12:36 in `team/CORVID-D-8G-VERIFY.md`). I authored
neither artifact; the three-way separation held.

## Declared check and probes

- `python3 /home/bmosher/memory-bake-off/team/D-8-backlog/check.py` — rc 0,
  "clean (10 candidates, each gateable, placed, and ranked without a tie)",
  run from three working directories (team/, /, sandbox HOME) — identical
  verdicts, no cwd or $HOME dependence (the caller-dependence defect class
  flagged elsewhere today does not reproduce here; the gate resolves its
  default against `__file__`).
- `--selftest` — rc 0, 21 fixtures (conforming and closed-sprint-empty
  accepted; prose-only, piped-check, cannot-fail, rank-tie, remeasure-
  without-prior and the rest rejected by exactly their own markers).

## The honest chain, confirmed

The gate's first live verdict (12:19) FAILED the backlog as first written —
`[PROSE-ONLY] no candidate table`, rc 1 — a correct fail of a prose-form
file. The artifact was rebuilt into the 6-column table (change log disclosed
in the file's own §Change log, quoting the rejection); the gate was not
modified to accept it. This is the direction of fit the gate exists to
force: instrument first, artifact second. Verified from the file's change
log and the row cell's own account; the gate bytes carry the pre-rejection
contract (mtime precedes the rebuild).

## Substantive review against the row's four terms

(a) **Goal served** — all ten rows name frozen G-goals and roadmap R-P*
items, or say "advances neither" plainly with the reason (ranks 8, 9, 10).
(b) **Artifact + runnable check** — all ten carry absolute artifact paths
and pipe-free absolute checks (`python3 .../check.py --selftest` ×5,
`test -f` ×5); the gate's PIPED-CHECK/CHECK-NOT-RUNNABLE machinery enforces
exactly the failure mode that silently ungated six live rows today.
(c) **What it stops building** — explicit "Stops ..." clauses in ranks 1-7,
9, 10; rank 8 carries its stop in substance (the Brian-as-only-discovery-
channel bottleneck) phrased as the positive. Minor phrasing observation,
not a gap.
(d) **Prior measurement** — every row cites a concrete prior or states
"none exists" per the standing re-measurement rule. Spot-checked four
against the artifacts themselves: rank 4's "418/450 (92.9%)" in
`team/ASSAY-SECOND-DRIVER-AGENTMEMORY-418.md` ✓; rank 9's "85.2%" in
`team/CACHE-AND-KEEPWARM-20260917.md` ✓; ranks 1-3's arm numbers
(0.600 pi-lcm / 0.500 bm25 / 0.250 claude-mem / 0.200 firehose, bm25 5/5
retrieve and 0/5 abstain) in `team/S6-SELECTIVITY/review.json`, whose
deviation note states rank 3's premise verbatim (bm25 fires on all abstain
cases because the tokenizer keeps function words; no prefilter declared) ✓;
rank 1's `team/S6-ROADMAP/next-experiment.json` exists as proposed-not-built
✓.

Ranking is a strict total order 1-10 with the blocked-on-Brian candidates
(1, 9) ranked by named value per the file's own stated exception. The
twelve sweep sources are named in the file and visibly reflected (EXTERNAL
cards → ranks 5-7, RETRO-4 → rank 10, CACHE-AND-KEEPWARM → rank 9,
S6-ROADMAP/next-experiment → ranks 1-4).

## Verdict

**VERIFIED PASS.** Declared check rc 0 (three cwds) + selftest rc 0;
substance matches the row's four terms with one phrasing observation
(rank 8's "stops" clause); every spot-checked prior citation is real and
accurately transcribed. The one structural fact a file-counting gate would
miss — that the gate's correct FAIL reshaped the artifact rather than the
artifact's reshape loosening the gate — is confirmed by the disclosed
change log and the gate's untouched contract.

---

# 2026-09-19 section — the 14:01:38 sprint-12 restock instance

**VERIFIED PASS, one finding recorded.** Full receipt:
`team/KILN-D-8-VERIFY-20260919.md` (this section is the conductor-route
summary; claimed 14:52, clock read at write).

Ran on the CURRENT bytes (sha `3f5ccff8…614cc3`, pinned twice): declared gate
rc 0 clean from a foreign cwd + `--selftest` rc 0 (21 fixtures); sprint-next
probes with SN_TEAM pinned — ranks [16-20] parsed, lint clean ×5,
already_admitted 16→S12-1 / 17→S12-2 / 18-20→None; census re-run — 1-15 each
cited exactly once (13/14/15 → S11-1/S11-2/S11-3), 18-20 uncited; prune
justified (all three S11 rows done + VERIFIED PASS, receipts on file);
ANSWER.md Q2/Q4/DECISION-READY quotes verified live; Alice Rev-2 unconditional
co-sign confirmed; go-budget present.

**On the cairn route's 10:1x flag — already disposed before filing.** The flag
cites the 13:58:04 draft bytes; corvid's own done-stamp records the self-caught
correction: the first draft's stale "10:1x" clock stamp was replaced with the
verified 13:58/14:01 stamps BEFORE the 14:01:38 filing. Current bytes carry no
"10:1x" anywhere — the only adjacent string is the legitimate 2026-09-17
"~10:09 first written" change-log line. The D-7 extrapolated-stamp class did
NOT land in the filed instance; the self-correction is the extrapolation trap
being caught by the very discipline D-7 exists to enforce.

**The one finding (newer than the route):** BACKLOG-NEXT.md was edited again at
14:44:33 — after the done-stamp — correcting the SWE-chat entry's no-token
claim in place ("CORRECTED AND UNBLOCKED 14:4x") with no change-log entry and
no board note naming the editor. Substance re-measured and TRUE: the token
exists at the real /home/bmosher HOME (this lane seat sees none at its
redirected home — the wrong-HOME trap is real, T-008 pattern); fetch-swe-chat
is RUNNING with Brian's authorization verbatim in its docstring; corpus 5,444/
5,850 transcripts (12 GB) and climbing; disk 105 GB/86% (down ~6 GB — the
download itself). Record-keeping gap only; the ranked table and sprint-12
admissions are consistent. corvid-dsh should fold the change-log line and
claim (or disown) the 14:4x edit in its next wake.

— kiln-flash, 2026-09-19 14:5x PDT (clock read at write in the full receipt)
