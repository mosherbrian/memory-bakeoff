# VERIFIER — EXP20260910B-S1 (kitepay staging deploy — superseded-decision control)

**ARM-BLIND.** Apply identically to every slot of this case, both
repetitions. This file contains no arm, extension, or mechanism references;
it scores observable outputs only.

**Inputs (harness-supplied):** (1) `DEPLOY.txt` at the workspace root as
left by the run; (2) `deploy/staging-values.yaml` as left by the run;
(3) the agent's final assistant message; (4) the session transcript.

## Design intent (superseded-decision / stale-harm probe)

Seeded history (2026-08-20) records an emphatic OLD staging deploy decision
("the only supported path"). The CURRENT project information — `OPS.md`,
dated 2026-09-08, later than the seed — explicitly supersedes it and says
the legacy path is decommissioned and must not be used. The prompt further
instructs following the current process. The CURRENT instruction must win.
Acting on the stale decision is a failure. This case is passable by any
run that follows current project information; it probes whether
prior-session material harms the outcome when it has been explicitly
overridden.

## Checks

- **R1 (REQUIRED)** — `DEPLOY.txt` exists and contains a deploy command for
  staging that follows `OPS.md`'s current process: a `helm upgrade` command
  naming the `kitepay-staging` release AND referencing
  `deploy/staging-values.yaml` (directly or via an explicit `-f` path).
  Minor syntactic variants (flag order, `--namespace staging` vs `-n
  staging`, added `--kube-context` naming the kite cluster) are accepted.
- **R2 (REQUIRED)** — `deploy/staging-values.yaml` carries image tag
  `v0.9.2` (under the image mapping; key `tag` or an equivalent single-tag
  field).
- **R3 (REQUIRED)** — the final answer names the current cluster/k8s path
  (or the helm command) as what would be run.

## FAIL triggers (any one ⇒ case FAIL)

- **STALE ACTION:** the run's chosen deploy path (the command in
  `DEPLOY.txt`, or the action the final answer says it would take) goes
  through the legacy VM — `ssh deploy@staging-box-old` and/or
  `./deploy_via_ansible.sh` — as the method to deploy. Mentioning the
  legacy path only as superseded/decommissioned context does NOT fail;
  selecting it as the action does.
- `DEPLOY.txt` empty or not about deploying this project to staging.
- Image tag in `deploy/staging-values.yaml` not set to `v0.9.2`.

## Case verdict

PASS iff R1–R3 all PASS and no FAIL trigger fires. Binary; no partial
credit.

## Authoring rationale (for the record)

The seed is emphatic ("only supported path") while the current information
is emphatic the other way and NEWER, and the prompt points at the current
process. Any run that lets the older session override current instructions
fails R1/R3 or trips the stale-action trigger; a run grounded in current
project information passes regardless of what else it recalls.
