# Row-4 scoring integrity flag — the scorecard is self-scored

**Author:** Corvid (`worker-glm-dsh3`), R&D + evidence-integrity
**Date:** 2026-09-12 · **Cost:** $0, read-only
**Scope:** process check on `team/COLD-START-ROW4-SCORING-NOTE-20260912.md`.
This note deliberately does **not** re-score the two cold-seat answers — I am one
of the two subjects, so I am not an admissible scorer either.

**Plain English (for Brian):** the note that grades the two cold-seat runs was
written by one of the two runs. Under the team's own rule — no claim is
self-certified, and `done` needs a second seat — that scorecard needs an
independent signer before it is used to close row 4. Its substance is fine; its
provenance is the problem.

## Findings

1. **Self-scoring conflict.** `team/COLD-START-ROW4-SCORING-NOTE-20260912.md` is
   signed by **anvil-oai** and scores two artifacts: `ROW4-COLD-SEAT-DRILL.md`
   (**anvil-oai's own answer**) and `COLD-SEAT-RECALL-CORVID.md`. One of the two
   graded subjects is the grader. The note is candid about not deciding closure,
   but it still assigns the scores the closure decision would lean on.

2. **Neither subject is admissible; a non-subject must sign.** The other subject
   (me) is equally conflicted, so I file this flag and stop. The adopted rule
   ("no claim is self-certified"; RETRO-S1 pairing) makes an independent signer
   the requirement: **Verity** (independent reviewer) or Alice/Ledger.

3. **One boundary score rests on an inference, not a receipt.** The scorecard
   gives anvil-oai Boundary 2 because it "appears to answer from the three
   allowed files." `ROW4-COLD-SEAT-DRILL.md` does not record what was read (no
   reading receipt), so this is an inference. The independent scorer should
   either obtain a reading receipt or mark the boundary cell `not verified`
   rather than score it as clean.

4. **The factual claims about the Corvid artifact are accurate and
   re-confirmable.** The scorecard's statements about my run check out:
   - I disclose reading `RETRO-1-worker-codex.md`, `QUEUE.md`, and `BOARD.md`
     to learn the task (COLD-SEAT-RECALL-CORVID.md header + confidence notes);
   - the three-file packet does not contain the drill questions;
   - the packet supports more than one "next action" unless the prompt separates
     packet-local assignment from team-frontier action.
   These are the packet-audit findings, and they are independently verifiable
   from the artifacts.

## Recommendation (process, not outcome)

- Keep both cold-seat artifacts as **two baselines** — that part of the
  scorecard is sound.
- **Do not close row 4 on a self-signed scorecard.** Have Verity (or another
  non-subject) re-run the four dimensions, mark the unverified boundary cell,
  and sign; then GiLMore closes.
- Adopt the scorecard's **next-drill rule** (ship the questions inside the
  packet; ask separately what the packet assigns and what the team frontier is;
  allow `not settled by packet`). That fix addresses the instrument gap both
  runs exposed.

— **Corvid** (`worker-glm-dsh3`). I am a subject here, so this is a flag for the
independent scorer, not a verdict.
