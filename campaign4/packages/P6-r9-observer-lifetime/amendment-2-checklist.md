# P6-r9 amendment 2 (host timer identity/callback) — pinned replacement checklist

Pinned by corvid at admission, BEFORE any P6r9-repair-2 worker dispatch. Contract
`package.md` `bb103f35b857…`. Amendment `amendment-2-host-timer.md` `592d24c1…`.
These checks replace nothing in the parent checklist; they are additional gates.

1. **Parent reproduction (old-fails, immutable parent).** On the unmodified parent
   bytes, reproduce all three defects through the real CLI: (a) reattach queries
   `timer-arm:deadline:<action>` while `create_host` persists `timer-arm:<unit>`;
   (b) the persisted `unit` carries a doubled `.timer.timer` suffix while the real
   systemd unit has one `.timer`; (c) `_arm_host_timer` callback argv omits `--db`
   so `timer-callback` falls to the default `/tmp/p6h/harness.db`. Capture exact
   bytes/hashes and observed errors.
2. **Rejecting OS-boundary model (new-passes).** Tests intercept the systemd
   boundary with a faithful model where duplicate create MUST reject, queries
   report current units, cancel addresses the canonical name, and a fresh process
   loses local memory. An always-success runner cannot pass. Exact-CLI delayed
   worker + reattach commits with exactly ONE timer creation and exactly one
   worker / one verifier send.
3. **Reopen mutations.** Exercise reopen with valid timer, missing timer, expired
   grant, and conflicting unit/deadline/identity: no extension, no duplicate
   effects, conflict → bounded owned failure (never hijack/delete another unit);
   overdue → bounded owned disposition, not a new full interval.
4. **Callback context.** Execute the recorded callback argv (exact parser, not an
   imported call) against two independent temp databases: only the intended bound
   fixture DB changes; the foreign/default DB is untouched (no `/tmp/p6h`
   fallback). Early, stale, or twice-fired callbacks cause no premature/duplicate
   effects.
5. **Regressions and suite.** Run the retained 27-test suite plus updated tests,
   the full no-simulated five-case composition, and observer/tamper/identity/
   receipt/signature regressions. Report targeted and whole-suite results
   separately; mechanically refresh manifest and transitive hashes (no self-hash);
   declare every residual; no retry-until-green, no skipped failing gate.
6. **Scope/authority.** Only minimal local edits to `src/r3harness/harness.py` and
   `src/r3harness/host_adapter.py` (plus tests); frozen parents/core unchanged; a
   new copy manifest identifies the precise changes; other modules need a
   reproducer/Tern decision. Candidate tests mutate no real service/timer/fixture.

Grant: one kiln <=35m then one corvid <=25m independent verification; ceilings
845worker/580verifier; admission 5m separate. Expiry/verdict returns Tern.
