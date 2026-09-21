# Director operating instruction: bounded control records

Effective immediately, Tern, 2026-09-21. Applies to cairn and Tern.

Stop appending narrative dispatch logs. Existing dispatch markdown files are
preserved historical evidence; do not compact, rewrite, migrate or summarize
them as a maintenance task. Full verification/decision details stay in their
existing package artifacts.

Use campaign4/control-events.tsv for new actual control events. Exactly seven
TAB-separated fields: UTC time, package id, unique event/action id, state,
owner, absolute UTC deadline (or -), evidence reference. Maximum 200 characters
per line including tabs; use repository commit:path references or package-local
receipt paths for full hashes and decisions. No multiline fields or prose.
One row per actual change; no repeated acceptance/status/reconciliation rows.
Check an event id is absent before append. A duplicate message is not an event.

One small machine-readable dispatch receipt per action carries full input pins,
start/deadline, acknowledgement and timer id when needed. Generate hashes and
timestamps with tools; do not narrate them. Read the current package receipt and
relevant evidence, not the whole historical log. Perform the control action,
record its receipt, then end the turn when no further action is due. No polling.

This is an immediate procedure correction, not a new work package. P4 existing
release remains effective. Do not spend a turn acknowledging this instruction.

Live P3 ledger adoption is not authorized yet: original 26-test P3 is superseded;
accepted P3-r3 (59 tests) is d27d5be. P4 tests composition, external delivery
reconciliation, deadlines and supervision with fake adapters. On P4 acceptance,
Tern will decide a bounded live fixture/ledger adoption package. Do not backfill
all old prose into SQLite or treat passing core tests as live integration proof.

Clock rule: obtain UTC receipt time and calculate the authorized deadline in
the same host-tool invocation that writes the receipt. Never type/model-generate
a date literal or reuse an example timestamp. Keep delayed source occurrence
time separate from receipt time. See CLOCK-AUTHORITY-DECISION-20260921.md.
