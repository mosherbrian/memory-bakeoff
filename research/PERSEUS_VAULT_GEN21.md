# Perseus Vault Generation 21

Status: **complete raw-product late-entry evaluation; no reader run**.

Perseus Vault was added after Round 1's corpus, truth, queries, scorer, and
metrics were frozen.  It receives no architecture-specific benchmark changes.

## Identity and contract

- Official `Perseus-Computing-LLC/perseus-vault` v2.23.2, annotated tag
  `4f405f53f4c9b6a403df0d42cf0d59bf80c64da4`, source commit
  `9c829207a4b44a8e679ba912b4c1c5608c8f1e36`, MIT.
- Official `perseus-vault-aarch64-apple-darwin.tar.gz`: published and verified
  SHA-256 `e9b0912c5a2279f84d59a5ec8fb98e437a8f0feea8dac63dbca36759ff920dcb`.
- M1/macOS arm64 binary reports `perseus-vault 2.23.2 (9c82920)`.
- Fresh encrypted SQLite and fresh temporary AES-256-GCM key per repetition.
- Bundled quantized all-MiniLM-L6-v2, 384 dimensions; native hybrid recall
  explicitly selected (FTS5 + dense cosine RRF); no reranker, LLM, decay,
  maintenance, capture, correction, or supersede call in the scored lane.

The evaluated raw-product composite is **documented operator CLI `write` seed
plus native MCP `perseus_vault_recall(mode=hybrid)`**.  This distinction is
material: agent-facing MCP `remember` without an admission envelope creates a
non-serveable pending proposal, so it was not silently substituted.

## Frozen mapping and preflight

Every record uses generic category `benchmark_record`, key `record-<canonical
ID>`, and a workspace equal to SHA-256 of copied canonical scope.  The stored
JSON copies only canonical ID, assertion text, reference time, scope, and
constant source kind.  It contains no correction link, answer-specific key,
relation, tag, importance, or query hint.

An eight-record fresh-Vault preflight validated exact/semantic recall, M011/M012,
scope isolation for Atlas/Beacon, success/failure content, and a negative query.
All returned records carried a native entity ID and persisted canonical marker;
the adapter fails closed on any mismatch.  Atlas and Beacon returned only their
own workspace records.  The negative query natively filled results (negative
empty rate 0), preserved as product behavior.

## Frozen Round-1 results (three fresh audited repetitions)

| Lane | Hit@5 | MRR range | All relevant@5 | Prohibited@5 | Context chars |
|---|---:|---:|---:|---:|---:|
| Core (50) | 1.000 | 0.875–0.938 | 1.000 | 0.117 | 417.8 |
| Stress (500) | 0.958 | 0.868–0.889 | 0.958 | 0.108 | 423.0–423.5 |

Exact per-request native requests/responses, IDs, receipt maps, post-ingest
stats, and workspace scans are in `results/perseus_vault_gen21_audited_*`.

## Lifecycle audit

Core retained 50/50 active records in every run.  Stress received 500 native
write receipts but the native post-ingest scan retained only **393 active
records** in every run: **107/500** receipt-mapped records were absent after
ordinary writes.  This is native write-time consolidation/dedup, not harness
filtering.  Retrieval results must not be credited without this state loss.
Classification against correction truth remains a separate interpretation step;
no benchmark truth was supplied to the product during ingestion.

## Explicit capability and temporal smoke

Separately, an explicit caller-driven `perseus_vault_supersede` on M011→M012
deprecated M011, created a native `supersedes` link, preserved M011 through
`as_of`, and made M012 the current recall result.  This is capability evidence,
not automatic correction quality.

Native `valid_at` and `bitemporal` APIs also returned a freshly written fact
with its transaction and valid-time fields.  No new temporal fixture or bonus
score was created; engine-independent bitemporal evaluation remains deferred to
Generation 22.
