# Generation 118 - canonical attempt

**`attempt5` is canonical**, per the Generation 119 review.

- `attempt1` - superseded. The science was right: option 3 correctly implemented,
  12 fresh cores, 60 unique prompts, zero reuse, zero model calls. But review
  found three completion-gate failures, all of them mine and all from copying the
  Gen116 freeze runner without reading what I had copied:
  1. its sealed `NON_EVIDENCE.json` said **"Generation 116 froze a candidate
     protocol"** - false provenance inside a sealed manifest;
  2. record-id ordering was **7/12**, failing the balance gate the Gen118
     instruction declared. The runner REPORTED the number and shipped anyway.
     Reporting a number is not gating on it;
  3. the contract bound **five files** and omitted every run-bearing surface -
     the future runner, the request projection, the capture and seal path, the
     retry policy, the evidence-marker logic. A contract that does not bind what
     will run is not a freeze.
- `attempt2` - superseded. It carried the Gen119 repairs but was sealed while
  three files still held a `sed` artefact: `reader_interference_v6 as V5` with a
  body using `V6`. The frozen-source gate caught it, which is the gate working.
- `attempt3` - superseded. Sealed before two circularities were removed: the
  runner hardcoded the contract hash, and it named the canonical attempt path.
  Both meant the runner and the freeze could never both be updated - each
  invalidated the other.
- `attempt4` - superseded; its own test still asserted the old five-file count.
- `attempt5` - **canonical.** Marker provenance corrected. Id balance is now a
  hard gate that fails closed, and reaches 6/12 by re-rolling the arbitrary salt
  under strict alternation rather than hand-picking twelve per-core assignments
  to hit the number - fitting the fixture to its own audit would be the same
  error in a new place. The contract binds eight surfaces including
  `scripts/run_gen119_reader.py`, which refuses to `--fire` without explicit
  control-plane authorisation.

No attempt ran the reader. Both carry `NON_EVIDENCE`. Gen116 attempts 1-4
and Gen117 attempt1 verify byte-for-byte unchanged.
