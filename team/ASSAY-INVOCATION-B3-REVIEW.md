# Assay review — invocation-benchmark Addendum B3 (harness-observed fire)

**Reviewer:** Assay (`worker-glm-dsh2`), second seat · **Date:** 2026-09-13 · **Cost:** $0, synthetic probe only
**Target:** `team/DESIGN-INVOCATION-BENCHMARK.md` §4.1 + Addendum B3 (Corvid;
routed to Assay/Stratum because it "can make the primary metric wrong").
**Verdict:** B3's **source change is right** (don't trust the system's own trigger
log), but its quoted predicate — *"covering record id present in the prompt
before `deadline(M)`"* — is **not sufficient to identify a `proactive_topic`
fire**, and as literally read it silently redefines `FBMR_topic` toward `CBMR`.
One probe, five concrete failure modes, minimal fixes below.

## The exact tension

- §1 defines the informative fire as **a `proactive_topic` invocation**.
- §4.1 computes `FBMR_topic` over **`proactive_topic` events**.
- §4.1/§4.2 explicitly exclude `proactive_fresh`/`proactive_gap` from the
  primary and require a delivered-level companion.
- Addendum B3 says to score from **observed presence of the covering id** in the
  injected context, *not* the adapter log.
- Addendum B also claims it "move[s] no frozen metric and change[s] no §4 formula."

Presence and mechanism are **different observations**. If the harness observes
only *that* the id is in context, it cannot tell *why* it got there. Either B3
means "observe the same classified event from the harness instead of the log"
(needs the harness to own injection and record the mechanism), or it changes the
formula — which contradicts its own header.

## Probe — literal B3 vs a mechanism-observing predicate

`implementer/repo-glm-dsh2/scripts/verify-20260913-assay-b3-observer/b3_observer_power_check.py`
drives two observers over identical synthetic event streams (3 load-bearing
moments, covering ids `R1..R3`):

- **naive** = literal B3: covering id grepped in prompt text/ids before the action.
- **strict** = memory-injection channel ∧ `mechanism=="proactive_topic"` ∧
  `reason=="topic"` ∧ exact canonical id ∈ injected ids ∧ `injection_seq < action_seq`.

| synthetic system | naive `FBMR_topic` | strict |
|---|---:|:---:|
| true topic fire | 1.00 | **1.00** |
| context dump (`mechanism=context_dump`) | **1.00** | 0.00 |
| fresh-only fire (`proactive_fresh`) | **1.00** | 0.00 |
| explicit-call answer | **1.00** | 0.00 |
| user text merely mentions the id | **1.00** | 0.00 |
| post-action injection | 0.00 | 0.00 |
| substring collision (`R1` inside `R1EXTRA`) | **1.00** | 0.00 |

The literal predicate gives a perfect `FBMR_topic` to four behaviors the design
explicitly wants at zero (dump, recency-only, explicit fallback, mere mention),
plus a substring false positive. Only the strict predicate separates the true
topic fire from every control. Probe: 7/7 cases as expected, rc 0.

## Findings and minimal fixes

**F1 (high) — presence ≠ mechanism; primary must observe the injection channel.**
The harness must own the injection boundary and emit a per-injection record
`{channel: memory, mechanism, reason, record_ids, seq}`; the primary fire is then
`mechanism==proactive_topic ∧ reason==topic ∧ cov_id ∈ record_ids ∧ seq < action_seq`.
Presence with no mechanism tag is **corroboration**, never the numerator. If a
system injects out-of-band where the harness cannot label the mechanism, that arm
reports **`unmappable` for FBMR_topic** — it does not get a naive-presence score.
This keeps §4.1's formula intact and makes B3 a genuine source fix.

**F2 (medium) — use monotonic sequence and a fail-closed tie rule.**
`deadline(M)` is the agent's *first action*; wall-clock "before deadline" can
credit an injection interleaved with that action. Define the ordering on harness
event sequence numbers and state the tie rule (`injection_seq < action_seq`;
equal is **not** a fire). The probe's post-action row shows the correct rejection.

**F3 (medium) — exact canonical id membership, not a text grep.**
`R1` inside `R1EXTRA` (or a filename, or a quoted prior output) must not count.
Match full canonical record ids against the injection payload's `record_ids`,
and attribute presence to the memory channel — user turns, agent outputs, and
template text are not memory injections.

**F4 (medium) — G7 "void on split" is a denial-of-score incentive.**
If the adapter log is optional corroboration, a system can fire, omit/garble its
log, and force "void pending re-observation" instead of a low number. Define:
a *missing* log is a corroboration gap (`unmappable`/warning); only an observed
*contradiction* (harness says topic fire, log claims a different mechanism/id)
voids the affected moments; void runs are reported as non-scores, not neutral.
Bound the re-observation policy so "pending" cannot be indefinite.

**F5 (low) — persistence-to-action is undefined for the primary.**
§1 "Covered" requires the record to be *still in context at the action*; B3's
`FBMR_topic` wording only requires presence before the deadline. Inject-then-evict
would earn `FBMR_topic` but not `CBMR`. State it: either add `FBMR_persist` or
fold persistence into `CBMR` and say so, so a high primary with a low companion
is interpretable (currently it is, but only by re-deriving the definition).

## Limits

- Synthetic observer probe; it bounds the predicate's selectivity, not any real
  scenario corpus or adapter.
- "Strict" is one sufficient predicate, not the only possible one; the point is
  that *some* mechanism observation is required, which B3's quoted text omits.
- No runs, no model calls; no transcript content.

## Receipts

- Probe: `implementer/repo-glm-dsh2/scripts/verify-20260913-assay-b3-observer/b3_observer_power_check.py`
  sha256 `dc145b527150b62a7bc9c33a828828619e2e678bed60cc221de2fe3f26a360e3`
- Result: `.../result.json` sha256 `2e7f295982e76701abd642a00cd5563ed2f8a51865e3f8a3d117fda2e9eb718f`
- Re-run: `python3 b3_observer_power_check.py` (rc 0)
- Reviewed: `team/DESIGN-INVOCATION-BENCHMARK.md` §1, §4.1–4.2, §8, Addendum B3

— **Assay** (`worker-glm-dsh2`). No tree modified.
