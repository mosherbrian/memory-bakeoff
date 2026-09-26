# R56 readiness (offline; zero participant calls)

**Implemented and checked.**
- Primary fixed: `target_autonomous` only when the run used TARGET and ASSUMPTION and QUESTION are both NONE. Running at TARGET while stating an assumption or asking about context is `target_with_uncertainty` (not primary). An unrelated question does not remove autonomy. Truth table 17/17 (tests/results.json; the R55 14 cases plus 3 new ones).
- Local permission amendment (launch/common.sh copy only; no global settings): session-2 allow list is `Bash(./bench.sh --ctx:*)`, Read, Write. The svc permission is removed. bench.sh accepts exactly `--ctx N`, with 1 <= N <= 1048576 an integer. 8 argument cases (tests/bench-args.txt): only the valid form runs and logs.
- Runner (operator/run-arm.sh) handles the 6 two-session paths and the 2 D one-call paths. All 8 ran with a stub claude (stub/runs.txt: calls 2 x 6, 1 x 2).
- Opaque identities: cwd `/tmp/c4x-<12 hex>` and operator log `/tmp/campaign4-r56-op/o-<12 hex>/log`. Hex only, so no random suffix can look like a label. The label->target mapping is kept only in map.jsonl under the operator root, which the scan gate denies. Leak check over every participant-visible file and rendered prompt (stub/leak-check.txt): no target outside the intended R session-1 note and D prompt, no other-target text, no label-like text, no label or target in any visible path.
- Frozen 14-call proposal and order unchanged (protocol-R55.json). No screening.

**Unverified.** Live permission behaviour of `Bash(./bench.sh --ctx:*)` under dontAsk, and model behaviour. Participants can still read bench.sh and see the opaque log path (same-user limit; the path carries no information).

**One next step.** Tern's decision on a live release of the frozen 14-call cohort on this runner (Max calls only; corvid 8 x 5 + final 10), or a 1-call D technical check first if Tern wants the permission form proven live.
