# Generation 118 - canonical attempt

**`attempt12` is canonical**, per the fourth Generation 120 rival review.

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
- `attempt6` - superseded. Same science, byte-for-byte: 12 cores, 60 unique
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
  Superseded within the same generation: the blind rival review (glm-5.3 and
  glm-5.3-flash, independently) found four further defects, all in the apparatus
  and none in the science.
- `attempt7` - superseded. Science identical again; only the bound apparatus
  changed. The four:
  1. **a witness test rewrote a real frozen source in the shared checkout.**
     `test_editing_a_frozen_source_blocks_the_run` mutated
     `reader_interference_v6.py` and restored it in a `finally`. Both reviewers,
     reading that same checkout while the other ran the suite, saw a tampered
     frozen source and reported a defect neither could attribute. The test now
     runs in a throwaway `git worktree`, so it cannot make the tree lie to anyone
     else - and a `finally` was never protection against a crash between the two
     writes anyway. The rival harness now gives each reviewer its own worktree
     for the same reason: reviewers sharing mutable state are not independent,
     they are each other's confounder;
  2. **`verify_closed` computed `unexpected` from manifest keys only**, so a file
     sitting on disk that the manifest never listed did not deny closure - the
     same blind spot as F1, one level up. It now scans the directory;
  3. **the execution contract called one value `authorised_by_generation`**,
     conflating the generation that authorised a run with the one executing it.
     They are required to match, which is the typo gate, but the record may not
     imply they are the same fact. Now recorded separately;
  4. **preflight still labelled its checks `attempt4_verified`** while the
     canonical pointer resolved elsewhere. Renamed to `canonical_verified`.
  Contract `7e3a73e63e546b94d46d6faf76b0f915b423b2be79a185db6e20384e7a9c0c58`.
  Superseded after a SECOND blind rival review of the repaired code.
- `attempt8` - superseded within minutes, by my own sequencing error, and kept
  because evidence is append-only: I froze it and only then finished repairing two
  contract-bound TESTS, which invalidated it immediately. The freeze must be the
  last action of a generation, after every code and test edit. Science identical for the fourth time; apparatus
  again. The findings, most serious first:
  1. **the id-balance gate tolerated the imbalance it was named for.** It read
     `abs(id_first - 6) > 1`, so **7/12 would have passed** - the exact number
     attempt1 was superseded for, and the number every handoff since has
     described as "a hard gate that fails closed". No published attempt was ever
     wrong; all were genuinely 6/12. The GATE was weaker than every claim made
     about it, and a tolerance nobody asked for is how a declared invariant
     quietly becomes a preference. Now exact equality, with a control asserting
     7/12 and 5/12 are both rejected;
  2. **a mutation witness had decayed into a prose check.**
     `test_the_contract_records_the_runtime_authorisation` asserted a field name
     appeared in the source; after attempt7 renamed the field, the string
     survived only in the COMMENT explaining the rename, so the test passed
     regardless of what the contract contained. It now builds a real contract and
     inspects the object. This is the disease the Gen120 test file was written
     about, growing inside that same file within one generation;
  3. **the Gen116/v5 naming vestiges** persisted in contract-bound prose: the
     verifier claimed to rebuild "the v5 contract", the runner's docstring named
     Gen116 attempt4 when it resolves the gen118 pointer, its preflight message
     said "Gen116 NON_EVIDENCE", the contract labelled a hash `v5_module_sha256`,
     and preflight validated the vestigial gen116 pointer rather than the one it
     actually consumes;
  4. **the lineage subprocess ran with a hardcoded `PATH=/usr/bin:/bin`**,
     host-brittle and failing for a reason unrelated to the thing it gates;
  5. **current-facing docs pointed at `attempt2`**, superseded twice over, and
     `CODEX_HANDOFF.md` still carried Gen116-era suite figures and instructions to
     `pip install` the engine under test - the sibling of the `AGENTS.md`
     staleness repaired one commit earlier and missed here.
  Also corrected, in the handoff rather than the code: the claim that 30 witnesses
  each fail against the pre-fix runner. The measured number is **19 of 36**; the
  rest are immutability guards that correctly pass in both trees. Recorded with
  method and node ids in `reviews/gen120-negative-control.md`.
  Contract `b38a33f33529dd2fe200315151746dd3702c4c042b0daf77a6ed2b1c1073f26f`.
- `attempt9` - superseded. Byte-identical science to attempt8; it exists only
  because two contract-bound test files were repaired after attempt8 sealed:
  `test_contract_binds_every_run_bearing_surface` still demanded the
  `v5_module_sha256` key that finding 3 renamed, and
  `test_runner_never_writes_into_gen116` asserted the runner reads
  `results/gen116` - pinning in place the very vestige that finding had removed.
  A test that asserts the defect keeps the defect. Contract
  `85a5e8aa839bf6f0dcc23c0427379f8d5a89de69fa2f083c0d5bf3c72cd2861d`.
- `attempt10` - superseded. Science identical a fifth time. Third review:
  1. **a check that could never fail, in preflight.** "contract disagrees with
     itself" compared `contract["contract_sha256"]` against a helper that read the
     same field from the same file, while its comment claimed it verified a
     recomputation. Nothing in the run path ever recomputed the sealed hash; it
     was protected only transitively, by the manifest binding the file's bytes.
     Preflight now recomputes sha256 over the sealed payload plus source pins,
     exactly as the freeze does, and a witness confirms the value moves when a
     pin is perturbed;
  2. **the F1-F3 witnesses were the one unbound test file**, so the 37 checks for
     the defects this generation headlines could have been weakened after the
     freeze without invalidating it. Now bound. attempt9 exists BECAUSE
     contract-bound tests drifted, which is exactly why the asymmetry mattered;
  3. **the balance-gate control asserted against a lambda it defined itself**,
     proving only that the test agreed with itself. The predicate is extracted as
     `id_balance_ok` and the control now calls the function `main` gates on.
  Contract `4179b1221bcbc82c2a6040fe69be23faa355afa70fda9333c7d58993accedba4`.
- `attempt11` - superseded immediately, and by the SAME sequencing error that
  produced attempt8: I ran the freeze after the first of six repairs instead of
  after all of them. Twice in one generation. Preserved because evidence is
  append-only.
- `attempt12` - **canonical.** Science identical a sixth time. Fourth review:
  1. **the balance gate enforced ONE of the four invariants it publishes.**
     Value-length balance, lexicographic balance and the conflict-order
     counterbalance were computed, printed and shipped un-gated, so a future
     refreeze could have passed with 8/12 length balance while the report said
     "balanced". This is the "reporting a number is not gating on it" failure
     Gen119 was named for, surviving inside the gate Gen120 had just repaired.
     All four are now gated;
  2. **a malformed 200 response was treated as a transport failure and RETRIED**,
     with its raw bytes discarded and only the exception type kept. The server
     answering badly is a scientific outcome; retrying it is sampling until a
     favourable answer appears, which the contract forbids in the same breath it
     promises raw evidence sealed as it arrives. Parsing now sits outside the
     transport handler; a malformed answer is `TERMINAL_MALFORMED_RESPONSE` with
     the raw bytes kept;
  3. **the known-failures guard was blind to ERROR-class outcomes.** It parsed
     only `FAILED` lines, so five collection errors were invisible to a guard
     whose docstring promised to catch any unlisted failure - a stated claim
     exceeding its mechanism. It now reads both classes and the errors are pinned;
  4. **that guard also reproduced the hardcoded `PATH=/usr/bin:/bin`** that the
     previous round removed from the runner as host-brittle;
  5. **manifest writes were not atomic**, a durability hole in the machinery
     guarding the one artifact that can never be regenerated. Now temp + replace;
  6. **the canonical pointer was parsed as "the first backtick in a prose file"**,
     so any earlier backtick would silently retarget the run. It now matches the
     declaration itself and refuses when absent.
  Contract `20d9fe9b6f3992997907dcb8b83fa849ebb932298cab8dea20d4a3e41306ea5f`.

No attempt ran the reader. Every one carries `NON_EVIDENCE` with zero calls. Gen116 attempts 1-4
and Gen117 attempt1 verify byte-for-byte unchanged.
