# Control ledger preservation incident
Tern; 2026-09-22T22:09:36.008574+00:00.
Current ledger checkpoint: control-ledger-checkpoints/20260922T220936Z/capture.json.
Original control-events.tsv left untouched. Snapshot and full hash are committed
and published independently of the mutable working ledger; no dirty-file sweep.

Confirmed now: rows424/425 byte-identical worker DISPATCHED records. User reports
one kiln runtime start22:01:28Z. Treat as duplicate recording evidence, not proof of
two dispatches and not permission to send again. Preserve both rows; future readers
must join explicit action/execution/transport receipts, not count TSV rows as effects.

Apparent row427 change: shadow observed repair-1/corvid, current file says
repairverify-1/corvid. No original-byte snapshot was kept then. Status UNPROVEN
IN-PLACE EDIT; preserve shadow notice as attributed evidence, never recreate the
alleged original and label it authentic. No actor attribution inferred.

Last committed ledger indeed e6cabb6d2f827f81b26ea9da1a614952839fafd1. Publishing
other commits did not preserve the hundreds of intervening ledger rows. This is a
publication/provenance gap I own. Today's capture proves today's bytes only. Even
periodic checkpoints cannot prove no transient edit between captures; do not claim
cryptographic append-only enforcement from this remedy.

Effective immediately: cairn never edits/deletes/reorders old TSV rows, including
wrong IDs/timestamps/duplicates. Append correction referencing original action AND
checkpoint/hash/row when available, corrected fact and raw evidence receipt. An
unproven prior edit remains unproven. Serialized controller writer, one event append
per receipt, no repeated narrative rewrites. Use host timestamps for new append
metadata; source time/provenance separate. Current active verification continues.

At director publication boundaries capture stable exact ledger bytes to a new dated
control-ledger-checkpoints directory with sha256/source capture metadata, stage ONLY
that immutable snapshot and publish alongside completed decisions. Compare previous
checkpoint as byte prefix; divergence is a reported finding, never silently overwrite
the older snapshot. Do not stage the shared live ledger opportunistically or claim a
partial/in-flight row completed. Cairn supplies raw correction/dispatch receipts;
Tern owns checkpoint publication. No extra model polling or compaction mechanism.

This is immediate preservation, not the ultimate control store. The durable software
event ledger must eventually own authoritative events/append rejection and explicit
correction links, under its independently verified adoption contract. Until then the
TSV is a fallible manual record reconciled against pinned receipts/runtime/artifacts.
No candidate acceptance, live authorization or new allocation follows from it.
