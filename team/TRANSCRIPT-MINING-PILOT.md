# TRANSCRIPT-MINING PILOT — pipeline + pilot stats (Brian directive, via GiLMore)

Pilot complete on the memory-bake-off project dirs. **All transcript-
derived content stays local** (`~/.local/share/memory-bakeoff/transcript-
mining/pilot-20260913/`); this note carries aggregate numbers and
class-level precision only — no excerpts, by policy and by self-test.
Pipeline code + synthetic-fixture tests are committed in this lane
(`scripts/experiment_20260912_transcript_mining/`); the corpus itself is
untouched and read-only.

## Pipeline (deterministic, no model in the loop)

Streaming JSONL parse → operator-voice extraction → pattern detectors.
The pilot's real work was the exclusion rules — raw counts were ~2× before
them, and nearly everything they removed was NOT operator speech:

| Filter | Rationale |
|---|---|
| `isMeta`, `tool_result` blocks, command wrappers | not speech |
| subagent JSONLs (whole files) | their "user" records are the ORCHESTRATOR's briefs, model-authored |
| session-continuation summaries | auto-generated, injected as user records |
| `<task-notification>` records | system events |
| conductor seat-dispatch templates (`fsync —`, `RETRO-1 (`, …) | dispatch voice, not Brian's |

Detection classes (per dispatch): corrections = wrong / negation / i_said /
env-fact-correction ("X, not Y") / actually / repeated-instruction
(normalized 60-char prefix, ≥2 turns); durable facts = convention
(always/never/from-now-on/we-decided/remember/instead-of) / env-fact
(paths, ENV=, ports, URLs, versions, pins).

## Pilot stats (memory-bake-off* dirs, 16 JSONL files, 384 MB)

- Operator text turns after exclusions: **223** (of ~2,700 user records —
  system-voice records dominate; exclusions were the precision lever)
- Correction events: **15** (negation 3, actually 2, env-fact-correction 7,
  wrong 1, repeated-instruction 2 groups)
- Durable facts: **21** (convention 10, env_fact 11)
- Precision (local eyeball of excerpts; content stays local): negation and
  actually **100%**; env-fact-correction ~5/7 (quoted third-party speech is
  the residual noise); facts ~85–90% (same); `i_said` fired **0** genuine
  times — the class needs the full corpus to matter.
- Repeat groups are mostly deliberate benchmark probes ("list the integers
  1 to 60") — real repeated-instruction detection needs the full corpus.

## Scaling plan (awaiting go)

Same command, `--project-glob '*'` (13 project dirs, 1.3 GB). Expected
yield ~5–10× the pilot. Two known upgrades before scaling, both cheap:
quote-aware matching (operator quoting a model is not an operator
correction), and a per-project breakdown in stats. Raw corpus is never
sent anywhere; dsh would get anonymized patterns only, Muse never.

## Containment observation (flag, not action)

The largest session file (`-var-home-bmosher-memory-bake-off/`, 380 MB)
has mtime TODAY 01:16 — a Claude session with cwd `/var/home/bmosher/
memory-bake-off` was written recently. R0 covered launchers and timers;
GiLMore may want to confirm whose session this is. The pilot read it as
data only.

— Kiln, 2026-09-13. Pipeline turn ~50 min, $0, all local.
