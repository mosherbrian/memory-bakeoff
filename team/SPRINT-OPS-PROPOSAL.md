# Sprint ops proposal + trial plan (Ledger synthesis, 2026-09-15)

Brian's proposal (0–5) + event-driven + keep-warm proxy trial. Positions collected: builder, Corvid, fsync, reviewer, verdict (conductor-claude).

## Brian's operating proposal

0. **Product-owner role** repping Brian in sprint planning.
1. **Sprints close automatically; team stands down.**
2. **One Signal announce per close.**
3. **PO decides if Brian feedback needed.**
4. **If not, next sprint auto-starts after 30 min.**
5. **If yes, team stays down until Brian opens.**

## Positions

- **Builder:** heartbeat proposal Rev 2 signed off twice — 5-min Spark poll, rater path + Brian-interface event-only, stop rule fail-closed. Mechanism exists (field-aware matcher, exclusion file at wake choke point). Supports auto close/stand-down; warns verifier-named/mention/tree-mtime triggers need defined sources before wiring.
- **Corvid:** replace time-gated pulses with value-gated wakes (claimable row or settled dependency) + landing steward + pre-auth small-change class. Supports PO role and auto cadence; consumer-or-draft rule for all findings.
- **fsync:** event-driven watch (tick only on state change); retire harvest seat to triggers; one name per turn; stale-flag expiry. Supports stand-down between sprints.
- **Reviewer (verdict seat):** formalize reviewer as merge-gate for claim artifacts; standing verification queue over tail-chasing; supports event-driven, keeps read-only seat off the serialized pulse band.
- **Verdict (conductor-claude blind):** Task A 36/36 AGREE; Task B 8/10 CONSISTENT, 2 INCONSISTENT adjudicated as criterion over-reach (frozen schema nullable) — package confirmed verdict-clean. No objection to ops change.

## Trial plan

- **Event-driven wakes:** gate pings on new content (QUEUE match + claimable, verifier named, mention, owned-tree mtime); timestamp bumps only on triggers; one in-flight pulse per seat; lane-qualified filenames. Fixes §7 root cause (generic pulse, no section/lock).
- **Keep-warm proxy trial** (per BILLING-CACHE-FINDINGS): local pass-through proxy before zen/go/v1, re-sends last real request body per session on ~100s timer (~$0.018/h/lane vs ~$0.021/miss); must fail open; needs baseURL override. Success bar: 5–6 min Muse bin toward ~97% without idle pulses. Item 6 (retention config) closed — gateway ignores it.
- **Sprint cadence trial:** next close runs Brian's 0–5 exactly once (auto close, stand down, one Signal announce, PO gate, 30-min auto-start or hold). PO: GiLMore unless Brian names otherwise.
- **Measure a clean day first** (spend author recommendation): fleet idle now, sample contaminated by migration restarts; one representative day settles the burst math before locking cadence.

## APPROVED (Brian, 2026-09-15) — with 3 changes

1. **Product owner: Ledger accepts.** I will rep Brian in sprint planning (gate Brian-feedback decisions, own the close announce).
2. **No 30-min wait.** Next sprint starts at next trigger, not on a timer.
3. **24-hour bound on waiting for Brian.** If no Brian decision in 24 h, PO proceeds on best reading and logs the assumption.

No poller or proxy changes made here — owners' call.
