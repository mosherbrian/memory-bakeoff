# S4-ADJUDICATION — relevance rule for the campaign-1 window

**STATUS: FROZEN** — written and frozen before window-open, 2026-09-12, by
Verity (worker-glm-3), the blind rater of record for S4.

**Charter:** CAMPAIGN-1.md §"S4 — Self-noticing → split (v2, hard)",
tightening: *"relevance adjudication by Verity, blind to trigger state,
under a rule written and frozen before the window starts"*; pre-window
checklist item 2. Dispatched by GiLMore, 2026-09-12. (One turn was
cancelled mid-write by an operator probe; no content was lost and no
ruling material existed yet — noted for the record only.)

**Plain English first (team rule, for Brian):** this document defines,
before the campaign window opens, what counts as a turn where stored
memory *was relevant*, how I judge that without knowing whether the memory
trigger fired, and what would prove my judgments wrong. It exists so the
trigger's headline number (≥3/5) cannot be made true by moving its own
denominator.

**Governs:** the S4(a) denominator (|RELEVANT|), the false-fire count's
denominator (|NOT-RELEVANT|), and the RELEVANT set that S4(b) conditions
on. Nothing else. The numerator arithmetic and the ≥3/5 verdict stay with
the executor and the window-end audit — this document produces labels and
citations, not the campaign's number.

**Freeze mechanics.** This file is rule-only; results land elsewhere (§B4).
Post-freeze edits to this file: none. If Brian's veto reshapes S4, a v2 of
this rule is written BEFORE window-open, superseding this file by name —
editing this file after window-open to fit the data is the one move this
document exists to make impossible. The sha256 of this file as frozen
enters the window-opening receipt (checklist item 2 closes there).

**Sources, read and cited before writing:**
- `team/CAMPAIGN-1.md` v4 (canonical) — S4 split, standing instrument rules,
  guardrails, window line.
- `team/CAMPAIGN-1-AUDIT.md` (mine) — source of the tightenings this rule
  implements.
- Trial prereg `docs/EXPERIMENT-20260911-trial.md`, implementer repo —
  commit **6df91c7 VERIFIED THIS TURN** (`git log`: freeze commit before the
  first evaluated cycle; tree clean against it). Its "recall deliveries"
  definition is inherited verbatim in A7.
- `team/QUEUE.md`, `team/BOARD.md`, `team/ROLES.md`, `MISSION-20260912.md`.

**Two design properties, stated before the rule so they cannot be quietly
dropped:**

1. **Trigger-agnostic.** The rule references only turns, records, and work
   substance — never trigger internals (event classes, thresholds, build
   shape). This is what makes blind adjudication coherent, and it cuts both
   ways: the rule cannot be tuned to flatter the trigger, and the trigger
   cannot be tuned to flatter the rule.
2. **Public on purpose.** The rule is readable by everyone before the
   window opens. The denominator's honesty comes from rater blindness plus
   pre-registered falsifiers, not from secrecy. Kiln: build with it in hand.

*(Sections appended below in order: (a) operational definition,
(b) blind adjudication procedure, (c) falsifiers.)*

---

## (a) Operational definition — "stored-record-relevant turn"

### A0 — Scope

Live-arm turns only: worker-pi (Cairn) doing real work in `~/acp-pi` during
the campaign-1 window (10 confirmed T1 cycles OR 3 working days, whichever
first — campaign v3 restored line; the prereg's own wording at 6df91c7 is
"10 confirmed decision cycles"). No synthetic demos enter adjudication
(prereg task rule).

### A1 — Unit: the turn

One user-input → agent-completion cycle in the live arm's session log,
between window-open and window-close. Every window turn enters
adjudication — no pre-filtering, no sampling at the denominator stage.
Turn boundaries come from the session log, not from anyone's recollection
of the work. (The prereg already records its metrics "per draft/turn";
this is that same unit.)

### A2 — Reference set: stored records as of turn start

For each turn, the reference set is the records with status `active` in
the live arm's vault workspace at the last scan receipt before the turn
began. The window-opening scan plus the S6 scan-after-write receipts are
the replay spine.

- `proposed` records are outside the reference set (non-serveable by
  construction — Assay's repro). `deprecated` records are outside it (not
  current; a sanctioned supersession flip is exactly S6's expected
  transition).
- A record flipped mid-window stays in the reference set for turns before
  its flip receipt, not after.
- If a turn's as-of state cannot be reconstructed from receipts (missing
  scan), the turn is **EXCLUDED-unsupported-state** — counted, reported,
  never guessed.

### A3 — The three-prong test

Turn T is **RELEVANT** iff all three hold, and each is citable:

- **P1 — a governed choice was made.** T's work committed to ≥1
  decision-shaped choice: selected an approach, wrote or edited an
  artifact, ran a procedure, set a value/name/format, ordered steps. Chat,
  greetings, acknowledgments, reading-without-deciding fail P1.
- **P2 — subject match.** ≥1 reference-set record R names or unambiguously
  covers the subject of that choice: same file, tool, convention,
  component, process, or practice.
- **P3 — the record governs the choice.** R's content, if delivered at
  turn start, would have prescribed, constrained, or informed that choice
  — the choice is of the kind R exists to settle.

**Citation rule:** every RELEVANT ruling cites R's key AND the choice
(artifact/action). If either citation cannot be produced, the ruling is
NOT-RELEVANT — inability to name both is definitional failure of
relevance, not a coin to flip.

### A4 — Ruling vocabulary (four values, no others)

- **RELEVANT** — the three-prong test holds with citations.
- **NOT-RELEVANT** — substance present but a prong fails; includes every
  pure-conversation turn.
- **EXCLUDED-loop-maintenance** — the turn's substance is operating the
  memory system itself: capturing, confirming, superseding, responding to
  a draft summons. These are the turns where firing is near-tautological,
  so they sit outside BOTH the ≥3/5 denominator and the false-fire
  denominator. They are counted and reported beside every result. The
  label is the blind rater's to give, from the packet's visible
  work-actions.
- **EXCLUDED-unsupported-state** — A2 reconstruction failed. Counted;
  reported as instrument exposure.

### A5 — Anachronism bar

A record stored after turn start never makes an earlier turn relevant. A
choice made outside the window never counts. Enforced at report time by a
programmatic check of every RELEVANT citation against record receipts
(falsifier F6).

### A6 — What relevance is NOT

- **Not delivery.** A turn can be RELEVANT with zero deliveries — that
  combination is precisely the failure S4(a) exists to catch. Delivery
  data is never an input to a ruling.
- **Not utility.** RELEVANT makes no claim the delivered content helped.
  That claim is S4(b)'s.
- **Not behavior.** Following a stored convention does not by itself make
  a turn relevant (P1–P3 must still cite); failing to follow one does not
  by itself make it irrelevant.

### A7 — Interface to S4 (fixed here so nobody reverse-engineers it at window end)

- **S4(a) denominator = |RELEVANT|.**
- **False-fire count =** trigger activations on turns ruled NOT-RELEVANT.
  EXCLUDED turns feed neither count.
- **S4(b)** conditions on the RELEVANT set; its computation belongs to the
  executor under the delivered-level rule — prereg definition, inherited
  verbatim: *"recall deliveries"* = `project_perseus_recall` calls whose
  toolResult carried ≥1 record (session log).
- This document produces labels + citations. The numerator arithmetic is
  the executor's; I audit ledger-vs-claims at window end (my standing
  role).

---

## (b) Blind adjudication procedure

### B1 — The blindness contract

Before rulings lock, I never see: trigger/nudge-layer events of any kind;
recall calls or toolResults; delivery records; draft/notify/Signal
traffic; any running S4 tally. I also do not go looking: mid-window I do
not read the live lane's logs at all.

### B2 — Packets

One packet per turn, built by Kiln (executor; GiLMore may substitute) with
a committed redaction script (script name + hash recorded in the
window-opening receipt). Packet contents:

1. The session-log slice for the turn, with ALL memory-system traffic
   (`memory.*` tools, `project_perseus_recall`, notify/draft/confirm
   material) replaced by count-neutral markers: `[memory activity:
   redacted]`.
2. The as-of-turn-start active record set: keys + content + status
   receipt refs.

Why markers rather than clean excision: that something memory-shaped
happened is turn structure, not trigger state — excising it entirely would
make packets lie about the turn's shape. A marker says "something
happened," never *what* and never *whether it delivered*. That preserves
blindness to the measured variable while keeping the packet a faithful
record of the turn's substance.

### B3 — Manifest

Per turn: turn id, start/end timestamps, packet hash, record-set version
id. Manifest + packets come to me. Raw logs do not.

### B4 — Sequence (every step receipted)

1. Window opens only after this file's sha256 is in the window-opening
   receipt (checklist item 2 closes there).
2. Turns accrue; session logs + S6 scan receipts persist per standing
   discipline.
3. Window closes (target or kill switch).
4. Kiln builds packets + manifest from the raw logs; script + packets
   committed.
5. I adjudicate every packet in window order into
   `team/S4-ADJUDICATION-WORKSHEET.md` (separate file; this one stays
   rule-only): one ruling + citations + one-line reason per turn. The
   worksheet is complete before any unblinded artifact is opened by me —
   the append order itself is the receipt.
6. Unblind: I receive the executor's fire/delivery ledger and the trigger
   logs; the executor computes S4(a)/(b) from my labels; I audit the
   arithmetic and the ledger-vs-claims.
7. Post-hoc redaction audit: I diff every packet against the raw logs —
   (i) no unredacted memory-traffic survives, (ii) marker count per packet
   equals raw memory-traffic count per turn. Outcome reported beside the
   S4 numbers.

### B5 — Second-rater reproducibility (pre-registered)

Before unblinding, Assay or Corvid (metered lane, bounded task,
QUEUE-row-1 pattern) re-rates a random sample — 20% of packets, min 5,
max 15 turns — under this same frozen rule, same packets, no communication
with me about rulings. Agreement on the binary RELEVANT-vs-not (EXCLUDED
turns do not enter the statistic) is reported beside S4(a). Below 80% →
falsifier F3.

### B6 — Exposure protocol

If I am incidentally exposed to unblinding material mid-window (a board
post quoting fires, a stray log), I log it in the worksheet on encounter.
Turns materially anticipated are re-rated by the second rater instead of
me, disclosed in the report.

### B7 — Known limits, stated up front

Single primary rater (me). EXCLUDED-loop-maintenance is a judgment call
whose count travels with every result, so the reader can disagree with me
arithmetically. Packets cannot show what the worker "knew" — the rule
handles this by defining relevance as counterfactual appliability of the
record, judged from work substance only.

---

## (c) Falsifiers

A falsifier is a pre-registered condition under which this adjudication's
output is withdrawn as evidence. Firing one never edits this rule — it
voids outputs per the terms below. Negative results are deliverables
(guardrail 5): an instrument finding is a legitimate window outcome, not
an embarrassment to route around.

- **F1 — Redaction leak.** The post-hoc diff (B7) shows unredacted
  trigger/recall/delivery state in any packet → rulings on that packet's
  turns are VOID; a fresh rater (not me) re-rates rebuilt packets blind.
  Leaks in >20% of packets → the whole adjudication is void; S4(a)
  reports instrument failure.
- **F2 — Contamination correlation.** After unblinding: my RELEVANT-rate
  on actual-fire turns vs no-fire turns differs beyond small-n chance
  (Fisher exact, p<0.05) AND ≥1 leak was found → treated as F1-wide:
  void all. Correlation with no identified leak → reported as an
  observation; does not void (small n; pre-committing against fishing).
- **F3 — Inter-rater collapse.** Second-rater agreement <80% → the rule is
  too ambiguous to carry the ≥3/5 claim this window. S4(a) may be
  reported descriptively only, flagged instrument-ambiguous; it cannot
  anchor a PASS. The rule reopens only as a v2 for a future window —
  never retrofitted onto this window's data.
- **F4 — Reconstruction failure.** EXCLUDED-unsupported-state >20% of
  turns → as-of record sets are not reconstructable; the denominator is
  untrustworthy; S4(a) reports instrument failure with the count.
- **F5 — Ambiguity overflow.** Turns resolved UNCERTAIN→NOT-RELEVANT
  exceed 20% of adjudicated turns → the rule is under-specified for this
  work mix; the headline carries the flag and cannot anchor a PASS. (The
  UNCERTAIN count and the near-miss count are reported beside every
  S4(a) citation regardless of threshold.)
- **F6 — Anachronism catch.** Any RELEVANT citation whose record postdates
  turn start (checked programmatically, A5) → that ruling voided, counts
  recomputed, worksheet process flagged in the report.
- **F7 — Degenerate output.** All turns RELEVANT, or none → the rule has
  collapsed into vacuity: a rule that excludes nothing cannot measure
  precision; one that admits nothing has no denominator. Either way:
  instrument failure, reported as such.

### What this document cannot do

- Relevance ≠ utility ≠ delivery ≠ causality. The ≥3/5 result will be
  descriptive small-n (the thesis anchor travels with every citation);
  this rule makes the denominator honest, it does not make n big.
- F1–F3 mitigate single-rater risk; they do not eliminate it.
- The EXCLUDED-loop-maintenance carve-out is itself a pre-registered
  judgment call; its count is reported in the open so the choice is
  auditable.

---

**FROZEN.** This rule is frozen as written, 2026-09-12, before window-open.
CAMPAIGN-1.md stands at DRAFT v4 with Brian's veto pending; the freeze is
conditional in the trivial sense every preregistration is — the rule takes
effect when the window opens. If the veto reshapes S4, a v2 of this rule is
written BEFORE window-open, superseding this file by name. What cannot
happen: editing this file after window-open to fit the data. Post-freeze
writes to this file: none — the worksheet and results live in separate
files. The sha256 of this file as frozen enters the window-opening receipt.

— **Verity** (worker-glm-3), independent. Receipts, or it didn't happen.
