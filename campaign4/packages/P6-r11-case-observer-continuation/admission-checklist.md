# P6-r11-case-observer-continuation — pinned admission checklist

Pinned by corvid-dsh at `P6r11-admission-1`. Brief pin: `package.md` sha256
`a966c15176c7c2089c74ef952dd4233f3b01fd291243e333ce06568970e7344e`.
Baseline commit `f1d7c86`, manifest `161afac5…`; on-disk `case_entry.py`
`9a1bb23c…`, `harness.py` `d7b4e517…`, `host_adapter.py` `231f45f0…`;
34-test gate `77d5b03ec040…`; prior review `ebb6ff9d…`; control review
`04b6501f…`. Every item is required; skipped failure, repeated-until-green run,
unreported timeout, or rc-only claim is a FAIL. Corvid tests/reviews on frozen
final bytes. Change confined to `case_entry.py`; harness/host_adapter/core stay
byte-identical unless concrete evidence returns to Tern first.

1. **Baseline reproduction first (pre-implementation).** Pin exact CLI
   acceptance cases reproducing BOTH branches on the immutable baseline with
   **worker > 8 s and verifier > 8 s**, using intercepted external collaborators
   on the real production paths (no `--simulated`), demonstrating the original
   8 s truncation before the valid grant expired. Worker fixes must not silently
   edit these expectations.
2. **Failed-verification after repair.** Delayed worker AND delayed verifier
   produce durable handoff; actual post-commit *before-verifier* tamper with
   distinct before/after hashes; real verifier rejection; `accept-open` / never
   `COMPLETE`; exactly one worker and one verifier send. Require
   artifact/claim/ledger evidence, not final rc; `induced:true` alone is not
   proof. Preserve real-case onset; no fake clock. Missing onset or unapplied
   corruption stays INCOMPLETE.
3. **Quiet-rest after repair.** Delayed setup genuinely completes; observation
   and reopen yield `duplicate-end-ignored`, no new dispatch, no false alarm.
   Reopen tested in worker and verifier phases; original deadlines preserved;
   grant expiry and stricter outer stop return bounded failure/INCOMPLETE, never
   a fresh interval or task; one-shot callback cannot duplicate.
4. **Full gate retained.** The retained 34-test gate plus new cases, on the same
   changed entrypoint, remains green; positive slow-turn and the timer
   canonicalization / reconcile / two-DB callback guarantees retained. Corvid
   adds an unshared delayed/expiry case and checks the whole gate on frozen
   final bytes.
5. **Manifest/provenance.** Complete manifest (29 inherited + declared new
   files), no stale R3 copy hashes and no self-hash; original provenance
   preserved; mechanical hash refresh only; no fabricated receipt or successful
   late timing. Exact diff, candidate plan and proposed live commands for the
   two cases described without signatures or fresh prep. Code stays stdlib.
6. **Bounds.** ONE kiln ≤ 40 m, ONE corvid ≤ 30 m; ceilings
   `925worker/670verifier`; runtime must fit or honest INCOMPLETE; no repair
   grant, extension, or deadline reset. R10 unused grants cancelled, not
   transferred. Corvid implementation pass gets its own host-stamped
   start/deadline; at expiry stop/preserve and return Tern; no implementation by
   the verifier.
7. **Scope.** Candidate-only; no fixture launch, host timer/service, live send,
   research/shadow/adoption/retirement, multi-project expansion, main-seat
   reset, shared wrapper/credential or live-service change. Lost-completion and
   queued/ambiguous remain blocked and OUT. R10 matrix stays incomplete; earlier
   positive witness unchanged.
