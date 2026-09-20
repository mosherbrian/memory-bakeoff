# Cache findings, and a retraction

**2026-09-15, ~23:30 PDT.** Follow-up to `FLEET-SPEND-20260914.md` (Rev 2) and
to the Ledger synthesis. Written for the morning; **nothing has been changed on
the fleet** — dispatch is stopped, marker in place, all lanes idle.

Three things were measured tonight. One kills team item 6, one narrows item 1,
and one retracts a number I gave Brian an hour earlier that was wrong by more
than an order of magnitude.

---

## 1. MEASURED — the cache lifetime is ~150s, and it is not guaranteed

Three independent ladder runs, one session each, 24k-token stable prefix. Every
call re-writes the cache, so each rung measures the gap that preceded it. Hit
rates read from `opencode.db`, not from client-side usage events.

| gap | run 1 | run 2 | run 3 |
|---|---|---|---|
| 45s | 99.6% | | |
| 60s | 99.5% | | |
| 90s | 99.4% | | |
| 120s | 99.8% | | |
| 130s | | **0.0%** | |
| 140s | | 99.3% | 99.0% |
| 150s | | 99.7% | |
| 160s | | 0.5% | 0.0% |
| 170s | | 0.0% | |
| 180s | 0.0% | | |
| 300s | 0.0% | | |

**The cliff sits between 150s and 160s.** It is a cliff, not a decay — 99.7% at
150, 0.5% at 160. Confirmed at both ends by separate runs.

**The one anomaly matters.** A 130s gap missed completely while 140s and 150s
hit in the same run. So the lifetime is not a hard guarantee: something can
evict earlier, probably gateway-side pressure. Any cadence built on this needs
real margin, and even then some misses will happen.

Corollary: **the team's ≤60s figure for item 1 is sound**, with roughly 2.5×
margin. Note also that every call re-primes, so a lane pulsed inside the
lifetime stays warm indefinitely.

## 2. MEASURED — item 6 is dead

Two arms, identical prompts and gaps, per-arm config in the probe's own
directory so the live fleet was untouched:

| | prime | +30s | +6min |
|---|---|---|---|
| A: current config | 0.0% | 99.4% | **0.0%** |
| B: `setCacheKey: true` + `promptCacheRetention: "24h"` | 0.0% | 99.5% | **0.0%** |

Byte-identical behaviour. The knobs are real — they are in the client's own
schema (`promptCacheRetention: enum ["in_memory","24h"]`,
`promptCacheOptions: {type, ttl:"30m"}`, `promptCacheKey`) and
`provider.<name>.options.setCacheKey` is documented — but the Go gateway does
not honour them for Muse.

**So item 6 cannot beat item 1.** The hoped-for "keep the cache alive by
configuration" route is closed.

Related, and unexplained: `x-opencode-session` appears **zero times** in the
client bundle, though the Go docs instruct clients to send a stable session id
in that header "so we can optimize routing and prompt caching". If the gateway
keys its prefix cache on that header, its absence would explain both the Muse
decay and why neither of our models matches the documented ~5 min TTL. Worth
someone else's eyes — it lines up with Corvid's gateway-TTL addendum.

## 3. RETRACTED — "event-driven saves 81%"

I told Brian that going event-driven would save **$6.16 of $7.63 (81%)** of the
miss cost. **That is wrong.** The correct figure at the measured cache lifetime
is about **6%**.

The error: I clustered calls into "work bursts" using a **6-minute** gap
threshold, then counted one cold miss per burst. But 6 minutes was never
measured — I chose it because it was the band where the idle pulse fires. The
cache actually dies at ~150s, so bursts must be clustered there instead.

| clustering threshold | bursts | saving vs 352 misses |
|---|---|---|
| 120s | 411 | **−17%** (worse than now) |
| **150s — measured** | **330** | **6%** |
| 180s | 285 | 19% |
| 360s — my guess | 62 | 82% |

The saving is entirely an artefact of the threshold. At the measured value there
is almost nothing to reclaim, because **the work is genuinely spaced wider than
the cache lives**:

| lane | calls | bursts @150s | misses now |
|---|---|---|---|
| glm | 506 | 79 | **79** |
| implementer (kiln) | 329 | 61 | 63 |
| reviewer (verity) | 298 | 63 | 53 |
| memory-bake-off (fsync) | 245 | 62 | 35 |
| conductor-chat (builder) | 346 | 62 | 56 |
| proposal-drafter (ledger) | 417 | **3** | 66 |

`glm` has 79 bursts and 79 misses — **every miss is already its own genuine work
burst.** There are no surplus pulse-driven misses to delete. Event-driven would
not help it at all.

`proposal-drafter` is the opposite: 417 calls in 3 bursts, i.e. near-continuously
active and genuinely warm. It is the one lane event-driven clearly helps.

**This is the second time tonight I overstated a saving by choosing a
convenient threshold.** The first was reporting a token share (94.6%) as a
dollar share (66.7%), caught by fsync. Both errors ran the same direction.

## 4. What this does to Brian's keep-warm idea

Brian proposed a separate process, outside the OpenCode sessions, that refreshes
each lane's cache on a cache-preserving cadence without injecting anything into
the team's context — so the fleet can be event-driven while caches stay warm.

Given §3, **this is now the only lever that helps.** If real work is naturally
spaced 2–5 minutes apart — and §3 says it is — then nothing but an out-of-band
refresh avoids the miss.

Economics, at the measured numbers:

- a cold miss: 210,153 tokens × $0.10/M = **$0.021**
- a keep-warm refresh: the same context as a *cache read* at $0.002/M, plus a
  little output = **~$0.0005**
- at a 100s interval (inside the ~150s lifetime, with margin): 36 refreshes per
  hour per lane = **~$0.018/hour/lane**

So warming pays for any lane that would otherwise miss more than about once an
hour. Tonight the Muse seats missed **7–17 times each per 4.6 h** (~2–4/hour).
**Warming wins, by roughly 2–4×** — much better than the "costs more than it
saves" I said earlier, which used a 40s interval and the wrong burst model.

**The hard part is not cost, it is prefix fidelity.** A prompt cache is keyed on
the exact serialised prefix. A refresh only works if it reproduces byte-for-byte
what the lane will send next — same system prompt, same tool schemas, same
message formatting. Reconstructing that from `opencode.db` is fragile; get it
wrong and you write a *second* cache entry while the lane still misses, paying
twice for nothing.

The robust shape is a **local pass-through proxy** in front of
`https://opencode.ai/zen/go/v1`: it records the last real request body per
session and re-sends it on a timer, so the prefix is identical by construction.
That also delivers the thing missing all of 2026-09-14 — **visible per-request
status.** Every refusal that morning arrived as a stream error inside OpenCode
and never reached ACP, which is why lanes hung silently and hours went into the
wrong hypotheses. A proxy would have shown the 429s immediately.

Costs to weigh: it puts a new component in the path of every lane (must fail
open), and it needs `baseURL` override support in the provider config.

## Recommendation

**Measure a clean day before changing anything.** Specifically:

1. Tonight's sample is contaminated — every lane was stopped and started about a
   dozen times during the migration, and each restart is a guaranteed cold
   session.
2. The burst analysis in §3 turns on a threshold I have already got wrong once,
   and the bracket (120–180s) swings the answer from −17% to +19%.
3. The decision rests on a number I have misreported twice in one evening.

The fleet is shut down and nothing is burning, so a day of representative
traffic costs nothing to acquire and would settle this better than more
arithmetic from me.

If the team wants to act now rather than wait, the ranking on current evidence
is: **item 2** (free GLM window for background seats) and **item 3** (spread to
1.2/MiMo budgets) are unaffected by any of this and can proceed; **item 1**
(≤60s Muse pulse) is confirmed viable but conflicts with the sprint retro's
request to stop idle polling; **Brian's keep-warm proxy** is the option that
satisfies both, at the cost of building and trusting a new component; **item 6**
is closed; **item 5** (compaction) remains declined.

---

Probe artefacts: `~/cache-edge-probe.md`, `~/cache-edge-probe-coarse.md`,
`~/cache-edge-fine.md`, `~/cache-retention-probe.md`. Probe cost for the whole
evening: a few cents.
