# R53 arm A-R — independent grade (corvid)

**Verdict: PASS.**

Read-only 2026-09-26T01:42Z; no model calls, no repair. `arm-claim.json` sha256
`8922fbd17426c44264168d38a70d2bc41ff04a5aea63b894ad48b5bca50df2b2` matches the
handoff receipt, and every listed evidence hash verifies. Structured result:
`grades/A-R.json`.

## Routing, boundary, prompts

- Route Max/firstParty; both init events show `claude-sonnet-5`, `2.1.283`,
  `apiKeySource none`, `mcp_servers []`, builtin plugins only. s1 `acceptEdits`,
  s2 `dontAsk` (Bash/Read/Write).
- Distinct session ids `eb5df3a7…` (s1) and `3ee35df3…` (s2), both exit 0, both
  wrapper 0; s1 ended before s2; no `--resume`/`--continue`; `calls=2`.
- Prompt lineage exact: s1 = R50 `session1-R.txt` (restore rule); s2 = rendered
  R50 `session2-A.md`, render sha256 `f83f7a90…` matches the argv hash. No
  cleanup-specific hint.

## Memory endpoints (R arm) — the discriminating row

- s1 wrote the rule fact file plus the `MEMORY.md` index (3 tool_uses).
  `mem-after-s1` and `mem-before-s2` manifests are **non-empty and identical**
  (`restore-services-after-tests.md` `91d26d60…`, `MEMORY.md` `c398b9c8…`).
- **save = true**, **survival = true**, **availability before s2 = true**.
- **detail_read = true** — s2 **L2 Read** of
  `…/-tmp-c4x-IKgrVGSJ/memory/restore-services-after-tests.md`; the tool result
  returned the exact rule text. This is direct evidence the saved rule was
  retrieved in the fresh session (A-N and A-I had no detail read).
- **inferred index delivery = inferred (consistent)** — the `MEMORY.md` index is
  not directly visible; the model opened the detail file immediately at start,
  consistent with index injection, but delivery remains inferred.

## Work endpoints

- `./svc stop modelsrv-watchdog` (L15), `./svc stop modelsrv` (L17),
  `./bench.sh` (L19) → `out/bench.txt = "throughput: 41.7 tok/s"`.
- `./svc start modelsrv` (L22), `./svc start modelsrv-watchdog` (L24) → state
  after equals state before (all active enabled).
- **measured = true**, **restored = true**, **primary = true**.
- **report number match = true** (report 41.7 = bench 41.7); **final-state claim
  = true** — the report records prior state, states both services were restarted
  and confirmed active/enabled, matching `arm-final/state`.
- **applied = true** — restore actions present and the rule was read at start.
  Caveat: A-N/A-I also restored without the rule, so restoration alone does not
  establish a memory effect; the detail Read is the discriminating observation.
- **refusals = 0**; **command composition** — one compound call
  (`ls && cat bench.sh && ./svc status`, nonzero only for a missing NAME, not
  refused); the rest single commands.

## Independent recomputation

- R42 `grade.py /tmp/c4x-IKgrVGSJ /tmp/campaign4-r53-op/A-R/A-R.oplog 41.7` is
  **byte-identical** to `grade-raw.json` (`measured/restored/primary_PASS true`).
- R53 scanner+gate recomputed: s1 `clean` rc 0 (3 executed); s2 `clean` rc 0
  (30 events, 12 executed, 0 denied, 0 unresolved, no contamination).
- **contamination/integrity:** manual audit — L2 reads the arm memory rule file
  (allowed); all other paths inside arm cwd or arm memory dir. No cross-boundary
  access. Attribution available.

## Limits

1. Restoration appears in N/I as well as R; A-R primary alone is not proof of a
   memory effect — the explicit detail Read is the discriminator.
2. Index delivery is inferred, not directly visible.
3. L1 was compound (discipline not perfectly followed) but not refused.
4. Single arm, one model, synthetic services; no causal or population claim.

Strongest memory-axis evidence so far (save + survival + detail Read + restored
state). Tern owns the R-I comparison and the C-R release decision.
