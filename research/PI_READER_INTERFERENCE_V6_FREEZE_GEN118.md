# reader-interference-v6, frozen and unrun (Gen118)

**Status: candidate protocol awaiting review. Not a result.** Zero reader, model,
endpoint, sidecar, GPU or memory-engine calls.

Canonical attempt `results/gen118/attempt1`.
`contract_sha256` `93b4a3148b460ff385edf36306e5af29de477b0386883a525b17815abb7db2a9`.

## What changed, and the reasoning that must not be lost

Gen117 ran v5 and produced `NON_EVIDENCE`. Values were symmetric two-word phrases
(`bay tolliver`); the reader replied `tolliver`. In **36 of 48** selections it
returned the distinguishing token alone, so correct selections scored
`UNSUPPORTED_VALUE` and 0 of 12 cores passed their controls.

The control plane ruled **option 3**: require the reader to copy the complete
phrase, stated in the prompt. It said plainly that it was **not** choosing the
option that would have rescued Gen117 — accepting the distinguishing token — on
the grounds that the acceptance class *was suggested by the observed failures*.
A rival's independent check had computed that option 2 would yield 9 of 12
interpretable cores, not 12; that number is in the ruling as a reason against it,
not for it.

That is the discipline this whole line exists to protect: **the repair may not be
chosen by which repair scores better.**

## Freshness, proven rather than asserted

Twelve entirely new cores. The audit derives the burned set from the v5 fixture
itself rather than a typed list, and scans the complete model-facing input:

| check | result |
|---|---|
| reused subjects, values or tokens | **0** |
| reused record ids | **0** |
| reused prompt hashes | **0** |
| values containing digits | **0** |
| role words in records or ids | **0** |
| conflict order counterbalanced | **12/12** |
| revision-2 value longer | **6/12** |
| revision-2 value lexicographically later | **6/12** |

One collision was caught during design and removed: the head noun `wing` had been
used in Gen116. **Reusing half a burned value is still reuse.**

The value assignment was chosen by search over the 12 booleans for length and
lexicographic balance — not by eye, and not by how the Gen117 reader answered.

## "Verbatim" and the matcher are made to agree

Gen118 required that the prose not be stricter or looser than executable
behaviour, so the canonicalisation policy is named in the contract rather than
implied by the code:

> casefold and collapse internal whitespace; nothing else. No suffix,
> token-subset, semantic, fuzzy, embedding, edit-distance or judge-based
> acceptance.

| accepted | rejected |
|---|---|
| `bay tolliver` | `tolliver` (the Gen117 failure) |
| `Bay Tolliver` | `bay` |
| `bay  tolliver` | `the bay tolliver`, `bay tolliver.` |
| `  bay tolliver  ` | `tolliver bay`, `bay tollivers` |
| | `bay tοlliver` (Greek omicron) |

27 tests draw exactly that boundary. The other three legs of success remain
independently load-bearing: the right value with the wrong record fails, with no
citation fails, and with an unshown citation fails.

## Immutability

`results/gen116/attempt1-4` and `results/gen117/attempt1` all verify unchanged.
Gen117 remains `NON_EVIDENCE` and is not regraded.

This is a frozen candidate. Whether it may run is the control plane's call.
