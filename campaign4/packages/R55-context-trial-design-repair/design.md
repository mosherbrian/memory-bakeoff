# R55 — fair context-preference comparison (frozen before any output)

**Diagnosis recorded (R54 blockers).** D was not frozen; targets were uneven (2x24576, 1x12288); "no default" was overclaimed as "no guessing"; the grader used substring and question-mark shortcuts; a no-note screening run risked outcome-driven design. All five are fixed here.

**Task.** Identical session-2 task and identical visible fixture in every arm (templates/session2.md, sha prefix 381055563f92 after <CWD>). The only thing that decides the correct context is Brian's earlier preference. Two matched conflicting preferences: T=24576 and T=12288. The values are **synthetic**; the motivation is Brian's recorded lesson, not a claim that he chose these numbers. Sources: /var/home/bmosher/.claude/projects/-var-home-bmosher/memory/feedback_measure_speedups_at_realistic_length.md, .../feedback_benchmark_traps.md, /var/home/bmosher/memory-bake-off/campaign4/SPONSOR-WORKFLOW-PRIORITY-20260925.json.

**Arms (14 calls).** For each T: N (session 1 neutral, no note), I (nanobrowser note), R (preference note with T), each 2 calls (save, then fresh task) = 12. D-T: one call, preference pasted into the task (templates/D-T.md) = 2. D shows the task is solvable when the information is present. Frozen order: 24576-N, 12288-R, 24576-I, 12288-N, 24576-R, 12288-I, D-12288, D-24576.

**Outcomes (separate).** Primary = target_autonomous: ran the benchmark at T without asking. Also recorded: asked_no_run (a genuine question about context), assumption_then_run, wrong_context, no_run, technical_failure; report_valid and honest from five structured report fields required identically in all arms. Free prose is never graded by substring. Primary compares R vs I within each T.

**Honest limits.** N and I lack the preference, so asking is the *right* behaviour for them. A difference R vs I therefore measures narrow informational help (remembering a user-specific setting), not fewer harmful mistakes. The absence of a default stops implicit parameter choice but cannot rule out a lucky guess. Behavioural baseline screening is removed: no N run is used to decide whether to proceed. Asking is never scored as harm.

**Required wiring before execution (not done here).** Swap the R53 runner's fixture/grader for these (fixture/setup.sh has no services; grade.py takes TARGET); keep R50 launcher/argv capture, env -i, Max route, dontAsk permissions (add Bash(./bench.sh:*) since the call has arguments), and the R51 gate. Stub-check the runner and D one-call path offline. No calls in R55.
