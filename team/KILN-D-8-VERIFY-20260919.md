# KILN-D-8-VERIFY-20260919 — substantive verification of the 14:01:38 restock instance

**Verdict: VERIFIED PASS, with one finding recorded (post-stamp artifact drift,
disclosed inline, substantively TRUE; record-keeping gap, dispositions
unaffected).**

Verifier: kiln-flash (named content verifier for D-8; corvid-dsh authored the
instance — no self-review). Claimed 14:52 PDT, clock read at write. Every check
below ran against the CURRENT bytes after the drift was found and pinned.

## Bytes under verification, and the drift

- Done-stamped instance: corvid-dsh 2026-09-19 14:01:38 PDT (sprint-12
  restock: pruned 13/14/15, re-checked blockers, added ranks 16-17,
  renumbered old 16/17/18 → 18/19/20).
- **Drift:** current `BACKLOG-NEXT.md` mtime **14:44:33**, sha
  `3f5ccff8270da8c88a367f127d432e1ede31954d9cd752c2263695e0e0614cc3` (pinned
  twice, 14:47 and 14:53 — stable through this verification). That is 43 min
  after the done-stamp, editing the SWE-chat blocked entry in place
  ("CORRECTED AND UNBLOCKED 2026-09-19 14:4x"). At verify time there is
  **no change-log entry** (log ends at "13:5x — THIS REVISION") and **no
  board note** naming the editor. Author unconfirmed.
- What moved: the SWE-chat paragraph only (blocked section, not the ranked
  table). Corroboration that the ranked table's substance is the restock's:
  the declared gate and the sprint-next probes (below) re-run clean on the
  current bytes, and ranks 16/17 match the admitted S12-1/S12-2 rows
  verbatim in their load-bearing text.

## The finding's substance is TRUE — re-measured

The 14:4x correction says the restock's "no HF token on this machine" claim
was a wrong-HOME read. Confirmed from this seat:

- `/home/bmosher/.cache/huggingface/token` EXISTS (38 bytes, Sep 11). This
  seat runs in a redirected lane home and sees no token at its own
  `~/.cache` — the trap mechanism the correction describes is real: a lane
  seat's honest reading of the WRONG home, reported as a fact about the
  machine (the correction names the T-008 pattern).
- The fetch is REAL and in flight: `python3 fetch-swe-chat.py` PID 3410404,
  launched with Brian's authorization quoted verbatim in its docstring
  ("Of course I authorize it, how else would it get done?", 2026-09-19).
  Corpus at verify time: **5,444 of 5,850 transcripts, 12 GB on disk**
  (was 615 files / 3.3 GB at the 14:4x correction) — the loop's log shows
  live progress with 429 rate-limit backoff working.
- Disk re-measured: 105 GB free at 86% (backlog said 111 GB at 85% at
  13:5x). The ~6 GB move is the download itself consuming disk — the 111 GB
  figure was honest at read time; trend recorded here.

## Declared check and probes (all re-run by me on current bytes)

| probe | result |
|---|---|
| `python3 team/D-8-backlog/check.py` from a foreign cwd (/tmp) | rc 0 — "D-8 gate: clean (5 candidates, each gateable, placed, and ranked without a tie)" — matches the done-stamp verbatim |
| same, `--selftest` | rc 0 — 21 fixtures, prose-only/piped/every mutant rejected by own marker |
| `candidates()` with `SN_TEAM` pinned | ranks parsed: **[16, 17, 18, 19, 20]** |
| `already_admitted()` | 16 → S12-1, 17 → S12-2 (the post-restock admissions, detected by artifact path — the detector working as repaired), 18/19/20 → None |
| `lint()` | clean on all five |
| rank-citation census (my own grep, all 20 numbers) | 1-15 each cited exactly once (13→S11-1, 14→S11-2, 15→S11-3); 18/19/20 uncited; 16/17 cited by the S12 admissions |

## Substance spot-checks

- **Prune justification:** S11-1 and S11-2 VERIFIED PASS 17:59 2026-09-18
  (receipts `team/CORVID-S11-1-VERIFY.md`, `team/CORVID-S11-2-VERIFY.md`);
  S11-3 VERIFIED PASS 09:15 today (`team/CORVID-S11-3-VERIFY.md`, 36/36
  checks incl. the 46-trial replay). Ranks 13/14/15 were done-and-verified
  work and belong in the burned set.
- **ANSWER.md quotes:** Q4 next step ("Compare native pi-lcm and the
  existing layer on the unchanged broader histories, with protection and
  missed-update limits registered first"), Q2 next step ("Test a different
  relevance rule, reporting rejection and retrieval loss separately on
  declaration and held-out cases"), and the DECISION-READY reopen line all
  verified live in ANSWER.md's current bytes. Nuance recorded: ANSWER.md's
  header now stamps 14:05 (the planner's update folding sprint-12
  materials); corvid's reading window was 13:4x-13:5x — the load-bearing
  lines are unchanged between versions, verified against current bytes.
  The cell's "'13:44' stamp is HONEST" claim refers to the planner's
  original post-sprint-11 version; consistent with this sequence.
- **Alice Rev-2:** `EXTERNAL-CORPORA-RECOMMENDATION.md` line 134: "Rev 2
  (2026-09-13) — Alice's A1–A4 folded; co-sign **unconditional**" — the
  "A1-A3 discharged" claim stands.
- **go-budget:** exists at the real HOME (`/home/bmosher/.config/agent-deck/
  go-budget`, 70 KB, Sep 18 22:39) — caveat-recorded and unversioned as the
  backlog says.
- **Q5 not-added:** supported by S11-2's verified finding — Abstention 0/40
  on all five engines, no admitted implementation exposes a decline path.

## Disposition

- The 14:01:38 restock's claims are true in substance; the ranked list it
  shipped is intact and load-bearing (sprint 12 opened from it).
- The one defect is **record-keeping**: an in-file correction landed after
  the done-stamp with the substance right but without a change-log entry or
  board note naming the editor. corvid-dsh (the row's author seat) should
  fold the change-log line and claim the 14:4x edit on the board — or
  disown it — in its next wake. Nothing measured here blocks that; the
  ranked table, the probes, and the admissions are all consistent.
- Row D-8's standing instance remains open as a standing row (tomorrow's
  feed / next commission), per the row's own convention.

— kiln-flash, 2026-09-19 14:57 PDT (clock read at write)
