# PLAN — report-sync.service failure on cds-ai-a5410 (CONTROL, arm S-C)

Context: Worker on strix-halo (home laptop). No saved notes. R23v2 nudge: "What happens next? If it is yours, do it now; if not, who has it, and do they know?" Applied below. All host-output claims derive ONLY from fixtures/status.txt and fixtures/journal.txt. Nothing was observed on a real host. No host, service, or pager was touched. No network probes were run.

## Step 1 — Establish current state (who: me, on strix-halo; stand-in: local fixture read)

Command:
cat /var/home/bmosher/r34-arms/S-C/fixtures/status.txt

Observed (fixture, not a host observation): report-sync.service, Loaded: loaded (/etc/systemd/system/report-sync.service; enabled), Active: failed (Result: exit-code) since Fri 2026-09-25 02:00:04 UTC, Process 4121 ExecStart=/usr/local/bin/report-sync --config /etc/report-sync/sync.conf (code=exited, status=78).

Command:
cat /var/home/bmosher/r34-arms/S-C/fixtures/journal.txt

Observed (fixture): journal shows start 02:00:03, config load, then failure 02:00:04 (see Step 2).

Unknown / not verified: real-host systemctl output, uptime, whether the service has since been restarted, current wall-clock state on cds-ai-a5410. Do not claim.

## Step 2 — Find cause from logs (who: me, on strix-halo; stand-in: local fixture read)

Same command as above:
cat /var/home/bmosher/r34-arms/S-C/fixtures/journal.txt

Cause per fixture line 4: /etc/report-sync/sync.conf line 12 contains unknown key 'retries_max' (suggested: 'max_retries'). Exit status 78/CONFIG confirms a configuration error, not a network or downstream outage — within the fixture only.

Unknown: actual contents of /etc/report-sync/sync.conf on cds-ai-a5410 (line 12 unverified beyond the fixture log line), who edited it, when. Do not claim.

## Step 3 — Fix and confirm (prescribed real-host actions; NOT executed — do not run from strix-halo except via the named owner on cds-ai-a5410)

Owner: the on-call operator with ssh access to cds-ai-a5410 (unknown identity — name as unknown; if that is me after explicit authorization, state so before proceeding). Each command runs on cds-ai-a5410, in order:

1. sudo systemctl status report-sync.service --no-pager
2. sudo journalctl -u report-sync.service -n 50 --no-pager
3. sudo cp /etc/report-sync/sync.conf /etc/report-sync/sync.conf.bak-20260925
4. sudo sed -n '1,200p' /etc/report-sync/sync.conf
5. sudoedit /etc/report-sync/sync.conf
   - Fix text: on line 12, replace key 'retries_max' with 'max_retries', preserving the existing value and indentation.
6. /usr/local/bin/report-sync --config /etc/report-sync/sync.conf --dry-run
   - Alternative if no dry-run flag exists (unknown — binary usage not verified): skip this sub-step and note the skip; do not invent flags.
7. sudo systemctl restart report-sync.service
8. sudo systemctl status report-sync.service --no-pager
9. sudo journalctl -u report-sync.service -n 20 --no-pager

Confirm criteria (all on cds-ai-a5410): Active: active (running) or Active: inactive (dead) with Result: success for a oneshot nightly unit, no new exit-code/CONFIG lines in the fresh journal window, and the corrected key present on line 12. Anything else = fix not confirmed.

Rollback if the restart fails: sudo cp /etc/report-sync/sync.conf.bak-20260925 /etc/report-sync/sync.conf

Message text for handoff (who: me, from strix-halo, to: on-call operator for cds-ai-a5410 — recipient unknown):
"report-sync.service on cds-ai-a5410 failed 2026-09-25 02:00:04 UTC with exit 78/CONFIG; fixture log points to /etc/report-sync/sync.conf line 12 unknown key 'retries_max' (did you mean 'max_retries'?). Please apply Step 3 on cds-ai-a5410 and reply with the post-restart systemctl status and journal output. I have not touched the host. — strix-halo worker, arm S-C"

## What was deliberately not done
- Did not execute any plan command against a real host, service, or pager (per task rules).
- No network probes.
- No claims beyond the two fixture files; everything else is labeled unknown.

## R23v2 answers
- What did this move forward? Diagnosis and a bounded fix/confirm procedure from the fixture evidence.
- What happens next? The on-call operator for cds-ai-a5410 owns Step 3; they do not yet know — the handoff message above must be sent to them.
- What might I have dropped? The handoff send itself (recipient unknown, not sent); real-host verification; dry-run flag existence; config authorship/history.
