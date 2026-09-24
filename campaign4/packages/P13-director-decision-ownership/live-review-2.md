# P13-live-2 — independent live review (corvid)

- **Action:** `P13-livereview-2`, owner corvid, `19:18:07Z`–`19:28:07Z`.
- **Inputs:** `live-review-receipt-2.json`, preserved `live-p13l2/`; **41/41 receipt
  hashes match**.
- **Verdict: PRECONDITION INVALID preserved — fixture noncompliance, not a driver
  defect.** Ladder unexecuted; no product FAIL, no retro-PASS.

## Bound evidence

- `INDUCTION PASS` (both director/duty confirmed run/seat-bound exact nonces),
  `DECISION PASS` (incident `D-Dp13l2-Dp13l2-v1`, deadline `19:18:07Z`),
  `STOP PASS` (marker `19:17:13Z`).
- Archived DB `loop-pkg:Dp13l2`: `step=closed`, `verdict=PASS`,
  `decision.resolved=19:17:17Z` (`resolve_actions ["00610196476f ok"]`),
  `deadline=19:18:07Z` — resolved **50 s before** the deadline.
- `PRECONDITION INVALID 19:17:18Z` — "incident resolved … before the plan's decide
  (rung 0): the ladder test is invalid, not a product result".
- Cleanup `19:17:31Z` verified: exact 4 IDs absent, scope `inactive/dead`.

## Actual resolving actor / command

Transport `wake-fixture-extract.txt`: priming to director/duty `19:16:32Z`,
worker dispatch `19:16:48Z`, verifier dispatch `19:16:56Z`, and the product's
decision notice to the director `19:17:07Z` ("verifier PASS … Decide with:
`agent-loop decide …`"). The DB `resolved=19:17:17Z` (10 s later) confirms the
**fixture director seat `cb8ac44f-1790277148` ran the product-generated `decide`
command** from that notice.

## Noncompliance vs driver defect

- **Fixture noncompliance.** The nonce-primed director was instructed not to decide;
  but the priming is **instruction-only**, and the real seat followed a genuine,
  authoritative `decide` command delivered by the product. An instruction cannot
  override a real model obeying a valid command.
- **No driver defect.** The driver **correctly** detected the premature resolution
  and classified `PRECONDITION INVALID` (rc 4), treated it as not-all-pass, and
  cleaned up exactly. This is the intended fail-closed behaviour.

## Smallest deterministic fixture correction (not instruction-only)

Give the **director and duty fixture seats a lane/wrapper that deterministically
denies the `decide` / `decision-ack` subcommand** during the ladder window (e.g. a
wrapper on their `PATH`/lane that blocks those subcommands and records the blocked
attempt), while the **real wake transport still delivers** the notice and the
product's decision/authority path is exercised when the driver **authorizes** it
(flip the wrapper to allow). This removes reliance on instructions, preserves the
actual transports/actors and the product's authority tests, and is deterministic.
(Equivalently, withhold the candidate binary from the fixture director's `PATH` for
the window.) **Do not** retry with another instruction-only priming.

## Preserved

Ladder (`0/+20/+40`), capability ack, same-key recurrence, decide-suppression after
recurrence, and restart-no-duplicates remain **unexecuted / unproven**. No edit/live
effect by corvid. Live remains separately held.
