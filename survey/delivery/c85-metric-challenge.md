# c85 — challenging the seven-day fleet metric definitions (Corvid)

**corvid · 2026-09-26 · delivery c85.** Signed opinion; existing local logs only. Confidence
**medium**. Evidence used: `campaign4/liveness-reconciliation-20260923/` (`watcher-units.json`,
`watcher-journal.json`, `campaign-timers.json`, `registry.json`, `delivery.json`, `decision.json`).

**Provenance caveat first.** These logs are 22–23 Sep, a *different regime* (transient 45-min
watchdog, recorded rest) and may not cover the seven-day window. Where they don't, record
**missing/unobservable**, do not substitute zero.

**1. Attribution: manual wakes ≠ timers ≠ dispatch.** `delivery.json` shows explicit manual dispatches
(`wake … -> started`, `notify-claude … delivered`), while `watcher-units.json` shows a **timer**
(`OnActiveSec/OnUnitActiveSec=45min`) that fires on its own. A "manual intervention" count that
includes timer/notification emissions overcounts. Count only wakes/notifies carrying an actor id, and
dedupe per episode.

**2. Idle minutes ≠ alarm duration.** The 45-min cadence is interval, not uncovered idle. The 23 Sep
alarm was a **FALSE POSITIVE against legitimate rest** (`decision.json`: `pause_required:false`;
cause = silence-only watcher at closeout). Idle must require an **open deadline** AND **no eligible
independent task** AND **no recorded rest**; a watcher tick alone is not idle.

**3. Repeated emissions ≠ repeated failures.** The journal repeats
`moving (changed=yes active=0)` every ~45 min — one condition observed many times, not N failures.
Count **distinct causal episodes** by state transition. Also treat the persistent
`changed=yes` with `active=0` as suspect: the watcher may report churn that is not real state change.

**4. Idle observability is unproven.** `registry.json` `status` (idle/waiting) is not activity, and
`last_activity_at` was **stale** (2021-09-21) across seats. An idle metric from that field is wrong;
without an explicit heartbeat, mark idle **unobservable**, not zero.

**5. Classify by cause, not seat.** The recorded class was *silence-only watcher during legitimate
rest* — not a failure. Use classes: legitimate rest, blocked external dependency, missing dispatcher,
false alarm, actual uncovered idle.

**Strongest cheap operational measure.** **Distinct confirmed uncovered-idle episodes** (open
deadline ∧ no eligible task ∧ no recorded rest), counted once per transition with start/end and
responsible dispatcher, plus **attributable manual interventions** deduped per episode. Extract from
the watch journal transitions + decision/delivery receipts + agent-deck snapshots; no new
instrumentation.

**One failure mode.** The watcher's **silence-is-success ambiguity** (`state.json` absent → falls
through to silence after recognizing valid rest) means absence of alarm cannot be scored as "no
idle." The baseline must record **unobservable** distinctly, or it will credit both false positives
and false negatives as clean.
