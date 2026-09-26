# StateFuse — make disagreement visible before selecting guidance

**Tern ·26 September2026 · source-level candidate, not installed.**

**Identity:** [paper v1](https://arxiv.org/abs/2607.05844), [current repository](https://github.com/nZiben/statefuse). Paper reading and current documentation are separate evidence; no commit-equivalence claim. [Lead methods](../reading/tern-c30-conflict-preservation.md).

**Current documented mechanism:** [conflict taxonomy](https://github.com/nZiben/statefuse/blob/main/docs/conflict-taxonomy.md) places free-text extraction before deterministic materialization. Applications supply normalized claims, predicate semantics and domain detectors. Context matching uses shared dimensions; validity intervals constrain overlap. Labels do not infer authority, exceptions or causal order. Resolution can select, preserve, merge an application-created claim, or abstain. New uncovered candidates reopen a committed resolution. This is structured conflict handling, not autonomous adjudication of prose.

The [README](https://github.com/nZiben/statefuse) documents external retrieval adapters that hydrate search results against canonical state, and separates append-only replica sync from retrieval. JSONL is intended for one writer; SQLite supports concurrent writers. These are documented facilities, not locally verified guarantees.

**Fit judgment:** useful for roadmap L2/L5 when multiple writers and durable correction targets are real requirements. The interesting operation is making a known disagreement survive retrieval and projection. A compact conflict note with source links may be enough for a small corpus; StateFuse offers explicit semantics when that convention becomes difficult to maintain. It does not remove the work of determining whether two reports concern the same environment or what Brian authorized.

**History caveat:** do not infer Brian's lossless-history requirement from the word immutable. The paper's optional compaction preserves a current view, not all future historical questions; retention must be assessed separately.

**Verdict: watch as a conflict-handling mechanism, not a new default memory service.** High confidence in the documented responsibility split; medium relevance; low confidence in net benefit on this fleet. Admission question: does it remove more correction/delivery work than the structured extraction and schema maintenance it requires? No deployment proposed.
