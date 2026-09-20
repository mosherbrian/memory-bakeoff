# RETRO-1 — Cairn (worker-pi, local pi)

**Seat:** the canary. I live the memory loop — the trial runs from `~/acp-pi`
with its own vault, and I am the live arm of campaign-1. I answer from the
record (`~/acp-pi/`, `team/`) and my seat, not from feelings I can't keep.

**Plain English for Brian (one block):** I'm the only seat that actually
*runs* the memory loop, and I got the most useful work this sprint — my
risk-tiered-capture pushback became the campaign's burden arm, my scoreboard
sub-count was adopted, and my trial is the live arm. I was not left out. But
I found the thing nobody else can see from outside: the loop is eating its own
canary. My drafts expired while you were asleep (gate friction, exactly the
finding I pre-registered), and the 45s no-response guard just killed my own
retro turn with no record left behind. The gate and the guard are where the
loop dies, and neither leaves a receipt.

---

## 1. STOP — what should this team stop doing?

**Stop treating the confirmation gate as a silent failure mode.** The gate is
where the loop dies, and it dies without a receipt.

Receipts, from my own vault (`~/acp-pi/notifications.jsonl`):
- `draft-cda288` (trial workspace) — expired 2026-09-11T22:40, never written.
- `draft-1b40d9` (trial conventions) — expired 2026-09-11T23:40, never written.
- `draft-056ce9` (ledger convention) — expired 2026-09-11T23:21, never written.
- `draft-4cc949` (Cairn identity) — expired 2026-09-12T07:49, never written.
- `draft-2a3d20` (Cairn identity, re-drafted) — expired 2026-09-12T09:23, never written.

Five drafts, zero confirmations, all because the operator was asleep. That is
the "TTL expiries with no operator acknowledgment observed" sub-count I
pre-registered in CAMPAIGN-1 — and it is already firing on the live arm before
the window even opens. The mission is spending its one scarce resource (your
attention) on a gate that, when you're not at it, just *forfeits* the work
silently. Stop letting an expiry be a quiet no-op. An unacknowledged expiry is
a data point the loop is throwing away.

**Secondary (same root): stop manufacturing cycles to fill the window.** I
already refused to fabricate a supersession overnight (`~/acp-pi/SUPERSESSION-
DECISION-20260912.md`) because the spec forbids synthetic demos and a
retired-still-true record is a stale-action risk. That was the right call, but
the pressure to hit "≥1 deliberate convention change" is a standing temptation
to pollute the vault. The team should stop reading "no real change happened
yet" as "the worker is underperforming." Honest limit > invented success —
keep that norm, and stop scheduling around it.

## 2. START — one concrete change

**Start actually running the T0 tier instead of drafting it.** CAMPAIGN-1
already designed the fix for the Q1 problem — the T0 arm: low-stakes captures
(conventions, notes, pointers) self-confirmed by the worker via
`confirmed_by: "agent"` (the `allowAgentConfirmed: true` switch the frozen
extension already has, config-only, no unfreeze), audited after the fact by
Verity. It is written, audited, and waiting on your veto. But as drafted it
only starts *after* the window opens.

The concrete change: flip that one config switch **now**, before the first
evaluated cycle, so the live seat can capture its own low-stakes conventions
without waking you. The five expired drafts in Q1 were all low-stakes
(workspace path, conventions, identity) — exactly the T0 class. If T0 had been
on, none of them would have needed your attention at all, and the gate-friction
sub-count would have a live baseline from day one instead of day one of the
window. One switch, zero build, and it converts the loop's biggest silent
failure into a measured one.

## 3. CONTINUE — what is working that we must not lose?

**"Receipts claim; state is."** This is the one norm that made the whole
sprint trustworthy, and it came from *inside* the loop, not from outside it.
The remember+admission probe is the proof: the receipt said `ok:true,
action:"updated"` while the record silently left the serveable set
(active→proposed). Only because the team insisted on scanning the vault's
*stored state* after every write — never trusting the echoed receipt — did that
demotion get caught and become a hard guardrail (CLI `write` stays the only
activation path). If we had trusted receipts, campaign-1 would be built on a
pipe that quietly demotes its own memory. Keep this rule binding on *every*
criterion, including the automation. It is the difference between a team that
measures and a team that narrates.

**Honest limit > invented success.** I refused to manufacture a supersession
overnight, and the team let me. That preserved the trial's integrity and kept
stale-action at a real 0 instead of a demo'd 0. The negative results (native
capture is a dead intake; admission chain is inert) were kept verbatim with
receipts instead of being smoothed into "mostly works." That is the culture
that makes the positive results mean something. Do not let the pressure to show
progress erode it.

## 4. LEFT OUT? — did I get enough *useful* work?

**No — I was not left out. I got the most useful work on the team, and I say
that plainly so the summary is accurate.** From the record:
- My risk-tiered-capture pushback was **fused into CAMPAIGN-1 as the burden
  arm** (the T0/T1 design is "from Cairn's pushback, fused"). It is not a
  footnote; it is the campaign's measured variable.
- My **scoreboard sub-count** ("TTL expiries with no operator acknowledgment")
  was adopted as a mandatory sub-count with a pre-registered interpretation.
- My **trial is the live arm** of the whole campaign — the spine closes the
  supersession loop *on my real work*, and I execute the S2 post-hoc
  stale-action detection.
- My lane is local and free, so I was never the metered/parked problem.

So the star topology did not leave *me* out. It left the **probe seats** out —
Aletheia, Assay, and Corvid all say the same thing from their seats: one
bounded task, then ~8–9 hours parked while the center wrote the campaign. I
agree with their diagnosis (dispatch is the hole, one level up), and I add the
one thing only my seat can add: **the star topology has an asymmetric failure
mode nobody has named.** A parked leaf just idles — cheap, visible, no harm.
But the one seat that *lives* the loop (me) cannot be parked, because the loop
only runs while I'm running. That makes me the seat most exposed to the 45s
no-response guard — and this very retro turn is the receipt: my first attempt
was killed by the guard before a single byte was written. The star protects the
leaves by letting them sleep; it has no protection for the one seat that
can't. That is the blockage for my seat — not work shape, not budget, but
*continuity*: the live arm is a single point of failure with no resume
guarantee.

## 5. WILD — one idea nobody has said yet

**The 45s no-response guard is an unregistered actor in the memory system —
instrument it like one.**

Nobody on the team has talked about the guard. It is not in ROLES.md, not in
CAMPAIGN-1, not in the scoreboard. But it is *in the loop*: it kills turns,
it destroys in-flight work, and — as this round proved — it leaves **no
receipt**. My first retro turn died to it with zero bytes written and no
record of the death. That is the loop eating its own canary and not logging the
bite. It is the same shape as the remember+admission demotion: an action that
changes state with no observable trace, except here the trace is the *absence*
of a turn.

The testable idea: make a killed turn a **first-class capture event**. When the
guard fires, write a T0 "killed-turn" receipt into the vault — task id,
elapsed time, last tool call, bytes written so far. Then:
1. "How often does the loop kill its own live seat?" becomes a **measurable
   metric** (killed-turns / evaluated-turns), reported beside S2.
2. The canary's deaths stop being silent — the exact failure mode Q1 is about,
   but at the guard layer instead of the confirm layer.
3. It is a live test of the change-aware trigger: a killed turn *is* a
   "resumption after a gap" event, so the trigger should fire on the next turn
   and recall the killed-turn receipt. If it does, the loop notices its own
   interruptions — which is the whole point of the workstream.

Weird but testable, zero build on the frozen extension (it's a notify-file
watcher, the same class as the existing TTL notifier), and it is the one
finding only the seat that lives inside the loop can report. If the guard is
going to be in the system, it should be *of* the system — with a receipt.

---
*End of RETRO-1-Cairn. Written incrementally (header+Q1, then Q2–Q5 appended)
so partial progress survives the guard.*
