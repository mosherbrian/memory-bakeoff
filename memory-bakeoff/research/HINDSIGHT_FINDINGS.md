# Hindsight runtime findings

Hindsight was investigated against `vectorize-io/hindsight` release **v0.9.2**
(tag commit `ebad478240d3171bb88201ececda5e8d9883d22d`; released 2026-08-25).
Current `main` was also inspected at
`b7880ba3a8accb7ef88b24b34f6e0c3caf9ed548` while checking post-release
configuration and retrieval code.

## No synthetic Hindsight score

Hindsight recall is not a small in-process retriever that can be faithfully copied
into the harness. Its own test suite defines a DB-backed multi-arm pipeline:

1. semantic/vector retrieval — baseline arm and not optional,
2. BM25/full-text retrieval,
3. graph retrieval,
4. temporal retrieval,
5. optional cross-encoder reranking/fusion after candidate collection.

The semantic and lexical arms are implemented together over the persisted
`memory_units` store, while graph and temporal retrieval are also store-backed.
The supported database implementations are PostgreSQL-family/Oracle rather than an
embedded SQLite fallback. Rewriting those pieces in Python inside the bake-off would
measure our reimplementation, not Hindsight, so **no pseudo-Hindsight leaderboard row
is emitted**.

## Embedded PostgreSQL is proven runnable here

The apparent PostgreSQL blocker was solved through Hindsight's documented embedded
DB path. `hindsight-all` uses `pg0-embedded`; the underlying pg0 project publishes a
self-contained PostgreSQL+pgvector runtime.

A Linux x86_64 pg0 **0.15.1** Actions artifact was transferred through the authorized
GitHub connector and preserved at:

`vendor/pg0-bin/pg0-linux-x86_64-gnu`

SHA-256:

`3b2a129c761ed371dfb0908e227bc90e652a7d60d8bcc1be037c3767f855b91f`

A throwaway smoke run as the unprivileged `oai` user successfully initialized and
started **PostgreSQL 18.1** with **pgvector 0.8.5**, accepted SQL on localhost, and shut
down cleanly. The initial root attempt failed only because PostgreSQL correctly refuses
to run `initdb` as root.

This means Hindsight is **not blocked on the database** in this sandbox.

## Shared-embedding controlled arm is supported upstream

Hindsight's real `OpenAIEmbeddings` provider accepts a custom OpenAI-compatible
`base_url` and configurable dimensions. Therefore a future controlled arm can point
stock Hindsight at a localhost `/v1/embeddings` service backed by the same shared LSA
representation used for the MemBukkit/Mem0/agentmemory ablations. That would preserve
Hindsight's real persistence, semantic+BM25 SQL retrieval, graph/temporal arms, and
fusion while holding the semantic representation constant.

This is preferable to patching Hindsight's embedding code.

## Remaining blocker: compiled Python dependency transfer

The current ChatGPT coding container has no ordinary outbound network access. Hindsight
v0.9.2's Python service package requires runtime dependencies that are not installed
here, most importantly compiled PostgreSQL client support (`asyncpg`; the Python
`pgvector` package is also absent).

We found all of the required upstream artifacts, including:

- Hindsight v0.9.2 release wheel `hindsight_api_slim-0.9.2-py3-none-any.whl`;
- asyncpg 0.31.0 CPython 3.13 manylinux wheel;
- Hindsight's release `python-packages` GitHub Actions artifact.

But the transfer boundaries differ:

- GitHub **Actions artifacts** can be moved through the connector into this sandbox;
- generic GitHub release binaries / PyPI wheel CDN files cannot;
- Hindsight's one-day `python-packages` Actions artifact had already expired;
- this GitHub installation exposes no writable user repository, so a temporary Actions
  relay workflow cannot be created safely from this chat.

Accordingly the honest status is: **database path proven; official embedding seam
proven; Python service runtime blocked on compiled-wheel transfer; no Hindsight score
yet**.

## Exact next run when dependencies are transferable

1. Install Hindsight v0.9.2 and its compiled dependencies in an isolated environment.
2. Start preserved pg0/PostgreSQL as an unprivileged user.
3. Start a localhost OpenAI-compatible embeddings endpoint backed by the benchmark's
   shared LSA representation.
4. Configure Hindsight to use that embeddings base URL and `LLM_PROVIDER=none` for the
   raw round; disable the cross-encoder via supported configuration if its model is not
   available.
5. Ingest the canonical records with stable `document_id`/metadata provenance.
6. Run core and 500-record stress corpora through Hindsight's real recall API.
7. Preserve service version/config, SQL-backed traces, retrieved record IDs, and exact
   context sizes.
8. Run a separate product-mode round with the normal LLM extraction pipeline through
   the existing ChatGPT/OpenAI-compatible sidecar.
