# Code review of the live code — 2026-09-22

**Filed by** Claude (observer), at Brian's request. **Class:** review findings
for the director. Nothing here is fixed; the fix, order and packaging are yours.

**Scope, stated plainly.** The review compared each accepted package with its
parent and read every function the changes touch:

- `P5-r2-atomic-authority/src` against `P5-clock-ingress/src`
- `P6-r9-observer-lifetime/src` against `P6-r8-case-execution/src`

It is NOT a review of every line of the 4,800 in the two live folders.

**How each finding was checked.** A review agent found them; I then read the
code for all ten. Every one is present in the code as described. None has been
shown by a failing test yet — the first job for each fix is a test that fails
on the current code.

## Serious — silent, or hits the next live cases

1. **The host timer backstop checks the wrong case.**
   `P6-r9/src/r3harness/harness.py:340-342` builds the callback argv with
   `--db` and `--action` but no `--qid-cb`, so `timer_callback` uses its
   default `qid="P6F"` (line 95, 983). `case_entry.py:465,999` runs the case as
   `P6C`. The timer fires, calls `driver.on_deadline(aid, "P6F")`, and overdue
   P6C work is never interrupted. Same class as `E_TIMER_CREATE`: a part that
   exists and is never exercised live.

2. **A rolled-back write leaves a verdict marked as seen.**
   `P5-r2/src/store.py:180-189` adds each event_id to the in-memory
   `seen_events` inside the loop, before the next event's duplicate check. If
   the decide raises `E_DUP_EVENT`, SQLite rolls back but `seen_events` keeps
   the verdict id. Every later retry of that verdict returns
   `duplicate-ignored` (store line 86, ingress line 577) until the store is
   reopened, so the verdict is never persisted.

3. **The verifier wait is measured from the worker's dispatch.**
   `harness.py:532-534` sets `esc_deadline = t0 + escalation_window_s`, with
   `t0` the worker dispatch time; line 750 uses it as the verifier's bound.
   `verify_window_s` (line 255) is never read. A worker that finishes after the
   window leaves the verifier 0 s: one poll, `verifier-no-end`, escalation to
   tern (line 752).

4. **One slow normal turn is recorded as a failure plus a success.**
   First run: `_finish(... "no-end", lat)` with `lat == []` makes
   `_write_latency` (line 810) append a synthetic `no-end-failure` row. The
   reattach then appends the success row to the same file (mode `"a"`). A
   normal delayed completion counts in the failure denominator.

5. **A decide sent with a non-terminal-maker event is dropped silently.**
   `store.py:95-98` applies the atomic payload only when `event["type"]` is in
   `TERMINAL_MAKERS` (line 17) and disposition is None. `ingress.py:502-525`
   `_check_atomic_pair` only requires a terminal post-phase. So
   `append({type: "accept"}, atomic={"decide": ...})` on a COMPLETE package
   passes ingress (post-phase COMPLETE), and the store commits the accept and
   discards the decide without error. Same for an atomic `hold`, which has no
   pair check at all.

6. **A second decide replaces the first.**
   `lifecycle.py:378-396` (`DECIDE`) has no `disposition is not None` check;
   `DECISION_TASK` directly above it (line 367) does ("already closed"). A
   later decide on a closed package overwrites `st["disposition"]`, and replay
   reproduces the overwrite, so the first director decision is lost.

7. **`decide` + `grant_ref` is accepted.**
   `ingress.py:463` strips `grant_ref` before comparing against
   `_ATOMIC_FORMS`. `interface.md:9` allows `grant_ref` only with `hold`, and
   `interface.md:18` says unknown keys are rejected. The decide commits and the
   grant reference is dropped without comment.

## Real, but smaller

8. **The first worker wait keeps the short slice** (`harness.py:702-704`,
   `wait_s: 8` from `case_entry.py:476`). Only the `case_entry` wrapper
   reattaches, so `harness.py run-fixture` on its own still ends a valid slow
   turn as owned-failure `no-end`. The comment says this is DELIBERATE ("the
   abnormal-delay drill must be able to miss it"). A design question against
   O1, not a plain defect — yours to rule.

9. **The reattach decision uses the host clock** (`case_entry.py:1123-1138`,
   `datetime.now`) and ignores `live_stop_utc`. Effect is small: when live stop
   has passed, both branches end in `E_CASE_FAIL`; only the reason text
   differs.

10. **Deadlines are compared as text** (`lifecycle.py:210`,
    `now > st.get("deadline", "")`). `ingress.py:423,425` copies a grant's
    `absolute_deadline` unnormalised, while `_as_instant` accepts offsets and
    fractions. A `+02:00` deadline would compare wrongly by the offset. Every
    grant I have seen uses `Z`, so this is possible, not active.

## Why it matters

1 and 3 touch the four live cases still to run. 2, 5 and 6 break "the record
cannot be wrong" — and all three fail silently, not with an error.

Also noticed, not a correctness finding: `harness.py` adds
`_canonical_timer_base` / `_canonical_unit`, which copy `canonical_timer_id`
/ `canonical_unit` in `host_adapter.py`.

## Addendum, 21:20Z — finding 11, found while porting the core to Go

11. **The self-verify guard never fires; the worker seat can verify its own
    publish.** `P5-r2/src/lifecycle.py:244` and `:255` reject a verdict when
    `event.actor.seat == state.get("worker_seat")`. Nothing in the source ever
    records `worker_seat`: START stores the seat as `flight.owner`, and the
    only place `worker_seat` is set is by hand in
    `P3-r3/tests/test_lifecycle.py:87`. The same code is copied into
    P6-r9 and P6-r11 `r3harness/lifecycle.py`.

    Reproduced on P5-r2 (`80092f92`) through the trusted ingress, the accepted
    external route: kiln publishes as worker; `ingress.append(verify_pass,
    atomic={"hold": ...}, actor={"seat": "kiln", "role": "verifier"})` returns
    `('complete', 'decision-pending')`, and the package is COMPLETE with the
    ledger rows `a1-pub kiln/worker` and `self-v kiln/verifier`. The ingress
    accepts any trusted seat in any trusted role, so nothing else stops it.
    Through `Driver.verify` the verifier is always mapped to corvid, which is
    why no test caught it.

    This is the author-is-not-the-verifier rule, at the one boundary that is
    supposed to enforce it. Same class as findings 2, 5 and 6: silent.
