# CORVID-S6-3-VERIFY — artifact verification of row S6-3

Verifier: corvid-dsh, 2026-09-17 10:49 PDT. Author: kiln-flash (claimed 08:33,
closed 08:47). Artifact: `team/S6-ROADMAP/{map.md,evidence.json,
next-experiment.json,review.json}`. Declared check:
`python3 team/S6-ROADMAP/check.py`. I am the row's named verifier and did not
author the artifact or its gate (gate S6-3G is plumb-fable's, verified
separately in `team/CORVID-S6-3G-VERIFY.md`).

**Verdict: VERIFIED PASS with one named minor defect (correction required from
the author, non-blocking — the structured data in the same artifact is
correct).**

## What was run

- Declared check on the live artifact: rc 0 ("S6-3 gate: clean"). `--selftest`:
  rc 0.
- Independence re-confirmed on the live directory: gate mtime 2026-09-17
  07:39:40 predates every artifact file (earliest evidence.json 08:38:01;
  latest review.json 08:39:07).
- Stamp discipline: claimed 08:33 → artifacts 08:38:01–08:39:07 → closed
  08:47. No stamp precedes its evidence; no future stamps. (Kiln's "S6-2
  closed 08:32 first" cross-reference matches the S6-2G timeline I verified.)

## Independent recomputation (my own code, not the gate's)

1. **Quotes (11/11 verbatim).** All commitment quotes are substrings of
   `implementer/repo/research/PHASE2_ROADMAP.md`. Ten match raw; R-DUR3
   ("we copy this into the repo as research/PHASE2_ROADMAP.md and link it from
   the project") spans the source's own line wrap at its lines 6–7 and matches
   exactly once whitespace-normalized. The gate normalizes whitespace on both
   sides, so its clean pass is correct; my first raw-substring check was the
   stricter of the two and I confirmed the unwrap by hand.
2. **Cited artifacts exist (16/16).** Every `artifact` and Phase-F `evidence`
   path resolves on disk, plus `team/PORTFOLIO-CHARTER-draft.md` and
   `team/SPEC-OUTCOME-PROTOCOL.md`.
3. **Charter reconciliation verified against live records.**
   - All 7 section names/values appear in the charter (whitespace-normalized),
     including the full "**Seat labor:** free flash lanes (Kiln, Verity,
     Stratum) as today; dsh lanes..." line.
   - "2026-09-15 furlough roster" is real: `team/BOARD.md:846` (GML 2026-09-15
     ~19:0x PDT, FURLOUGH ROSTER, Brian verdict) and the charter's own header
     note ("fleet was furloughed to three seats on 2026-09-15"). The QUEUE
     roster header is dated 09-16 but the furlough event is 09-15 — the
     artifact cites the event, correctly.
   - "Brian's 2026-09-16 decision 2" is verbatim:
     `team/QUEUE.md` §BRIAN'S DECISIONS, 2026-09-16 evening, item **2. AFTER
     2026-09-20, THE FLEET FITS INSIDE THE OPENCODE GO PLAN BUDGET** —
     including "budget per row, not turns in flight."
   - "QUEUE self-organization rule (2026-09-12)": `team/QUEUE.md:13`
     (SELF-ORGANIZATION (Brian, 2026-09-12)), GiLMore named there exactly as
     the supersession claim says.
   - Verity-blind → S3-4: `team/KILN-S3-4-VERIFY.md` documents the disclosed-
     rater seating and `CORVID-BLIND-QUORUM-REGISTER.md` exists.
   - Live-as-written: Budget envelope (≤$5 appears throughout the charter);
     "G0 approved 2026-09-12" is supported by the charter's own Patch 2
     ("post-G0 pre-P2", dated 2026-09-12); Shared harness spec and Phase gates
     sections exist as named.
4. **Phase F matrix matches the measured record.**
   - adopt: claude-mem "cannot abstain" — recomputed 0/5 abstain-empty, mean
     0.250, i.e. firehose-level; agentmemory 92.9% (418/450) false-supersession
     is the protected finding, present in both R-PA support documents.
   - compose: the complementarity claim reproduces exactly from
     `team/S6-SELECTIVITY/results.jsonl` + `manifest.json`: pi-lcm mean 0.600
     with **5/5 abstain-empty** (perfect abstention) but only 1/5 exact on
     retrieve cases; bm25 mean 0.500 with **5/5 exact-helpful on retrieve**
     but 0/5 abstention; claude-mem 0.250, never abstains (coverage). The
     arms are complementary, not ranked — the artifact's reading is the data's
     reading, and matches my independent S6-2 verification.
   - build: gated behind a compose attempt, with the transcript-miner and S3-6
     probe cited as buildable pieces (both files exist).
   - ONE deciding uncertainty, one sentence, naming the unmeasured property
     that flips compose↔build (state layer holding abstention with
     false-supersession far below 92.9%).
5. **next-experiment.json.** `status: proposed-not-built` (and no results
   field); baseline = the charter's Patch 3 locked baselines — verified:
   Patch 3 (2026-09-12, POST-G0 BRIAN DIRECTIVE) "BASELINES LOCKED. Two
   explicit arms join the long-context null... pi-lcm"; M1/M2/M3 usages match
   `team/SPEC-OUTCOME-PROTOCOL.md` §M1 (time-to-complete, tokenUsage),
   §M2 (errors committed), §M3 (redundant re-discovery); the stopping rule is
   pre-declared (n=8 matched pairs, early-stop on 3 consecutive regressions,
   cannot-distinguish reported as the completed result). The cited arm means
   "0.600 / 0.500 / 0.250" reproduce to the third decimal.
6. **Two absences kept distinct.** R-PF not-evidenced-here (no decision record
   anywhere; matrix is its first population) vs R-PG never-done (no prototype
   build exists; held under the roadmap's own ban). Both carry
   `artifact: null` and separate next_decisions.

## DEFECT (minor, named)

`map.md`, charter item 1: "**ten of the eleven named seats are parked**". The
charter's Per-seat assignment map names exactly 11 seats (Kiln, Verity,
Aletheia/Alice, Assay, Corvid, Ledger, Cairn, fsync, Stratum, worker-codex,
GiLMore). Three are live in the current arrangement (kiln-flash, cairn-pi,
corvid-dsh), so **eight** are parked — and `evidence.json`'s own
`superseded_by` lists exactly those eight. The structured data is right;
map.md's count clause is an arithmetic slip. It changes no classification and
breaches no row distinction (the row asks WHICH sections are superseded and by
WHAT — both correct), so the verdict stands, but the author must append a
disclosed correction line to map.md quoting the error — no silent rewrite
(D-7 rule).

## Limits

- I verified the artifact against the sources it cites; I did not re-adjudicate
  whether the roadmap's commitments are the RIGHT commitments.
- The Phase F matrix is a first population from existing evidence; its
  compose-lean is an assessment I confirmed is CONSISTENT with the cited
  measurements, not a prediction I validated.
- The one defect above is open until kiln's correction line lands.
