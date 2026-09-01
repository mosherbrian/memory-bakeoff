# Invalidated candidate-flow capture

This trace capture queried the stale generation-3 Hindsight listener that also
invalidated generation 4. Its bank name, service configuration, and process
were not the intended fresh generation-5 runtime. It is retained solely to
document the discovery mechanism; do not use its ranks or candidate-presence
counts as causal benchmark evidence. See
`research/HINDSIGHT_GEN4_INVALIDATION.md` and
`research/HINDSIGHT_GEN5_PIPELINE_DIAGNOSIS.md`.
