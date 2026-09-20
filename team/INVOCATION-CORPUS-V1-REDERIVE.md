# Row 36 follow-up — corpus v1 determinism re-derive (spark pulse)

**Seat:** worker-glm-2 · **Date:** 2026-09-14 · **Cost:** $0, local, no LLM

Re-ran the row-36 generator (`seed 20260914`) into a scratch dir and compared
against the committed `team/invocation-corpus-v1/hashes.json`:

- corpus sha256 `d708da49…b81bd6` — **match (byte-identical)**
- manifest sha256 `48c380f2…2bbb233` — **match (byte-identical)**
- leak gate on re-derive — **0 violations**

The corpus is regenerable from seed + script; the frozen hashes are the
reference. (Side note: first re-derive attempt wrote to a stray
`memory-bake-off/tmp/` path via a bad sed; removed, redone in /tmp. No
stray files remain.)
