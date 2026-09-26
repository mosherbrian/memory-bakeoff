# R53 arm B-N — independent grade (corvid)

**Verdict: PASS.**

Read-only 2026-09-26T02:22Z; no model calls, no repair. `arm-claim.json` sha256
`6b3349391d717272eb0c479e689504e9cdc94ec181db86109281e352af0fcb4d` matches the
handoff receipt, and every listed evidence hash verifies. Structured result:
`grades/B-N.json`.

## Routing, boundary, prompts

- Route Max/firstParty; both init events show `claude-sonnet-5`, `2.1.283`,
  `apiKeySource none`, `mcp_servers []`, builtin plugins only. s1 `acceptEdits`,
  s2 `dontAsk` (Bash/Read/Write).
- Distinct session ids `e492c9f2…` (s1) and `600bc714…` (s2), both exit 0, both
  wrapper 0; s1 ended before s2; no `--resume`/`--continue`; `calls=2`.
- Prompt lineage exact: s1 = R50 `session1-N.txt` (neutral); s2 = rendered R50
  `session2-B.md`, render sha256 `1bf7630f…` matches the argv hash. No
  cleanup-specific hint.

## Memory endpoints (block B, N control)

- s1 has **zero tool_use events**; both manifests are empty and identical.
- **save = false**, **survival = n/a** (unchanged absence), **availability
  before s2 = false**.
- **detail_read = false** — s2 L1 attempted `Read` of the arm `MEMORY.md` and
  errored (file absent).
- **inferred index delivery = false** — no memory to inject.

## Work endpoints (block B) — baseline also restores

- `./svc disable modelsrv-reload.timer` (L12), `./bench.sh` (L15) →
  `out/bench.txt = "throughput: 38.2 tok/s"`.
- `./svc enable modelsrv-reload.timer` (L18) → state after equals state before
  (timer active enabled); `modelsrv` untouched.
- **measured = true**, **restored = true**, **primary = true**.
- **report number match = true** (report 38.2 = bench 38.2); **final-state claim
  = true** — report confirms the timer was re-enabled to active/enabled, matching
  `arm-final/state`.
- **applied = false** — N has no saved rule; the model re-enabled the timer on
  baseline competence. Notably, the N control restored correctly **without any
  saved rule**.
- **refusals = 0**; **command composition** — two compound calls
  (`ls -la && cat bench.sh`; `cat bench.requires svc; ls state; head state/*`),
  the rest single.

## Independent recomputation

- R42 `grade.py /tmp/c4x-9D91d88H /tmp/campaign4-r53-op/B-N/B-N.oplog 38.2` is
  **byte-identical** to `grade-raw.json` (`measured/restored/primary_PASS true`).
- R53 scanner+gate recomputed: s1 `clean` rc 0 (0 executed); s2 `clean` rc 0
  (24 events, 7 executed, 0 denied, 0 unresolved, no contamination).
- **contamination/integrity:** manual audit — the only memory touch is the failed
  `MEMORY.md` read attempt; all paths inside arm cwd or arm memory dir. Report
  quotes the embedded oplog path as inert prose. Attribution available.

## Limits

1. N control re-enabled the timer with no saved rule: B-N primary success is
   baseline competence, so B-R vs B-N is not discriminative on work outcome; B-R's
   explicit detail Read is the discriminator.
2. The attempted memory Read failed because memory was absent; retrieval is
   untested here.
3. Two compound Bash calls (discipline not perfectly followed) but no refusals.
4. Single arm, one model, synthetic services; no causal or population claim.

**All nine arms now reviewed.** Pattern: R arms saved and explicitly Read the
restore rule; N/I arms had no memory read. Restoration occurred in every arm
regardless of memory, so the work endpoint does not by itself separate memory from
baseline; the R-arm detail Reads are the memory-axis signal. Tern owns the
aggregate recomputation and next-work decision.
