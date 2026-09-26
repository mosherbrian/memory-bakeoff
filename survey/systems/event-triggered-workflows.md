# System card: GitHub Actions events as procedure runner

**kiln · 2026-09-26 · source: official GitHub Actions docs (events-that-trigger-workflows; read this session). Reusable-workflow (`workflow_call`) specifics uninspected — bounded, marked. Quoting ROLES fit duty. Roadmap inputs, principles, matrix requirement 5 (procedures/skills stored and relevantly loaded) as context.**

## The mechanism (documented)

Stored YAML procedures run on declared triggers with no agent in the loop: dozens of event types (push, pull_request, issues, discussion, schedule/cron ≥5min, workflow_dispatch, repository_dispatch) refined by activity types, branch/tag filters, and **path filters** (run only when matching files change). Selection is static declaration, evaluated by the platform at event time.

## Execution vs guidance-loading (kept distinct)

This is actual automatic execution — stronger than loading guidance into a prompt. The procedure runs as code on a runner. What it is not: relevance *judgment* (filters match strings, not task meaning), nor agent-task delivery (scope is repo events, not an agent deciding it needs a skill mid-task).

## Missed-trigger / permission / approval / budget conditions (documented)

Scheduled runs drop under high load and disable after 60 days of repo inactivity; forked-PR runs need approval and get read-only tokens; GITHUB_TOKEN-triggered events mostly create no runs; environments can gate on approvals; minutes/concurrency/runner hosting bound throughput (GitHub-hosted or self-hosted). Ownership: repo maintainers + whoever pays for runners. Reusable-workflow composition details uninspected — not claimed.

## Verdict: **partial** on requirement 5, narrowly construed

It genuinely covers "a stored procedure runs on a declared event without actor selection" — but requirement 5 concerns procedures/skills relevantly loaded for agent work, and Actions covers CI-scope execution with statically declared relevance. Not stretched into memory, not installed for a green cell: partial, with the relevance gap (declared filters ≠ task judgment) and scope gap (repo events ≠ agent task contexts) named as the missing halves.
