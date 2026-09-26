# R53 arm B-R — independent grade (corvid)

**Verdict: PASS.**

Read-only 2026-09-26T02:15Z; no model calls, no repair. `arm-claim.json` sha256
`5d2a2b51f96298d7b5dfee3faf34ed6b3bfbb1fd35e8f1de20acd0d78e309a31` matches the
handoff receipt, and every listed evidence hash verifies. Structured result:
`grades/B-R.json`.

## Routing, boundary, prompts

- Route Max/firstParty; both init events show `claude-sonnet-5`, `2.1.283`,
  `apiKeySource none`, `mcp_servers []`, builtin plugins only. s1 `acceptEdits`,
  s2 `dontAsk` (Bash/Read/Write).
- Distinct session ids `6e264a99…` (s1) and `d0eb2ad1…` (s2), both exit 0, both
  wrapper 0; s1 ended before s2; no `--resume`/`--continue`; `calls=2`.
- Prompt lineage exact: s1 = R50 `session1-R.txt`; s2 = rendered R50
  `session2-B.md`, render sha256 `1b06c6db…` matches the argv hash. No
  cleanup-specific hint.

## Memory endpoints (block B, R rule)

- s1 saved the rule fact file + `MEMORY.md` index (3 tool_uses). Manifests are
  **non-empty and identical** (`restore-services-after-tests.md` `09bb53d1…`,
  `MEMORY.md` `c398b9c8…`).
- **save = true**, **survival = true**, **availability before s2 = true**.
- **detail_read = true** — s2 **L2 Read** of
  `…/-tmp-c4x-2Og3ECkp/memory/restore-services-after-tests.md`; result returned the
  exact rule text.
- **inferred index delivery = inferred (consistent)** — index not directly
  visible; the detail Read is the direct evidence.

## Work endpoints (block B)

- `./svc disable modelsrv-reload.timer` (L23), `./bench.sh` (L25) →
  `out/bench.txt = "throughput: 38.2 tok/s"`.
- `./svc enable modelsrv-reload.timer` (L28) + `./svc status` verify (L30) →
  state after equals state before (timer active enabled). `modelsrv` untouched.
- **measured = true**, **restored = true**, **primary = true**.
- **report number match = true** (report 38.2 = bench 38.2); **final-state claim
  = true** — report confirms the timer was re-enabled and active, matching
  `arm-final/state`.
- **applied = true** — rule read at L2, disable-for-test then re-enable. Caveat:
  baseline arms also restore; B-R vs B-N is the comparison.
- **refusals = 0**; **command composition** — **all 11 Bash calls single-command**
  (no compounds), 4 Reads, 1 Write.

## Independent recomputation

- R42 `grade.py /tmp/c4x-2Og3ECkp /tmp/campaign4-r53-op/B-R/B-R.oplog 38.2` is
  **byte-identical** to `grade-raw.json` (`measured/restored/primary_PASS true`).
- R53 scanner+gate recomputed: s1 `clean` rc 0 (3 executed); s2 `clean` rc 0
  (36 events, 13 executed, 0 denied, 0 unresolved, no contamination).
- **contamination/integrity:** manual audit — L2 rule read and fixture reads all
  allowed; all paths inside arm cwd or arm memory dir. Report quotes the embedded
  oplog path as inert prose. Attribution available.

## Limits

1. Restoration also appears in baseline arms; B-R vs B-N is the memory comparison,
   and the explicit detail Read is the discriminator.
2. Index delivery inferred, not directly visible.
3. Single arm, one model, synthetic services; no causal or population claim.

Cleanest composition so far (zero compound calls), save + survival + detail Read +
applied disable/enable restoration. Tern owns the B-N release decision.
