# Invalidated execution artifact

This directory is preserved for audit only and is **not** an authoritative
Mem0 repetition.  Execution-session handling accidentally allowed multiple
processes with the same configuration and output path to run concurrently.
Although the stored run is internally valid, its process identity is ambiguous.

Do not aggregate or compare this artifact.  The three independent authoritative
stress repetitions are `mem0_raw_product_gen10_stress-clean-r1`,
`mem0_raw_product_gen10_stress-clean-r2`, and
`mem0_raw_product_gen10_stress-clean-r3`.
