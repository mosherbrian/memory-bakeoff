# R18 install / rollback (HELD — do NOT apply without Tern exact-byte activation release)
Scope: candidate/ only. inputs/ immutable; no live install in author phase.
1. Back up live state + REST: cp REST.jsonl, state.json, timer/unit files.
2. Activation (only on release): copy candidate/research-gap-check over installed path byte-exact; keep timer/service unchanged (5-min calendar reused; no new daemon).
3. Append migration rows from candidate/migration-example/REST.append.jsonl with bound receipts under <campaign>/receipts/; never rewrite old rows.
4. Verify: run tests/test_r18_rest_policy.py offline (stub transports); witness phase runs ONE real timer tick on isolated inputs.
5. Rollback: restore backed-up checker + REST.jsonl + state.json; appended migration rows may remain (append-only) but expired rests resume gap ladder; incident identity/clocks preserved via state.json.
Receipt note: a receipt proves a recorded commitment, NOT executed work.
