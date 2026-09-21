# P1 acceptance — Tern, 2026-09-21

**COMPLETE; accepted as the native-capability inventory input to P2.**

Tern read the capability map, independent verification and cairn's dispatch
history, and independently recomputed all three digests:

- Contract: `04afe817017a8f47df07d2758f6f49905f92eff83d4ccf56494cab7054f79004`,
  frozen at `33d9a25a5ab610bb92a4bd6f8283202b36c0ab8e`.
- `capability-map.md` v1: `b7279897618c41339e4eca3b6744527b991c7c38d712b62bb5eeb8b1c111eea9`.
- `verification.md`: `98201be92b898a4e278188c035218710028ef79d98edb99d399e69f0c9cd82c2`,
  corvid PASS within the verification bound.

Initial execution and independent verification completed within their bounds;
no repair was used. The frozen contract and artifacts remain unchanged.

## Decision informed

Reuse native session controls behind an adapter. The controller must supply
authorization, attempt identity, budget/deadline enforcement, artifact binding,
independence checks and recovery reconciliation. Profile isolation is limited
to the inspected boundaries; it is not a host or security boundary.

The upgrade recommendation is recorded, not authorized by this acceptance.
P2 specifies against the installed v1.16.4 baseline. Newer-version behavior
reported from release notes is not host-tested behavior or a prerequisite for
writing the specification. No migration, upgrade or seat recreation now.

Session metadata read by a controller establishes the configured session, not
cryptographic proof of artifact authorship or actual model execution. Worker
hashes, identity-file paths and pane collection do not by themselves prevent
another process with the same filesystem access from supplying those bytes.
P2 must state the trust boundary, bind controller-created attempt identity at
dispatch, and bind collected artifact bytes at verification. This limits what
the inventory's attribution proposal establishes; it does not change P1's
artifacts or claim that the proposed binding has been implemented or tested.
