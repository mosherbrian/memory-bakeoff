# Generation 116 - canonical attempt

**`attempt4` is canonical.**

Earlier attempts are preserved under the evidence contract and superseded:

- `attempt1` - first freeze. The fixture audit it produced showed two real biases:
  the revision-2 value was longer in only 3 of 12 cores, and the revision-2
  record id sorted first in only 2 of 12. Both are recency signals the protocol
  is supposed to forbid, so the freeze was not shippable.
- `attempt2` - biases removed. The revision assignment was rebalanced to 6/12 on
  both length and lexicographic direction, and record ids are now derived from an
  opaque SLOT with an alternating slot-to-revision map, so an id cannot carry the
  role even by accident. Its contract still hashed the grader and verifier as
  `null`, because neither file existed yet.
- `attempt3` - superseded. The tracked future grader
  (`scripts/grade_gen116_v5.py`) and independent verifier
  (`scripts/verify_gen116_contract.py`) exist and are inside the fingerprint.
  That gap was Gen114's defect - a runner absent from the pinned commit - and the
  Gen116 test suite fails closed on it. Its grader, however, still had four
  load-bearing defects, found by the control plane and both rivals.
- `attempt4` - **canonical.** Four grader defects repaired:
  1. a reply naming the right value while selecting the WRONG record scored as
     success - the v4 habit of scoring on value presence, reintroduced;
  2. an `INSUFFICIENT` reply that also selected a value scored as a correct
     abstention, so an incoherent answer could pass the very control that exists
     to police "choose the closest record";
  3. a reply citing nothing at all scored as success;
  4. the focused tests were outside the contract fingerprint.
  Simultaneous contradiction is now ASSERTED (both values named in the single
  `selected_value`) rather than inferred from a null selection, and the two
  `TEMPORAL_RECONCILIATION_*` classes are collapsed into `*_WITH_HISTORY`,
  because under a structured contract they are the same response. Nine classes,
  not eleven; the deviation from the Gen116 brief is deliberate and recorded.
  Seven mutation witnesses, up from three.

No reader, model, endpoint, sidecar, memory engine or GPU was called in any
attempt. Every attempt carries `NON_EVIDENCE.json`.
