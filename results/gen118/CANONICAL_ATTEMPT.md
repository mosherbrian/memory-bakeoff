# Generation 118 - canonical attempt

**`attempt6` is canonical**, per the Generation 120 review.

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
- `attempt5` - superseded, and superseded for a reason worth stating precisely:
  nothing in it is wrong. It remains valid historical zero-call evidence and it
  still verifies. It stopped being the executable freeze because the Gen120
  review found three defects in the runner it binds, and repairing a
  contract-bound runner necessarily invalidates the contract that binds it. The
  freeze did not fail; the thing it froze needed fixing. Marker provenance corrected. Id balance is now a
  hard gate that fails closed, and reaches 6/12 by re-rolling the arbitrary salt
  under strict alternation rather than hand-picking twelve per-core assignments
  to hit the number - fitting the fixture to its own audit would be the same
  error in a new place. The contract binds eight surfaces including
  `scripts/run_gen119_reader.py`, which refuses to `--fire` without explicit
  control-plane authorisation.
- `attempt6` - **canonical.** Same science, byte-for-byte: 12 cores, 60 unique
  prompts and cases, no exposed-term reuse, exact 6/12 balance on id order,
  value length and lexicographic sort, the verbatim rule in every prompt, the
  nine-class ontology and the option-3 success predicate unchanged. What changed
  is the apparatus the contract binds, on three findings from the Gen120 review:
  1. **the raw responses were not manifest-bound.** `reader_raw.jsonl` was
     written with a bare `write_text` and its hash kept only in `raw_seal.json`.
     `EV.verify` walks the manifest, so the verbatim reader output - the one
     artefact that can never be regenerated - was never verified. It could have
     been edited after the fact and every gate would still have read green;
  2. **the evidence gate was authored, not observed.** The runner passed
     `manifest_ok=True` into the marker logic, so the strongest claim the
     apparatus makes was an assertion by the run's own author. It is now derived
     from `EV.verify_closed` over the exact required inventory, and the marker is
     written last so it never verifies itself;
  3. **run provenance was hardcoded.** `GENERATION = 119` and a Gen116-line
     commit were module constants, so authorising a later run meant editing a
     contract-bound file - bookkeeping that would have forced a scientific
     refreeze. The runner is now `scripts/run_reader_v6.py`, with generation,
     source commit and authorisation supplied at runtime and checked fail-closed.
  Contract `819e79964ec07bdbe3c77b22339e647829402071b0edd6cdaeb97ee917fb5f98`.

No attempt ran the reader. Every one carries `NON_EVIDENCE` with zero calls. Gen116 attempts 1-4
and Gen117 attempt1 verify byte-for-byte unchanged.
