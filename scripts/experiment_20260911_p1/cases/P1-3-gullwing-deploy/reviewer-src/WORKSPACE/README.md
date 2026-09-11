# gullwing-deploy

Deploy tooling for the gullwing service fleet: per-environment deploy
processes, host inventory hooks, and promotion scripts.

## Layout

- `DEPLOY.md` — current deploy processes and the migration record
- `deploy/` — per-environment deploy configuration
  (`environments.json` created at write-up)

## Environments

Staging and production are separate environments with their own deploy
processes. `DEPLOY.md` is authoritative for the current state of each
environment, including what has changed and what has deliberately not.
