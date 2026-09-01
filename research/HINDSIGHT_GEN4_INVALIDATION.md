# Hindsight generation-4 invalidation

## Status

All generation-4 Hindsight result directories are invalidated and excluded from
leaderboards, comparative analysis, and product claims.

## Discovery

An audit on 2026-08-31 found a generation-3 Hindsight process already listening
on `127.0.0.1:8891`. The generation-4 launcher did not reject an occupied port,
so its readiness checks and benchmark clients attached to that stale service
instead of the service it had just attempted to launch. The intended launch also
set `HINDSIGHT_API_EMBEDDINGS_ONNX_MODEL_PATH` to the model snapshot directory.
Hindsight requires the ONNX file itself (`onnx/model.onnx`); a clean start
failed with ONNX `InvalidProtobuf` while parsing the directory path. The stale
listener masked that startup failure.

The run metadata's unique database namespaces, banks, and service configuration
therefore describe the attempted service, not the process that served requests.
This violates the fresh-service and exact-configuration requirements.

## Affected artifacts

- `results/hindsight_gen4_core_r1/`
- `results/hindsight_gen4_core_r2/`
- `results/hindsight_gen4_core_r3/`
- `results/hindsight_gen4_core_r4/`
- `results/hindsight_gen4_stress_r1/`
- `results/hindsight_gen4_stress_r2/`
- `results/hindsight_gen4_stress_r3/`

The artifacts are preserved to make the failed isolation auditable. Each
directory contains an `INVALIDATED.md` sidecar. Corrected generation-5 runs use
the ONNX file path and fail before launch when port 8891 is occupied.
