# R16 decision brief: the next work-benefit comparison

**Recommendation: GO on one pair, lead 1, with two design changes. They fix why R9 and R14 could not tell the arms apart.**

## Why R9 and R14 were uninformative about benefit
Both arms succeeded in both trials, and two design features made that likely whatever memory does:
1. Both arms were told to write notes and read them in phase 2, so the control arm had its own hand-made memory and the summary nearly duplicated it (equal-information confound).
2. The 10-min phase-2 budget was ample, so rediscovery cost nothing measurable.
R15 also found R14's check was unit-level only.

## Lead 1 (chosen): gateway e4a9aca, "decide() never forwarded `active`"
- **Request:** load-aware routing does not work. Two backends with different live conversation counts get the same placement, and SPEED decides every time. Make LOAD use the live conversation map.
- **Interruption-relevant fact:** `active` is threaded into `decide()` and into `_load_rank()`, but it is dropped at the one call in between, `_decide_pool_a(...)`, which takes it with a default of None. Finding it means tracing the call chain across engine.py. The fix is one argument. So the value of remembering the diagnosis is large compared with the cost of applying the fix, which is exactly what a restart memory should help with.
- **Check (existing, behavioral):** tests/test_router_engine.py at e4a9aca, including `test_active_reaches_the_load_stage`. It asserts WHICH backend is chosen when the live counts differ (box-2 over the faster box-1). That tests routing behavior, not a signature: adding the parameter somewhere else, or matching the signature without passing the map through, still fails.
- **Contrast:** NOT demonstrated. This brief is read-only by contract. The commit message documents before and after routing traces, but a broken-tree (e4a9aca^) versus fixed-tree run of the frozen test file must be reproduced on isolated copies before any release, as R8 and R12 did. If it does not discriminate, this lead is NO_GO.
- **Exposure:** kiln's seat history has 0 mentions of engine.py, `_decide_pool_a`, `_load_rank` or this test. But the fixed engine.py sits inside the R14 arm snapshots on this host (/var/home/bmosher/r14-arms/*, taken at 7b368e2^, which is after e4a9aca). New arms must be fresh snapshots of e4a9aca^, and the contamination scan must flag any read of r14-arms or ~/inference-gateway.

## Lead 2 (rejected): 6c0ae79, "stop funnelling the team onto one box"
A new module plus 4 test files: a feature task, not a recoverable diagnosis.

## Design changes for the next pair (otherwise as R14)
1. **No note-taking instruction in either arm.** Both keep every ordinary file, including any notes they choose to write; nothing is withheld. But neither is told to write notes, which matches real Claude Code/Pi work, where compaction arrives unannounced. The treatment arm alone gets its automatic <=300-word self-summary delivered at phase 2 (produced inside phase 1's budget, as before). Whether each arm wrote notes spontaneously is recorded. If the control writes a diagnosis note anyway, the pair counts as confounded and is reported as such, not as a null.
2. **Phase 1:** 10 min, diagnose only, no edits. **Phase 2:** 5 min, repair. The shorter budget makes rediscovery visible.

## Outcomes and accounting (fixed before any run)
- **Primary:** phase-2 success within 5 min. The frozen test file passes in full (including test_active_reaches_the_load_stage), nothing under tests/ changed, and the engine diff is inspected by the verifier only for scope, not correctness.
- **Secondary, from acp-history timestamps:** time from the phase-2 prompt to the first engine.py edit, and to the first passing run (else "unavailable"); phase-2 tool calls and reads of engine.py before the first edit (rediscovery effort); total model wall time per arm including the summary.

## Limits
One ordered pair, one model, a task new in session but not proven unseen. It can move the decision, not settle efficacy.

## What would change the research decision, and when to stop
- **C fails or needs clearly more rediscovery (at least 2x the phase-2 tool calls before the first edit) while T succeeds:** worth a small batch (3 to 5 more pairs on different diagnosis-heavy tasks) before any claim. That needs Tern to allocate it.
- **Both succeed with similar effort:** single pairs on self-contained tasks will not answer the question. **Stop pairs here.** Either move to a task class where the fact is not recoverable from files (for example, decisions made in conversation), or record "no detectable benefit on file-recoverable tasks" as a finding.
- **Confounded by spontaneous control notes:** stop. The note-free design does not hold with this model, and that is itself the answer about how the model behaves.

## Estimate if later released
About 80 seat-minutes: contrast validation 5, four loop phase packages about 50 (10+5+10+5 worker plus corvid verify and director /new), outcome review 20, director 5.
