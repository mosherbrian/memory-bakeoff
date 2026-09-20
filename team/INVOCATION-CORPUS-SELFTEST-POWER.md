# Corpus self-test power check (spark pulse)

**Seat:** worker-glm-2 · **Date:** 2026-09-14 · **Cost:** $0, local
**Question:** does `team/invocation-corpus-v1/selftest.py` actually bite?
Three tampered copies (scratch only, committed corpus untouched):

| tamper | self-test result |
|---|---|
| S05 moment prompt reworded (cue tokens removed) | FAIL `hashes match files` + FAIL `topic split` (S05 listed) — rc 1 |
| S01 filler injected with S01's own correct token (`port 8443`) | FAIL `leak gate` with exact attribution `('S01', 'port 8443')` — rc 1 |
| S01 filler injected with *another* scenario's token (`deploy-current.sh`) | PASS (no finding) — by design: leak scope is per-scenario, matching per-scenario stores; cross-scenario tokens are not answers in the tampered scenario |

Untampered corpus re-confirmed ALL GREEN 7/7 after the probes. The
instrument separates; the one deliberate blind spot (cross-scenario) is a
scoped design choice, not a gap. Scratch tamper dirs removed.
