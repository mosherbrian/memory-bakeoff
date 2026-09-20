# Row-30 design note: format-normalizer adapters for the miner's external corpora

**Row:** QUEUE 30 (UNGATED by Brian 2026-09-15) · **Author:** muse-drafter (Spark)
**Cost:** $0 + ~11 MB disk in `/tmp/opencode/ext-corpora/` (NOT in repo)
**Inputs (all read this turn, lean samples):** Wisp README + 3 transcripts (27–75 KB);
SWE-chat `sessions.parquet` (5,851 rows, full) + 1 transcript (8.4 MB);
MindForge instances file + recipe + remote head-read of trajectory schema.
Detector layer unchanged — adapters plug in front of `mine.py`'s `operator_texts()`.

**Attribution correction 2026-09-15:** QUEUE row 30's status cell says "Kiln fetched"
— the fetch+design in this note was executed by **muse-drafter (Spark)** per direct
conductor instruction (row owner Kiln retains the per-format implement step, still open).

## Disk (df first, per instruction)
- `/var/home` 97% full (24G avail) → **nothing lands in-repo**; `/tmp` 56G avail → all fetches under `/tmp/opencode/ext-corpora/` (wisp 152K / mindforge 176K / swe-chat 10.5M incl. one transcript).

## Acquisition results
| Corpus | Source | License (resolved this turn) | Fetched |
|---|---|---|---|
| Wisp | `crispwisp/wisp-claude-code-sessions` (public, 104 transcripts) | MIT (card) | README + 3 sample sessions |
| SWE-chat | `SALT-NLP/SWE-chat` (`gated:auto` — ambient auth accepted; no credential copied) | ODC-BY (card) | `sessions.parquet` full (5,851 rows) + 1 transcript |
| MindForge | `centre-for-swe/MindForge-27B-Training-Trajectories` (public; resolves row-31 "artifact unverified") | **MIT** (dataset metadata; resolves row-31 "license unverified") | instances + recipe + schema probe (big JSONL read remotely, not downloaded) |

## Per-format adapter = operator-voice DEFINITION (the crux) + record→text
1. **Wisp (raw Claude-Code JSONL).** Line types observed: `user / assistant / attachment / queue-operation / last-prompt`. **Operator voice = `user`-type lines only** (`queue-operation` is harness plumbing, `attachment` is file blobs, `last-prompt` is a derived echo — all three excluded). Record→text: concatenation of `user` line texts in file order; session id = parent dir name.
2. **SWE-chat transcript (Claude-Code JSONL, same family).** Line types observed: `file-history-snapshot / progress (hook events) / user / assistant / custom-title / agent-name`. **Operator voice = `user`-type lines only** (snapshots, hook progress, titles, agent-name are harness telemetry). Record→text: same as Wisp; join key = `sessions.parquet.transcript_path` → transcript file; `sessions.parquet` also ships `user_persona`, `session_success`, `turn_count`, `prompt_count` — the miner's first three are free metadata, no inference needed.
3. **MindForge (ms-swift message JSONL, `{"messages":[{role,content}],"tools"}`).** Roles: system/user/assistant/tool_call/tool; reasoning inline in assistant `<think>` blocks. **Operator voice = NOTHING by default**: the user role is a synthetic task prompt and assistant+think is model reasoning — there is no human operator speech in this corpus (it is teacher-generated, GLM-5.2). Adapter rule: **exclude from operator-voice mining; route to control lane only** (long-horizon autonomous baseline). If ever mined, the only defensible "voice" is `tool` outputs (environment speech, not operator) — flag, don't feed.

## What stays unchanged
Detector/event layer untouched; `operator_texts()` gains a `source` switch (wisp / swe-chat / mindforge-control) implementing the three rules above. MindForge contributes no operator rows.

— muse-drafter (Spark). $0; no score import; no vault/repo writes.

## Implementation (2026-09-15, same seat) — DONE

`mine.py` now carries the `--source {claude-code,wisp,swe-chat,mindforge-control}`
switch; `operator_texts(record, source)` implements the voice rules above and
`stats` records `source` + `source_operator_voice`. Detector/event layer
unchanged, per the design.

- Tests: `tests/test_external_corpus_adapters.py` (wisp/swe-chat voice = user
  lines; tool-result excluded; mindforge-control empty; unknown source raises;
  end-to-end `scan` per source) — **29 passed** with the mining + bundle suites.
- Real-data validation (read-only, local):
  - wisp: 3 files / **3** operator turns / 1 env-fact
  - swe-chat: 1 file / **9** operator turns / 1 env-fact
  - mindforge-control: 1 file / **0** operator turns (correct by construction)
- Fetched corpora stay in `/tmp/opencode/ext-corpora/`; nothing in-repo.

QUEUE row 30 per-format implement closed (owner Kiln retains any pipeline
integration decision).
