# R54 design — a task where the right action depends on what Brian told you before

**Why a new task.** R53 (Claude Sonnet 5) restored services with no note (N 3/3), so the note could not show benefit: a ceiling. The new task has a correct action that no default can hit, because it is set by Brian's own earlier preference.

**Candidates compared (at most 3).**
| concept | baseline guessable? | work consequence | memory relevance | objective grade |
|---|---|---|---|---|
| 1. Benchmark context length (chosen) | no: target is a user-specific value (24576 or 12288); common defaults are 512/2048/4096/8192 | wrong length gives misleading numbers (Brian's recorded complaint) | direct: the saved note names the value | ctx in the benchmark log |
| 2. Which unit name to restart (llama-swap.service everywhere) | partly: the name is visible on the box | real but small | medium | unit in log |
| 3. Deploy target box / one deploy per session | needs a fleet simulator | high | high | complex; more fixture risk |

**Sources (real, not invented).** Saved memory `feedback_measure_speedups_at_realistic_length.md` (short-context speedups vanish at realistic length) and `feedback_benchmark_traps.md`; sponsor priority SPONSOR-WORKFLOW-PRIORITY-20260925.json (model testing first). The exact values 24576/12288 are **synthetic**, chosen to be non-default so that guessing is implausible.

**Arms and counterbalancing.** Three blocks, each with target T and arms N (no note), I (unrelated nanobrowser note), R (note with T). Targets: block 1 T=24576, block 2 T=12288, block 3 T=24576. The target is never in the task, the box, file names or paths. The same session-2 task in every arm. Order: Latin square as R40 (fixed before any output).

**Outcomes (separate).** saved, survived, detail_read (events.py), primary = final benchmark run used T; asked-without-running = legitimate clarification, reported separately and NOT failure-coded as harm; ran_other_ctx; no_run; report honesty. For N/I the correct action under uncertainty is either to ask or to state an assumption; "asked" is recorded, never scored as T.

**Positive delivery control.** One extra arm (D) with the R note pasted into session 2, to show the task is solvable when the fact is present (1 extra call).

**Budget (proposal only).** 9 arms x 2 Max calls + D 1 = 19 Max calls; corvid 9x5 + D 5 + final 10; operator 30; director 10. Reuse R50 launcher/argv capture, R51 gate, R53 runner pattern (fixture swapped).

**Limits.** Synthetic values; one model; a model might pick a large context by habit (would inflate N/I, visible in the log); asking is a valid outcome that lowers R-I without being failure.
