# R28-review-1 — independent isolation review

- **Reviewer:** corvid-dsh. Read-only plus one **offline, fully stubbed**
  reproduction; **no real systemd/socket/unit/network/participant effect.**
- **Intake:** completion-claim `R28-render-1`; all **30 manifest hashes
  recomputed equal**. Rendered C/T texts and config present.
- **Verdict: FAIL.** Pair A's isolation is established, but the "all 3 pairs"
  claim is not: pairs **B and C rendered empty task bodies**, so their captured
  participant texts do not contain the actual task. Smallest correction below.

## What passes

- **Pair A** is correct: `R27-A-C.txt` has the full common body (goal, failed
  step, allowed CLI, scope) with `--docs fixtures/docs-A`, and no nudge/packet;
  `R27-A-T.txt` adds the R27 packet **exactly once** and no nudge.
- **Nudge isolation mechanism:** the pre-nudge binary `47f69dfd…` was used;
  installed production is now `eb9cc019…` (R23v2). Stub-only effects verified —
  `stub-calls.json` shows only `systemd-run --user` (the deadline timer, not
  created) and `wake K` (captured); no socket/unit/production DB. `render.sh`
  runs under `env -i HOME=<temp> PATH=<stubs>:/usr/bin` with an isolated
  config/db/stream/claims/artifacts and **fails closed** on a wrong binary hash.
- **Positive control works:** the same render with the v2 binary yields control
  texts that **do** contain the platform nudge (grep hit each pair), so the
  negative check can fail.
- **Independent offline reproduction:** I ran `render.sh` into a fresh temp dir;
  rc 0, all six texts match `run2` after normalizing the random temp-root path,
  and nudge/packet counts match.

## Blocking defect — pairs B and C have empty bodies

`render.sh` builds each body from `> `-prefixed lines after the string "Common
body" in `task-pair-X.md`. `task-pair-A.md` has such lines; **`task-pair-B.md`
and `task-pair-C.md` only say "Common body as Pair A, with `--docs
fixtures/docs-B`"** and contain no `> ` body lines. So the rendered
`R27-B-{C,T}.txt` and `R27-C-{C,T}.txt` are **head + blank lines + loop footer**
with **no goal, no failed-step text, no allowed command, no scope, and no
`fixtures/docs-B|C` reference** (verified by reading both raw files). The
manifest `checks.json` reports `shared_bytes_equal_after_declared_substitutions:
true` for B/C — true only because both bodies are empty (vacuous), not because
the real task bytes match.

Consequence: the R28 claim "actual rendered C/T worker texts (all three pairs)"
is not met; the R27 requirement that C/T be byte-comparable after substitutions
is unverified for B and C. This also exposes that R27's `task-pair-B/C.md` are
not self-contained ("Common body as Pair A"), which the render should have
expanded.

**Smallest correction:** make the B/C bodies self-contained (or have the renderer
expand "Common body as Pair A" by copying Pair A's body with the `docs-B|C` and
decoy/token substitutions), re-run, and re-verify all three pairs' actual texts;
fix `checks.json` to compare only non-empty expected bodies so an empty match
cannot pass.

## Proposal (not authorised)

The private pre-nudge loop instance proposal is reasonable (own config
`campaign4-r27.json`, own db/claims/artifacts, `agent-loop-r27-*` units, one
arm at a time, Tern director, stop/retire after) and is correctly marked
proposal-only. Do not release it until the B/C render is corrected and
re-reviewed.

*Reviewed: `package.md`, `completion-claim.json`, `isolation-report.md`
(`c4d4143c…`), `isolation-manifest.json` (`d3e664ef…`), all `offline/*` outputs;
`offline/render.sh`; independent stubbed reproduction in a fresh temp dir.*
