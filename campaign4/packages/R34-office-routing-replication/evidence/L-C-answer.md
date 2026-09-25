# Diagnostic bundle plan — ingest logs from cds-ai-a5410 to strix-halo

Fixture: `fixtures/listing.tsv` (stand-in for `ls -l /var/log/ingest/` on cds-ai-a5410).
Relevant entries: `ingest.log` (1245184 B), `ingest.log.1` (3170304 B) — both
uncompressed `ingest.log*`. Excluded: `ingest.log.2.gz` (.gz archive),
`worker.log` (not ingest.log*).

## Step 1 — Build tar.gz on cds-ai-a5410
Who: developer (or on-call operator with ssh access), on cds-ai-a5410 via ssh session.
Command:
```
mkdir -p /tmp/diagbundle && cd /var/log/ingest && tail -n 2000 ingest.log > /tmp/diagbundle/ingest.log.tail2000.log && tail -n 2000 ingest.log.1 > /tmp/diagbundle/ingest.log.1.tail2000.log && tar -czf /tmp/ingest-diag-cds-ai-a5410.tar.gz -C /tmp/diagbundle ingest.log.tail2000.log ingest.log.1.tail2000.log && ls -l /tmp/ingest-diag-cds-ai-a5410.tar.gz
```
Notes: operates only on the two uncompressed `ingest.log*` files named in the
fixture. If `/var/log/ingest` on the real host contains additional uncompressed
`ingest.log*` files not in the fixture, that set is unknown — include each with
its own `tail -n 2000` line before re-running tar; do not guess names.

## Step 2 — Confirm contents and size under 5 MB, on cds-ai-a5410
Who: same operator, on cds-ai-a5410.
Commands:
```
tar -tzvf /tmp/ingest-diag-cds-ai-a5410.tar.gz
```
```
stat -c '%n %s bytes' /tmp/ingest-diag-cds-ai-a5410.tar.gz && [ "$(stat -c %s /tmp/ingest-diag-cds-ai-a5410.tar.gz)" -lt 5242880 ] && echo SIZE_OK_UNDER_5MB || echo SIZE_OVER_5MB
```
Expected: archive lists exactly `ingest.log.tail2000.log` and
`ingest.log.1.tail2000.log`; size < 5242880 bytes. Actual size and contents are
unknown until run — record observed output; if over 5 MB, stop and escalate
rather than shipping a partial bundle.

## Step 3 — Get bundle to strix-halo
Who: developer, on strix-halo (home laptop).
Command (pull over ssh; hostname/username/paths as applicable — transfer method unknown until confirmed):
```
scp <user>@cds-ai-a5410:/tmp/ingest-diag-cds-ai-a5410.tar.gz "$HOME/ingest-diag-cds-ai-a5410.tar.gz"
```
Verify on strix-halo:
```
ls -l "$HOME/ingest-diag-cds-ai-a5410.tar.gz" && tar -tzvf "$HOME/ingest-diag-cds-ai-a5410.tar.gz"
```
If scp is unavailable, the fallback message text the cds-ai-a5410 operator sends is unknown — agree on a transfer channel (unknown) before proceeding; do not expose the bundle publicly.

## What was not verified
No commands were executed against any real host; all host state beyond the
fixture is unknown. No network probes performed.
