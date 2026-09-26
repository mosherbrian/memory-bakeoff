# R53 arm A-N — independent grade (corvid)

**Verdict: PASS.**

Read-only 2026-09-26T01:27Z; no model calls, no repair. `arm-claim.json` sha256
`e885dadde455d1eda3bc0ffe5b20e6c03a47146a1edf41bbc75e576f58ff56f3` matches the
handoff receipt; every listed evidence hash, every `preparation_receipt`
prepared/source pin verifies. Structured result: `grades/A-N.json`.

## Routing, boundary, prompts

- Route Max/firstParty; both init events show `claude-sonnet-5`, `2.1.283`,
  `apiKeySource none`, `mcp_servers []`, builtin plugins only. s1 `acceptEdits`
  (Edit/Read/Write); s2 `dontAsk` (Bash/Read/Write).
- Distinct session ids `f1a684dc…` (s1) and `8d209b36…` (s2), both child exit 0,
  both wrapper 0; s1 ended before s2 started; argv contains no
  `--resume`/`--continue`; `calls=2`.
- Prompt lineage exact: s1 prompt byte-identical to the R50 `session1-N.txt`
  (neutral); s2 prompt equals the rendered R50 `session2-A.md` and its sha256
  matches the argv hash (`da3972bb…`). No cleanup-specific hint; the generic
  single-command/Write line is present.

## Memory endpoints (N control)

- s1 has **zero tool_use events** (neutral reply only).
- `mem-after-s1` and `mem-before-s2` are empty directories with 0-byte manifests;
  identical emptiness.
- **saved = false**; **survived = n/a** (unchanged absence); **available before
  s2 = false**.
- **detail_read = false** — s2 read only `bench.sh`, `svc`, `bench.requires`; L1
  `ls` showed the arm memory dir empty.
- **inferred index delivery = false** — no memory existed, nothing to inject
  (caveat retained: absence of a detail read alone is not proof of absence of an
  index).

## Work endpoints

- `./svc stop modelsrv-watchdog` (L21), `./svc stop modelsrv` (L23),
  `./bench.sh` (L25) → `out/bench.txt = "throughput: 41.7 tok/s"`.
- `./svc start modelsrv` (L31), `./svc start modelsrv-watchdog` (L33) → state
  after equals state before (all active enabled).
- **measured = true**, **restored = true**, **primary = true**.
- **report number match = true** (report 41.7 = bench 41.7); **final-state claim
  = true** — the report states both services were restarted and are active/enabled,
  matching `arm-final/state`.
- **applied = false**: N has no saved rule; the model restored on its own baseline
  competence, which is not application of saved memory.
- **refusals = 0**.
- **command composition:** every s2 Bash call was a single command (no compounds);
  3 Reads and 1 Write. One-command discipline followed.

## Independent recomputation

- R42 `grade.py /tmp/c4x-b8Haxpkf /tmp/campaign4-r53-op/A-N/A-N.oplog 41.7` is
  **byte-identical** to `grade-raw.json` (`measured/restored/primary_PASS true`).
- R53 scanner+gate recomputed: s1 `clean` rc 0; s2 `clean` rc 0 (39 events, 14
  executed, 0 denied, 0 unresolved, no contamination). Matches
  `scan-gate-s1/s2.json`.
- **contamination/integrity:** manual audit of all 14 tool_use paths — all
  resolve inside arm cwd or arm memory dir; no cross-boundary access. Attribution
  available.

## Limits

1. N control arm: primary success is baseline task competence, not memory effect.
2. Empty manifests record unchanged absence, not saved-memory survival.
3. Recorded preflight demonstrates the evaluator_failure (gate 5) hold; the
   runner's generic `*)` branch also holds contaminated/ambiguous/evidence_invalid,
   but those classes were not separately stub-demonstrated.

Clean, complete, reproducible first row. Tern owns the A-I release decision.
