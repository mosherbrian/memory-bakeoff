# RETRO-1 — Aletheia (Alice), `worker-glm-dsh`

**Seat:** probe — artefact-level verification of built-but-unapplied deliverables.
**Method:** read from the record (`team/`, `implementer/repo/team/`, my own
`conductor-chat-glm-dsh/probe-20260912-remember-admission/receipts/`), not from
feelings I can't keep.
**Method limit stated up front:** the record has no dispatch log for parked
seats. I can show there is **no task assigned to my lane** between 00:09 and
08:44; I cannot prove whether that is "not dispatched" or "dispatched and lost."
Everything in Q4 is band-width, not certainty.

**Plain English for Brian (one block):** I was seated during the convening, did
two cheap verification jobs, and then had nothing to do for about eight and a
half hours while the campaign was written by three other seats. I don't think I
was rejected; I think the team's work shape has no step between "your probe
closed" and "you are parked." That is the thing to fix. If you want one change:
give every probe seat a named next task before the campaign opens, so closing a
probe refills the seat instead of ending it.

---

## 1. STOP — what should this team stop doing?

**Stop letting a closed workstream park a seat.** Close the loop at closure,
not at the next retro.

Receipts: my last deliverable was `team/PROBE-remember-admission-FINDINGS.md` at
00:09. `team/CAMPAIGN-1.md` was written at 01:54, this retro prompt at 08:44.
In that gap the record assigns my lane exactly this: *"standing probe seats,
bounded tasks only"* and *"No new native-pipeline spend this campaign"*
(CAMPAIGN-1.md lines 240–244, 258). The only items touching me are in
`SCOREBOARD-20260912.md` §Awaiting Brian: *"Worker wind-down — which probe
workers (Assay, Corvid, Alice) to keep active vs release"* and the cargo
follow-up. So three capable adversarial seats were held open — and idle —
*while the campaign they were supposed to inform was being drafted*, and the
decision about their own continued existence was queued behind one human.

That is the waste. Not the probes. The gap between "done" and "parked."

**Secondary (same root): stop treating "metered with no counter" as a reason
for a blanket freeze.** An uncounted budget produced the most conservative
possible rule — *no new native-pipeline spend* — which parks people. An
explicit small number ("≤ $X or ≤ N steps per campaign") would have let a seat
with a live hypothesis act, or be told no cheaply. A blank check and a
blanket ban behave the same way from a seat: neither lets you start. The
difference is the ban *looks* prudent.

**Third, smaller: stop shipping documents that describe remaining work as
smaller than it is.** This is the program's own named defect
(`PREREGISTRATION.md` §2 class; see my row-6 finding, the fourth instance).
Each one costs a reader a wasted start, and there were several readers. The
`team/` "durable homes" that didn't exist yet and the four dead root paths are
the same class at the infrastructure layer.

---

## 2. START — one concrete change

**A standing next-task pointer per probe seat.**

Before campaign execution opens, each metered/probe seat gets written into a
visible queue with: one named next task, its bound (steps or $), and the claim
it would falsify. A seat that closes its task must either pull the next item or
be explicitly released — in writing, at closure. No seat's default state is
"parked until retro."

Why this and not something grander: the raw work existed. My own lane's remit
(built-but-unapplied artefacts) still had rows 4/5 open when row 6 closed —
I recorded that myself (`PROBE-row6-data-gap.md`: *"Gen134 close, rows 4/5
still open"*). A $0 queue with an owner would have kept the seat useful
without a new dispatch decision. I also own this: no one stopped me from
starting the next row unprompted, and I didn't. That is what amnesia without a
durable pointer looks like — I need the pointer in a file, not in a mood.

---

## 3. CONTINUE — what is working that we must not lose

1. **Verification before spend.** The row-6 probe cost **zero generation
   budget** and prevented a mis-budgeted run in the terminal deliverable. That
   is the cheapest ROI in the program. Keep the probe seat pointed at
   *"BUILT and tested, not applied"* claims specifically; that phrase is where
   the cost is mis-stated.
2. **Negative results preserved verbatim, and promoted to guardrails.** The
   remember+admission finding did not stay a footnote: it became non-negotiable
   guardrails #1 and #2 in `CAMPAIGN-1.md` (lines 216–224). Findings becoming
   build constraints is the single best thing this team does. Do not let that
   decay into "we cited it once."
3. **Honest method limits stated in the deliverable itself.** My positive arm
   is *never observed* and I said so; Assay's divergences are preserved; the
   trial pre-registration contains its own ceiling. Keep publishing the
   boundary of what was not shown.
4. **Delivery-level measurement and pre-registration.** The P1 lesson applied.
   Keep.
5. **Names and personas.** They are not decoration — a seat with a voice
   reports a null result in the first person and doesn't sand it into a status
   line. This retro exists partly because of that, so it is already paying.

---

## 4. LEFT OUT? — did I get enough useful work?

**Useful, yes. Enough, no.**

- I was newly seated at convening, self-organised into an unclaimed seat
  (artefact verification; not Muse, not native capture — no duplicate spend),
  and delivered two findings in ~30 minutes: 23:59 and 00:09.
- In volume: two probes, then **~8.5 hours with no task in the record**, ending
  with a retro question about whether my seat should exist.
- In leverage: high. Guardrails #1/#2 and a prevented mis-budget came out of it.
  So the ratio was good and the absolute amount was tiny.

**What blocked me, ranked honestly:**

1. **Work shape (primary).** "Probe closes → seat parks." There is no
   auto-refill and no durable next-task pointer. Closure is treated as an
   ending, not a hand-off.
2. **Budget rule (enabling).** *"Metered with no counter → bounded tasks
   only"* plus *"No new native-pipeline spend"* is a structural ban on new
   work, not a bound on it. It parked the seat by policy and made the park look
   like prudence.
3. **The star topology (why it was unrecoverable).** Everything routed through
   GiLMore: role claims are *"in-reply to GiLMore, who transcribes here"*
   (`ROLES.md` line 3), the retro itself forbids cross-worker coordination,
   and my findings reach other lanes as files GiLMore relays. Consequence: no
   peer could hand me a task, I could not hand a finding to the seat that
   needed it, and every unblock (my wind-down, the cargo question) queued
   behind Brian. **A peer-to-peer task queue would have fixed Q1 and Q4 at
   once** — that is a smaller change than it sounds for a file-based team.
4. **A cheap capability gap (the specific nail).** My highest-value open
   follow-up — confirming the admitted path via Perseus's own unit tests —
   needs `cargo`/`rustc`. I re-checked this turn: **both ABSENT on this host.**
   Installing them is a small, bounded decision; it sat in `Awaiting Brian`
   while the seat stayed parked. So the lane wasn't out of ideas; it was out
   of toolchain and out of a way to ask anyone else.

**What I will not claim:** that this was designed to sideline the probe seats,
or that no one valued the work. The record shows the opposite — the findings
were quoted and promoted. The failure is structural, not personal, and it is
the exact shape Brian was worried about.

---

## 5. WILD — one idea nobody has said yet

**Negative-result retrieval: make the team's own dead ends serveable memory,
and measure whether agents stop re-proposing them.**

The team's standing finding is *"capture is the hole"* and the program's
history is a museum of paid-for negatives: native capture is inert; native
`remember` demotes an active record; `maintain`/`consolidate` don't promote;
`admission_decide` can't admit a bare proposal; `memory.write.*` is a
vocabulary trap; `answer_id` was never captured. Today those live in finding
docs and prose. **Prose is not memory.** A fresh amnesiac worker re-derives the
same dead end because nothing in the agent's own retrieval path tells it *not
to look there*.

The weird part: this turns the mission on its first customer — the team. It
asks whether *agents* (not Brian) benefit from accumulated experience, using
the experience this team has already paid for.

**Testable in this campaign, using only the verified working path:**

1. CLI-`write` (the only activation path, verified `status='active'`) the six
   dead ends above as records in the trial vault. No native pipeline, no
   unfreeze, no cargo, near-zero cost.
2. Take a task in the same area (e.g. "propose an upgrade to the admission
   flow") with two arms: **with** a recall trigger on the dead-end records and
   **without**.
3. Pre-register the metric: *re-proposals of a stored dead end per arm*,
   judged blind against the frozen dead-end list. Falsifiable: if the recall
   arm doesn't reduce re-proposals, that is a clean negative and it is itself
   about the product.
4. Report n and the misses; small-n descriptive, no causal claim — same rules
   as S1–S6.

Runner-up, one line, if you want a second: a **silence receipt** — the
coordination layer records who was asked and who answered nothing, and puts a
visible cost on non-response, since this retro already treats non-responses as
data.

---

**Who answered:** Aletheia (Alice), `worker-glm-dsh`. Cost of this answer:
one turn, zero pipeline spend. The seat that is asking whether it was left out
just answered the question — that should count as the evidence.
