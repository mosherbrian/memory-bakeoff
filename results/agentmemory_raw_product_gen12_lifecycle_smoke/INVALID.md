# Invalidated diagnostic trace

This first Generation 12 lifecycle trace is preserved for audit but is not the
authoritative sentinel.  It was created before the snapshot code established
that the pinned `/agentmemory/memories?project=...` endpoint does not enforce
the requested project filter.  Its live counts include a prior one-record
provenance probe from another project.

Use `results/agentmemory_raw_product_gen12_lifecycle_smoke_clean/trace.json`
for the clean authoritative diagnostic.  No score was derived from either
directory.
