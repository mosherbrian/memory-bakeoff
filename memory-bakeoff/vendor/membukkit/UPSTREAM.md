# Vendored MemBukkit core

Upstream: `memseekai/membukkit`

Pinned commit: `f28a2e58cdc0e77758c0f6d9a1e050f80dcad807`

The following semantics-bearing files are copied byte-for-byte from that commit and
verified with Git blob SHA by `scripts/verify_membukkit_vendor.py`:

- `config.py` — `ffef9fe8649fd9a3d59bc88cee1447930689fd90`
- `time_utils.py` — `6dd31a6e5b1f26e02c118454797af3107a318cad`
- `storage/base.py` — `933015fd6e78cbdbedd3bdee4beef7280ac49f85`
- `storage/memory.py` — `e3256902ac9e054377b2e167af43372b1d17f73a`
- `retrieval/bucket_index.py` — `b6dba922cb9409c16db8f530c61b88308230bed6`
- `retrieval/buckets.py` — `5cd4c114b9cbf9e121b25e0d72dab6d9c54550e5`
- `retrieval/router.py` — `cfca79b838eb1494798c1ef4423a7e59557b2f7f`
- `supersession.py` — `319556707aea9468816efcfffff0ed8781cd48d6`
- `pipeline.py` — `295893c704e6582f9f979c007439e60eed92e0e3`

Local shims: package `__init__.py`, `storage/__init__.py`, `retrieval/__init__.py`,
`telemetry.py`, `progress.py`, and `usage.py`. They remove optional packaging,
observability, persistence, and accounting dependencies in the isolated sandbox; they
do not implement ranking, routing, temporal filtering, storage candidate generation,
or RRF semantics.

## Raw benchmark mode

Raw mode is an architecture ablation, **not a stock-pretrained product score**. It
uses the same corpus-fit 32-D LSA representation as the benchmark dense baseline and
feeds it into the pinned upstream `MemorySystem`/`InMemoryBackend`. Default
`MEMBUKKIT_SELECT=none` isolates MemBukkit's topic-bucket scan gate. Set
`MEMBUKKIT_SELECT=hybrid` to exercise upstream hybrid RRF with the deterministic
lexical reranker copied from `tests/test_union_parity.py`; that reranker is a CI test
double, not MemBukkit's pretrained cross-encoder.

`ingest_facts()` is used exactly as the upstream public structured-ingest path: it
bypasses LLM distillation and does not infer supersession. Product mode will be a
separate experiment with the intended extractor/models.
