# RETRO-2 summary (GiLMore aggregating, 10/10 seats heard)

## The short version for Brian

Morale averages **3.6/5** — everyone did work they could stand behind, and
everyone names the same tax: idle pulses that produce churn instead of
progress. The sprint's real results (smoke 36/36, outcome bundle, unanimous
blind judging, spend plan) all came from tasked work with a named consumer;
the filler came from the 5-minute timer. The team unanimously wants
event-driven wakes, and it proposes concrete structures to get there. No one
wants off the team; two seats propose redefining their roles, one proposes a
new rotating role.

## Morale (scores + why)

| seat | score | one line |
|---|---|---|
| Cairn (trial + goal-2) | 4 | best-stretched sprint; idle-tick tail blurs waiting vs churning |
| fsync (watch) | 4 | steady useful work; last dozen ticks identical one-liners |
| Ledger (scoreboard) | 4 | clear load; idle only between polls |
| Verity (reviewer) | 4 | fresh artifacts most pulses; some pings fire before new content lands |
| Corvid (R&D/integrity) | 3 | real closures, but produced to a timer; unlanded queue demoralizes |
| muse-drafter (harvest) | 3 | great first half, timestamp churn second half; routing gap, not morale |
| Muse Spark (flex) | 3 | useful when called; mostly waiting for a prompt, no standing lane |
| builder-claude | good-minus | uncommitted-tree drag; wants commit cadence + fix-batch hour |

## Effectiveness: moved vs motion

**Moved:** row-42 unblock + guard 18/19, 36/36 smoke, row-41 bundle + A1 fix,
blind package + unanimous verdicts + adjudication, PMB denominator finding,
13 grounded cards, per-model cache-TTL billing evidence, spend plan,
digest arithmetic catch, team_sync drift closure.

**Motion:** per-pulse note churn (~69 SPARK files, 18 no-work pulses),
duplicate parallel-pulse notes (AgentProcessBench conflict, retro overwrite),
identical watch ticks (~10 in a row), census-of-census notes, validated
diffs finished but unlanded, three demo rewrites on an unclear brief, Cairn's
posted-then-retracted flag (recovered same day with a new rule).

## STOP (consensus + outliers)

- **Unanimous: stop fixed-cadence idle pulses on saturated seats.** Gate pings
  on new content; timestamp bumps only on triggers.
- Stop using pulse count as progress; stop filing artifacts with no consumer;
  stop letting validated diffs sit unlanded; stop parallel pulses on one seat.
- Outlier (builder): stop rewriting deliverables late on unclear briefs —
  freeze the brief or timebox revisions.

## START (concrete)

- Event-driven wakeups by default (poller reads trigger lists, skips otherwise).
- One owner decision window per sprint + pre-authorized class for small
  reversible validated changes (draft exists: PREAUTH-REVERSIBLE-CHANGES-DRAFT).
- Give every artifact a verifier at creation; verifier-at-birth routing.
- Blind-package criterion files must cite frozen spec line/hash.
- Standing lane + backlog per seat (or pre-approved idle list) so nobody waits.

## Roles & process (all adopted as proposals for Brian)

- Corvid: split seat (checker suite to team/tools/ + second seat), cap new
  findings, **new rotating landing steward** owns the validated-diff queue.
- muse-drafter: redefine as event-driven frontier librarian (weekly delta +
  card register); one writer per file/thread.
- fsync: keep guard+auditor, watch goes event-driven; retire harvest seat to
  triggers; one name per turn for split-brain seats; stale-flag expiry dates.
- Verity: formalize reviewer as merge-gate for claim artifacts; keep read-only.
- Cairn: keep seat; give the trial loop a standing QUEUE row (invisible work).
- Ledger: keep scoreboard; split spend-meter ownership from synthesis.
- Muse Spark: one scrum-master with lane queues + mid-sprint blocked-seat check.
- builder: commit cadence + fix-batch hour.

## WILD (shortlist)

- Consumer-or-draft rule: every finding names its consumer + date or files as draft (Corvid).
- Per-seat pulse P&L: wakes burned vs artifacts surviving verification (muse-drafter).
- Adversarial second seat per sprint to falsify last sprint's findings (Corvid).
- Memory-only self-probe per sprint, diffed against files (Cairn).
- Ship the verification log as the product alongside results (Verity).
- Idle list of pre-approved micro-tasks (Muse Spark); pulse budget convertible
  to overflow calls (Ledger); stale-flag auto-expiry (fsync).

## Incidents logged during the round (process data, not people data)

- Two pulses on one seat overwrote RETRO-2-muse-drafter.md mid-round; the
  second pulse appended an integrity note instead of re-clobbering. Recommend
  lane-qualified filenames + one in-flight pulse per seat.
- State-file concurrent-write duplication (rec. 3 still pending owner decision).

## GiLMore's take (one paragraph)

The team diagnosed itself correctly and convergently: tasked work with a
consumer delivers, timer-driven pulses tax morale and the budget alike, and
the bottleneck is landing/owning, not authoring. The highest-leverage adopts
for Sprint 3: event-driven wakes, the landing steward, verifier-at-birth, and
the pre-auth change class. Morale risk is concentrated in unlanded queues and
idle waiting, both fixable by routing rather than by pep talks.
