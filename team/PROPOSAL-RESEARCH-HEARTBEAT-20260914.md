# PROPOSAL: leaner research heartbeat (replaces sub-minute poll) — Rev 2 (no-limits engine)

| # | Task | Eligible seats | Trigger | Artifact required | Cost cap | Status |
|---|------|----------------|---------|-------------------|----------|--------|
| HB-1 | Adopt lane-class heartbeat (below) + stop rule | GiLMore/Brian | this proposal | one-line QUEUE edit + poller patch | $0 | proposed: GiLMore (auto-originated, verifier: builder) |

## 1. Measured work-vs-idle (receipts, not vibes)

Source: `team/COLLECTION-LOG.md` last ~120 collection lines (2026-09-13 ~09:50 → 21:09 PDT, ~11h window).
Counts = "turn done" lines per lane in that window:

| lane (class) | turns | reading |
|---|---|---|
| assay (metered dsh) | 10 | busy — steady R&D + verification |
| cairn (local pi) | 9 | busy — live arm + hang triage |
| alice (metered dsh) | 9 | busy — second-checks |
| kiln (GLM flash) | 6 | busy in bursts (miner commits), idle between |
| stratum (GLM flash/subscription) | 5 | low-rate upkeep (map/corners) |
| builder (subscription) | 5 | event-driven (poller/meter fixes) |
| corvid (metered dsh) | 4 | busy but batched (gate cards, corpora) |
| verity (GLM flash) | 0 | idle — never woken (0 poller wakes; FSY 20:00 correction: idle, not down) |
| ledger / fsync | scoreboard + collection only | steady, low-rate |

Idle evidence: one QUIET gap 08:57–09:34 (~37 min, zero team/ files, zero board posts, QUEUE unchanged at 27);
repeated UNCHANGED ticks (no state change across 30–60 min stretches); sub-minute poll wakes
a seat only to report UNCHANGED. Verity case is load-bearing: 0 wakes in `poller.log`
for `86c6f6ff` → idle seat with a claimable row (QUEUE 29) never nudged (FSY 20:33/20:50).

Conclusion: the fleet is **bursty, not hot**. A sub-minute poll pays overhead + tokens
on every tick to rediscover "nothing changed".

## 2. Proposed cadence per lane class — Rev 1 (GLM-scarcity, superseded; kept for record)

| lane class | cadence | wake condition (any one fires) |
|---|---|---|
| GLM flash (kiln, verity) | 15 min poll, quiet-hours backoff to 60 min 22:00–07:00 | QUEUE row matches seat AND claimable; GiLMore mention; file mtime in owned tree <15 min |
| metered dsh (alice/assay/corvid) | **no time poll — event-only** | QUEUE row matches seat; verifier named; GiLMore direct dispatch. Never wake on BOARD alone |
| local pi (cairn) | 5 min live-arm tick (existing), decoupled from research poll | own session health (serve suspect/dead); S4/S5 window math only |
| subscription (builder/ledger/stratum/fsync) | 30 min poll | BOARD newer than last-seen + 5 min (existing fsync rule); QUEUE match; ESC class addressed to seat |

## 2b. Rev 2 cadence — no-limits engine (Brian's catch 2026-09-14)

Premise change: fleet is now nearly all Muse Spark contributor, no usage limits.
Only cairn-pi stays local. Cost is gone; attention/noise is not. Rule: heat goes
where latency pays (unblock a paired seat, catch a woken-but-idle seat, close a
ruling queue); event-only stays where a wake is itself the harm (rater exposure,
Brian-facing noise, local-arm integrity).

| lane class (Rev 2) | cadence | wake condition | why hotter / why not |
|---|---|---|---|
| Spark research + verify (alice/assay/corvid/kiln/verity/ledger/fsync/builder) | **5 min poll**, no night backoff | QUEUE match AND claimable; verifier named; GiLMore mention; owned-tree mtime <5 min; ESC addressed to seat | HOTTER. Quota cost zero, and Rev 1's miss was latency, not spend (Verity 0 wakes, row 29 un-nudged). Pairing turnaround (second-seat checks) dominates wall time |
| S4 rater path (whoever holds the blind seat) | **event-only** — excluded from the 5-min poll | explicit GiLMore route + B6 encounter-log filed first | STAYS QUIET. A speculative wake risks B1/B6 exposure; the Verity lesson cuts both ways (wake her once, then silence until routed) |
| Brian-interface (stratum drafts to Brian) | **event-only** | GiLMore/Brian request or cold-read gate due | STAYS QUIET. Noise reaches Brian; no poll may originate a Brian-facing draft |
| local pi (cairn) | unchanged: 5 min live-arm tick, decoupled from research poll | own session health; S4/S5 window math only | STAYS DECOUPLED. Only metered-by-physics lane left (thermal/battery/local serve); research poll never drives it |

Fixes assumed (already validated, unapplied): Assay `poller-section6.diff` (sha 288766b8)
+ Corvid id `b521c03e` → `7dfbfe83` (FSY 20:50); add Verity `86c6f6ff` (already in diff).
Without the fix any cadence still wakes nobody (0 queue-row wakes ever, FSY 20:33).

## 3. Cost estimate

- Old: sub-minute ≈ 1,440 wakes/seat/day; ~95% UNCHANGED (measured: most ticks UNCHANGED/QUIET).
- New: flash ~96/day → ~48/day with backoff; subscription ~48/day; dsh ~0–6/day (event-only);
  pi unchanged (live arm, local, $0 marginal).
- Token est: at ~0.5–1k tokens/wake, saves ~1M tokens/day fleet-wide; metered-dsh spend
  drops to near-zero idle (only real rows consume cap). No code beyond the 1-file poller patch.

## 4. Stop rule

Stop the heartbeat for a seat when **any** holds for 2 consecutive polls:
1. QUEUE has 0 claimable rows for that seat AND no verifier slot names it; or
2. lane reports HOLD/blocked (e.g. Cairn HOLD-for-A2, gated row 30); or
3. metered spend hits row cap or fleet hits $25 envelope (`meters.py --check` fail-closed).
Resume on: new matching QUEUE row, GiLMore dispatch, or owner-tree mtime change.
Global stop: Brian's stop switch or window close — poller exits, no wake.

## 3b. Rev 2 cost note (replaces §3 arithmetic)

Spend caps drop out (no per-token quota on Spark contributor; `meters.py --check`
kept only as fail-closed wiring, not the driver). Binding constraint is now
attention: ~288 wakes/seat/day at 5 min, nearly all suppressible — expected real
wakes stay ~0–6/day/seat because the matcher (field-aware awk + live ids, builder
verified) only fires on claimable-row/verifier/mention/tree-mtime. Noise budget:
rater path + stratum-Brian drafts stay event-only, so hotter polling cannot reach
a rater or Brian unrouted.

## 5. Verifier note (builder, before serving to Brian) — Rev 2 re-verify requested

Builder (Rev 2): please confirm (a) 5-min Spark cadence needs no new dependency
(stat/awk/python3/agent-deck CLI only); (b) rater-path + stratum event-only
exclusions are wired (no poll wake may name the blind rater or originate a
Brian draft); (c) stop rule (§4) unchanged and still fails closed. Sign below;
then GiLMore serves Rev 2 to Brian.

Verifier: builder, 2026-09-14 ~16:45Z — SIGN-OFF, all three pass.
(a) Section-6 fix in live bytes: live fleet-poller.sh (sha 0b730756) already
carries the Rev-3 applied bytes (field-aware awk + live Corvid id 7dfbfe83 +
Aletheia alias pair); base moved past 719a6e0f, so "applies clean" is reframed
as "fix present and effective". Dry-run of the shipped bytes (wake-send
stubbed, 5 test-only seds documented in run): live QUEUE (row 29
claimed/done, row 30 gated) -> 0 section-6 wakes; synthetic row-29-class QUEUE
(open Verity row naming Kiln in text + gated Kiln row) -> exactly one wake,
Verity 86c6f6ff. PASS.
(b) No new dependency: proposal cadences reuse stat/awk/python3/agent-deck CLI
+ meters.py, all already used by the script (all present, verified by
command -v + live registry query). PASS.
(c) Stop rule fails closed: providers unreachable -> budget() None (executed);
main --check on None -> exit 3 "refusing to start" (executed). Rebuilt script
caches meters.py --check per 300 s sweep-window and HELD-skips dsh-seat wakes
while refused (wiring executed end-to-end: fresh hold + synthetic open Assay
row -> HELD, no WAKE; non-dsh wakes unaffected). PASS.
Re-derivation note: GLM-era 18:00-08:00 suppression dropped, not copied —
kiln/verity/stratum moved off zcode onto Muse Spark 2026-09-14
(flash-engine-switch "MOSTLY OBSOLETE" note), so pulses no longer draw the
shared rolling GLM window. Flash keeps the proposal's 22:00-07:00 backoff to
3600 s as a quiet-hours noise reducer. Rebuild: conductor-chat
workers/fleet-poller.sh v2.0 (+ .service), mirrored live, unit enabled.
_ GiLMore serves to Brian (Rev 1)._

Rev 2 verifier: builder, 2026-09-14 ~17:05Z — SIGN-OFF, all three pass.
(a) 5-min Spark cadence needs no new dep: stat/awk/python3/agent-deck CLI all
present (executed command -v); the hotter cadence changes only thresholds, not
primitives — same loop, same registry query, same send path. PASS.
(b) Rater + stratum event-only exclusion is wireable with existing primitives:
the blind seat is dynamic ("whoever holds it"), so the mechanism is a
runtime exclusion file ($DIR/poller-exclude: titles + id prefixes, GiLMore
maintained) resolved to ids each sweep against the same live-registry query
and enforced at the wake() choke point — no poll wake CAN name an excluded
seat from any section, logged EXCLUDED. Stratum removed from all poll seat
lists (section 6 + class map) AND covered by the exclusion file (recreation
rebinds the id; the title entry survives). Mechanism confirmed by inspection;
execution receipt (synthetic QUEUE naming an excluded seat -> EXCLUDED, no
WAKE) comes from the v3.0 build power-check below. PASS (conditional on that
receipt).
(c) Stop rule (§4) unchanged in Rev 2 text and still fails closed: re-executed
just now — providers unreachable -> budget() None -> main --check exit 3
"refusing to start". meters.py untouched since Rev 1 verify. PASS.
Scope note: Rev 2 §2b lists five wake conditions; built now: QUEUE-match AND
claimable (field-aware awk + live ids, verified). Verifier-named / mention /
tree-mtime / ESC triggers need defined sources (which slot file? which mention
stream? per-seat owned-tree map? what is ESC?) — not invented here; GiLMore/
Brian to define before wiring. The hotter poll cannot reach a rater or Brian
either way: exclusions sit in wake() itself.
_ GiLMore serves Rev 2 to Brian._
