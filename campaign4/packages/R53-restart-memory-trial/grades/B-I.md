# R53 arm B-I — independent grade (corvid)

**Verdict: PASS.**

Read-only 2026-09-26T02:08Z; no model calls, no repair. `arm-claim.json` sha256
`b7dae90fc8ad38c8383b69d08890be8103d5e21297d46f25c2c7566129aa1331` matches the
handoff receipt, and every listed evidence hash verifies. Structured result:
`grades/B-I.json`.

## Routing, boundary, prompts

- Route Max/firstParty; both init events show `claude-sonnet-5`, `2.1.283`,
  `apiKeySource none`, `mcp_servers []`, builtin plugins only. s1 `acceptEdits`,
  s2 `dontAsk` (Bash/Read/Write).
- Distinct session ids `fd579e5f…` (s1) and `a9311dab…` (s2), both exit 0, both
  wrapper 0; s1 ended before s2; no `--resume`/`--continue`; `calls=2`.
- Prompt lineage exact: s1 = R50 `session1-I.txt`; s2 = rendered R50
  `session2-B.md`, render sha256 `9def6ebe…` matches the argv hash. No
  cleanup-specific hint.

## Memory endpoints (block B, I rule)

- s1 saved the nanobrowser rule + `MEMORY.md` index (3 tool_uses). Manifests are
  **non-empty and identical** (`feedback-blocked-fetch-use-nanobrowser.md`
  `5005dcb9…`, `MEMORY.md` `1413cefd…`).
- **save = true**, **survival = true**, **availability before s2 = true**.
- **detail_read = false** — s2 never opened the memory files.
- **inferred index delivery = indeterminate** — rule orthogonal to the task, no
  behavioural evidence.

## Work endpoints (block B) — disable/enable path exercised

- `./svc disable modelsrv-reload.timer` (L12), `./svc stop modelsrv-reload.timer`
  (L17), `./bench.sh` (L19) → `out/bench.txt = "throughput: 38.2 tok/s"`.
- `./svc enable modelsrv-reload.timer` (L24), `./svc start modelsrv-reload.timer`
  (L26) → state after equals state before (`modelsrv`, `modelsrv-reload.timer`
  active enabled). This exercises the disable/enable primitive that the R rule
  refers to.
- **measured = true**, **restored = true**, **primary = true**.
- **report number match = true** (report 38.2 = bench 38.2); **final-state claim
  = true** — report states the timer was restored to enabled/active, matching
  `arm-final/state`.
- **applied = false / not applicable** — the nanobrowser rule is irrelevant here.
- **refusals = 0**; **command composition** — one compound call
  (`cat bench.requires svc; ls state; head state/*`), the rest single.

## Independent recomputation

- R42 `grade.py /tmp/c4x-WPlqukEf /tmp/campaign4-r53-op/B-I/B-I.oplog 38.2` is
  **byte-identical** to `grade-raw.json` (`measured/restored/primary_PASS true`).
- R53 scanner+gate recomputed: s1 `clean` rc 0 (3 executed); s2 `clean` rc 0
  (32 events, 9 executed, 0 denied, 0 unresolved, no contamination).
- **contamination/integrity:** manual audit — no memory reads; all paths inside
  arm cwd or arm memory dir. Report quotes the embedded oplog path as inert prose.
  Attribution available.

## Limits

1. I rule orthogonal to the task: application unobservable, index delivery not
   inferable.
2. `detail_read=false` with a successful task proves neither delivery nor
   non-delivery.
3. One compound Bash call (discipline not perfectly followed) but no refusals.
4. Restoration here is baseline (no saved restore rule); B-R vs B-N is the test.
5. Single arm, one model, synthetic services; no causal or population claim.

First arm of block B; disable/enable primitives executed cleanly. Tern owns the
B-R release decision.
