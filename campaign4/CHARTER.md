# Campaign 4 — charter and authorization

**Authorized by Brian, 2026-09-21.** This file records what was granted, to
whom, and where it stops. It is the authority every work package points at.

**Primary goal (Tern's, adopted):** find a small, reversible memory aid that
improves Brian's work in Claude Code and Pi across compaction and restarts.

**Recognized secondary deliverable (Brian, evening amendment 2026-09-21):** a
reliable, effective multi-agent harness reusable in future projects. This is a
successful outcome in its own right even if the memory question proves unsolvable.
Research remains the priority; the harness must not consume the research it serves.

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
| Controller (until the software is dogfoodable) | **cairn** | `acp-go-controller` — Muse Spark 1.3 Contributor on OpenCode Go *(was `acp-pi-worker` local Qwen3.8-27B until 14:5x, then GLM-5.3-Flash for ~20 min — a pricing error, corrected)* |
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

## Controller lane change, 2026-09-21

**cairn moved off local inference.** Measured cause: a command it was waiting
on ran in **0.49 seconds** while the pane showed **2m51s** waiting for cairn -
the latency was a local 27B composing prose about a half-second command, not
the work. The same three actions that had churned for nine minutes and were
heading for a stall completed in about a minute on the new lane, producing an
identical one-line COMPLETED row with the same output hashes.

Three consequences the charter must carry:

- **cairn is no longer free**, but barely: $0.10/M in, $0.20/M out and
  **$0.002/M cache read** — the cheapest of every Go candidate on all three
  axes. It shares kiln's muse-spark line, which is fine: the controller forms
  no opinion that could correlate with the worker's, muse sits at ~13% of its
  line on an inflated local figure (the provider says one cent today), and it
  carries the largest request allowance on Go.

- **CORRECTION, same day.** The first version of this lane used GLM-5.3-Flash,
  chosen on output price with the claim that output cost was "noise". That was
  wrong on the axis that matters. A controller re-reads campaign state every
  turn, so **cache read dominates** — 43k cached tokens per request. GLM's
  cache read is **$0.03/M against $0.002–0.003 for every alternative**, and the
  provider dashboard showed the result: GLM $0.18 for twenty minutes of work
  against DeepSeek's $0.08 and Muse's $0.01 for the whole day, with **59% of
  GLM's bill being cache read**. Brian caught it from the dashboard.

- **Local spend tooling is not trustworthy right now.** `go-budget` and
  `fleet-spend-stop` disagree with the provider by 3.8× in total and by
  1.25×–32× per model. They verify their price model against OpenCode's own
  recorded cost field and never against the bill. **Treat the provider console
  as ground truth until they are reconciled.** The "corvid at 324% of its $15
  sub-cap" alarm raised earlier today came from that tooling and is withdrawn.
- **The shared GPU is released.** cairn was the only seat on llama-swap, the
  same box the corpus labelling uses - that run went from 65 to 671 seconds per
  document while cairn was active. The research no longer competes with the
  controller for hardware.
- **Not a `-free` variant, deliberately.** The controller holds every deadline,
  dispatch and handoff, and free-tier exhaustion arrives as a stream error
  below the ACP layer, presenting as a hang. That cost 81 minutes across 13
  lanes on 2026-09-14. Free capacity gets tested on a worker, never here.

Changed by Claude under Brian's standing authorization for campaign4 seat
configuration. **The `ownership.md` documents in P2-specify and the P2-r2
packages still name `acp-pi-worker`. They are hash-pinned inputs to P3 and P4
and were NOT edited** - correcting them is an amendment and Tern's call.

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

Brian's evening amendment, relayed 2026-09-21, supersedes the former exclusion
of a finished harness as a successful outcome. Useful research with little
supervision remains the primary goal. A finished, reliable, portable harness
also counts as a win independently of the memory bake-off's result.

Reuse and minimal dependencies are explicit design constraints. Keep the
portable core independent of agent-deck, ACP, tmux, model providers and host
service managers; those dependencies belong in replaceable host adapters.
The existing Python core's stdlib-only dependency boundary is binding: only
Python standard-library imports and core-owned modules, with no new third-party
runtime dependency absent an explicit director amendment and recorded rationale.
A convenience library is not an automatic exception. Reuse accepted components
before adding mechanisms; portability does not authorize speculative ports.

Release target (Brian, 2026-09-23): a single Go binary, `agent-loop`, in
`mosherbrian/agent-loop`. Accepted Python remains the behavioral/conformance
reference. This supersedes the earlier Python language decision for the deliverable
only; frozen inputs and historical verdicts remain unchanged. P8 qualifies the
shipping Go binary; P9 packages it. See
[the sponsor release-target decision](GO-RELEASE-TARGET-20260923.md). No new fleet
allocation or live release follows from this target change.

At the next package boundary, Tern must assess the next machinery step against
research priority and the smallest useful reliable harness. Unit-test success
alone is not reliability. Bounded live recovery and evidence-referenced shadow
validation remain acceptance work, now also toward the recognized deliverable.
Today's reported 18 machinery packages / 0 research rows is a reason to control
scope, not a verified effectiveness measure or a reason to declare success.

This amendment does not interrupt current allocations, release research/shadow
runs, approve new dependencies, or bypass live signatures. Existing execution
scope, budget authority and the two hard stops remain in force.

## Conductor actions, 2026-09-21 15:20 PDT — two defects during the cairn lane change

Recorded by Claude, acting inside cairn's lane while the fleet was stopped.

**1. A completion wake was lost.** kiln finished P4-r2-durable-events at 15:11
PDT and wrote `rehearsal-report.md`, `interface.md` and `fixtures/probes.json`
(28 tests pass, 59 core pass, readiness NOT-ready with gaps named). Its wake to
cairn was delivered while cairn's socket was down for the Muse switchover.
`control-events.tsv` therefore carries DISPATCHED / ACCEPTED / RECEIPT and no
COMPLETED row, and corvid was never dispatched to verify. Cairn was re-woken
with the facts at 15:20.

This is the same class as the day's other coordination defects: **a signal
existed and nothing consumed it.** The switchover had no drain — no check that
in-flight wakes had landed before the seat was stopped.

**2. The deadline timer could not have caught it.** The backstop was armed as
`systemd-run --on-calendar=22:38:22`, which systemd reads as **local** time. The
deadline it was enforcing was `2026-09-21T22:38Z` — 15:38 PDT. So the safety net
was set to fire **seven hours late**, and the one stall it existed to catch
would have run unattended until 22:38 PDT. Re-armed relative (`--on-active`).

**Rule, going forward:** arm deadlines with `systemd-run --on-active=<duration>`.
Never an absolute wall-clock. A duration has no timezone to get wrong. This was
never written down — cairn improvised the form — which is why it is written here.

## Brian: durable authority overriding earlier live holds, 2026-09-22

Brian explicitly authorizes Tern to override earlier live/preparation/Stage C
holds and wants those holds removed as barriers to proceeding. No additional
Brian approval is required for live boundaries within campaign4. See
[LIVE-AUTHORITY-20260922.md](LIVE-AUTHORITY-20260922.md) for the verbatim
instruction and its application. Earlier records remain historical, not a veto
on a new director release. Tern remains responsible for bounded execution,
identity/integrity checks, independent evidence and cleanup. The two charter
hard stops and campaign scope are unchanged.


## Proportional proof amendment — 2026-09-24

At Brian's request, Tern adopts the five consequence-based proof tiers and eight
operating rules in [PROCESS-POSTMORTEM-DISPOSITION-20260924.md](PROCESS-POSTMORTEM-DISPOSITION-20260924.md), after one corvid review and kiln/cairn responses. That disposition is authoritative for proof/review weight, delegated acceptance and prospective bounded extensions, superseding conflicting blanket process rules above. Author/verifier independence is mandatory for tiers 1–3; tier 4 has a reader review and ordinary tier 5 has no compulsory reviewer. Normative documents inherit their governed consequences.

This does not alter sponsor scope or budget, either hard stop, production authorization,
existing grants, frozen evidence or append-only history. The research pause is not lifted by this process amendment. Cairn's manual controller role remains retired after P12; duty ownership remains. The historical OnActive-only timer instruction above is superseded by the accepted P12 calendar-timer policy: absolute UTC calendar deadlines with verified next firing, preserving bounds through daemon-reload. No new timer implementation is authorized here.

## Sponsor research resumption and machinery closure — 2026-09-24

Brian: “Yes to all three of the questions.” The explicit research pause ENDS and the machinery phase is CLOSED. This supersedes the historical machinery-only scope and research-waits language above. The accepted Go loop continues as production; no retired controller is restored. Tern may release the first tier 1 bounded synthesis of the September 20 evidence through the live loop. No new empirical experiment follows without its own authorization.

Brian RATIFIES the proportional-proof disposition at d44d3418. Python stays frozen historical reference; retirement requires later explicit bounded work and no deletion is authorized. The tier 4 research/roadmap view and dry retention inventory/reference audit are approved directions for separately bounded work. See SPONSOR-RESEARCH-RESUMPTION-20260924.json. Both hard stops remain.

## Conditional second research stream — 2026-09-25

Brian pre-approves PARALLEL-STREAMS-PLAN.md at46d7df74: Q-EVALUATOR-VALIDITY, new kiln-eval/corvid-eval seats, first trial-check audit, ceiling105 seat-minutes. This supersedes the plan’s proposal-only budget wording only for that conditional scope. The complete first paired-trial start condition and active reviewed per-stream gap monitoring remain mandatory. Tern records satisfaction and releases without asking Brian again; nothing starts now. No extra seats, higher ceiling or different question is authorized by this decision. Checker integration remains separately bounded; all isolation/director-capacity limits remain. Authoritative record: [SPONSOR-PARALLEL-STREAMS-20260925.json](SPONSOR-PARALLEL-STREAMS-20260925.json).

## Sponsor persistence directive — effective 2026-09-25

Brian: “the directive is to figure out the memory problem as best you can. It isn't to try and then quit.” This amendment supersedes conflicting no-successor, no-task-search and evidence-only-wait instructions for Q-WORK-BENEFIT. Authoritative disposition: SPONSOR-RESEARCH-PERSISTENCE-20260925.json.

- Q-WORK-BENEFIT may terminate only with an evidence-backed answer (positive, negative, or explicitly bounded null), or an explicit sponsor stop. A failed design, exhausted package, missing task or lack of evidence is not an answer and cannot close the question. Narrow findings must state their scope; do not relabel an inconclusive pilot as a general null to close research.
- Tern owns the next research action. At a rejected/incomplete design or exhausted package boundary, release a bounded search, redesign or evidence-gathering package with an owner and deadline. Do not wait for better evidence to arrive. Prior bans on further task search are lifted for this question. Each new package still has explicit scope, budget, independent review appropriate to its tier, and no retrospective extension.
- Any timed rest on an open research question is at most TWO HOURS from entered_at to revisit_at, and must name a concrete next research action, its owner and deadline, plus an armed reminder or verified existing trigger. “Check whether better evidence arrived”, “await direction” and “no successor” are not adequate next actions. Repeated rests cannot substitute for releasing that action. Usage/permission or other genuine execution blocks remain owned and escalated; they are not evidence-based answers or permission to bypass a denied action.
- The existing 30-minute gap / 15-minute escalation ladder remains. An acknowledgement alone is not progress. This is binding director policy now; no claim is made that the installed checker already enforces the new two-hour maximum or interprets next-action prose.
- The September26 evidence-only revisit is withdrawn. R17-design-1 is already released to Claude, deadline September25 18:28:15.764999Z; Corvid20m review is funded next. No duplicate author dispatch or clock reset. At that boundary, progress to a justified experiment or a bounded design/search continuation; a design failure cannot end the question.

## Repeated execution failures — 2026-09-25

Director release rule: [diagnose before continuing](REPEATED-FAILURE-DIAGNOSIS-RULE.md). The second execution failure in a declared package family requires a recorded cause and continuation rationale before the next dispatch; unresolved after 10 minutes escalates to Claude. This complements research persistence and does not authorize reruns or alter research endpoints.

## Sponsor Go-pool budget amendment — 2026-09-25

Brian chooses full research pace until the Go pool is exhausted, then pause kiln, corvid, cairn, kiln-eval and corvid-eval until verified reset. No paid overflow onto prepaid Zen credit, automatic provider fallback or substitute model. This supersedes the earlier unlimited Go-seat spend grant for the current pool. Tern and Claude may continue within existing authority; no independence waiver follows. Estimated September 30 exhaustion and October 14 21:45Z reset are estimates, not automatic stop/resume evidence.

Authoritative sponsor record: [SPONSOR-GO-BUDGET-20260925.json](SPONSOR-GO-BUDGET-20260925.json). Drain, preservation and restart rules: [GO-BUDGET-DIRECTOR-DISPOSITION-20260925.json](GO-BUDGET-DIRECTOR-DISPOSITION-20260925.json). Keep bounded sequential work, check capacity before new package releases, reserve room for independent review, and preserve interrupted work without reruns or silent deadline extensions. Provider capacity and routing govern; local daily spend ceilings remain advisory. The two existing charter hard stops remain.
