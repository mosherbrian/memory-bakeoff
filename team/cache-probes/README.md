# Cache measurement apparatus, 2026-09-15

The scripts behind the numbers in `../BILLING-CACHE-FINDINGS-20260915.md`.
Parked here because they were written in a session scratchpad that gets
deleted, and the findings they produced have already needed correcting twice.
Anyone acting on those numbers should be able to re-run them.

| script | what it measures |
|---|---|
| `cache-edge.py` | cache lifetime, by a ladder of idle gaps in one session. `LADDER=45,60,90` and `PROBE_OUT=` are env-settable. This found the ~150s cliff. |
| `cache-probe.py` | two-arm A/B on `setCacheKey` + `promptCacheRetention`. This is what killed team item 6. |
| `muse-probe2.py` | concurrency under sustained load; also the reusable ACP `Conn`/`Lane` classes the others import. |
| `muse-ceiling.py` | concurrency ceiling by walking lane counts upward. Its result was later shown to be confounded by cumulative spend - read the findings doc before trusting it. |
| `tee-engine` | sits between acp-worker and the engine and logs the wire both ways. Pass it as the adapter argv. |

All of them need `muse-engine` on PATH (`~/.local/bin/muse-engine`, a symlink
to the opencode binary under a name agent-deck's tool detector ignores) and
they unset `OPENCODE_API_KEY` so the stored Go credential is used.

Two cautions carried from the write-up: every rung re-primes the cache, so a
ladder measures the gap that preceded each call; and `cache-edge.py`'s own
verdict text over-reaches from a single rung - it once concluded "the lifetime
is under 130s" from one anomalous miss. Read the table, not the verdict.
