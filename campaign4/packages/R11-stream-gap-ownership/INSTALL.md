# R11 per-stream research-gap-check: schema, migration, install, rollback

## Registry: campaign4/RESEARCH-STREAMS.json (held; not created by this package)

    {"schema_version": 1,
     "streams": [{"stream_id": "A", "question_id": "Q-WORK-BENEFIT", "status": "active"},
                 {"stream_id": "B", "question_id": "Q-EVALUATOR-VALIDITY", "status": "inactive"}]}

- `status` is `active` (watched), `inactive` (not watched) or `retired`.
- `retired` needs `retired_at`, `by` and `reason`. A retirement resolves only that stream's open incident.
- `stream_id` and `question_id` must each be unique.
- Anything else (bad JSON, unknown status, duplicate, retirement without its fields) makes the registry unusable. The check then keeps every existing incident, keeps R5's top-question coverage, and puts "stream registry ... unusable" into every notice, so a bad file is owned and never quiet.
- Activating B is one edit (`"status": "active"`), made only on the director's stream-B release.

## Semantics
- Each active stream has its own gap clock, incident and question-bound rest (existing REST.jsonl).
- A package quiets a stream only when it is in `worker`/`verify` and its records bind it to that stream's question. If a record also names a `stream_id`, that id must match the registry, or the binding is contradictory (UNKNOWN).
- A stream removed from the file without a retirement record keeps its incident open.
- The 30 min (Tern) then 15 min (Claude) ladder, the escalation ledger, the dedupe and the state file are unchanged.

## Migration
Gap state stays keyed by question id, so adopting the registry does not reset any clock. An R5 gap for Q-WORK-BENEFIT continues as stream A's gap (tested: test_r11_migration_keeps_legacy_clock). Order: install the new bytes first, which is a no-op while no registry exists, then create the registry.

## Install (after independent PASS and director release, exact reviewed bytes)
    cp -p ~/.config/agent-deck/research-gap-check ~/.config/agent-deck/research-gap-check.bak-R11
    install -m 755 candidate/research-gap-check ~/.config/agent-deck/research-gap-check
    cp RESEARCH-STREAMS.proposed.json ~/memory-bake-off/campaign4/RESEARCH-STREAMS.json   # separate director step
The service and timer are unchanged (same bytes as R5), so no daemon-reload is needed. The next 5-minute tick uses the new file.

## Rollback
    install -m 755 ~/.config/agent-deck/research-gap-check.bak-R11 ~/.config/agent-deck/research-gap-check
Leave RESEARCH-STREAMS.json in place or move it aside: R5 code ignores it. The state file is compatible both ways (same keys), so open incidents and clocks survive a rollback.
