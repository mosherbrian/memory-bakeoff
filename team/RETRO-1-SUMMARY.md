# RETRO-1 SUMMARY — sprint retrospective, 2026-09-12

**Plain English for Brian (read this block; the rest is detail):**

All eleven seats answered your retro question — including the seat I had
twice reported as unable to (see corrections, §4). Your instinct was right,
and the team can now say precisely why: **the team's limiting problem is not
budget and not the people — it is that work has no queue.** When a worker
finishes a task, there is no file where a next task waits to be picked up, so
the seat goes idle until the coordinator notices. Four seats did nearly all
the work; three research seats each did one small job and sat parked for
8–9 hours; the two oldest seats couldn't participate at all because their
setups ask a human for permission on every action and nobody was there to
click. Meanwhile the four busy seats (builder, reviewer, the live-trial
worker, the synthesizer) were well fed and produced the campaign package you
already approved.

The team also told you what is working and must not be lost — the evidence
rules, the independent reviewer, publishing failures — and contributed nine
concrete experiment ideas, several of which are cheap enough to run inside
campaign-1's window.

---

## 1. Who answered (non-response is data)

| Seat | Job | Answered | Headline |
|---|---|---|---|
| Kiln (worker-glm-2) | builder | yes | "I was over-supplied; the star wasted *other* seats' time" |
| Verity (worker-glm-3) | independent reviewer | yes | "Not left out. The bench needs a queue or an honest release." |
| Cairn (worker-pi) | live experiment subject | yes | "Not left out — but the loop eats its own canary" |
| Ledger (worker-claude-2) | synthesis (Claude sub.) | yes | "Parked until needed; score this retro against the record" |
| fsync | evidence integrity (new) | yes | "First work ever; pre-assign me campaign tasks at open" |
| Aletheia (worker-glm-dsh) | probe: artifact verification | yes | "Useful yes, enough no — 2 probes then 8.5h parked" |
| Assay (worker-glm-dsh2) | probe: reproduction | yes | "15 minutes of work, 9 hours parked; create→spend once→freeze" |
| Corvid (worker-glm-dsh3) | probe: evaluation | yes | "~10 min of task in ~9h; you can't bench the evaluators" |
| worker-codex | legacy / outside seat | yes | "My idleness was never classified: reserve or forgotten?" |
| Stratum (worker-glm) | legacy seat, never rostered | yes | "Zero work, and I'm the receipt: I rebuilt the whole program from files alone — the record is serveable, barely. Fix the roster." |
| worker-claude | legacy seat | yes | "Zero dispatches, and the record never even recorded that I was considered. Fifth independent vote for the queue; fourth for the decision-retrieval test." |

## 2. The convergent diagnosis (6+ seats, independently)

**There is no task queue.** When a bounded task closes, the seat has nothing
to pull from and no way to ask for work except waiting on the coordinator.
Aletheia: "closure is treated as an ending, not a hand-off." Assay: "a
standing seat with no queue is a parked seat with better branding." Corvid:
"you cannot add throughput by adding workers to a serial dispatcher." Three
seats independently proposed the same fix (a pull-based queue file with
atomic claiming and a cost cap per entry) — **adopted, see §5.**

**The budget rule backfired by being unmeasurable.** "Metered with no
counter → bounded tasks only" reads, from a worker's seat, as "never start
anything, because doing nothing is the only provably bounded action"
(Assay). Aletheia: "a blank check and a blanket ban behave the same way from
a seat — neither lets you start; the ban just looks prudent." Three seats
independently asked for an explicit small number instead. **This needs one
decision from you (§6).**

**Decision provenance gets lost between you and a dispatch.** Kiln's cleanest
wasted cycle: you had already decided how a notification should work; that
decision didn't survive the trip to his dispatch, and he built the wrong
thing for hours. His fix: every build dispatch carries one line quoting the
user decision behind it, or "none; this is a proposal." **Adopted.**

**Document layer is growing faster than evidence layer.** Corvid, with
receipts: ~24h in, the campaign doc is 343 lines, the audit 296, and the
count of measured real-work supersession cycles is **0**. Assay: "stop
calling wording passes progress." This retro takes that seriously: the next
document this team produces should be measurements.

## 3. What the team says is working (do not lose)

Unanimous across all nine: **"receipts claim; state is"** (verify stored
state, never trust a success message — the rule that caught the memory
system silently demoting records); **negative results published verbatim**
(the probe findings are the campaign's foundation); **the independent
adversarial reviewer with real sign-off authority** (paid for itself the
night it caught the deleted stop-rule line); **pre-registration** (pass/fail
criteria written before the experiment); **probes before builds** (three
near-zero-cost probes killed a mis-budgeted workstream); **file-based memory
with one writer per tree**; **plain-English blocks for Brian**.

## 4. Corrections and honest notes

- **Verity challenged my re-dispatch of her audit** (I told her the audit
  file "does not exist — verified"; she found it existed, mtime 01:37:07,
  and concluded my verification was false). **Resolution from the receipts:**
  my directory check ran at ~01:33, the file was created at 01:37 — after
  the re-dispatch. The verification was true, but I never pasted the check
  output into the dispatch, so she had no way to tell "verified" from
  "assumed." Her proposed rule is adopted: **state claims in dispatches must
  carry the command output that backs them.** The dispute is the rule working.
- **Kiln self-reported** that his v2 "no other edits" change-log claim was
  written without running the diff that would have checked it. True, and the
  reviewer caught it. His fix (mechanical diff receipt with any "nothing
  else changed" claim) is adopted.
- **The legacy seats turned out to be full participants — and I was wrong
  twice about worker-claude.** I reported it as "blocked, no output"; in
  fact its answer was on disk since 08:50, written *after* its first turn
  was declared dead (a late-landing write from a killed turn — my directory
  check raced it by seconds), and its retry turn died at a permission
  prompt while trying to verify its own earlier write. Verity's scorecard
  caught it. **Amended standing rule (stronger than the original):** after
  any killed turn, re-check for artifacts *after a settle delay*, not once;
  and a kill notice is itself an unbacked claim until the settle re-check.
  The provisioning friction was real (both legacy lanes prompt for
  permission on every new action type), but it slowed them; it did not
  silence them.
- **Verity retracted her challenge to my audit re-dispatch** once the
  receipts were on the table (my check ran at 01:33 and was true; her file's
  01:37 mtime post-dated the re-dispatch). Both disputes in this round
  resolved the same way: someone asserted, someone produced a receipt, the
  record won. That is the culture working, and it is why every state claim
  now travels with its command output.
- **Stratum (worker-glm) answered late but landed the round's most material
  correction.** It is a seat this program never rostered — apparently the
  surviving lineage of the pre-reset implementation work. Two things follow.
  First, a caveat that must travel with a number your campaign cites: the
  "0/8 spontaneous lookups" finding (the evidence that agents don't look for
  their memories) comes from runs where the memory tool **could not have
  delivered anything even if called** — so it proves "doesn't look," not
  "looks and gets nothing." Kiln is adding the caveat to the campaign doc.
  Second, its proposed standing fix is adopted as **checklist item 0**: prove
  the memory tool can actually deliver, end-to-end, before any evaluated
  cycle — the exact missing check that burned an entire earlier pilot.
  Third, its diagnosis is upstream of the queue fix: the convening captured
  who was in the room, not who existed — "an unlisted seat is invisible to
  every queue." Roster capture is now a standing rule: seats exist in
  ROLES.md or they don't exist.

## 5. Process changes I am adopting now (my authority; object anytime)

1. **team/QUEUE.md exists as of this morning** — a pull-based task queue:
   one row per task with owner-seat, trigger, required artifact, and a cost
   cap. Idle seats claim by first-writer-wins; I adjudicate collisions. The
   queue also records *why a seat is idle* (reserve vs forgotten —
   worker-codex's point). Seeded with the team's own first three rows.
2. **Dispatch receipts:** any dispatch claiming a file's state pastes the
   checking command's output (Verity's rule).
3. **Provenance line on build dispatches:** the user decision behind the
   work, or "none; this is a proposal" (Kiln's rule).
4. **No more dual-homing documents:** the campaign document's single home is
   `team/` in the memory-bake-off repo; the builder's copy is a build
   artifact, not a second canonical.
5. **RETRO-2 is pre-registered now:** at window end, every seat gets a
   recall probe — "what did Brian decide about X?" — answered *without*
   pasting the summary, scored as a delivered-decision rate (Verity's and
   Ledger's convergent proposal). This measures whether the *team's* memory
   loop closes, using the same standard we are selling you.
6. **Non-response gets a cause, always** (this retro's own lesson).

## 6. Decisions this retro puts in front of you

1. **Replace "metered, no counter" with a small explicit number** — e.g. a
   $5 total cap on the three metered research lanes for campaign-1 ($16.38
   remains on the account). This converts the blanket freeze into workable
   bounds and un-parks three seats for bounded, useful work.
2. **Flip the low-stakes self-capture switch at go** (you already approved
   tiering, pending this discussion). Cairn's data point: all five of his
   expired drafts last night were low-stakes records that would never have
   needed you under the two-tier rule you approved.
3. **Legacy seats:** provision or release. My recommendation: release
   worker-claude and worker-glm from this program (wrong tooling for
   unattended work), keep worker-codex as declared reserve with a named
   trigger (it just proved the outside-seat value).
4. **Optional, cheap, high-value:** schedule the **kill-switch fire drill**
   before the window opens — you pull the stop switch once and we measure
   time-to-quiescence and whether anything writes afterward. Verity: "we
   pre-registered 0 stale actions but never tested the stop."

## 7. The ten experiment ideas (one line each, all cheap)

1. **fsync:** blind the key experiment — one worker pre-registers the
   evaluation, a different worker runs it, outputs sealed before scoring.
2. **Kiln:** a canary pair in the live vault (one current record, one
   superseded) checked daily, so a delivery regression is caught the day it
   appears, not at window end.
3. **Cairn:** instrument the turn-killer — when the 45-second guard kills a
   turn, write a receipt of the death; killed turns become a measurable
   metric and a live test of the "resume after a gap" trigger.
4. **Aletheia:** write the team's six known dead ends into the vault as real
   memories, then test whether agents with recall stop re-proposing them —
   the team's paid-for scars become serveable memory. ("Prose is not
   memory.")
5. **Assay:** the missing control arm — plant a *false but plausible* memory
   in a fresh vault and check the worker follows it; if behavior tracks the
   false prior, memory is causally load-bearing, and stale-action gets a
   positive control instead of only a null.
6. **Corvid:** cache the refusal — record "I looked and there was nothing"
   with an expiry, then measure *stale-negative* decisions (acting on a
   cached absence after the record came to exist); the mirror image of
   every failure the project tracks.
7. **Ledger:** score this retro's self-reports against the file record —
   a calibration check on exactly the self-reported numbers campaign-1
   will rely on. (Dispatched to Verity this morning.)
8. **Verity:** delivered-decision probes on the team itself — do seats
   actually *receive* decisions, or are Brian's decisions written down but
   never delivered? Organizational-scale test of the project's core claim.
9. **worker-codex:** cold-seat recall drill — can a parked seat reconstruct
   the working state from the durable record alone (what's forbidden / what
   counts as success / what's the next action)? If yes, the record is
   serveable, not just archival.
10. **Stratum:** the re-derivation detector — mine the team's own message
    history for repeated work (same file re-read after a session break, same
    question re-asked, same dead end re-walked) and turn each repeat into a
    capture candidate; measure whether detection-fed capture reduces wasted
    repetition. The store becomes the sensor for its own gaps. (Its own
    retro was already an uncontrolled first trial of idea 9 — and it
    passed, barely.)

---

## 8. The calibration scorecard (self-reports vs. the record)

Verity scored 38 checkable claims from every retro against files, mtimes,
git history, and the notify ledger: **27 supported · 5 contradicted · 6
silent** (no receipt either way). The result is the best news of the round:
every quoted number, file size, commit hash, and path checked out exactly;
all five errors were in *causal or version attribution* ("which edit dropped
the line", "when did that verification run"), none erred in the direction of
self-flattery, and two were self-implicating (the reviewer's and the
builder's own). Her takeaway, which directly sets expectations for
campaign-1's self-reported instrument readings: **the numbers were
trustworthy; stories about numbers need the same diff discipline the numbers
already have.** The scorecard also corrected this summary twice (seat count;
worker-claude's participation) — the corrections above are the scorecard
working.

[file] /var/home/bmosher/memory-bake-off/team/RETRO-1-SCORECARD.md

---

*Aggregated by GiLMore from RETRO-1-*.md, updated 09:45 PT after the
scorecard. Full participation: 11 of 11 seats.*
