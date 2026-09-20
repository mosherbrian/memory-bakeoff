# muse-drafter: MemStrata artifact check — arXiv source, repo census, claim class (spark pulse 2026-09-14)

Closes the one open P1 item from `SPARK-MEMSTRATA-GROUNDING-20260914.md`
("artifact availability and code license are UNVERIFIED"). Method: extracted
both arXiv source tarballs, then censused the author's public repos via the
GitHub API. $0, read-only.

## 1. The arXiv release contains no code/prompts/datasets

Both e-prints extracted (`https://arxiv.org/e-print/…`, gzip):

- `2606.26511` → `MemStrata_Paper1_Temporal_Validity.tex`, `references.bib`,
  `00README.json` (3 files, 22 KB).
- `2608.20685` → `MemStrata_Paper2_SWEbench_Longitudinal.tex`, `references.bib`,
  `00README.json` (10 KB).

No ancillary files, no harness, no datasets, **no URLs at all** in either `.tex`
(only reference DOIs in the `.bib`). The comment "Code, prompts, and evaluation
datasets **included**" therefore means *included as paper appendices* (Appendix C
lists prompt content-hashes), **not published as files**. The paper body's "We
release the harness, prompts, datasets" is not backed by the arXiv submission.

## 2. Public repo census (`github.com/yadu9989`, same author)

| Repo | License | Pushed | What it is |
|---|---|---|---|
| `memstrata-client` | Apache-2.0 | 2026-07-29 | open Python client / protocol validator |
| `memstrata-evidence-kit` | Apache-2.0 | 2026-07-26 | schemas + offline tamper-evident evidence verification |
| `memstrata-inspeximus-connector` | MIT | 2026-09-09 | optional durable connector |
| `memstrata-lme500-harness` | **MIT** | 2026-09-07 | LongMemEval-S 500 verification harness |
| `memstrata-binaries` | **NOASSERTION** (`LICENSE-COMMERCIAL`) | 2026-09-05 | compiled **product** packages |
| `memstrata` (from the earlier search snippet) | — | — | **404 / not public now** |

Two consequences:

- **The paper's own evaluation artifacts are still not public.** The six
  synthetic benchmarks, their hashes, the calibration dataset, and the reported
  per-run logs are not any of these repos; the only released harness is
  LongMemEval-S-specific. So a re-derivation of the 0.95–1.00 / stale-0 numbers
  is **not possible** from public artifacts. P1 stays: do not plan adapter work.
- **Claim class is vendor-affiliated.** Author affiliation on Paper 1 reads
  "MemStrata.dev — Called It Inc. (Enterprise)", and `memstrata-binaries` ships
  under a commercial license. MemStrata is a **commercial product**, so its
  numbers are vendor claims (single-author, self-run), and "we release" refers to
  open tooling around a closed runtime — not to a research artifact.

## 3. Side find worth a hand-off: `memstrata-lme500-harness`

Not the paper's harness, but an MIT-licensed, provenance-heavy **LongMemEval-S
500 verifier** by the same author, and it is unusually disciplined:

- unit `data/` with `DATA_PROVENANCE.md`, `DATASET_RELEASE_NOTES.md`,
  `PROTOCOL.md`; gold-free input (answers/session IDs/categories stripped before
  retrieval), hash-pinned blinded JSONL; per-item project namespaces with
  isolation checks; provider failure ⇒ run incomplete, never counted as wrong;
  Wilson intervals + paired tests; six question types.
- Its own README disclaims the marketing read: *"verification apparatus and
  immutable data, not a newly measured product score or a demonstrated
  reproduction of the historical R454 result."*

This matters to our LME thread (L-LME-*) as an example of the exact
provenance/gold-free/hash-pinned discipline we demand, and as a possible
independent way to check LME-S claims — but it is single-vendor and its scope is
MemStrata Conversational, so it is **not** a neutral third-party result.
Recommend handing it to **Alice** (claim class) and the LME thread owner; no
import.

## Net

MemStrata's paper numbers are **not re-derivable from public artifacts**; the
public code is a commercial product line plus a LongMemEval-S verifier. Grounding
stays as a *design* reference (the supersession mechanism and the marker-free
invariant), not a data source. My prior artifact's "UNVERIFIED" is now resolved to
"verified absent / vendor-affiliated".

$0, web + arXiv-source reads only, no Muse batching. — muse-drafter (Spark)
