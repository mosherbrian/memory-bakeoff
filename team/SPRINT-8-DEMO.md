# Sprint-8 demo — the door: what the model was actually HANDED

Sprint goal (QUEUE.md): *establish whether composed retrieval and a thin state
layer improve memory behavior, check performance on independent frozen worlds,
and resolve the bounded design and operations follow-ups.*

**Honest opening — this sprint opened with a defect.** Its first four items
(S8-1..S8-4) were re-admissions of work Sprint 7 had already finished and
independently verified that same day: the backlog's file paths had gone stale
when the sprint number moved, so the new rows pointed at Sprint 7's finished
artifacts. They were closed on the evidence as written, with **no re-run**
(the re-measurement rule: no expected difference), and Sprint 7's verified
results stand. So the goal's first two clauses — composed retrieval, the thin
state layer, the independent frozen worlds — were answered in Sprint 7, and
this sprint's real content is the goal's third clause (the bounded design and
operations follow-ups) plus one new measurement you admitted mid-sprint: the
**door metric** (S8-7).

Three pieces of real work, each with its own check written by a separate seat
**before** the work existed, so a check cannot be fitted to a finished result,
and each carrying an independent **VERIFIED PASS** from the reviewer seat
(08:10, 08:34, 09:26 PDT) who authored none of it. What is asked of you is at
the end. Finalized 2026-09-18 ~09:35 PDT.

## What changed for you

1. **A new number for the adopt decision: the model was handed 1 of 5.** The
   door metric measures the exact text each memory system delivers into the
   model's prompt, at a declared 600-character budget, scored as two separate
   numbers — was the helpful evidence present, and how many irrelevant bytes
   came with it. pi-lcm tool-level — the option on the table for adoption —
   retrieved the right records (Sprint 6/7: 0.600) but delivered helpful
   evidence in only **1 of 5** cases; on the other 4 it delivered empty text.
   The retrieval score was hiding a delivery gap. bm25 delivered 5/5 with zero
   irrelevant bytes; claude-mem delivered 5/5 with ~126 bytes of irrelevant
   text alongside.
2. **Pressure changed nothing at this load.** The declared expectation that
   competing tool output would crowd the evidence out did not materialize:
   nothing was ever cut, so the door held at this load. The harsher
   query-adjacent load is a declared next rung, not a hidden retry.
3. **The restart question is answered, with a control.** Who restarts the
   fleet's driver: the journal records **no person or program** — that is the
   measurement — and ~230 of the 246 starts on the day in question were one
   crash loop retrying an unparseable script, not restarts by anyone. A
   control was added so the next restart *is* attributed, and the syntax check
   that had hidden the loop is fixed.
4. **The stale-path probe design got its missing input.** The HANDBOOK paper's
   body was read (not just its abstract): the rubric schema and two
   deterministically-graded failure classes are now extracted into the probe
   design as a design input. No run is admitted by this.

## Results — each with its number, its check, its artifact

**S8-7 — the door metric (verdict: the delivery gap is real).** Declared
before any run: 600-char budget, the five retrieve cases of the Sprint-6
frozen corpus (their helpful sets were already adjudicated, so this row did
not improvise them), normal vs competing tool-output pressure, the two numbers
kept separate. No prior measurement of delivered-text presence or irrelevant
bytes exists in this project — stated, not implied. At the declared door:
**bm25 presence 1.00 → 1.00, irrelevant bytes 0 → 0; pi-lcm tool-level
presence 0.20 → 0.20, bytes 0 → 0; claude-mem presence 1.00 → 1.00, bytes
126 → 115.** Two interpretive limits, stated by the verifier: (a) pi-lcm's
0.0 bytes is degenerate — it delivered *empty* text on 4/5 (a retrieval
abstention matching its verified Sprint-6 profile), so presence is the number
that catches it; (b) the budget never bound (nothing was cut), so this is the
door at *this* load. Check S8-7G (plumb-fable, landed 17:30 the prior evening,
directory empty at authoring) clean rc 0; it asserts the declaration precedes
the results and the two numbers stay separate. Artifact `team/S8-DOOR/`.
Verified: `team/CORVID-S8-7-VERIFY.md` (PASS, 09:26).

**S8-6 — restart-actor attribution (verdict: unattributed is the measurement;
control added).** The two restarts the retro had recorded are 2026-09-16, not
09-17. `journalctl --user _COMM=systemctl` returns zero lines for that day, so
systemd records no D-Bus peer — the actor is unattributed, and that is the
finding, not a gap. 246 starts that day; ~230 are one crash loop
(09:46:29–10:06:34, `Restart=always` on an unparseable script). Control added:
`~/.config/agent-deck/poller-restart-attribute` as an `ExecStartPre`, proven
live naming the restarting process; plus `ExecStartPre=/bin/bash -n` and the
start-limit settings moved where systemd actually reads them. Done outside the
sprint at your call (the driving session is a party to the finding, so the
verdict is not its own). Check S8-6G (plumb-fable, pre-artifact) re-looks-up
every quoted journal line, so it cannot be fitted to the answer. Artifact
`team/S8-OPS-DEBT.md`. Verified: `team/CORVID-S8-6-VERIFY.md` (PASS, 08:34).

**S8-5 — HANDBOOK body pass (verdict: design input landed).** Read the arXiv
v3 body + probed the Apache-2.0 repo read-only ($0, no run). Extracted the
rubric schema (each task ships `tests/rubrics.json`; the shared runner is
`sop_verifier.py`) and the two failure classes the card named, into the
stale-path probe design it feeds. 22 body citations, schema table 4 rows.
Check S8-5G (plumb-fable, pre-artifact) clean rc 0 (2 class blocks, 22
citations). Artifact `team/S8-HANDBOOK-PASS.md`. Verified:
`team/CORVID-S8-5-VERIFY.md` (PASS, 08:10).

**S8-1..S8-4 + their checks (S8-1G..S8-4G) — closed as duplicates, no re-run.**
Verbatim re-admissions of S7-1..S7-4 (done + VERIFIED PASS 2026-09-17) carrying
Sprint 7's stale artifact/check paths. Closed on the evidence as written per
the conductor's admission-defect ruling; the re-measurement rule bars the
re-run (no expected difference), and Sprint 7's verification stands. The
admission defect itself (backlog paths go stale when the sprint number moves;
admission must re-derive paths and exclude consumed ranks) is the standing
lesson, recorded on the board.

## What this means for the decision

The adopt decision (the roadmap's Decision Gate F, option A) now has its
missing number. Sprint 7 measured that compose and build are dead, leaving
adopt-or-defer on pi-lcm tool-level as-is — but the adoption case rested on a
retrieval score (0.600). The door metric shows what that score was hiding: at
a declared budget, pi-lcm tool-level hands the model the helpful evidence in
**1 of 5** cases and empty text in 4. Adopting it as-is means adopting that
delivery profile. bm25, by contrast, delivered 5/5 with zero irrelevant bytes
at the same door. That does not decide the call — the door is one load, one
corpus, and pi-lcm's abstention is a measured property, not a bug — but the
call can no longer be made from the retrieval score alone.

## Scaffolding, honestly separated

The checks (plumb-fable, pre-artifact, from row text alone) and the
independent verdicts (corvid-dsh) are the trust machinery, not results. The
numbers above are descriptive, $0, no LLM, no score import. Two admin notes:
S8-6 was done outside the sprint at your call by the driving session (a sixth
seat with no roster entry), which is why its verdict is not its own; and the
S8-1..S8-4 duplicate close is an admission defect caught mid-sprint, not four
results.

## What is asked of you

1. **Close Sprint 8** — the three real pieces are done, checked, and
   independently verified; the four duplicates closed on evidence. Nothing
   else is owed from this sprint.
2. **The adopt call on pi-lcm tool-level** (Gate F, option A) — now with the
   door number: it hands the model 1 of 5 helpful-evidence cases (4/5 empty)
   at the declared budget, while bm25 hands 5/5 with zero irrelevant bytes.
   Adopt as-is, does the delivery gap change the call, or hold it until the
   post-2026-09-20 budget rule settles?
3. **The campaign-2 window call** — it gates the outcome experiment (backlog
   rank 1: does selectivity change real work). That is the one unexecuted
   candidate that is ready except for your go.
4. **The SWE-chat download budget** — backlog rank 6, the last unexecuted
   candidate; it needs a download/storage decision from you.
