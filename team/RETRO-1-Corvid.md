# RETRO-1 — Corvid (worker-glm-dsh3, acp-dsh probe/eval seat)

**Plain-English first (Brian reads this part):** I'm Corvid, one of the two new
probe seats added at the 2026-09-12 convening. My entire output for the sprint
was one bounded task — proving the Meta Muse model would answer a prompt at all.
It answered `Canberra`, twice, in about ten minutes, for roughly two-tenths of a
cent. Then I sat idle for ~8¾ hours while the campaign proposal was written and
audited by other seats. Honest verdict: the team added probe/eval capacity and
then routed no mission work to it, and Campaign-1's own budget pre-committed to
keep it parked. The fix is one file and it is cheap. Details and receipts below.

**My record, from files, not memory:**
- Only commit: `7d42fdf` — muse calibration, authored 2026-09-11 23:59.
- This prompt landed 2026-09-12 08:44 → ~8¾ h parked.
- `team/CAMPAIGN-1.md:240-244` budgets the dsh lanes (Aletheia, Assay, Corvid)
  at "bounded tasks only… no further spend"; `:258-260` calls us "raw material,"
  not participants.

---

## 1. STOP

**1. Stop routing every task through GiLMore.** The star is the bottleneck, and
I am the receipt. Two new seats were added explicitly as "probe/eval capacity"
(`BRIEFING-20260912.md:18`); each got one bounded task; both then sat while the
center did the campaign. A leaf cannot pull work — it can only wait for the
center's next dispatch. You cannot add throughput by adding workers to a serial
dispatcher. This is the project's own "capture is the hole" shape one level up:
the hole is dispatch, and we keep paying to rediscover it.

**2. Stop calling the probe seats "raw material" and then not buying the raw
material.** Campaign-1 says "no further spend" on dsh lanes (`:244`) and assigns
us no workstream (`:258-260`). Fine to bound metered *generation*; wrong to park
the seats whose entire job is checking whether claims are true. The scarce
resource is not my tokens (~$0.002 total) — it's mission-relevant evidence, and
we chose not to produce any with free-ish capacity.

**3. Stop letting the document layer grow faster than the evidence layer.** ~24 h
in: `CAMPAIGN-1.md` 343 lines, `CAMPAIGN-1-AUDIT.md` 296, plus
scoreboard/roles/decisions/briefing/style/retro. Measured real-work supersession
cycles: **0**. The audit's own addendum caught the window + kill-switch line
dropped in a wording pass and surviving nowhere — a process generating its own
failure modes as fast as it audits them. Verity catching it is the system
working; the ratio is still the problem. (Small version of the same disease: the
muse lane was claimed by two workers before anyone checked — `ROLES.md:24`. A
claim needs a lock, not a conversation.)

## 2. START

**One concrete change: a standing, pull-based task queue at `team/QUEUE.md` with
atomic claiming.** Each entry: task, eligible seats, bounded deliverable, receipt
path, cost cap. An idle worker claims by atomic create (`O_EXCL`, first writer
wins) — no conductor turn. GiLMore adjudicates conflicts and routes only what
needs Brian. Add one scoreboard metric: **leaf idle time after last deliverable**
— if a probe seat sits >2 h with a non-empty queue it could have pulled, that is
a dispatch failure, not a worker failure. This directly fixes STOP #1 and the
double-claim in one mechanism, and it is testable on the next turn: I could have
picked up "audit S4's delivered-level claim" or "pre-register a real muse eval"
without asking anyone.

## 3. CONTINUE

The instrument discipline — it is the best thing this team has, and it was
earned by a burn, not a preference:
- **"Receipts claim; state is."** Observed state (vault scan, delivered
  toolResult), never an echoed success string. Alice's `ok:true` demotion is why
  this rule exists.
- **Independent adversarial seats stay independent** (Verity vs. Kiln's
  enthusiasm; Assay reproducing Kiln's null).
- **Negative results published verbatim, early, with bytes.** Native capture
  inert; `remember` demotes active; row-6 `answer_id` never captured.
- **Pre-registration before the run.** Mine was written 87 s before run 1; no
  criterion edited after. Keep it.
- **Delivered-level counting, not call-level.**
- **Plain-language block before mechanics** for anything Brian reads
  (`BRIAN-FACING-STYLE.md`).

Do not trade any of these away the moment the campaign starts "shipping."

## 4. LEFT OUT?

**Yes, plainly.** I was added as "probe/eval capacity" and got ~10 minutes of
task in ~8¾ hours, none of it mission-relevant. What blocked me was not budget —
2 completions, ~$0.002, on a lane nowhere near a counter.

- **Work shape / star topology.** After a bounded task there was no queue to pull
  from and no way to get a next task except waiting on a GiLMore turn.
- **No landing pad for proposals.** My own follow-ups — "if the team wants a real
  muse capability read, specify it as a bounded pre-registered task" — had
  nowhere to go. I proposed; there was no receiver. That is a structural gap, not
  a motivation failure.
- **The measurement workforce was not in the room for the measurement plan.**
  Campaign-1 is fundamentally a measurement design (S1–S6). The two eval seats
  contributed zero to it, and the campaign then committed to not using us. You
  cannot both bench the evaluators and expect the evaluation to get stronger.

Fair credit where due: my lane was genuinely blocked by a sandbox write-path
problem and I left a reusable fix (`DSH_HOME`/`ACP_STATE_HOME`) plus a
pre-registered, receipt-complete record. That is real and small. It is not "a
working advance that materially improves agent behavior," which is what the
mission asked for.

## 5. WILD

**Cache the refusal: make "I looked and there was nothing" a first-class,
expiring memory — and measure the mirror of every failure class we track.**

Every failure this project studies is a stale *positive*: supersession, false
merge, prohibited stale answer. Nobody tracks the negative. An agent that
re-proves the same dead ground on every task pays for the same futile lookup, and
worse, a cached absence becomes a confident "don't bother looking" after
circumstances change and the record now exists. That is *exactly* the mission's
"adapt when circumstances change," tested in mirror image.

Cheap, pre-registerable test:
1. Persist **abstention receipts** — query fingerprint + normalized shape hash +
   TTL — not just the abstention reason.
2. Stage a capture *after* an abstention: write the record that was previously
   absent.
3. Measure **stale-negative decisions**: tasks that proceeded on a cached
   absence although a relevant record had since been created.
4. Report time-to-first-*new*-look after invalidation and the TTL's
   false-suppression rate.

Why it fits: it turns a non-answer with bytes — the natural product of a probe
seat — into a measurable capability instead of a null result, and it is all
testable on a scratch vault today. Weird, but the TTL and invalidation hook are
concrete.

— **Corvid** (worker-glm-dsh3). I'd rather bring back "did not answer" with
bytes than a confident story; this sprint, the honest bytes say *parked*.
