# tessellate-export

Batch export worker for the tessellate reporting stack. Pulls queued
export jobs, renders them, and ships the artifacts to the report store.

## Layout

- `docs/limits.md` — platform limits (batch sizes, file sizes)
- `config/worker.json` — runtime worker configuration (created at deploy)

## Configuration

Worker runtime settings live in `config/worker.json`. Platform-level
limits are recorded in `docs/limits.md`.
