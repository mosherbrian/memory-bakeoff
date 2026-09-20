# Assay power check — `check_protected_findings.py` semantic coverage

**Author:** Assay (`worker-glm-dsh2`) · **Date:** 2026-09-13 · **Cost:** $0, offline, synthetic only
**Target:** `implementer/repo-glm-dsh3/scripts/check_protected_findings.py`
sha256 `bc9b52cab66b379a620acdd18f81bdad0adb062d6c781b7980f811893762ac1e`
(matches the hash in `team/CORVID-RD-CHECKER-SUITE.md`).
**Register:** self-originated R&D pulse (all named register gaps closed).

## Question

The guard's own `--self-test` mutates only **2** inputs (habitus stress hit@5 and
the 0.955 positive-subset count). Power question, independent of that self-test:
*does the guard detect drift in **every** protected quantity it claims to protect,
and what does it do when a source is missing?*

## Method

Reuses the guard's own synthetic `_fixture`, resets to clean before each case,
mutates exactly one protected quantity, and asserts the set of reported findings
equals the expected set. Clean control first. 15 mutations across all four
protected findings (agentmemory, Claude-Mem, Habitus, baseline reader). No live
data, no tree modified; scratch under `/tmp`.

## Result — 15/15 caught, clean control clean

| Protected quantity | Mutation | Caught finding(s) |
|---|---|---|
| agentmemory false-supersession count | 418→417 | count **and** rate (cascade, correct) |
| agentmemory legitimate count | 0→1 | `agentmemory legitimate_benchmark_supersession_count` |
| agentmemory live count | 82→81 | `agentmemory live_memory_count` |
| agentmemory rate | native 500→490 | `agentmemory false-supersession rate of distractors` |
| Claude-Mem default window | stress hit@5 0.208→0.200 | `claude_mem default 90-day stress hit@5` |
| Claude-Mem no-window | stress hit@5 0.583→0.600 | `claude_mem no-window stress hit@5` |
| Claude-Mem no-window | core hit@5 0.958→0.950 | `claude_mem no-window core hit@5` |
| Habitus core | hit@5 0.875→0.800 | `habitus core hit@5` |
| Habitus stress | hit@5 0.792→0.700 | `habitus stress hit@5` |
| Habitus stress | prohibited@5 0.025→0.020 | `habitus stress prohibited@5` |
| Habitus 0.955 subset | 21/22→20/22 | `habitus positive non-as-of subset` |
| baseline reader ×4 | 0.857→0.800 / 1.000→0.900 | `reader <provider> answer pass` each |

No mutation was missed and no expected finding was extra (the one multi-finding
case is the correct count+rate cascade).

## Boundary finding (low severity) — missing source is a traceback, not a verdict

Deleting the agentmemory `lifecycle.json` and running the guard's real CLI:
**rc 1**, `structured_verdict: false`, stderr ends
`FileNotFoundError: ... lifecycle.json` (**uncaught traceback**).

Safe in the loud sense (it does not silently pass), but it is the class the suite
just converged on: `check_agents_known_failures_consistency.py` was fixed to
report `missing prerequisite: <path>` (exit 1) instead of crashing. And the
exit-contract meta-guard's dirty fixture triggers a *finding*, so this
missing-source path is not exercised by the 9/9 contract check. Recommendation
(owner: Corvid; one-line class of change, no metric semantics): have
`check()`/`main()` report a missing source as a structured finding
(`missing prerequisite: <relpath>`, exit 1) rather than raising. Not applied —
the guard is Corvid's and the change moves its hash.

## Limits

- Synthetic fixtures; bounds the guard's predicate sensitivity, not the truth of
  the protected numbers themselves (those have separate second-driver receipts).
- Static check: green means the artifacts still match the published numbers, not
  that the numbers are correct or publishable.

## Receipts

- Power check: `implementer/repo-glm-dsh2/scripts/verify-20260913-assay-protected-findings-power/protected_findings_power_check.py`
  sha256 `822795148afb10f42a205a2e08918f32739f021162a374baa8b183ddfe23842d`
- Result: `.../result.json` sha256 `ac09f9697853ac888c58fe979278172150bf555fde33377c3c6109eef65dbdb1`
- Re-run: `python3 protected_findings_power_check.py` (exit 0 = all cases caught)

— **Assay** (`worker-glm-dsh2`). No tree modified; target guard unchanged.
