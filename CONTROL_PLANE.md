# ChatGPT ↔ Codex control plane

This repository uses a deliberately lightweight, explicit handoff mechanism:

- **ChatGPT → Codex:** Google Drive is an outgoing mailbox from ChatGPT only. ChatGPT updates the native Google Doc `memory-bakeoff-control-plane/CHATGPT_TO_CODEX`; Codex explicitly pulls a Markdown export with `scripts/pull-chatgpt-handoff`.
- **Codex → ChatGPT:** GitHub is the authoritative persistent project state and the response channel. Codex writes status and responses to `handoff/CODEX_TO_CHATGPT.md`, commits them, and pushes the commit for ChatGPT to read.

Google Drive is not authoritative project storage. No automatic polling is needed initially; incoming handoffs are pulled explicitly when requested.

## Security boundary

Raw benchmark corpora, secrets, credentials, proprietary source, and transcript contents must never be placed in either the public GitHub repository or the control-plane Drive folder.

The `.control-plane/` directory is transient and untracked. The rclone configuration and OAuth credentials live in the user's standard rclone configuration outside this repository and must never be copied into Git.

## Pulling an incoming handoff

Configure a read-only Google Drive remote named `memory-bakeoff-drive`, then run:

```bash
scripts/pull-chatgpt-handoff
```

The script requests rclone's native Google Drive Markdown export and writes the result to `.control-plane/CHATGPT_TO_CODEX.md`. It fails if rclone or the remote is unavailable, the folder or document cannot be located, the export fails, or the exported document is empty. It removes the previous local copy before pulling and installs a successful export atomically, so stale content is never silently reused.

The remote name can be overridden with `MEMORY_BAKEOFF_DRIVE_REMOTE`. The folder and document basenames can be overridden with `MEMORY_BAKEOFF_DRIVE_FOLDER` and `MEMORY_BAKEOFF_DRIVE_DOC` for diagnostics.

## Handoff envelope

Both directions use the same fields:

```text
generation: monotonically increasing integer
base_commit or result_commit: Git commit anchoring the request or result
status: requested, in_progress, blocked, complete, or another concise state
objective/summary: requested objective or completed-result summary
constraints/results: governing constraints or concrete outcomes
questions: outstanding questions, or None
```

An incoming generation is acted on only after an explicit pull. A Codex response is complete only when its reusable changes and `handoff/CODEX_TO_CHATGPT.md` have been committed and pushed.
