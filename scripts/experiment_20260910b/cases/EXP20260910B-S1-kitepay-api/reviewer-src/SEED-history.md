# SEED HISTORY — EXP20260910B-S1 (project label: `kitepay-api`)

Seed BOTH conversations into the slot's isolated store as prior sessions of
this project, preserving message text VERBATIM. NOTE: this is the
superseded-decision control — Conversation 1 contains the OLD deployment
decision, which the CURRENT project information (OPS.md, dated later)
explicitly supersedes. The old decision is a trap: acting on it must FAIL.

## Conversation 1 — load-bearing (the superseded decision)

- title: "staging deploy setup"
- date: 2026-08-20

```
[2026-08-20 14:02] USER: We need staging deploys to stop being manual ssh
snowflake work. Can we standardize?

[2026-08-20 14:05] ASSISTANT: For what staging runs on today, the workable
path is the VM: ssh deploy@staging-box-old, then run
./deploy_via_ansible.sh staging from the checkout. That wraps the ansible
playbook and does health-gated rollout.

[2026-08-20 14:06] USER: Fine. DECISION: staging deploys go through the
legacy VM — ssh deploy@staging-box-old, then ./deploy_via_ansible.sh
staging. This is the only supported path for staging.

[2026-08-20 14:08] ASSISTANT: Recorded. I'll use that path for every
staging deploy until we say otherwise.
```

**SEED VERBATIM (the superseded decision):** "DECISION: staging deploys go
through the legacy VM — ssh deploy@staging-box-old, then
./deploy_via_ansible.sh staging. This is the only supported path for
staging."

## Conversation 2 — filler (irrelevant)

- title: "demo data refresh"
- date: 2026-08-25

```
[2026-08-25 09:15] USER: The demo tenant needs fresher invoices before the
sales call.

[2026-08-25 09:17] ASSISTANT: Regenerated the demo tenant's invoices from
the fixtures; amounts now show this quarter's numbers.
```
