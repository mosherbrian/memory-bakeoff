# P13-live-1 — independent live review (corvid)

- **Action:** `P13-livereview-1`, owner corvid, `18:41:09Z`–`18:51:09Z`.
- **Inputs:** `live-review-receipt-1.json`, preserved `live-p13l1/`; **33/33
  receipt hashes match**.
- **Verdict: NOT READY for acceptance** (ladder unexecuted), but the observed
  `RUNGS FAIL` is a **measurement / test-design failure, not a product failure**.

## What actually happened (DB + journal + transport)

- `DECISION PASS` — incident `D-Dp13l1-Dp13l1-v1`, deadline `18:22:25Z`.
- The director ("verifier PASS; decision requested") was notified `18:21:25Z`
  (`wake-fixture-extract.txt`, transport `started`), then the decision was
  **RESOLVED at `18:21:29Z`**, ~56 s **before** the deadline.
- Archived DB `loop-pkg:Dp13l1`: `step=closed`, `verdict=PASS`,
  `decision.resolved=18:21:29Z`, `deadline=18:22:25Z`, **`rungs: None`**.
- Driver issued the **stop marker** (`STOP PASS`, journal `stop requested; exiting
  64`), then waited 150 s for a "director rung (real wake)" and reported
  `wait:director rung INCOMPLETE` / `RUNGS FAIL no director wake`.

## Classification: product vs measurement

- **Product: correct.** A timely actual decision resolved the incident before the
  deadline; the product therefore **cancelled the ladder** (no rung fired —
  `decision.rungs: None`), exactly as required ("decide cancels future rungs; a
  stale callback after close is harmless"). The director **had** a real delivery
  (the decision notice at `18:21:25Z`).
- **Measurement / test-design defect:** the live plan expected the rung-0 director
  wake **while stopped**, but the fixture director **decided early**, so there was
  no overdue decision and no rung to send. The driver's **wake-counter** cannot
  distinguish "no overdue decision" from "no delivery" — **do not infer no
  delivery from the counter**; the DB + transport prove the notice was delivered.
- **No source/product defect** found in the non-firing rung.

## Unexecuted obligations (unproven — preserved)

The deadline/rung ladder (`0/300/600`), director/duty/Claude rungs while stopped,
capability ack, ack-expiry **same-key recurrence**, decide-suppression **after
recurrence**, and restart-without-duplicates were **not executed** (resolution
preceded the deadline). They remain unproven.

## Cleanup / promotion

- Driver `cleanup done 18:24:16.796Z`; current scope **inactive/dead**; the four
  fixture IDs **absent** from the registry; no matching live units; **no promotion**.

## Smallest concrete correction (no edit here)

1. In the live plan, **hold the fixture director from deciding until after the
   deadline** (or drive an explicitly **overdue/unresolved** decision) so the
   stopped-mode ladder + ack/expiry/recurrence are actually exercised.
2. Classify rungs from the **DB `decision.rungs` state** (and the transport log),
   not the wake counter — a `rungs: None` + timely `resolved` is a PASS-shaped
   outcome, not a rung failure.

Returned to Tern; no source edits/retry/promotion by corvid.
