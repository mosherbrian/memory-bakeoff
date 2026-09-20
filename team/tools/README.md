# team/tools — durable copy of the evidence-integrity checker suite

**Copied:** 2026-09-15 by Corvid (QUEUE S3-7) · **Cost:** $0
**Source:** `implementer/repo-glm-dsh3/scripts/check_*.py` (byte-identical; 21
files, sha256 below). This directory is the **durable backup** in the shared
canonical root; the suite previously existed **only** as untracked files in one
lane (`CORVID-CHECKER-SUITE-TRACKING-GAP.md`).

## How to run

- **Meta-guard is self-contained and works from here:**
  `python3 team/tools/check_checker_exit_contracts.py` → **20/20 hold** (verified
  from this copy, 2026-09-15). Its fixtures are in-tree.
- **The other guards assume the repo tree for their default paths** (they compute
  the repo root from their own location), so from here they need explicit args,
  e.g. `--team ../../team`, `--map ../../team/CORVID-CHECKER-COVERAGE-MAP.md`.
  Their canonical home remains `implementer/repo-glm-dsh3/scripts/`, and the
  `CORVID-P2-EVIDENCE-GATE-CARD.md` invocations assume that location.
### Runnability from this copy (2026-09-15)

`--self-test` run for all 21 files from `team/tools/`: **20 pass**. The only
failure is `check_invocation_corpus_reachability.py` — its `--self-test` loads the
trigger source via a `HERE`-relative default (`/var/home/bmosher/implementer/repo/...`),
the documented path caveat (the self-test branch does not read `--extension`).
Run the guard itself with explicit paths and it works from here:
`python3 check_invocation_corpus_reachability.py --corpus ../invocation-corpus-v1 --extension ../../implementer/repo/extensions/pi-change-trigger/index.ts`
→ 0 findings. The meta-guard's full 20/20 control sweep also runs from here.

- **Not committed:** this is a copy in `team/`, not a version-controlled home.
  The durable fix is still a **canonical commit + `REPO-CANONICAL.txt` `shared:`
  declaration** (owner: GiLMore/Corvid).

## sha256 manifest (first 12 hex; recompute with `sha256sum check_*.py`)

```
c15e62a4bead  check_agents_known_failures_consistency.py
86c0b9025dc1  check_card_register_consistency.py
99d7c814d06f  check_checker_exit_contracts.py
c9832632edee  check_cross_copy_drift.py
b7edb9011fb7  check_experiment_class_schema.py
d090ebfcf46f  check_frozen_id_provenance.py
0506656b2dac  check_gen38_anchor.py
45922e9185ca  check_identifier_lifecycle.py
a29253b754a6  check_invalidated_pointers.py
e7a7fb211086  check_invocation_corpus_reachability.py
d74ab1e99775  check_ledger_counts.py
55e94f16238b  check_longmemeval_qualifiers.py
cda1ee4a1ef0  check_map_hashes.py
502be027c505  check_membukkit_parity.py
5ebef46f0e8d  check_orphan_evidence.py
131c9fe24c03  check_protected_findings.py
0fd895cdffc5  check_query_fork.py
33c3365f0cd7  check_rd_thread_labels.py
0b8fd3aa5666  check_record_text_identity.py
09814e25dcba  check_required_metrics.py
bbe06ca64391  check_results_value_pointers.py
```

(These must match the coverage map's Layer B hashes; `check_map_hashes.py` is the
maintenance guard for those cells.)

**Verified 2026-09-15:** computed sha256 of each copied guard and compared to the
coverage map's Layer B rows — **20/20 match, 0 missing**, so this durable copy
matches the authoritative map exactly.

— Corvid (`worker-glm-dsh3`). $0.
