# pi-observational-memory Gen28 — the v2 citation contract

## Status

`complete_citation_contract_v2_regrade_over_frozen_gen27_captures`.

Gen27 measured the agent-visible context OM produces for itself and graded it
with a citation contract that was internally inconsistent. This generation
repairs the contract as a new versioned artifact and applies it to the same
frozen captures and the same frozen reader responses. No product ran. No answer
was regenerated. v1 is untouched.

## The defect

The v1 reader prompt asked for citations as "OM IDs such as `obs-...` or
`ref-...`". The v1 grader looked each citation string up directly in a support
map keyed by the bare native entry ID. A reader that obeyed the prompt was
therefore scored as citing something that does not exist.

The clearest case is Q10, which failed in all three repetitions while citing
`obs-82e397393ad2`. In every repetition `82e397393ad2` maps to A04, the anchor
Q10 requires.

## What v2 changes, and what it does not

v2 changes only how a citation string is resolved to captured provenance. The
answer rules — required terms, prohibited terms, the UNKNOWN cases — are
inherited from v1 unchanged. The fixture is unchanged and still hashes to
`cce9fdf494ad6965897646beff1ef535d4aeb73ba81f3ea83e6fe68e1218acdc`.

Public identity is `om-context-production-v2`, scorer
`om-context-production-scorer-v2`, contract SHA-256
`f6250dc2acb3b168eb994261763d931b671ff9236bf57370484aa6722b331286`.

Prefixes are parsed, not stripped. `obs-<native-id>` and `ref-<native-id>` are
the only recognized forms, and each must match a role the frozen fold actually
assigned that ID. Everything else fails closed: an unknown prefix, an ID absent
from the capture, an ID that is not twelve lowercase hex characters, a prefix
that contradicts the captured role, and a bare ID whose roles disagree about
which anchors support it. Nothing is ever inferred from text similarity.

## OM re-emits a promoted observation as a same-ID reflection

Typing the ID space turned out to be the substantive part of the work, because
the ID space is not partitioned by type. In every repetition a handful of IDs
appear in both the `observations` and the `reflections` list of the same
`om.folded` record — 7, 5 and 4 of them — with identical content, and with the
reflection listing itself as its own supporting observation.

A grader that assigned one type per ID would reject `ref-36fe2ec6b897` in
repetition 1 as a type mismatch, and would have scored this generation lower
than the recorded diagnostic for the wrong reason. v2 therefore treats a role as
one of possibly several the capture assigns, and accepts a typed citation when
the capture assigns that role. A bare ID is accepted only when every role it
holds agrees on the anchor set; the three repetitions contain no disagreement,
so bare citations resolve unambiguously here.

## Provenance gate before regrading

Each repetition is rebuilt from its own frozen `om.folded` record: observations
carry `sourceEntryIds` into the native anchor map, reflections resolve through
`supportingObservationIds`. The rebuilt typed projection must reproduce the v1
support map for that repetition exactly, or the regrade refuses to run. It
reproduces it in all three.

The regrade also refuses to run if the stored capture was made under a different
v1 fixture or scorer hash than the frozen module reports.

## Result

v1 remains the historical result under its own contract. v2 is the corrected
citation reading of the same responses.

| rep | run | v1 | v1 failures | v2 | v2 failures | recovered | regressed |
|---|---|---|---|---|---|---|---|
| 1 | `gen27-context-valid-r1c` | 9/12 | Q05, Q08, Q10 | **11/12** | Q05 | Q08, Q10 | none |
| 2 | `gen27-context-valid-r23` rep1 | 10/12 | Q03, Q10 | **11/12** | Q03 | Q10 | none |
| 3 | `gen27-context-valid-r23` rep2 | 9/12 | Q03, Q07, Q10 | **11/12** | Q07 | Q03, Q10 | none |

Aggregate: v1 28/36 (0.778), v2 33/36 (0.917). No case regressed.

This was verified, not assumed. The recorded Gen27 diagnostic predicted exactly
this outcome from a much cruder rule — stripping the prefix — and the typed
contract reaches the same three-repetition result by a stricter route.

The three surviving failures are genuine and each is a different case: Q05 in
repetition 1, Q03 in repetition 2, Q07 in repetition 3. In each the reader cited
an entry that the capture really contains but which does not carry the anchor
the case requires. That is the fail-closed provenance signal Gen27 was built to
produce, and it survives the correction.

## Identity of the regraded material

Deterministic correction over the same responses is provable from these
fingerprints, recorded per repetition in the results summary: the SHA-256 of the
ordered stored responses, of the typed projection, and of the captured rendered
context.

| rep | responses | projection | rendered context | obs / ref / dual-role IDs |
|---|---|---|---|---|
| 1 | `0d495e01b811e16f…` | `d18e4990ed598966…` | `93a0317f6c970265…` | 19 / 31 / 7 |
| 2 | `7ebbf06d7db0b19e…` | `e88904df9066a5e2…` | `f1cb7a87f1b8b2e8…` | 17 / 33 / 5 |
| 3 | `7b22c904076b42d4…` | `556912951b7de61b…` | `451d541362fd5426…` | 12 / 26 / 4 |

`model_or_product_calls_in_gen28` is false in the machine-readable summary, and
a focused test enforces it by refusing the regrade a socket.

## Boundary

This is a downstream scorer correction over a frozen full-product
context-production capture. It is not a new product repetition, not new fixture
exposure, and not a retrieval score. OM still has no natural-language semantic
query surface, so no Hit@k or ranking number exists. Lifecycle is not scored
here.

`om-context-production-v1` stays exposed and frozen. Any future OM
context-production run needs a new unexposed fixture, not this one.

## Verification

Reproduce with `scripts/regrade_observational_memory_gen28_v2`, which reads only
local frozen artifacts and writes
`results/observational_memory_gen28_citation_contract_v2/summary.json`.

Focused tests cover v1 hash and behavior immutability, the v2 contract hash,
typed projection and support chains, dual-role acceptance, fail-closed handling
of unknown prefixes and unknown, malformed, type-mismatched and ambiguous IDs,
the no-network regrade, and the real Q10 resolution through its exact native ID.
