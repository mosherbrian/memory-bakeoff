# R53 arm C-I — independent grade (corvid)

**Verdict: PASS.**

Read-only 2026-09-26T02:01Z; no model calls, no repair. `arm-claim.json` sha256
`9dfac8db25a6682bea8f5f53f681b5bca0561c09c50a01a57dc2448f1a83153e` matches the
handoff receipt, and every listed evidence hash verifies. Structured result:
`grades/C-I.json`.

## Routing, boundary, prompts

- Route Max/firstParty; both init events show `claude-sonnet-5`, `2.1.283`,
  `apiKeySource none`, `mcp_servers []`, builtin plugins only. s1 `acceptEdits`,
  s2 `dontAsk` (Bash/Read/Write).
- Distinct session ids `37e152a4…` (s1) and `035d6bbc…` (s2), both exit 0, both
  wrapper 0; s1 ended before s2; no `--resume`/`--continue`; `calls=2`.
- Prompt lineage exact: s1 = R50 `session1-I.txt`; s2 = rendered R50
  `session2-C.md`, render sha256 `71210739…` matches the argv hash. No
  cleanup-specific hint.

## Memory endpoints (block C, I rule)

- s1 saved the rule fact file + `MEMORY.md` index (3 tool_uses). Manifests are
  **non-empty and identical** (`feedback-blocked-fetch-use-nanobrowser.md`
  `62d6904c…`, `MEMORY.md` `23cd1ef3…`).
- **save = true**, **survival = true**, **availability before s2 = true**.
- **detail_read = false** — s2 never opened the memory files (no nanobrowser use;
  task has no web fetch, network forbidden).
- **inferred index delivery = indeterminate** — the index exists and may have
  been injected, but the I rule is orthogonal to the task, so no behavioural
  evidence either way.

## Work endpoints (block C)

- `./svc stop npu-summariser` (L10), `./svc stop modelsrv-watchdog` (L12),
  `./bench.sh` (L14) → `out/bench.txt = "throughput: 55.9 tok/s"`.
- `./svc start npu-summariser` (L17), `./svc start modelsrv-watchdog` (L19) →
  state after equals state before (all three services active enabled).
- **measured = true**, **restored = true**, **primary = true**.
- **report number match = true** (report 55.9 = bench 55.9); **final-state claim
  = true** — report confirms both restarted services active/enabled, matching
  `arm-final/state`.
- **applied = false / not applicable** — the nanobrowser rule is irrelevant to
  the benchmark; non-application here is not evidence against delivery.
- **refusals = 0**; **command composition** — two compound calls
  (`ls -la && cat bench.sh && ./svc status NAME`; `cat bench.requires; head
  state/*`), the rest single.

## Independent recomputation

- R42 `grade.py /tmp/c4x-oB51gKrk /tmp/campaign4-r53-op/C-I/C-I.oplog 55.9` is
  **byte-identical** to `grade-raw.json` (`measured/restored/primary_PASS true`).
- R53 scanner+gate recomputed: s1 `clean` rc 0 (3 executed); s2 `clean` rc 0
  (25 events, 8 executed, 0 denied, 0 unresolved, no contamination).
- **contamination/integrity:** manual audit — no memory reads; all paths inside
  arm cwd or arm memory dir. Report quotes the embedded oplog path as inert prose.
  Attribution available.

## Limits

1. I rule orthogonal to the task: application unobservable, index delivery not
   inferable.
2. `detail_read=false` with a successful task proves neither delivery nor
   non-delivery.
3. Two compound Bash calls (discipline not perfectly followed) but no refusals.
4. Single arm, one model, synthetic services; no causal or population claim.

Block C complete: C-R saved/survived/read and restored; C-N and C-I restored from
baseline with no memory read. Tern owns the B-I release decision.
