# EXPERIMENT-20260911 — TRIAL-20260911 real-usage experiment (pre-registration)

**Frozen before the first evaluated cycle** (house rule: freeze before
evaluation). This file is the pre-registration; it is committed before any
evaluated cycle runs, and evaluated cycles start only on the conductor's go
after this freeze.

## Window

10 confirmed decision cycles OR 3 working days, whichever first. Brian may
stop anytime (kill switch `PI_PERSEUS_RECALL=0`; or he just says stop).

## Tasks

REAL work only, in `~/acp-pi` (worker-pi's own tree). Sources:

- conductor-dispatched chores that the experiment itself needs (ledger
  tooling, workspace docs),
- any tasks Brian drops directly into the thread.

No synthetic demos.

## Metrics (verbatim from docs/TRIAL-20260911-runbook.md §3)

Recorded per draft/turn; all **exploratory**, no causal claims:

| Metric | Definition |
|---|---|
| drafts raised | count of `notifications.jsonl` lines |
| recall deliveries | `project_perseus_recall` calls whose toolResult carried ≥1 record (session log) |
| confirm latency | draft timestamp → Signal send timestamp → operator confirm (confirm tool receipt time) |
| overhead vs no-memory turn | wall + tokens of a memory turn vs a comparable no-memory turn (pi session logs; descriptive pairing only) |
| stale-action events | acting on a superseded record — **target 0** (the whole point of supersession) |
| TTL expiry events | drafts never confirmed before `expires_at` |

Small-n honesty: this is a plumbing + shape trial on one worker and one
operator. It can show the loop closes and what it costs; it cannot show
that decision memory improves worker performance.

## Decision rules (descriptive, small-n — no causal claims)

- **Loop reliability:** every draft detected + summoned within 5 min +
  resolved (confirmed or expired) — target 100%, count misses.
- **Recall usefulness:** in stored-record-relevant turns, worker retrieves
  and applies unprompted — descriptively reported (x/y).
- **Stale safety:** stale-action events = 0 (target; any occurrence is
  reported prominently).
- **Burden:** confirms/day vs the proposal's 1–3/day estimate; Brian marks
  each prompt clear/unclear (finding-classification, per finding #1).
- **Overhead:** memory turn vs comparable no-memory turn (wall + tokens;
  pre-trial turns as baseline pairing) — report, flag if beyond +25%.
- **Supersession:** at least one deliberate convention change during the
  window → worker should draft a supersede; recall thereafter delivers
  current-only. This is the EXPLICIT_LINEAGE production test.

## Roles

- **Conductor:** dispatches tasks + monitors the notify file
  (`/home/bmosher/acp-pi/notifications.jsonl`) + sends the Signal summons.
- **Brian:** confirms (his latency + clarity ratings are data).
- **Reviewer (flash):** audits ledger-vs-claims at window end.

## Budget

worker-pi is local/free; conductor + reviewer on flash (free); Brian's
attention is the real cost — capped by the stop rule.

## Pre-freeze cycles (labeled as such; not evaluated)

- **task 1** — workspace + conventions record (plumbing cycle),
- **loop test** — probe draft (plumbing cycle),
- **finding #1** — draft-presentation clarity fix (presentation discipline,
  runbook-only).
