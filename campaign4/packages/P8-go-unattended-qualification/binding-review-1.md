# P8-go-unattended-qualification — binding review 1 (raw-fact reconciliation)

- **Reviewer:** corvid-dsh
- **Action:** `P8-binding-1` (existing ≤5 m grant)
- **Brief:** `preparation-release-1.json` + `preparation-instructions-1.md`;
  evidence `live-preparation-1/` (3 raws) and `post-registry.txt`.
- **Scope:** derive-only/read-only raw-fact reconciliation vs live
  registry/sockets/binary hash. No tasks, no source edit, no live effect.

## Verdict

**PASS (bounded).** All three real launch raws reconcile exactly to the live
campaign4 registry, all three sockets exist with captured incarnation, no streams
(no tasks sent), and the candidate binary hash and source commit match the signed
release. There is **no canonical `execution-binding.json`** here by design — Tern
is to author the concrete live config/signature next — so this is a raw-fact
binding check, not a schema derive. One metadata deviation is noted (release
`raw_path` filenames).

## Checks

- **Binary/source:** installed `/home/bmosher/.local/bin/agent-loop` sha256
  `8cc149bf5c74a0c39b720691787b4ed9a47c9621368250ddcecaad791a872c0b` = release
  `candidate_binary_sha256`; checkout HEAD `4a00d675d4384f3bb43d9ab25a291847c7944cb2`
  = release `source_commit`.
- **Raw→registry identity:** worker `1c0fc09f-1790141334` (acp-go, `idle`),
  verifier `404bad13-1790141334` (acp-go-deepseek, `waiting`), director
  `8bb0bff7-1790141334` (acp-go, `idle`); each raw's `session_id`/`title`/
  `resolved_command`/`path`/`profile` match the live registry row and
  `post-registry.txt` (14 sessions total). Workdirs =
  `/tmp/p8-live1-20260923T052526Z/workdirs/{worker,verifier,director}`.
- **rc:** `raw-worker.rc`, `raw-verifier.rc`, `raw-director.rc` all `0`; each raw
  `success: true`.
- **Sockets/incarnation:** all three sockets exist as real Unix sockets —
  `1c0fc09f` ino `23791931` mtime `1790141335.582`, `404bad13` ino `23791939`
  mtime `1790146335.634`, `8bb0bff7` ino `23791944` mtime `1790141335.931`.
- **No tasks:** `acp-stream/<id>.jsonl` absent for all three → no turns, no
  dispatch/claim/callback run; three fresh seats idle.
- **Release environment:** `unset_environment` clears
  `ACP_SOURCE_TEST_NOW/FIXTURE_LAUNCH_EXEC/PINNED_MODEL_OVERRIDE/ACP_GO_MODEL/
  ACP_MODEL` — no test-clock/capture leak; `AGENTDECK_PROFILE=campaign4`.
- **Config compatibility:** three seats (worker/verifier/director) match the
  release's live-plan outline (worker→verifier→pending decision→closed).

## Noted deviation (non-blocking)

- The release lists per-role `raw_path` as `live-preparation-1/worker.json`
  / `verifier.json` / `director.json`, but the files on disk are
  `raw-worker.json` / `raw-verifier.json` / `raw-director.json`. Same facts, name
  mismatch — record it and use the actual filenames when Tern authors the concrete
  binding/signature. No execution-binding summary was fabricated, per instruction.

## Effect

One bounded verdict: **PASS (bounded)** — raw launch facts, sockets, registry and
binary/source hash reconcile; no canonical binding yet by design. Returned to
Tern to author the concrete live config/signature.
