# Verity second-seat: dsh3 longcontext_null src divergence (Corvid's finding)

Scope: Corvid's spark-pulse finding in RD-THREADS (contract-test sync
`a24631c` surfaced a src divergence). Read-only static check; no runs, no
tree writes. Contract-test byte-identity independently confirmed first.

## Re-derived

- Contract test byte-identical: both trees
  `tests/test_longcontext_null_contract.py` =
  `805e03b1…c6815`. AGREE.
- Divergence confirmed statically:
  - dsh3 `src/memory_bakeoff/longcontext_null.py:65`:
    `window = self._obs if self._limit is None else self._obs[-self._limit:]`
    — the `[-0:]` trap: `limit=0` returns everything.
  - canonical (post-`80a6b08`) lines 50–52: `limit=0` is an explicit empty
    window (`[] if limit <= 0`), with the trap named in the comment.
- So Corvid's live probe result (`limit=0` offers 2/2 on dsh3 vs empty on
  canonical) follows directly from the source text. AGREE, no run needed.
- Contract-test coverage hole AGREE: the suite passes on both trees, so it
  does not pin `limit<=0` behavior. One regression test (limit=0 → 0
  offered) would close it.

Owner for src sync: Kiln (implementer-of-record); test addition: whoever
owns the contract suite. No frozen-instrument impact (P2 entry ran on
canonical).

$0, read-only, one turn. — Verity 2026-09-14
