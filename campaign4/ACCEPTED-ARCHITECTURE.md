# Campaign 4: bounded research, predictable execution

**Goal:** Find a small, reversible memory aid that improves Brian’s work in Claude Code and Pi across compaction and restarts.

**Operating principle:** An authorized work package runs through its handoffs unattended. Finishing it does **not** authorize starting another package.

Research proceeds without waiting for the new controller. Machinery earns its place by reducing operational failures and human babysitting.

## 1. Keep research and machinery separate

**Research track:** Run the authorized cairn pilot—two plumbing pairs, then eight scored memory-on/off pairs. Freeze the treatment, measurements and resource limits first. Measure task errors, repeated discovery and whole-task cost.

**Machinery track:** Build only the controller needed to execute a bounded package reliably. Give this engineering work its own fixed time/spend allocation before starting.

The pilot can use a manual execution path with the same contracts and receipts. It does not depend on completing the controller, database or dashboard.

Use a fresh agent-deck profile, not a reinstall. First inspect which native capabilities already cover launch, identity, status and stopping. A profile isolates only what that inspection confirms; shared services and hooks remain explicit.

Preserve both research repositories and their evidence by location and commit.

## 2. Assign roles and authority

These are responsibilities, not necessarily permanent agent processes.

| Role | Responsibility | Output |
|---|---|---|
| Director—Tern | Choose useful questions, propose packages, interpret findings | Work proposal, research disposition, roadmap update |
| Contract reader | Check that the proposed contract measures the intended question | Acceptance or one bounded rejection |
| Worker | Execute within the accepted contract | Artifact, results, raw evidence |
| Independent verifier | Reproduce or assess the work, then compare claims | Verification receipt and any discrepancy |
| Controller—software | Enforce authorized transitions, limits and handoffs | Dispatches, event records, current status |
| Duty owner—proposed: overseer | Handle operational blocks and overdue work | Resolution, deferment or escalation |
| Brian | Decide changes requiring his authority | Scope, budget or permission decision |

The overseer may stop overdue work, reconcile processes and resume eligible work within existing authorization. It may not change the research question, increase budgets or authorize another package.

Tern handles research interpretation and amendments. Brian is not the default operational fallback.

**Independence rules:**

- Worker and verifier must differ.
- Contract author and contract-validity reviewer must differ.
- The contract reader may subsequently verify execution.
- Someone who materially repairs a contract cannot independently certify that repair.
- Substantive disputes receive a bounded independent disposition, not unlimited review rounds.

These assignments and permissions must be explicitly accepted before unattended operation.

## 3. Use one compact work-package contract

The normal author-facing contract is:

```text
Task or question—and the decision it informs
Inputs and expected output
Completion check or named judgment reader
Worker, verifier and duty owner
Time/spend limits
Permitted data, tools and writes
```

The controller generates IDs, timestamps and hashes. Standard environment settings and limits can be inherited from named, versioned defaults.

Additional requirements depend on the work:

| Work type | Additional contract |
|---|---|
| Experiment | Metrics, controls, thresholds, exclusions and comparison method |
| Implementation | Required behavior, regression evidence and permitted changes |
| Judgment | Named reader, bounded effort and required disposition |
| Higher-risk action | Explicit permissions and recovery requirements |

The Director proposes the type; the contract reader checks it once. There is no bespoke schema or gate-authoring exercise for each package.

**Admission produces either an accepted contract or a bounded explanation of what is missing.** Judgment work remains visible alongside mechanically checked work; it does not acquire an artificial numeric success criterion.

## 4. Execute a complete, bounded lifecycle

| State | Exit condition and next state |
|---|---|
| **DRAFT** | Contract reader accepts → ADMITTED; otherwise return one bounded rejection |
| **ADMITTED** | Authorization and versioned contract recorded → REGISTERED |
| **REGISTERED** | Controller records start before dispatch → RUNNING |
| **RUNNING** | Required artifacts published → CHECKING; interruption → BLOCKED |
| **CHECKING** | Evidence satisfies contract → COMPLETE; eligible implementation defect → REPAIR_ALLOWED; impediment → BLOCKED |
| **REPAIR_ALLOWED** | Record repair allocation and launch → RUNNING |
| **BLOCKED** | Recorded resolution → previous eligible stage; otherwise defer, terminate or exhaust |
| **COMPLETE / EXHAUSTED / TERMINATED / SUPERSEDED** | Terminal for that revision |

One initial execution plus one repair is the default package budget. Each execution and verification activity also has a deadline and resource limit.

Resuming blocked work preserves attempt history and cumulative spending. It does not reset budgets or erase a spent attempt.

### Amendments

Changing the question, population or acceptance criteria creates a new revision:

```text
Old revision → SUPERSEDED
New revision → DRAFT → admission and authorization
```

Preserve old evidence and link the revisions. Question-level cost history survives renaming and amendment. No retroactive change turns an earlier failure into a pass.

### Completion is not success

Store workflow status separately from research outcome:

- `COMPLETE / negative finding`
- `COMPLETE / positive finding`
- `EXHAUSTED / inconclusive`

A valid negative experiment finishes the job. Invalid measurements do not become scientific nulls merely because execution ended.

## 5. Give each fact one authoritative home

SQLite is the proposed controller store; immutable directories hold execution artifacts.

| Information | Authority |
|---|---|
| Authorization, lifecycle, budgets and execution identity | Controller event ledger |
| What an attempt produced | Immutable, hash-addressed artifacts |
| Code and research inputs | Named source repository and pinned commit |
| Dashboard and summaries | Derived views—not independent state |

The controller records actor identity from the launcher, not from an agent’s self-description. Each attempt has linked start and end events, with its inputs, runner version, output hashes, deadline, cost and reason for ending.

Artifacts are published before recording transitions that depend on them. After a crash, unreferenced artifacts are recoverable leftovers—not proof of completion.

**On disagreement, do not overwrite one source with another.** Missing artifacts or mismatched hashes block the affected claim and produce an owned integrity issue.

A shared pending-decision record contains the exact question, owner, affected packages, deadline and source-linked resolution. Resolving it updates its dependents.

## 6. Build the controller as a small execution system

| Component | Function |
|---|---|
| Transition core | State + event → next state and permitted actions |
| Persistence | Transactional events, receipts and budget accounting |
| Agent-deck adapter | Launch, inspect and stop authorized attempts |
| Supervisor | Detect overdue or missing completion and apply authorized responses |
| Read interface | Status, evidence links, costs and pending decisions |

Use Go if that remains the agreed implementation choice. The transition core contains no model calls; it consumes recorded agent and human dispositions.

Use idempotent action IDs. On restart, reconcile recorded attempts with actual processes before dispatching or retrying.

The supervisor’s own liveness and recovery ownership must be assigned. Detection alone is not enforcement.

## 7. Build and validate without delaying research

| Stage | Machinery output | Acceptance evidence |
|---|---|---|
| Inspect | Native-capability and shared-resource map | Identify what can be reused and what is genuinely missing |
| Specify | Compact contracts, transition table, named ownership | Walk successful, negative, blocked and amended examples |
| Implement core | State handling, receipts, limits, fake executor | Transition, duplicate-event, crash and timeout tests |
| Connect | Agent-deck execution and verifier handoff | Harmless fixture completes unattended |
| Expose | One status view and pending-decision list | Injected failure appears with correct owner and next action |

The cairn pilot proceeds on the manual path while this work runs. At the engineering budget boundary, demonstrate the available capability and stop expansion pending an explicit decision.

Before unattended use, demonstrate that:

- Restart cannot duplicate execution.
- A hung attempt reaches an enforced, owned disposition.
- Workers cannot verify their own artifacts.
- Input changes invalidate affected registrations.
- Repair exhaustion stops further automatic attempts.
- Pending judgments visibly block dependent work.
- Evidence remains recoverable after interruption.
- Routine handoffs do not require Brian.

## 8. Make usefulness and overhead visible

One page should show:

- The project goal and conditional path: **local pilot → actual compaction/restart tests → representative work**.
- Current packages, owners, limits and blockers.
- Findings established, approaches retired and decisions changed.
- Exact questions requiring Brian.
- Research execution, verification, machinery maintenance and human interventions—including failed attempts.

A controller has not earned adoption merely because it runs. It must reduce handoff effort and operational failures within its agreed budget.

Loop changes receive evidence appropriate to their class. Bug fixes should demonstrate the intended regression against the parent; refactors and maintenance need suitable checks rather than artificial failing tests. The candidate implementation cannot approve itself. Emergency changes require an explicit authority, recovery owner and tested rollback or safe-stop procedure.

**Campaign 4 succeeds when useful research advances visibly with little supervision—not when we finish building a fleet platform.**