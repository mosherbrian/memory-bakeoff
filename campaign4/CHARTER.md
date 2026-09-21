# Campaign 4 — charter and authorization

**Authorized by Brian, 2026-09-21.** This file records what was granted, to
whom, and where it stops. It is the authority every work package points at.

**Goal (Tern's, adopted):** find a small, reversible memory aid that improves
Brian's work in Claude Code and Pi across compaction and restarts.

**Today's scope is the machinery only.** No memory bake-off research runs today.

**Operating principle:** an authorized work package runs through its handoffs
unattended. Finishing it does **not** authorize starting another package.

## Assignments

| Role | Seat | Lane |
|---|---|---|
| Director | **tern** | `acp-oai-worker` — gpt-6-astra via Codex |
| Contract reader | **corvid** | `acp-go-deepseek` — DeepSeek via OpenCode Go |
| Worker | **kiln** | `acp-go` — Muse Spark 1.3 contributor via OpenCode Go |
| Independent verifier | **corvid** | same seat, different role |
| Controller (until the software is dogfoodable) | **cairn** | `acp-pi-worker` — local Qwen3.8-27B |
| Duty owner | **cairn**, escalating to **tern** | |
| Sponsor | **Brian** | decisions requiring his authority only |

Profile: `agent-deck -p campaign4`. Four seats, created 2026-09-21.

**Note on kiln:** it was *not* re-pointed. Brian's assignment said Muse Spark and
kiln already runs `muse-spark-1.3-contributor` over OpenCode Go. Moving it to
`acp-muse` would have dropped it to the free tier. Left as is; this corrects a
wrong premise in the question that was asked.

**plumb-fable is retired.** It is not in this campaign.

## Independence rules (Tern's, binding)

- Worker and verifier must differ.
- Contract author and contract-validity reviewer must differ.
- The contract reader may subsequently verify execution.
- Whoever materially repairs a contract cannot certify that repair.
- Substantive disputes get one bounded independent disposition, never unlimited
  review rounds.

Corvid holds contract reader and verifier. It is neither the author of a
contract (Tern proposes) nor the worker (kiln executes), so both rules hold.

## Authorizations granted

**May, without asking:**

- Commit **and push** to `memory-bake-off` and `conductor-chat`.
- Create, start and stop seats **in the `campaign4` profile**, and write to
  `~/.config/agent-deck`.
- Spend on **kiln** and **corvid** freely — both are OpenCode Go and cheap.

**Requires Tern's approval:** touching anything outside those two repositories
and the agent-deck config.

**Requires Brian, and stops until he answers:**

- **Tern's Codex usage running out.** Tern is the only seat whose spend is a
  concern. *If Tern's usage is exhausted, stop and wait for Brian to intercede.*
  Do not substitute another model for the director.
- Anything Tern judges she cannot reasonably decide.

## Budgets and stop rules

| | |
|---|---|
| **Machinery** | today, until Brian stops it |
| **Research** | **waits** for the plumbing — unless the plumbing build can capture genuinely useful data at little extra cost, which Tern decides |
| **Tern / Codex** | run as needed; **on exhaustion, stop and wait for Brian** |
| **kiln, corvid** | no ceiling; cheap by construction |

## Decision authority

**Tern decides almost everything**, including research interpretation and
amendments. She does not need Brian for ordinary calls.

**Standing instruction from Brian, 2026-09-21:** At each terminal package
boundary, Tern opens and explicitly authorizes a warranted successor herself,
or records that none is warranted and why. She reports; she does not ask for
routine boundary permission. Finishing a package is still not authorization
for another: the separate authorization is Tern's decision within this
charter. If uncertain whether a routine boundary is hers, the default is yes.
The two hard stops below remain unchanged.

**If Tern judges she cannot reasonably decide: pause everything**, write the
exact question, the options and their consequences to `pending-decisions.md`,
and notify Brian. Do not pick the reasonable-looking option and continue. A
paused campaign is a correct outcome; a guessed decision is not.

## Controller constraint

**Cairn dispatches only when woken. It never polls.** A local 27B running a
dispatch loop previously made 92 real dispatches out of 23,793 calls and slowed
the shared inference box from 65 to 671 seconds per document. Authorized by
Brian as a standing guard, not a preference.

Cairn may stop overdue work, reconcile processes, and resume eligible work
inside existing authorization. It may **not** change a research question, raise
a budget, or authorize another package.

## What is switched off, and stays off unless a package says otherwise

`fleet-poller`, `sprint-next`, `gate-batch`, `fleet-window-up`,
`agent-deck-failover`, `fleet-stalled`, `poller-liveness`. Campaign 3's loop is
not part of campaign 4.

## Success

Campaign 4 succeeds when useful research advances visibly with little
supervision — not when a fleet platform is finished.
