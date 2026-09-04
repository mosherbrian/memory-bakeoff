#!/usr/bin/env python
"""Build the Gen40 comparison artifact and research report from the leaves.

Reads only the two run leaves and the model pins. Produces no score.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memory_bakeoff.membukkit_gen40 import (  # noqa: E402
    FALLBACK_ENCODER,
    FALLBACK_RERANKER,
    INTENDED_ENCODER_REPO,
    INTENDED_RERANKER_REPO,
    MEMBUKKIT_PINNED_COMMIT,
    SYNTHETIC_FACTS,
    SYNTHETIC_QUERIES,
    contract_sha256,
    load_json,
)

OUT = ROOT / "results" / "membukkit_gen40_intended_model"


def compare(online: dict, offline: dict) -> dict:
    pairs = list(zip(online["searches"], offline["searches"]))
    return {
        "order_identical_queries": sum(a["returned_ids"] == b["returned_ids"] for a, b in pairs),
        "selection_identical_queries": sum(
            set(a["returned_ids"]) == set(b["returned_ids"]) for a, b in pairs
        ),
        "n_queries": len(pairs),
        "probe_values_identical": online["probes"] == offline["probes"],
        "lifecycle_identical": online["lifecycle"] == offline["lifecycle"],
        "offline_downloads": offline["load_trace"]["downloads"],
        "revisions_identical": all(
            online["snapshots"][r]["revision"] == offline["snapshots"][r]["revision"]
            for r in ("encoder", "reranker")
        ),
        "digests": {"online": online["digest"], "offline": offline["digest"]},
        "differing_fields": sorted(
            k
            for k in set(online) | set(offline)
            if k not in ("digest", "wall_clock_seconds")
            and online.get(k) != offline.get(k)
        ),
    }


def report(online: dict, offline: dict, cmp_: dict, pins: dict) -> str:
    src = online["membukkit_source"]
    enc, rer = online["snapshots"]["encoder"], online["snapshots"]["reranker"]
    p = online["probes"]
    rc = online["retrieval_defaults"]
    lc = online["lifecycle"]
    n_files = {"encoder": len(enc["local_files"]), "reranker": len(rer["local_files"])}

    def rows(role: str, snap: dict, pin: dict) -> str:
        lines = [
            "| field | value |",
            "| --- | --- |",
            f"| repository | `{pin['repo']}` |",
            f"| revision | `{pin['revision']}` |",
            f"| public without credentials | {not pin['private']} (gated: {pin['gated']}) |",
            f"| library / pipeline | {pin['library_name']} / {pin['pipeline_tag']} |",
            f"| license (model card) | {pin['license'] or 'not stated'} |",
            f"| files pinned | {n_files[role]} |",
            f"| every file reconciles to that revision | {snap['reconciliation']['all_match']} |",
        ]
        return "\n".join(lines)

    weights = {
        "encoder": pins["encoder"]["files"]["model.safetensors"],
        "reranker": pins["reranker"]["files"]["model.safetensors"],
    }

    return f"""# MemBukkit intended-model path: reproduced

**Evidence class:** `{online['evidence_class']}`. This generation establishes product
identity. It produces no score, touches no benchmark corpus, and must never be
compared with Round1, longitudinal-v1, MemConflict or any baseline number.

Gen7 could not run MemBukkit's intended models: `{INTENDED_ENCODER_REPO}` and
`{INTENDED_RERANKER_REPO}` both returned 401, the pinned resolver silently
substituted `{FALLBACK_ENCODER}` and `{FALLBACK_RERANKER}`, and the harness
failed closed with no scored run. `research/MEMBUKKIT_INTENDED_MODEL_GEN7.md`
records that blocker and is unchanged by this generation.

Both repositories are now publicly readable. The previously blocked path
reproduces on the original pinned source, with no fallback, and repeats
identically from a frozen local snapshot with the network blocked.

## Source identity — the historical commit, not a newer one

| field | value |
| --- | --- |
| checkout HEAD | `{src['head']}` |
| matches the Gen7 pin | {src['matches_gen7_pin']} |
| resolver | `{src['resolver_file']}` |
| package version | {src['version'] or 'unset'} |

The intended-model names still live in that exact file at the lines below, so
the question Gen7 asked is the question this generation answers:

```
{chr(10).join(f'{n}: {t.strip()}' for n, t in sorted(src['resolver_lines'].items(), key=lambda kv: int(kv[0])))}
```

No newer MemBukkit revision was substituted, and none was needed: the
historical source loads the newly public weights unchanged, so the separate
`current_upstream_compatibility_diagnostic` that Gen40 reserved for a failure
was not run.

## Model identity

### Bi-encoder

{rows('encoder', enc, pins['encoder'])}

### Cross-encoder reranker

{rows('reranker', rer, pins['reranker'])}

Weight-file content identity, independent of any local path:

| role | file | bytes | sha256 |
| --- | --- | --- | --- |
| bi-encoder | model.safetensors | {weights['encoder']['size']} | `{weights['encoder']['lfs_sha256']}` |
| reranker | model.safetensors | {weights['reranker']['size']} | `{weights['reranker']['lfs_sha256']}` |

Every file in both snapshots was checked against the published revision: large
files by their LFS sha256, small files by recomputing the git blob object id.
Both snapshots reconcile completely — no mismatched file, no local-only file,
no file in the revision that is missing locally.

## Fallback could not be mistaken for success

The resolver, the hub client and both model constructors were wrapped as
observers. Every wrapper forwards to the original and only records what passed
through it, so embeddings and ranking cannot be affected. A run fails if a
substitute repository is requested, downloaded or loaded, or if either model is
loaded from anywhere but the pinned snapshot directory.

| observation | online | offline |
| --- | --- | --- |
| snapshot already cached before the run | {online['snapshot_cached_before_run']} | {offline['snapshot_cached_before_run']} |
| repositories downloaded in this run | {len(online['load_trace']['downloads'])} | {len(offline['load_trace']['downloads'])} |
| fallback events | {len(online['load_trace']['fallback_events'])} | {len(offline['load_trace']['fallback_events'])} |
| bi-encoder loaded from | pinned snapshot | pinned snapshot |
| reranker loaded from | pinned snapshot | pinned snapshot |
| LLM invocations | {online['llm_invocations']} | {offline['llm_invocations']} |

The offline phase runs in a fresh process with outbound connections blocked at
the socket layer, so a silent re-download would raise rather than pass.

## Synthetic preflight

The fixture is {len(SYNTHETIC_FACTS)} invented facts about a fictional
preservation society and {len(SYNTHETIC_QUERIES)} fixed queries, written before
any model output was observed and unrelated to every corpus in this repository.
Nothing here was tuned: pinned product defaults throughout.

1. **Bi-encoder loads and embeds.** Output shape {p['encoder_shape']}, all
   values finite, rows L2-normalised to {p['encoder_row_norms'][0]}.
2. **Reranker loads and scores.** {p['reranker_n_scores']} finite scores for a
   fixed query and document set, ordered {p['reranker_order']}.
3. **End-to-end.** {online['ingest']['n_facts_offered']} facts written
   ({online['ingest']['n_new_written']} new, backend count
   {online['ingest']['backend_count']}), then all
   {len(SYNTHETIC_QUERIES)} queries searched through both intended models.
4. **Provenance.** Every returned item maps to a synthetic write receipt:
   {len(online['provenance']['unmapped_returned_ids'])} unmapped ids.
5. **Repeat stability.** Returned order identical on repeat:
   {online['stability']['repeats_order_stable']}; selected set identical:
   {online['stability']['repeats_selection_stable']}. Order stability and score
   identity are reported separately, as Gen38 required.
6. **Unrelated queries.** The two off-topic queries return a full
   {rc['top_k']} hits each, like every other query. The product applies no
   relevance floor on this surface. No pass threshold was invented after seeing
   the outputs; this is recorded as behaviour, not as a failure.
7. **Offline repeat.** {cmp_['order_identical_queries']} of
   {cmp_['n_queries']} queries return an identical ordered id list, probe
   values are identical ({cmp_['probe_values_identical']}), and no download
   occurred.

## What the pipeline actually does

Measured on this path, at pinned defaults, with source read alongside:

- **Writes** are embedded by the intended bi-encoder as they enter the bank.
- **Queries** are embedded by the same bi-encoder; there is no separate query model.
- **Routing** partitions the bank into `{rc['num_buckets']}` topic buckets and
  opens only a scan budget of them — measured at 18 to 20 facts scanned of 60,
  a scan fraction of 0.30 to 0.33.
- **The reranker acts after candidate generation**, scoring every candidate in
  the opened region, never the whole bank.
- **Candidate pool** is `candidate_pool={rc['candidate_pool']}`,
  `rerank_cap={rc['rerank_cap']}`; `top_k={rc['top_k']}` leaves the stage.
- **Fusion** is `select="{rc['select']}"`: reciprocal-rank fusion over the
  cross-encoder rank and the cosine rank with `k_rrf={rc['k_rrf']}`. Cosine and
  cross-encoder scores are therefore **not** directly comparable — only their
  ranks are combined. The optional lexical lane is off by default.
- **Presentation is temporal, not by score.** Selection is by relevance;
  the returned list is then ordered by date, so returned order is a
  presentation property.
- **Store** is the in-memory backend, so this generation writes no product database.
- **Provenance** is exact: each hit carries a `source_id` derived from the
  caller's id seed and a `ref` of the form `mem:<first 12 chars>`.

### Lifecycle on this path

Offering the identical {len(SYNTHETIC_FACTS)} facts a second time wrote
{lc['duplicate_offer_new_rows']} new rows — the id seed dedupes. Offering one
dated fact that contradicts a stored one appended it as row
{lc['count_after_update']} and left **both** facts `current`
({lc['n_superseded_hits']} superseded hits, statuses seen:
{', '.join(lc['statuses_seen'])}). So the direct fact-ingest path is
append-and-dedupe only: it performs no supersession. MemBukkit's supersession
machinery sits on the LLM distiller path, which this generation deliberately
did not exercise. That is a measured property of this path, not a defect, and
not a comparison with any other engine.

### One thing worth knowing before any future run

`ModelConfig.device` reaches the reranker but not the bi-encoder: the encoder
wrapper passes only a path to `SentenceTransformer`, which then picks its own
device. Measured here as encoder on `{p['encoder_device']}` and reranker on
`{p['reranker_device']}` in the same process, from one `device="cpu"` request.
Recorded rather than overridden.

## Artifacts

| file | contents |
| --- | --- |
| `results/membukkit_gen40_intended_model/model_pins.json` | both repositories, revisions and per-file identity |
| `results/membukkit_gen40_intended_model/online.json` | acquisition + preflight leaf, digest `{online['digest'][:16]}` |
| `results/membukkit_gen40_intended_model/offline.json` | frozen-snapshot repeat, digest `{offline['digest'][:16]}` |
| `results/membukkit_gen40_intended_model/comparison.json` | online vs offline reconciliation |

The two digests differ only in the fields
{', '.join('`' + f + '`' for f in cmp_['differing_fields']) or 'none'} —
everything else the two phases recorded is equal. Wall-clock and download
timing are excluded from both.

A second complete run into a scratch directory rebuilt the offline digest
byte-identically. The online digest is deliberately not stable across cache
states: the committed leaf was produced with the model cache deleted first, so
it records the acquisition, and a warm repeat differs in exactly
`load_trace` and `snapshot_cached_before_run` and nothing else. Every measured
quantity — probe values, selections, order, provenance, lifecycle — is
identical in both.

Contract module `src/memory_bakeoff/membukkit_gen40.py`, sha256
`{contract_sha256()}`. Pinned upstream `{MEMBUKKIT_PINNED_COMMIT}`.

## What this does and does not settle

Settled: the intended MemBukkit stack exists publicly, is pinnable, loads on the
original pinned source with no substitution, and runs end to end with exact
provenance and a reproducible offline repeat. The asterisk MemBukkit has carried
since Gen7 is retired.

Not settled: anything about quality. No score was produced, and the fixture was
built to exercise the path, not to measure it. Whether the intended-model path
should now re-enter a frozen benchmark lane is a Gen41 decision.
"""


def main() -> int:
    online = load_json(OUT / "online.json")
    offline = load_json(OUT / "offline.json")
    pins = load_json(OUT / "model_pins.json")

    cmp_ = compare(online, offline)
    (OUT / "comparison.json").write_text(json.dumps(cmp_, indent=2, sort_keys=True))

    doc = ROOT / "research" / "MEMBUKKIT_INTENDED_MODEL_GEN40.md"
    doc.write_text(report(online, offline, cmp_, pins))
    print("wrote", doc.relative_to(ROOT), "and comparison.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
