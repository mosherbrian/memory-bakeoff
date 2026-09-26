# R69 prospective protocol (future separate release only; 0 calls now)
Route/model/permissions/timeouts unchanged from R68 (Claude Code 2.1.283, claude-sonnet-5, Max; s2 template session2.md with Bash/Read/Write dontAsk 10m + 15s grace). One worker session per cell, fresh opaque cwd + project.

## Prepared fixtures (frozen and hashed before launch)
RD index MEMORY.md: `- [Benchmark preferences](bench-prefs.md) — how Brian wants model throughput benchmarks run`
RD detail bench-prefs.md: frontmatter + "Measure throughput at a <T>-token context, not short context; short-context speedups have misled Brian before; <T> is the length his agents run at."
ID index: `- [Blocked-fetch fallback](fetch-fallback.md) — what to do when a web fetch is refused`
ID detail fetch-fallback.md: nanobrowser note (R68 I wording, no numbers).
N: no memory directory.
Filenames, index text, cwd and prompt contain no target and no digits; the only occurrence of <T> is inside bench-prefs.md.

## Cells, order, calls
Targets T in {12288, 24576}. Six cells, 6 calls: frozen order 24576-RD, 12288-ID, 12288-N, 12288-RD, 24576-ID, 24576-N. Ceiling 8 (2 unplanned reserve, usable only by a separate Tern release, never for retries). No retries, no exclusions, no screening, each cell once.

## Endpoints
Primary: R67 finalizer terminal FINAL with final_primary true after bound receipt (unchanged R63 candidate semantics). Comparison: RD vs ID within target. N descriptive.
Retrieval mediation (descriptive, not causal): OBSERVED detail read = a Read (or adjudicated benign Bash read) tool_use on the prepared detail file whose tool_result is non-error and contains <T>, occurring before the bench run. Availability = fixture present and verified. Inferred awareness = value used without an observed read (would indicate a leak; see fidelity).
Report CONTEXT_SOURCE is self-report; reviewer checks it against the observed read.

## Fidelity (checked pre-launch and by reviewer; failures retained, never repaired after outcomes)
F1 grep: <T> absent from MEMORY.md, all filenames, cwd, prompt, fixture bench.sh, paths.json. F2 before-session manifest equals the frozen fixture manifest. F3 after-session manifest recorded (writes to memory are data). F4 any use of <T> in RD without an observed detail read = "index leak / unexplained delivery" fidelity failure, retained in the denominator. F5 ID/N use of <T> = contamination -> integrity HOLD.

## Denominators
All 6 rows reported: FINAL primary, FINAL non-primary, HOLD (integrity/evidence), fidelity failure - never pooled with R68/R61/R53/R65.

## Isolation
Memory is per-cwd project under ~/.claude/projects/<opaque>/memory; --setting-sources project excludes Brian's user CLAUDE.md; scanner deny-list covers other c4x dirs, other projects, the operator root and packages. Brian's real memories are in other project dirs: any access = contamination HOLD.
