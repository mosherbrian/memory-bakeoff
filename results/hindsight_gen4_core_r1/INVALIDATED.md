# Invalidated diagnostic repetition

This first generation-4 core attempt completed retrieval with native, publishable
source provenance, but it exposed a reusable Hindsight adapter resource-lifecycle
defect: the native `aiohttp` client session was not closed after `run_provider()`.
It is preserved for diagnosis only and is excluded from the authoritative
three-repetition aggregate. The fix closes provider resources in the runner's
`finally` path; all scored repetitions will use fresh result directories after
that fix.

This directory is additionally invalidated by the later generation-4
service-isolation audit: a stale generation-3 listener on port 8891 served the
requests while the intended generation-4 service had an invalid ONNX directory
path. No generation-4 score is usable as evidence. See
`research/HINDSIGHT_GEN4_INVALIDATION.md`.
