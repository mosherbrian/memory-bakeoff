# agentmemory vendored retrieval core

Pinned upstream: `rohitg00/agentmemory` commit `e04ba88819c365c9acf9d6661ea802143e728bd6`.

Exact Git-blob matches used by the raw/core arm:

- `src/state/search-index.ts` — `67f3e2ef8f16cbc1108ad9d92e73575f6075c15c`
- `src/state/vector-index.ts` — `d4b8bda760d073cb748967a6744f09d7c95358a1`
- `src/state/stemmer.ts` — `7f210960b67a3178640e5711df47801c14e5d5c3`
- `src/state/synonyms.ts` — `0dab41575c372c23085d982e9884934e556c29d8`

The benchmark worker transcribes the two-stream BM25+vector weighted-RRF block
from upstream `src/state/hybrid-search.ts` (`dc762a6e04a5feb4c98e78a5fe0d9651b21ad964`)
with the graph lane explicitly disabled. It also reproduces `/remember` memory
shaping and >0.7 Jaccard write-time supersession from `src/functions/remember.ts`.

Local shim: `src/state/cjk-segmenter.ts`. It is not upstream source. The bake-off
corpus is English-only, so the shimmed CJK branch is not exercised. Product-mode
agentmemory still requires the real daemon/iii-engine and is tracked separately by
the `agentmemory` REST provider.
