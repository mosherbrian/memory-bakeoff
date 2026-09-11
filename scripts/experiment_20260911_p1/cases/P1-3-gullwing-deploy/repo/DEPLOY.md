# Deploy processes — current state (updated 2026-09-05)

## Production: flux-managed GitOps

Production ships via **flux-managed** GitOps: builds are promoted by
image tag, flux reconciles the cluster, and rollout health is gated by
the standard probes. This has been the production process since the
2026-09-05 migration.

### Replacement notice (production only)

Flux-managed REPLACES the old pull-deploy process for **production
only**. Production no longer runs `scripts/pull_deploy.sh`; that path is
retired for production. Older sessions describing pull-deploy for
production are superseded by this section.

## Staging: deliberately unchanged

The 2026-09-05 migration was scoped to production. **Staging
intentionally remains on its existing process** — the September ops
review validated it and ruled a migration unnecessary for staging. This
repository deliberately does not restate staging's process here; the
authoritative record of what staging uses is in the project's session
history. Do not change staging as part of production work.

## Environment config

Per-environment strategies are recorded in `deploy/environments.json`.
