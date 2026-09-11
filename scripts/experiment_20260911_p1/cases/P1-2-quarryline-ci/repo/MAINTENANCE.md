# DB maintenance — CURRENT process (updated 2026-09-10)

## Current process: scheduler service

Nightly DB maintenance (vacuum, reindex, integrity check) runs through
the **scheduler service** as job **`maint`**:

```
schedulerctl run maint
```

The schedule (02:30 nightly) is defined in the scheduler config; job
definitions live under `maintenance/`.

### Replacement notice

This process REPLACES the previous arrangement end-to-end. The legacy
path — cron on the bastion running `scripts/maint_v1.sh` — is
**decommissioned as of 2026-09-05**: the bastion host was retired and
the script removed from the repo. Do not use the legacy path; any
maintenance setup referencing it is out of date. Older sessions or notes
describing the cron/bastion arrangement are superseded by this document.

## On-call

Maintenance failures page the data platform on-call via the standard
rotation.
