# Corvid R&D checker suite — receipt for second-seat verification

**Author:** Corvid (`worker-glm-dsh3`), R&D + evidence-integrity
**Date:** 2026-09-12 (late) · **Cost:** $0, read-only, no LLM
**Purpose:** consolidate the eighteen checkers built this R&D cycle
so the standing second-seat check (Alice, QUEUE row 22 duty) is one pass
instead of four scattered receipts.

**Plain English (for Brian):** eighteen small scripts now guard the evidence index,
two load-bearing portfolio numbers, the list of protected findings, the
suite-baseline numbers in `AGENTS.md`, the exit contracts of the guards
themselves, the thread log's time labels, the ledger's own class counts, which
completed runs no document cites, whether a cited summary reports the
required harm/context metrics, whether a document cites an identifier the record
has superseded or withdrawn, whether this suite's own coverage map still
matches the live guard hashes, and whether shared policy files agree across
checkouts. Each has
a self-test that rejects
a synthetic bad input, and each is green on my tree. This note lists their
hashes and exact commands so another seat can verify them without re-reading my
log.

| Script | sha256 | Defect class it checks | Self-test | Verdict on `repo-glm-dsh3` |
|---|---|---|---|---|
| `scripts/check_invalidated_pointers.py` | `a29253b7…` | references to `results/<dir>` carrying `INVALIDATED.md` (cued vs uncued) **and** dangling `results/`/`research/` Markdown links, **plus a source-less root or a missing/directory/unreadable index `*.md` reported, not silently passed** | PASS | exit 0 (uncued 0, dangling 0) |
| `scripts/check_results_value_pointers.py` | `bbe06ca6…` | a `RESULTS.md` row whose stated Hit/all-relevant numbers no linked `summary.csv` contains, **or a missing/directory/unreadable `RESULTS.md` / linked `summary.csv`** (finding text is printed, so an unreadable source names itself instead of reading as an unbacked row) | PASS | exit 0 (0 pointer findings) |
| `scripts/check_frozen_id_provenance.py` | `d090ebfc…` | a frozen `detail.csv` with empty or non-canonical (`M\d{3}`) `retrieved_ids`, **or a root with no scannable `results/*/detail.csv`, or an unreadable one** | PASS | exit 0 (105 dirs, 24451/24451 canonical) |
| `scripts/check_query_fork.py` | `0fd895cd…` | two runs reporting the same `query_id` with different category/relevant/prohibited referents, **or no scannable/unreadable `detail.csv`** | PASS | exit 0 (26 query_ids, 0 forked) |
| `scripts/check_gen38_anchor.py` | `0506656b…` | the portfolio's Gen38 dynamic_conflict Hit@3 anchor (perseus 0.434 / mem0 0.419 / bm25 0.226) vs the frozen derived + scientific artifacts, **with missing/directory/unreadable artifacts reported structurally, not crashed** | PASS | exit 0 (1142/2631, 1103/2631, 594/2631) |
| `scripts/check_membukkit_parity.py` | `502be027…` | the claim that MemBukkit bucket routing equals full dense scan in the two repointed artifacts, **with each missing/directory/unreadable fixed artifact flagged (fail-closed on a partial repoint), not skipped** | PASS | exit 0 (both 0.5833/0.5417 stress, 0.9583/0.9583 core) |
| `scripts/check_protected_findings.py` | `131c9fe2…` | the machine-readable AGENTS "findings to protect" (agentmemory 418/450 + 82 live; Claude-Mem 0.208/0.583/0.958; Habitus 0.875/0.792/0.025 + the 21/22 non-as-of subset; baseline reader 0.857/1.000), **plus a missing/directory/unreadable prerequisite reported as a structured finding, not a crash** | PASS | exit 0 (0 drift, all three trees) |
| `scripts/check_longmemeval_qualifiers.py` | `55e94f16…` | a LongMemEval score line naming no split/version (**the number must be in the same sentence as the name** — a sentence-boundary number is not a score), **or a root with no scannable/unreadable prose** | PASS | exit 0 — **0 findings on all three trees**; the sentence-boundary false-positive class is closed |
| `scripts/check_agents_known_failures_consistency.py` | `c15e62a4…` | `AGENTS.md` known-failure totals disagreeing with `tests/KNOWN_FAILURES.json` `_totals`, drifts in `_recorded`, a "Pinned by <file> against KNOWN_FAILURES.json" claim whose named file never reads the JSON, **or a missing/directory/unreadable prerequisite (reported, not silently passed or crashed)** | PASS | **exit 1** — canonical `implementer/repo`: 3 (2 stale totals + false pin); `repo-glm-dsh2`/`repo-glm-dsh3`: 1 (false pin); see `team/CORVID-AGENTS-BASELINE-DRIFT.md` |
| `scripts/check_checker_exit_contracts.py` | `956f5338…` | meta-guard: each of the **17 sibling** guards' real CLI must exit 0 **without printing its finding marker** on a clean fixture, and **exit 1, non-traceback, printing its own finding marker** on a dirty fixture; every new control supplies its own argv (`--index`, `--map`/`--scripts`, `--trees`/`--files`, `--canonical`, path arg), so it is hermetic away from the live tree; and the **declared covered set is completeness-checked both ways** — a live `check_*.py` outside it is named `NO CONTROL` and a declared control with no live file is named `CONTROL WITHOUT A LIVE GUARD`, exiting 1 with an `INCOMPLETE` line rather than letting the summary read "17/17" (Muse 4.1 + Alice's crash/clean-marker/completeness power-checks; full sibling coverage completed from Assay's `ASSAY-EXIT-CONTRACT-COVERAGE.md` patch `58f8b323…`, base `55f4d791…`; Assay's reverse-direction patch `c19e0589…` superseded by the applied `6cd289e7…`) | PASS | exit 0 — **17/17 contracts hold** (and **17/17 in a scratch tree with no `team/`**; blinding `required_metrics`/`cross_copy_drift` → 15/17 with both named BROKEN; adding a synthetic 18th guard + removing one → **rc 1, both named**) |
| `scripts/check_rd_thread_labels.py` | `33c3365f…` | a dated label in an RD thread log later than the file's own **mtime** (clock-independent; column-0/indented/list-item labels all count, mid-line prose quotes don't), **or an impossible timestamp/date-only date (`[MALFORMED]`)**, **or a non-UTC time label surfaced as `[UNCHECKED-TIME]`** (default advisory; `--strict` fails); date-only labels are validated **and mtime-date-checked**; **a malformed/unreadable log is structured, not a crash** — additional hygiene guard, **not** in the meta-guard's root-fixture set because it takes a file path | PASS | exit 0 (`RD-THREADS.md`: **0 flagged**, 40 unchecked; `--strict` rc 1 on historical local-time labels) |
| `scripts/check_ledger_counts.py` | `d74ab1e9…` | the `CLAIMS-LEDGER.md` `## CLASSIFICATION` `**Counts:**` / `**Located … N of M rows**` lines **and the `## PROVENANCE` origin-count prose** disagreeing with their tables (classes canonicalized — qualifier inside/outside backticks, hyphenated refinements; unrecognized cells explicit; action-list tables ignored) — additional hygiene guard, **not** in the meta-guard's root-fixture set because it takes a file path | PASS | exit 0 (`CLAIMS-LEDGER.md`: **0 findings**; caught and fixed a real stale "twelve rows" in PROVENANCE) |
| `scripts/check_orphan_evidence.py` | `5ebef46f…` | a `results/<dir>` holding a completed artifact (`summary.csv`/`run.json`) that **no Markdown cites** (boundary/token match; self-citation excluded; labels uncited runs `replica_of_cited` vs `distinct` so the census is actionable, nothing suppressed; allowlist/grace/`--fail` options) — advisory by default because replicates are legitimately uncited; takes a results root + `--cite` roots, so not in the meta-guard set | PASS | advisory exit 0 (census: **54/106 uncited = 25 replica-of-cited + 29 distinct**; see `CORVID-ORPHAN-EVIDENCE-GUARD.md`) |
| `scripts/check_required_metrics.py` | `09814e25…` | a benchmark `*/summary.csv` that **omits a required metric** (`hit@5`, `prohibited@5`, exact context size proxy `mean_context_chars`) unless the dir carries `METRIC-WAIVER.json`, **plus the G-B leakage field** (rev: `3ae6cf05…`): a run declaring `LEAKAGE-REQUIRED.json` with boolean `leakage_required: true` must expose a whole-cell `leakage@\d+` column unless waived by exact token membership in `{"waived": [...]}`; absent/`false` declaration is the legacy floor, unparseable/non-object fails closed, and the marker check runs **before** the unknown-schema skip (Assay's `guard14-leakage-delta.diff` `f7b0ffeb…`, real-path matrix 17/17, Corvid-reproduced, Alice B1–B3 pinned); unknown-schema summaries skipped; missing/malformed/unreadable/unshaped canonical `results/SCHEMA.json` and a directory at `*/summary.csv` are structured, not crashes/silent-skips (adopted from Assay's U2 prototype `e6b50c25…`; schema-guard `b49b4636…` + shape fix `c9b1c696…` applied) | PASS | exit 0 — **0 findings** on `repo-glm-dsh3` (106 summaries, 1 skipped) and `repo-glm-dsh2`/canonical (102 each); real-CLI synthetic tree rejects declared-missing / `leakage_notes` / wrong-metric-waiver rc 1, clears legacy/`false`/present |
| `scripts/check_map_hashes.py` | `cda1ee4a…` | the coverage-map Layer B table cell's guard hash drifting from the live `scripts/check_*.py` file, **or a live guard with no map row (`missing guard row`)** (table cells only — a `c6e2f38b… → 3ae6cf05…` transition sentence is ignored; 8/64/no-ellipsis hash forms accepted; an unparsed hash cell is an `unparsed hash row` finding; adopted from Assay's prototype `439dd1e1…` + completeness patch `b96ecc54…`, host-independent defaults) | PASS | exit 0 — coverage map **0 findings** (all live hashes current; all guards covered) |
| `scripts/check_cross_copy_drift.py` | `f8bd89a9…` | a shared policy/index file (declared in `team/REPO-CANONICAL.txt`, which the guard **parses**: `shared:` drives the file list, `known-drift:` labels owned divergences so a new one shows `(NEW)`, and `tree:` now drives the compared set) whose bytes differ across the checkouts, or a declared file missing/unreadable in one. **Rev 3 (U8):** discovers every `implementer/repo*` checkout and reports `undeclared tree:` / `declared tree missing:`, so a new fork cannot silently go uncompared. **Rev 4–5 (U8 vacuous-scan):** **any** declaration with no `tree:` lines is a `no declared tree set` instrument failure (rc 1, not gated by `--fail`) — v2 closes the empty/comment-only residual v1 missed — so the discovery layer cannot go vacuous; explicit `--trees` still bypasses. Advisory by default because the live drift is owned by Kiln/GiLMore; `--fail` gates | PASS | advisory exit 0 — census **2 known drifts, both labelled `(known-drift)`**, 0 tree gaps; `--self-test` PASS; shared-only and comment-only declarations both fail loud on a staged layout; see `CORVID-U5-CANONICAL-DRIFT-GUARD.md` |
| `scripts/check_identifier_lifecycle.py` | `45922e91…` | a doc citing an identifier the declared index (**`team/IDENTIFIER-LIFECYCLE.txt`**, the only source of truth) has **superseded** (e.g. old `L-HS-02` after the split) or **withdrawn**, where the ±3-line window carries no strong cue (`superseded`/`withdrawn`/`no longer current`/`replaced by`) and no **lifecycle `split`** (rev 4: the anchored phrase `L-HS split`, a named replacement id, or `split` beside `ledger`/`lifecycle` only — the cited id and the generic `row`/`id`/`identifier` words are stripped as self-satisfiable); append-only `log:` records and mechanism `skip:` docs declared out; missing/malformed/unreadable index structured — closes coverage-map U4 / Muse 3.4. **Rev 5 adds declared-list hygiene (Muse-6 U6/U7):** a scan with **zero non-exempt Markdown files** is a `vacuous scan` instrument failure (never `--advisory`-suppressed), and a `log:`/`skip:` basename matching **no scanned file** is an `inert declared-list entry`. **Rev 6 adds U9:** optional `--ledger CLAIMS-LEDGER.md` cross-checks `SUPERSEDED` table rows against the index (`ledger supersession missing from index: <id>`), leaving the default run hermetic | PASS | exit 0 — **31 citations, 0 uncued**, 0 hygiene findings (point-in-time; with `--ledger ../../team/CLAIMS-LEDGER.md` also rc 0); second seat drove revs 2–4; dogfood found and fixed the live stale citations `CLAIMS-LEDGER.md:820`, `RESEARCH-HINDSIGHT-INDEPENDENCE-AUDIT.md:139`/`:165`; Assay's unapplied `split-cue.diff` (`037b5d43…`) is superseded — see `CORVID-IDENTIFIER-LIFECYCLE-GUARD.md` |
| `scripts/check_record_text_identity.py` | `0b8fd3aa…` | the same `M###` id carrying **different record text** across artifacts (`record-text fork:`) or disagreeing with the canonical `src/memory_bakeoff/corpus.py` table (`record-text drift:`); advisory `unindexed record text:` for generated distractors (`--no-unindexed`); scans `.json/.jsonl/.csv/.md/.txt` for `- [M###] <text>`; missing/unreadable/non-directory canonical or scan root structured — closes coverage-map U3 (adopted from Assay's prototype `5ae37253…`, second-seated by Alice) | PASS | exit 0 — **67 ids with text, 48 checked, 0 forks/drifts**, 19 advisory unindexed; `--self-test` PASS |

**Portable fix handoff:** `scripts/fix-results-pointer-defects.diff`
(sha `a72bf13b…`) applies the three row-12 pointer corrections (rows 81, 82,
85). It is applied and green in `repo-glm-dsh3`. An earlier 20:26 application
to the canonical reset tree `implementer/repo` was **reverted 22:06** under the
one-writer-per-tree rule, so the canonical tree is **red again** (2 unbacked
rows + 1 uncued pointer, re-verified 23:2x). `implementer/repo-glm-dsh2`
(Assay's active workspace) is also red. Both owners can apply it with
`scripts/apply-pointer-fixes.sh <repo> [--apply]` (sha `a1cecdc1…`), which
dry-runs or applies the diff and re-runs both checkers; it reports "already
fixed" on `repo-glm-dsh3`.

## Verification commands (read-only)

```bash
cd implementer/repo-glm-dsh3
for s in check_invalidated_pointers check_longmemeval_qualifiers \
         check_results_value_pointers check_frozen_id_provenance \
         check_query_fork check_gen38_anchor check_membukkit_parity \
         check_protected_findings check_agents_known_failures_consistency \
         check_identifier_lifecycle check_record_text_identity; do
  python3 scripts/$s.py --self-test
done
python3 scripts/check_invalidated_pointers.py .
python3 scripts/check_results_value_pointers.py .
python3 scripts/check_frozen_id_provenance.py .
python3 scripts/check_agents_known_failures_consistency.py \
  /home/bmosher/memory-bake-off/implementer/repo
# meta-guard: runs every sibling guard's real CLI on clean+dirty fixtures
python3 scripts/check_checker_exit_contracts.py
# RD thread label hygiene (pulse-end; default path team/RD-THREADS.md)
python3 scripts/check_rd_thread_labels.py \
  /home/bmosher/memory-bake-off/team/RD-THREADS.md
# ledger class counts vs the CLASSIFICATION summary table
python3 scripts/check_ledger_counts.py \
  /home/bmosher/memory-bake-off/team/CLAIMS-LEDGER.md
# orphan-evidence census (advisory; add --fail to gate, --allowlist to except)
python3 scripts/check_orphan_evidence.py . \
  --cite . --cite /home/bmosher/memory-bake-off/team
# required harm/context metrics present in every benchmark summary
python3 scripts/check_required_metrics.py results
# coverage-map guard hashes still match the live guards (cells only)
python3 scripts/check_map_hashes.py
# shared policy/index files agree across the three checkouts (advisory)
python3 scripts/check_cross_copy_drift.py
# sibling-tree handoff check (does not modify anything):
git -C /home/bmosher/memory-bake-off/implementer/repo apply --check \
  /home/bmosher/memory-bake-off/implementer/repo-glm-dsh3/scripts/fix-results-pointer-defects.diff
```

## Known limits (so a nonzero exit is not misread)

- **`check_longmemeval_qualifiers.py`** was the one guard that could exit 1 on a
  named false-positive class (an unrelated number near the word). The
  **sentence-boundary rule** now closes that class (a score must be in the same
  sentence as the name), so the checker is **green (0 findings) on all three
  trees** as of 2026-09-13. The prior census and the historical
  `reviews/accounting…:90` line are in `team/CORVID-P2-ENTRY-CHECKER-RECHECK.md`
  §3; a `LongMemEval-family` (generic-phrasing) class remains a possible future
  refinement, not a live finding.
- **`check_invalidated_pointers.py`** cue heuristic is ±3 lines plus a
  first-15-line banner; it is recall-oriented, so a "cued" result means
  "looks documented", not "verified".
- All of these are **static** checks. A green suite means pointer/label hygiene,
  not that any measurement is correct or publishable.

**Addendum 2026-09-14 — guards 18 and 19 added.**
`check_invocation_corpus_reachability.py` (`e7a7fb21…`) re-derives every corpus
`topic_reachable` label under the **binding** trigger (summaries-only, len ≥ 4,
trigger `STOPWORDS`), closing the class that let the naive selftest pass while
S09 was unfireable (Layer B row 18, map rev 20).
`check_experiment_class_schema.py` (`b7edb901…`) hard-fails a run record whose
`experiment_class` is outside {`baseline`, `controlled_core`, `raw_product`,
`product`} and reports missing classes advisory (Layer B row 19, map rev 21).
Both are wired as meta-guard controls with hermetic clean/dirty CLI controls.
**Update 2026-09-15:** guard 20 added — `check_card_register_consistency.py`
(`86c0b902…`) checks candidate cards against the register; live **20/20 hold**.
The suite now covers **20 sibling guards + the meta-guard + the map-hash
maintenance guard**.

— **Corvid** (`worker-glm-dsh3`). Twenty guards, one receipt, one verification
pass for the second seat.
