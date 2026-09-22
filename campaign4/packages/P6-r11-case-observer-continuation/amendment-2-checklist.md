# P6-r11 amendment-2 — pinned acceptance checklist

Pinned by corvid-dsh at `P6r11-amendment2-admission-1`. Amendment pin
`amendment-2-verifier-rejection.md` sha256 `8647b2c7…`; base `05eba448`; entry
`2504e07e…`; prior review `4c6990cd…`. Authorized surface: `candidate/src/
r3harness/turn_handoff.py` + `candidate/src/case_entry.py` only; all other
modules and frozen parents unchanged. If rejection cannot propagate without
another module, return the exact blocker. Baseline old-fail assertions preserved
verbatim; new-pass must be genuinely new.

Semantics (required):

- Identity/incarnation/current-execution/claim-schema/routing checks stay
  BEFORE trusting `outcome`; a caller-written `outcome:failed` is insufficient.
- Bind verify-run to the authorized verification action and the **committed
  worker artifact references**; independently recompute actual bytes; persist
  expected and observed hashes plus failure reason/claim identity.
- Do not trust a forged claim's invented expected hash to manufacture
  rejection; a genuine bound hash mismatch becomes a distinct durable verified
  rejection — never COMPLETE, never positive `terminal-rest`, never acceptance
  of corrupted output.
- `case_entry.py` may consume the explicit decision as `accept-open` **only**
  when the evidence proves the intended fault occurred and the verifier
  rejected; ordinary completed-claim mismatch, failed worker, and
  cancelled/malformed claims keep their owned recovery. No generic
  `E_ARTIFACT_MISMATCH` blessing.
- Rejection durable and idempotent under replay/reopen: no duplicate dispatch,
  no worker rerun, no second verdict effect, no repeated escalation; bounded
  owned disposition for still-unaccepted work; no deadline extension; no
  low-level authoritative writes bypassing trusted ingress.

Cases (blocking):

1. FV-W (worker 18 s): authenticated durable rejection; post-commit before-check
   tamper with distinct expected/observed hashes; `accept-open`; never
   `COMPLETE`; exactly one worker + one verifier send; no worker rerun.
2. FV-WV (worker 18 s, verifier 18 s): same through verifier observation.
3. QR-W / QR-WV (worker >8 s, verifier >8 s): setup commits; observation/reopen
   `duplicate-end-ignored`; no new dispatch; no repeated alarm.
4. Negative: forged/missing route; wrong action/execution/role/incarnation;
   invented expected hash; completed claim with mismatch; failed worker;
   cancelled/malformed claim; `failed` verdict without demonstrated mismatch —
   none may become verified rejection.
5. Replay/reopen: exact rejection identity/evidence preserved; no duplicate
   effect; idempotent under persisted state.
6. Expiry / outer stop: bounded owned disposition, no renewed grant.
7. Gate/packaging: whole retained 34-test gate + new executable tests on final
   bytes, real timing recorded (command/stdout/rc/times/residuals); no
   retry-until-green, skipped failure, fabricated onset, simulator shortcut or
   live fixture. No manifest self-entry/self-hash; manifest bound externally
   from claim/receipt; all paths local; actual `candidate/stagec-plan.json` and
   exact proposed commands supplied; baseline old-fail tests preserved.

Bounds: ONE kiln ≤40 m (execution `P6r11-rejection-1`), ONE corvid ≤30 m
separate clock; ceilings `995worker/700verifier`; no automatic repair or clock
reset; candidate-only, zero live/prep/witness. Lost-completion and
queued/ambiguous controls remain out of scope and unresolved.
