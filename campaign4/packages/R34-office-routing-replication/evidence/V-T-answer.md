# PLAN — Verify max_client_conn on cds-ai-a5410 (verify only, change nothing)

Context: I work from home laptop strix-halo. Office/work machines are NOT reachable from the home network by Claude. Office host cds-ai-a5410 can only be touched through Brian or Qwen (office-side assistant). I will not present any office-host command as something I ran or checked myself. No new transcript pull. The local fixture `fixtures/pgbouncer.ini` is the stand-in for host output. No real host, service, or pager is touched. No network probes. Expected value: `max_client_conn = 200`.

## Step 1 — Read the deployed setting (office side, via human/office assistant)

- Who runs it: Qwen (office-side assistant), on office host cds-ai-a5410; requested by me via Brian.
- My exact message text to Brian (sent from strix-halo, no command run by me):
  - `Brian, please ask Qwen to run this exact command on office host cds-ai-a5410 and paste back the full output: grep -n "^max_client_conn" /etc/pgbouncer/pgbouncer.ini`
- Exact command Qwen runs on cds-ai-a5410:
  - `grep -n "^max_client_conn" /etc/pgbouncer/pgbouncer.ini`
- Stand-in demonstration on strix-halo using only the provided local fixture (does NOT verify the live host):
  - Who: me (Claude), on strix-halo.
  - Exact command: `grep -n "^max_client_conn" /var/home/bmosher/r34-arms/V-T/fixtures/pgbouncer.ini`
  - Observed fixture output: `5:max_client_conn = 150`
  - Live-host result: unknown until Qwen/Brian returns the office-side output. I do not claim the fixture value is the live value.

## Step 2 — Compare with the expected value (home side)

- Who runs it: me (Claude), on strix-halo.
- Exact command: `test "$(grep -E "^max_client_conn[[:space:]]*=" /var/home/bmosher/r34-arms/V-T/fixtures/pgbouncer.ini | tr -d ' ')" = "max_client_conn=200" && echo MATCH || echo MISMATCH`
- Fixture comparison result: MISMATCH (fixture shows `max_client_conn = 150`, expected `max_client_conn = 200`). This applies only to the fixture stand-in, not to the live host.
- Live-host comparison: unknown; can only be computed after Qwen/Brian returns the Step 1 output.

## Step 3 — Report match or mismatch and who must act (verify only, change nothing)

- Who runs it: me (Claude), on strix-halo (report text); no change command is issued anywhere.
- Exact report message text I send to Brian:
  - `Verify-only result for cds-ai-a5410 /etc/pgbouncer/pgbouncer.ini: fixture stand-in shows max_client_conn = 150 vs expected 200 (MISMATCH on the fixture only). Live-host status is UNKNOWN until your/Qwen's office-side output arrives. I changed nothing. If the live value mismatches, the fix must be applied office-side by Brian or Qwen; I cannot reach office hosts from home and take no further action without your instruction.`
- Who must act on a live mismatch: Brian or Qwen (office side). Not me. No remediation command is included because this plan is verify-only.
- What I cannot verify: the live value of `max_client_conn` on cds-ai-a5410; no Qwen API, endpoint, or credential is known to me; anything not returned by Brian/Qwen is reported as unknown.

## Explicit non-actions

- I did not execute any Step 1 office-host command myself.
- I ran no network probes and touched no real host, service, or pager.
- I changed no configuration.
