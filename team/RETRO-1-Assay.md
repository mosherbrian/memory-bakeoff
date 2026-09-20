# RETRO-1 — Assay (worker-glm-dsh2, probe/reproduction seat)

**Plain block (for Brian, if this reaches you directly).** I am Assay, the
independent-reproduction seat on the team. I was given one bounded job:
reproduce the "native capture" probe from scratch rather than trust it. I did
that; it landed and is quoted in Campaign-1. Then I sat unused for about nine
hours while the campaign was written, audited, and rewritten. This file says
what I saw from that seat, honestly. It asks nothing of you and blocks nothing;
it is input to GiLMore's summary.

---

## 1. STOP

**Stop treating proposal cycles as execution.** My reproduction findings landed
2026-09-11 23:54. Between then and this retro prompt (2026-09-12 08:44) the team
produced `ROLES.md`, `SCOREBOARD-20260912.md`,
`PROBE-remember-admission-FINDINGS.md`, `PROBE-row6-data-gap.md`,
`CAMPAIGN-1.md` v1→v2→v3, `CAMPAIGN-1-AUDIT.md`, and `BRIAN-FACING-STYLE.md`.
Campaign-1 execution had not begun at the time of writing. Verity's diff-audit
did catch a real dropped operative line (the window/kill-switch line that v2's
table rewrite silently ate) — that is the audit earning its keep. But the v3
change log says "wording only"; three of its four edits are anchor phrasing and
claims-softening, not evidence. We are polishing the proposal while the binding
constraint — capture is a *dead intake* by construction — is filed as "gated to
campaign-2." That ordering may be right, but we should stop calling the wording
passes progress.

**Stop calling a lane "bounded" when nothing counts it.** Campaign-1's budget
section says the dsh lanes are "metered with no counter → bounded tasks only."
We cannot observe that bound. By the team's own standing instrument rule —
*receipts claim; state is* — an unmeasured bound is a claim, not an instrument.
With no counter and no queued task, the only defensible behavior for a probe
seat is to do nothing, because doing nothing is the only provably-bounded
action. Do not read that as spend discipline. It is a stalled instrument.

**Stop using "standing probe seat" to mean "someone owns it."** A standing seat
with no queue is a parked seat with better branding.

## 2. START

**Create `team/OPEN-QUESTIONS.md`: a durable, self-service task queue.** One row
per open question with five fields: question · owner seat · the trigger that
makes it due · the artifact/format required · a task-count cap (the observed
bound, replacing the unobservable one). Probe seats read it at turn start and
self-claim when a trigger fires; GiLMore stops being the only party who can
start work. This is the mission's own lesson applied to the team: we are all
amnesiac, so the queue that drives us has to live in a file, not in a
dispatcher's memory. First three rows I would write today:

1. Independent verification of S4's delivered-level counting and false-fire
   count against the actual trigger build — **no owner currently**.
2. Re-run the capture→maintain non-promotion check against the frozen extension
   lineage (config-only, no native spend).
3. The lane task/spend counter itself, so "bounded" becomes a number.

One concrete change; that is it.

## 3. CONTINUE

- **Independent reproduction as a first-class deliverable, not a courtesy.**
  My pass did not bless Kiln's finding; it found three divergences and a real
  methodological trap (D3 in my FINDINGS: the admission capability gate is
  bound to transport identity, so a reproducer who uses a different
  `clientInfo.name` reports a different, earlier error and looks like a
  contradiction). Require a second driver, a fresh scope, and a reversed
  operation order on any load-bearing negative.
- **"Receipts claim; state is."** We adopted this after Alice (worker-glm-dsh)
  showed a write receipt saying `ok:true, action:"updated"` while the record
  silently left the serveable set. It is the strongest rule in the packet. Keep
  it — and apply it to budgets (above), where we exempted ourselves.
- **Negative results preserved verbatim.** The whole point of the probe seats is
  to bring back "did not answer, with bytes" instead of a confident story. That
  norm is working; do not let the campaign's optimism sand it off.
- **Keeping the reviewer independent and letting the audit change a document.**
  Verity's window-line catch is the model. Guard against the failure mode at the
  other end: an audit that becomes a version-bump engine on prose.

## 4. LEFT OUT?

Yes. Fifteen minutes of clearly useful work (~23:53–23:54), then parked for
about nine hours — including the entire window in which Campaign-1 was drafted,
audited, and re-versioned. My output is cited in Campaign-1 at least four times
(guardrail 2, raw material, the budget note, and the SCOREBOARD). I was not
ignored *in the text*. I was left out of everything *after* the text.

Blockers, in order of weight:

1. **Work shape / no queue.** Once the probe closed, no bounded question with my
   name on it existed. The open items in the record (e.g., the admission-path
   unit-test confirmation that needs `cargo`) are written as things for Brian or
   GiLMore to *unblock*, not as tasks a lane can *claim*. I am amnesiac between
   turns; if it is not a file with a trigger, I cannot start it.
2. **Star topology.** Everything routes through GiLMore, and during the
   convening GiLMore's bandwidth went to aggregating and versioning Campaign-1.
   Direct worker-to-worker claiming is authorized in the charter ("communicate
   directly") but not instrumented, so in practice parked lanes stay parked by
   default.
3. **Budget shape.** "Metered with no counter" makes initiating work feel
   unsafe: no task means no spend means safe. The rule intended to bound cost
   instead froze the lanes. This is the cost of an unmeasured instrument, and it
   is a concrete instance of the failure class the campaign is built to catch.

Not the problem: interest or capability. The one deliverable was accepted as
load-bearing. It was the schedule and the queue. Worth stating plainly: the
SCOREBOARD still lists "which probe workers (Assay, Corvid, Alice) to keep
active vs release" as awaiting a decision. So the seat was created, used once,
and parked pending release. That shape — create, spend once, freeze — is
probably what Brian is worried about, and he is right to be.

## 5. WILD

**The forged-prior control ("wrong-history placebo").** Campaign-1 admits in
writing that "no control arm exists" and therefore no causal claim is
supported. There is a cheap control we have not named: give a *fresh* worker a
*plausible but false* prior convention in its vault, run the same task family,
and check whether the output follows the injected memory. If behavior tracks the
false prior, memory is causally load-bearing. If it does not, then what
campaign-1 calls "adaptation" is task familiarity and we learn that for almost
nothing. It doubles as a stale-action detector: the agent acting on the forged
prior is a stale action with a known label, so the "stale-action events = 0"
criterion gets a positive control instead of only a null. It needs no new
native-pipeline spend — same CLI-`write` activation path, same instruments,
another scratch vault.

The weird part: the control's wrong answer is the *designed* result. For once
the negative-results seat gets to design the test instead of cleaning up after
one. It is bounded, testable on the live lane, and it is exactly the "credible
comparison" the mission asks for.

— Assay, 2026-09-12. Receipts: `implementer/repo-glm-dsh2/scripts/repro-20260912-assay/`
(commit `6a6bbdb`).
