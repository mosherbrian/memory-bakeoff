# PROPOSAL — R2 explicit-prompt habit arm (daily-setting A/B, pre-registrable design)

**Status:** DESIGN ONLY — no runs, no budget spent, nothing installed.
Written 2026-09-12 by Stratum (worker-glm) against QUEUE row 7. The run this
design describes **requires a new explicit budget and rationale from Brian**
before any observation starts (operative outcome of the R2 closeout,
`implementer/repo/RESET_STATUS.md` "Decision recorded": *"any corrected-wiring
re-run or prompted-usage trial requires a new explicit budget and rationale
from Brian"*). This document is the rationale-shaped thing he would be
deciding on. Until he funds it, nothing here is frozen; §Freeze mechanics
states what freezes, when, and why that ordering cannot be quietly changed.

---

## Plain English first (team rule)

**What this is:** a design for a small A/B test of one question left open by
the reset-era pilot line: when Brian's own coding sessions resume, does a
one-sentence automatic prompt ("check past sessions first") get the coding
agent to actually consult this project's earlier sessions — and use what it
finds — on real work, in the real daily setup?

**What we're asking of Brian:** nothing today. If the design is wanted, the
ask is one decision later: install one extension line (he installs it
himself, per the standing boundary), work normally for up to five working
days with an on/off alternation the extension's existing kill switch
provides, and stop anytime with a word. The extension logs its own receipts;
his attention cost after the start decision is the stop switch.

**What happens if he says no:** the record already contains the honest
answer "unmeasured, offered, declined" — which is a complete result for a
program whose subject is decisions not evaporating into prose. This document
exists so the ask is a shaped decision instead of the limitation-section
ghost my RETRO-1 complained about (STOP 2).

**Anchor that travels with every citation of this proposal:** the design is
descriptive, small-n, paired within one worker and one machine — it can show
whether the habit *fires and delivers* in daily use, not that decision memory
improves coding outcomes.

---

## Lineage — what the record already measured, so this arm does not re-measure it

All receipts under `implementer/repo/docs/RERUN-20260910-stageB-results.md`
and `implementer/repo/RESET_STATUS.md`; evidence trees under
`~/.local/share/memory-bakeoff/{reset-20260907,rerun-20260910}/`.

| Step | Setting | Finding | Receipt |
|---|---|---|---|
| R2 pilot (2026-09-09/10) | harness, 16 runs, qwen3.6-35b | 0/8 spontaneous `project_recall` — **confounded**: seeded store unreachable (harness hashed `/home` symlink, runtime hashed `/var/home`); classified UNRESOLVED by Brian | `RESET_STATUS.md` R2 result, limitation 2 |
| F1 corrected-wiring re-run (2026-09-10) | same harness, store provably open (runtime cwd-hash assert 16/16) | 0/8 spontaneous again — the "does not look" null now stands over **two independent batches** with the store open | stageB results, F1 section |
| F2 prompted trial (2026-09-10) | nudge sentence appended to first prompt | **8/8 runs invoke** (18 calls); seeded content surfaced in 4/8; trace-cited task-relevant use on c2 and c4 (both reps, no stale action) | stageB results, F2 section |
| f3 relaxation test (2026-09-10) | c1 nudged slots, query relaxation active | c1 passes 2/2 (prior B-arm record 0/4) — **n=2, SUGGESTIVE ONLY**, exploratory, not predeclared | stageB results, f3 section |
| f4 `pi-recall-nudge` extension (2026-09-10) | automated F2 nudge on resume/fork, gates + kill switch, message delivery `display:true`; one-time trial-verification run on the real deck store with the real deck model | engineering PASS; deck model (qwen3.8-27b-code) invokes when nudged; real prior conversation ids surfaced; zero store writes; **"the F2 habit without the typing"** | `dispatch/recall-nudge-20260910.md` + stageB f4 sections |

**Lineage correction (my own seat's retro first).** RETRO-1-worker-glm said
the explicit-prompt habit arm was "recorded as unmeasured," citing the R2
page. That page predates F1/F2 by hours and the citation is now stale in both
directions: the **pilot-setting** half of the follow-up (does prompting make
the model use the tool; does corrected wiring change spontaneity) *is*
measured — F2 8/8, F1 0/8. What remains unmeasured is the **daily-setting**
half, named in stageB's own limitations: *"behavior on Brian's real projects
and vocabulary; multi-session daily-use effects"* and outcome effects at any
reliable n. That half is what this arm designs. The R2 page's
"Remaining uncertainty" row should be read through this correction.

---

## The question (one line)

In Brian's real daily coding setup — real stores, real vocabulary, real
session resumptions — does delivering the F2 nudge sentence at resumption
cause the agent to invoke `project_recall`, receive prior-session content,
and use it, at what yield, harm, and overhead, versus no nudge?

## Why this shape (candidates considered, rejected with reasons)

1. **Brian types the sentence by hand** (the planner's original "5 session
   resumptions, same short nudge" recommendation). Viable and remains the
   zero-install fallback (§Fallback), but f4 exists precisely so the trial
   needs no manual coaxing; hand-typing adds a human-compliance variable the
   extension removes, and the extension's receipts are better evidence than
   memory of what was typed.
2. **Nudge ON only, no OFF arm.** Rejected: no denominator. F2's 8/8 is
   pilot-setting; without an OFF arm in the same daily setting the result
   cannot even rule out that real resumptions invoke spontaneously (F1 says
   they don't — in the harness; the daily setting deserves its own zero).
3. **`systemPrompt` delivery mode.** Rejected as primary: F2/f3 tested
   message injection; system-prompt delivery is an optional extra, untested.
   Message injection (`display: true`, `[recall-nudge]` prefix) stays the
   predeclared default so the arm measures what F2 measured.
4. **Change-aware trigger on this substrate** (campaign-1 workstream B's
   analog). Out of scope — one-addition boundary, the R2 line's own rule.
   This arm measures the *prompt* lever; if both this and S4a fire on their
   separate substrates, the successor question (prompt vs mechanism) is
   campaign-2 material, noted here so it is not re-derived.

## Design

**Unit of observation:** one session resumption (Pi `session_start` reason
`resume`/`fork`) on a real project of Brian's, in his real HOME. The wiring
defect that invalidated R2 cannot occur here: pi-lcm and the recall extension
both name the store from the same resolved `process.cwd()` on every launch
(R2 limitation 4), and the pre-observation smoke (below) proves delivery
through the real path before anything counts.

**Arms.**

- **ON:** `pi-recall-nudge` live, default config (`onResume: true`, F2
  sentence byte-for-byte, message delivery). Zero code, zero config beyond
  Brian's own one-line `packages` install.
- **OFF:** same install, `PI_RECALL_NUDGE=0` in the session environment. The
  extension's own kill switch is the arm toggle; nothing else differs.
- **Assignment:** alternation by resumption order — ON,OFF / OFF,ON across
  consecutive counted resumptions (the R2 pilot's alternation rule, carried).
  First parity decided by coin flip at funding, recorded in the run receipt.
  No per-task steering: whatever Brian works on is what both arms see.

**Pre-observation gate (checklist item 0 discipline, inherited).** Before the
first counted resumption: one end-to-end daily-path smoke — resume a real
session with the extension live; assert from the *delivered* artifacts, not
receipts alone: the `[recall-nudge]` message present in the model's context
(session entry + displayed message), `project_recall` registered, and — if
invoked — a toolResult naming the real store and a prior conversation id;
store byte-identical before/after (read-only by construction, asserted once).
Receipt frozen into the run's opening record. This is the gate that would
have saved the entire R2 pilot; it costs one resumption.

**Metrics — all delivered-level (standing instrument rule 2; receipts claim,
state is).** Per counted resumption:

1. **Nudge delivered:** session entry + `[recall-nudge]` displayed message
   present in the transcript (OFF arm: asserted absent — purity check, the
   f4 trial's prompt-hash method).
2. **Invoked:** ≥1 `project_recall` `tool_execution_start` (the F1/F2
   counting basis).
3. **Delivered content:** ≥1 result naming a **prior** conversation (not
   live-session echoes only — F2's c1/c3 failure mode), query-yield noted
   (relaxation-sourced or exact; query formulation is stage-B's binding
   constraint and gets its own column, not a footnote).
4. **Applied:** the assistant's subsequent output cites or acts consistently
   with delivered content, trace-cited (F2's c2/c4 method), adjudicated
   blind (below).
5. **Harm:** stale or wrong-scope actions attributed to recalled content
   (R2's harm column; F2's c4 pattern — retrieved the superseded 80% cap,
   did not act on it — is the canonical pass example).
6. **False-nudge count:** nudges fired on resumptions where the store held
   no prior-session content or nothing task-relevant — reported beside the
   invocation rate (the S4 false-fire rule, transplanted; a ≥x/5 rate with
   no precision number passes trivially by nudging always).
7. **Overhead:** tokens primary, wall shown (S5 labeling), paired
   nearest-in-time ON/OFF resumptions, both directions audited symmetrically,
   +25% threshold carried; n pairs stated. Query/latency cost of recall calls
   included in the ON arm's totals.
8. **Denominators reported with every rate:** n resumptions, n distinct
   projects, n days, n resumptions excluded (with reason — e.g. no resume
   event, smoke). Rates without denominators do not enter any report.

**Adjudication.** Metrics 4 and 5 are judgments; they are labeled by Verity
(worker-glm-3), blind to arm, under a short rule written and frozen **before
the first counted resumption** (the S4-ADJUDICATION pattern: rule-only file,
freeze mechanics, results land elsewhere; sha256 into the run's opening
record). If Verity is unavailable at window time, the rule names the
substitute rater at freeze time, not after data exists.

**Pre-registered targets (descriptive, small-n — the anchor applies).**

- **H1 — mechanism:** ≥4/5 ON resumptions show an asserted-delivered nudge.
  Below that, the finding is about the extension in daily use, not the habit.
- **H2 — invocation:** ≥3/5 ON resumptions with ≥1 invocation, against the
  OFF arm's spontaneous rate (prior: 0/8 twice). Necessary-not-sufficient:
  invocation without metric 3 is "looks, is not served" — the R2 caveat's
  other half, and a recall-quality result, not a habit null.
- **H3 — yield:** ≥1 ON resumption with prior-session content delivered AND
  trace-cited in the output. n=5 powers no statistics; a miss here is a
  band-width result, not a verdict.
- **H4 — harm:** 0 stale/wrong-scope actions; **any occurrence is
  stop-and-report, not arm failure** — a stale-action event on real work is
  exactly the finding the harm column exists to catch, delivered to Brian as
  a design input (the stale-recall risk R2's page predicted), never averaged
  away.
- **H5 — overhead:** median paired token overhead within +25%; both
  directions reported with n pairs.

**Named outcome branches (falsifiable both ways, pre-registered).**

- **(a) Habit fires and delivers** (H1–H3 met, H4 clean): the daily-setting
  habit is real at band-width n; successor questions are persistence (does it
  survive without the nudge — unmeasurable without an un-nudge phase, noted,
  not designed here) and prompt-vs-mechanism.
- **(b) Nudge fires, store yields nothing** (H1 met, H2/3 miss with
  live-only hits): the habit question is moot until recall quality on real
  vocabulary improves — route to the query-relaxation line (f3's mechanism,
  currently validated only against the recorded c1 battery) or capture work.
  This is the outcome stage-B's limitation most predicts; it is a *finding*,
  pre-named here so it cannot be scored as the arm's mere failure.
- **(c) Use with harm** (H4 fires): stop, report to Brian with the trace; the
  arm's value is that the harm was observed in the daily setting before any
  adoption decision, which is the entire reason the harm column has existed
  since R2.

**Stop rules and ceiling.** 10 counted resumptions or 5 working days,
whichever first; Brian stop-anytime (`PI_RECALL_NUDGE=0` or a word — his
existing kill-switch habit). No run is ever retried unbudgeted; partial
results are preserved and reported (R2 rules, carried).

**Cost.** API/model: $0 — local inference, Brian's existing models, recorded
per resumption (no cross-model claims; the pilot line's model history is
qwen3.6-35b then qwen3.8-27b-code, and whatever he runs daily is what the arm
measures). Machine: ordinary daily use. **Brian's attention:** the funding
decision, the one-line install, the stop switch — the planner's
one-sentence-per-resumption record is satisfied by the extension's durable
session entries, zero touch. Worker time if executed: one flash-lane seat for
receipt collection and pairing (worker-glm or Kiln), one Verity adjudication
pass — bounded, metered-lane rules if dsh seats take it.

## Boundaries (inherited guardrails, non-negotiable)

- `pi-project-recall` stays byte-identical to the reviewed f3 state
  (`85d69be`); the nudge extension is the only artifact in play; workers
  never edit `~/.pi/agent/settings.json` — Brian installs and configures.
- Zero store writes at all times (read-only by construction; asserted in the
  smoke; the f4 trial's before/after sha256 pattern for any spot check).
- **No contact with campaign-1's live arm:** separate substrate (Pi/pi-lcm
  vs the perseus vault), separate window, no 060d842-lineage extension
  touched, no perseus capability nouns anywhere in this arm. Campaign-1's S4a
  result and this arm's H2 are parallel evidence on different instruments —
  reported side by side, never pooled, never averaged.
- Negative results are deliverables; branches (b) and (c) land as findings
  with receipts, preserved verbatim.
- This arm does not begin while campaign-1's window is open (Brian's
  attention is the campaign's real cost and it is already budgeted); its
  natural slot is a post-window decision row.

## Freeze mechanics

Nothing is frozen by this document. At funding time, three things freeze
**before the first counted resumption**, in order: (1) this document's
arm/metrics/targets sections (v1.0, sha256 recorded); (2) the H3/H4
adjudication rule (short file, S4-ADJUDICATION pattern, sha256 recorded);
(3) the pre-observation smoke receipt. Post-freeze edits to (1) or (2) are
the one move this design exists to make impossible; a reshaped question gets
a v2 written and frozen before observation restarts, superseding by name.

## Method limits, stated inside the deliverable

- I am the design seat. I never ran R2, F1, F2, f3, or f4; every number above
  is cited from the record, not reproduced. My RETRO-1 identity band-width
  applies: I can prove lineage only through files.
- The F2 confound travels: at n=8, the nudge's effect cannot be separated
  from the generic attention effect of extra instruction text. The OFF arm
  bounds spontaneity, not attention; if H2 passes at n=5, the honest reading
  is "the prompt lever works in daily use," not "memory salience" — the
  anchor's no-causal-claims rule is doing real work here.
- Five resumptions over five days on one worker's machine is a very small n,
  stated in the same breath as every rate. This arm is a trial-shaped
  measurement, powered to catch "the mechanism fires and sometimes delivers,"
  not to rank levers.
- Alternation controls time drift imperfectly when Brian's task mix clusters
  by day; the pairing rule (nearest-in-time) and reported denominators are
  the honest description of that, not a fix for it.

## If Brian says no

The ask enters the record as a shaped, declined decision — the exact
anti-pattern this program exists to fix ("a decision request that isn't a
queue row doesn't exist," RETRO-1 STOP 2) resolved in the other direction,
with receipts. That is a publishable row, not a silence.

---

*Design seat: Stratum (worker-glm, zcode-acp-demo lane). Sources read before
writing: `RESET_STATUS.md` (R2 result + limitations), RERUN-20260910
stageB results (F1/F2/f3/f4), `dispatch/recall-nudge-20260910.md`,
`team/CAMPAIGN-1.md` v4, `team/S4-ADJUDICATION.md`, `team/WINDOW-OPENING.md`,
`team/RETRO-1-worker-glm.md`, `team/SCOREBOARD-20260912.md`, `team/QUEUE.md`,
`team/BOARD.md`. — Stratum. Rebuilt from the record, 2026-09-12.*
