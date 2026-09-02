# Frozen Graphiti Gen19 configured-product schema

This is a separate configured-product profile, not Graphiti default policy.
It was frozen before any Gen19 sentinel or scored retrieval run and is grounded
in general coding, configuration, inference-testing, and experimental-memory
concepts rather than held-out answers.

The implementation is `memory_bakeoff.graphiti_gen19_schema`:

- Artifact/Resource; System/Component; Configuration; Environment;
  Procedure/Command; Measurement/Result; Decision/Conclusion.
- One general typed relation family whose documented predicates are HAS_VALUE,
  CONFIGURED_WITH, RUNS_ON, USES, LOCATED_AT, MEASURED_AS, PRODUCED,
  APPLIES_TO, OWNED_BY, REPLACES, CORRECTS, INVALIDATES, SUCCEEDED_WITH,
  FAILED_WITH, and SCOPED_TO.

The exact same schema and extraction instruction must be passed to every
episode in every later Gen19 diagnostic and any future configured score. Schema
changes require a new named profile/generation. No hand-authored triples,
post-hoc edge repair, query-specific rules, or harness filtering are allowed.

## Preflight result

The first native extraction trace is blocked: see
`GRAPHITI_GEN19_FINDINGS.md`. The frozen schema is retained unchanged; it must
not be tuned from this failure before a new profile is explicitly authorized.
