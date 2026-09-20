# Evidence-integrity decision register (open items, one page)

**Author:** Corvid (`worker-glm-dsh3`), evidence-integrity
**Date:** 2026-09-14 · **Cost:** $0, read-only synthesis (no new checks)
**Purpose:** the append-only log now holds several Corvid findings; this page
gives the owner a single decision list with a concrete acceptance test per item.
Nothing here is a ruling, and nothing is applied.

| # | Finding / recommendation | Owner | Acceptance test | Receipt |
|---|---|---|---|---|
| 1 | **Checker suite has no durable home** — 19 `scripts/check_*.py` exist only in `repo-glm-dsh3`, untracked; canonical/dsh2 have none | GiLMore / Corvid | `git ls-files scripts/check_*.py` > 0 in a canonical tree, **or** the scripts live under mirrored `team/tools/` | `CORVID-CHECKER-SUITE-TRACKING-GAP.md` |
| 2 | **Cross-copy declaration is incomplete** — P2 chain + safety files **and all of `extensions/`** undeclared, so "2 known drifts" understates the fork delta; **feature built: `canonical-only:` (guard 15, rev 22), dry run 6 findings zero missing-noise**; extension census adds the trigger (missing) + A2 vault (stale) | GiLMore (record-level) | paste the dry-run snippet; sync/declare `extensions/` too | `CORVID-CROSSTREE-FILE-CENSUS.md`, `CORVID-CROSSTREE-DECLARATION-DRYRUN.md`, `CORVID-EXTENSIONS-CROSSTREE-CENSUS.md` |
| 3 | ~~**`experiment_class` sparse**~~ — **CORRECTED 2026-09-14: current runner already emits it per record; the 131 class-less records are all pre-schema frozen dirs** (schema-versioned 75/75 carry it). Vocabulary now guarded (guard 19). No code change needed. | — | none (historical only) | `CORVID-EXPERIMENT-CLASS-CENSUS.md` §CORRECTION |
| 4 | **Product-mode gate trusts a flag, not a path** — 9 providers set `product_ingest=True`, only 1 product-mode run ever; **audit: AgentMemory is mode-blind, the 4 baselines + AgentMemory each have a validated fix diff, the other externals branch** | implementer-of-record | apply `CORVID-PRODUCT-INGEST-FIX-COMBINED.diff` (supersedes the baseline + AgentMemory singles; they conflict on the test file); path providers evidenced or ineligible; see `APPLY-QUEUE.md` | `CORVID-PRODUCT-PATH-CENSUS.md`, `CORVID-AGENTMEMORY-PRODUCT-FLAG.md`, `CORVID-AGENTMEMORY-PRODUCT-FIX.md` |
| 5 | **Cross-tree parity probe hardening APPLIED 2026-09-14** (no traceback on bad input, sha `6840a4a7…`); wiring still pending | GiLMore / Corvid | wire the golden half after the dsh3 `src` sync; census half as a scheduled census | `CORVID-CROSSTREE-PARITY-PROBE.md`, `CORVID-PROBE-PROMOTION-GATE.md` |
| 6 | ~~**Row-36 corpus: S09 unfireable; selftest predicate non-binding**~~ — **DONE 2026-09-14** (S09 fix + binding selftest landed and verified; adopted as guard 18) | worker-glm-2 / Corvid | `check_invocation_corpus_reachability.py` exits 0; corpus selftest uses the binding check | `CORVID-ROW42-CORPUS-FIX.md` |
| 7 | **S4/S5 blind quorum failed** — 0 eligible blind raters on the metered lane | GiLMore | rater call recorded; if none, B5 reported instrument-exposed | `CORVID-BLIND-QUORUM-REGISTER.md` |
| 8 | ~~**PrecisionMemBench precision receipts 3/13** — 10 rows not locally re-derivable~~ — **DONE 2026-09-15**: all 13 reports fetched to `team/row-pmb-precision/`; `verify_precision.py` matches 13/13 (denominator finding intact) | muse-drafter / Alice | 13/13 local and script matches (Alice sample-check still welcome) | `SPARK-PMB-RECEIPT-FILL-20260915.md` |

## Standing probes (built, unadopted; not in the meta-guard)

`probe_crosstree_parity.py`, `probe_experiment_class_schema.py`,
`census_verification_signatures.py` (the reachability probe graduated to
**guard 18**, `check_invocation_corpus_reachability.py`). The
promotion gate (`CORVID-PROBE-PROMOTION-GATE.md`) is the adoption checklist;
none is wired, so the meta-guard stays **17/17 hold**.

— **Corvid** (`worker-glm-dsh3`). $0, read-only synthesis.
