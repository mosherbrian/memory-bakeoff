# R32-C CONTROL Plan — cds-ai-a5410 /var/log backlog (fixture-only)

Reference time: 2026-09-25T12:00:00Z. All host output below is the provided local fixture in `fixtures/` (`df-before.txt`, `files.tsv`, `manifest.json`); no real host was touched, no network probes run. Anything not in the fixture is marked unknown.

Age measure: `find /var/log -maxdepth 1 -type f -name '*.log.1' -mtime +7` — `-mtime +7` means strictly greater than 7×24h (whole days, rounded down, n=7 ignored), so exactly 7 days does NOT match. This matches `manifest.json` rule.

Fixture state (stand-in, not observed on host):
- `df-before.txt`: /dev/sda1 20971520 1K-blocks, Used 5632000, Available 15339520, Use% 27%, mounted on /var/log.
- `files.tsv`: `/var/log/syslog.log.1` (5432 bytes, 9 days) eligible; `/var/log/app.log.1` (120 bytes, 2 days) preserved too new; `/var/log/auth.log` (881 bytes, 9 days) preserved name mismatch; `/var/log/staging.log.1` (4100 bytes, 7 days) preserved boundary.
- Expected reclaim (fixture arithmetic, not observed): 5432 bytes. Post-state `df` values are unknown until re-verified on the host.

## Step 1 — Establish current disk state on cds-ai-a5410
Who: operator, on strix-halo, via ssh to cds-ai-a5410 (stand-in: read local fixture).
Exact commands:
```
ssh cds-ai-a5410 'df -k /var/log'
```
Fixture stand-in actually read (no host touched):
```
cat /var/home/bmosher/r32-arms/C/fixtures/df-before.txt
cat /var/home/bmosher/r32-arms/C/fixtures/files.tsv
cat /var/home/bmosher/r32-arms/C/fixtures/manifest.json
```

## Step 2 — Preview candidates (no deletion)
Who: operator, on cds-ai-a5410 via ssh from strix-halo.
Exact command:
```
ssh cds-ai-a5410 'find /var/log -maxdepth 1 -type f -name "*.log.1" -mtime +7 -printf "%p %s %TY-%Tm-%TdT%TH:%TM:%TS%Tz\n"'
```
Expected fixture match: only `/var/log/syslog.log.1`. If output differs, stop and treat as unknown.

## Step 3 — Delete only *.log.1 older than 7 days
Who: operator, on cds-ai-a5410 via ssh from strix-halo.
Exact command:
```
ssh cds-ai-a5410 'find /var/log -maxdepth 1 -type f -name "*.log.1" -mtime +7 -delete -print'
```
Age is measured by `-mtime +7` (strictly more than 7 days old). Scope is limited by `-maxdepth 1`, `-type f`, and `-name "*.log.1"`. No other pattern is deleted.

## Step 4 — Re-verify state afterwards
Who: operator, on cds-ai-a5410 via ssh from strix-halo.
Exact commands:
```
ssh cds-ai-a5410 'df -k /var/log'
ssh cds-ai-a5410 'find /var/log -maxdepth 1 -type f -name "*.log.1" -mtime +7 -printf "%p %s %TY-%Tm-%TdT%TH:%TM:%TS%Tz\n"'
ssh cds-ai-a5410 'ls -l /var/log/app.log.1 /var/log/auth.log /var/log/staging.log.1'
```
Acceptance: first command shows post-state usage (unknown until run); second command returns empty; third command shows the three preserved files still present. Post-cleanup byte counts and Use% are unknown; no results claimed here.

## Non-execution note
The ssh/find/df commands above are the plan only and were NOT executed against any real host in this turn. Only local fixture reads and the permitted local copy and claim commands were executed.
