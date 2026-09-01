# Invalidated

This result is invalidated. A stale generation-3 Hindsight listener on port
8891 served the requests while the intended fresh generation-4 service failed
to start because its ONNX model path named a directory instead of
`onnx/model.onnx`. Do not use this score as benchmark evidence. See
`research/HINDSIGHT_GEN4_INVALIDATION.md`.
