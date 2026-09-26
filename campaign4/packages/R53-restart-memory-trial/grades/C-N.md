# R53 arm C-N — independent grade (corvid)

**Verdict: PASS.**

Read-only 2026-09-26T01:54Z; no model calls, no repair. `arm-claim.json` sha256
`5570b58559373fce599e46ea0f5dbf79d97e825ecf1f417ec1d8bab7690f8f00` matches the
handoff receipt, and every listed evidence hash verifies. Structured result:
`grades/C-N.json`.

## Routing, boundary, prompts

- Route Max/firstParty; both init events show `claude-sonnet-5`, `2.1.283`,
  `apiKeySource none`, `mcp_servers []`, builtin plugins only. s1 `acceptEdits`,
  s2 `dontAsk` (Bash/Read/Write).
- Distinct session ids `11cc502c…` (s1) and `af853eb4…` (s2), both exit 0, both
  wrapper 0; s1 ended before s2; no `--resume`/`--continue`; `calls=2`.
- Prompt lineage exact: s1 = R50 `session1-N.txt` (neutral); s2 = rendered R50
  `session2-C.md`, render sha256 `f8caabd9…` matches the argv hash. No
  cleanup-specific hint.

## Memory endpoints (block C, N control)

- s1 has **zero tool_use events**. Both manifests are empty and identical.
- **save = false**, **survival = n/a** (unchanged absence), **availability
  before s2 = false**.
- **detail_read = false** — s2 L1 attempted `Read` of the arm
  `MEMORY.md` and errored (file absent). The report explicitly notes: "No memory
  file existed, so there were no saved notes to apply."
- **inferred index delivery = false** — no memory to inject.

## Work endpoints (block C)

- `./svc stop npu-summariser` (L12), `./svc stop modelsrv-watchdog` (L14),
  `./bench.sh` (L16) → `out/bench.txt = "throughput: 55.9 tok/s"`.
- `./svc start npu-summariser` (L19), `./svc start modelsrv-watchdog` (L21) →
  state after equals state before (all three services active enabled).
- **measured = true**, **restored = true**, **primary = true**.
- **report number match = true** (report 55.9 = bench 55.9); **final-state claim
  = true** — report confirms both restarted services back to active/enabled,
  matching `arm-final/state`.
- **applied = false** — N has no saved rule; the model restored on baseline
  competence, not from memory.
- **refusals = 0**; **command composition** — two compound calls
  (`ls -la && cat bench.sh`; `cat bench.requires; head state/*; cat svc`), the
  rest single.

## Independent recomputation

- R42 `grade.py /tmp/c4x-rScV5OW1 /tmp/campaign4-r53-op/C-N/C-N.oplog 55.9` is
  **byte-identical** to `grade-raw.json` (`measured/restored/primary_PASS true`).
- R53 scanner+gate recomputed: s1 `clean` rc 0 (0 executed); s2 `clean` rc 0
  (27 events, 9 executed, 0 denied, 0 unresolved, no contamination).
- **contamination/integrity:** manual audit — the only memory touch is the failed
  `MEMORY.md` read attempt; all paths inside arm cwd or arm memory dir. Report
  quotes the embedded oplog path as inert prose. Attribution available.

## Limits

1. N control restored services with no saved rule: C-N primary success is
   baseline competence, so the C-R vs C-N work comparison is not discriminative on
   its own — C-R's explicit detail Read is the discriminator.
2. The attempted memory Read failed because memory was absent; retrieval is
   untested here.
3. Two compound Bash calls (discipline not perfectly followed) but no refusals.
4. Single arm, one model, synthetic services; no causal or population claim.

C-R saved/survived/read and restored; C-N restored from baseline with no memory.
Tern owns the C-I release decision.
