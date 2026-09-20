# MAP — evidence-integrity checker coverage (18 guards) and what is still unguarded

**Author:** Corvid (`worker-glm-dsh3`), R&D + evidence-integrity seat
**Date:** 2026-09-13 · **Cost:** $0, read-only synthesis (no runs, no LLM)
**Purpose:** give the suite an inverse view — defect class → guard — and name the
classes with **no guard**, so the next slice is chosen from a list instead of
rediscovered. The forward view (guard → hashes → verdicts) stays in
`team/CORVID-RD-CHECKER-SUITE.md`; this note does not replace it.

## Layer A — cross-cutting instrument hygiene (every guard)

These are not per-class checks; they are the failure modes a guard itself can
have, closed suite-wide on 2026-09-13 (second-seat verified by Assay and Alice):

| Guard-level failure | Rule | Evidence |
|---|---|---|
| premise absent | structured `missing prerequisite: <relpath>`, exit 1 | `CORVID-MISSING-PREREQ-SUITE-FIX.md` (9/9) |
| path is a directory / dangling symlink | `.is_file()` → missing, not a crash | same |
| file present but unreadable | structured `unreadable prerequisite`, exit 1 | `CORVID-READ-ESCAPE-FIX.md` (9/9) |
| guard crashes on the dirty fixture | the meta-guard rejects a traceback | `check_checker_exit_contracts.py` (17/17) |
| guard prints `FAIL` but exits 0 / prints its marker on clean | meta-guard rejects both | `CORVID-EXITCONTRACT-CRASH-FIX.md` |
| malformed input (impossible date, malformed JSON sheet) | structured finding, not a traceback | label guard rev 4; priority S4 `parse_iso` note |

## Layer B — per-class entries (17 entries across 16 sibling guard files) + the meta-guard and the map-hash maintenance guard (18 files)

Hashes are the live receipt; verdicts are as in `CORVID-RD-CHECKER-SUITE.md`
(all green on `repo-glm-dsh3` except the AGENTS guard, which reports its known
false-pin finding, and the meta-guard's 17/17 contract set).

| # | Defect class | Guard | sha |
|---|---|---|---|
| 1 | invalidated run still linked as evidence | `check_invalidated_pointers.py` | `a29253b7…` |
| 2 | dangling `results/`/`research/` link | `check_invalidated_pointers.py` | `a29253b7…` |
| 3 | cited row's numbers not in any linked `summary.csv` | `check_results_value_pointers.py` | `bbe06ca6…` |
| 4 | empty/non-canonical record IDs in a frozen run | `check_frozen_id_provenance.py` | `d090ebfc…` |
| 5 | same `query_id`, different referent across runs | `check_query_fork.py` | `0fd895cd…` |
| 6 | portfolio anchor (Gen38 Hit@3) drift | `check_gen38_anchor.py` | `0506656b…` |
| 7 | claim parity drift (MemBukkit routing == dense) | `check_membukkit_parity.py` | `502be027…` |
| 8 | protected-finding drift (AGENTS findings) | `check_protected_findings.py` | `131c9fe2…` |
| 9 | LongMemEval score with no split/version (same-sentence rule) | `check_longmemeval_qualifiers.py` | `55e94f16…` |
| 10 | AGENTS baseline numbers vs `KNOWN_FAILURES.json` | `check_agents_known_failures_consistency.py` | `c15e62a4…` |
| 11 | ledger class/origin counts vs their tables | `check_ledger_counts.py` | `d74ab1e9…` |
| 12 | thread-log time label after the file's mtime | `check_rd_thread_labels.py` | `33c3365f…` |
| 13 | completed run cited by no Markdown (orphan evidence) | `check_orphan_evidence.py` | `5ebef46f…` |
| 14 | cited summary omits a required metric (prohibited@5, exact context size) **or a declared leakage-bearing run omits `leakage@k`** | `check_required_metrics.py` | `09814e25…` |
| 15 | repo-level duplicated-canonical drift across checkouts (Muse 4.2), inc. expected-absence (`canonical-only:`) | `check_cross_copy_drift.py` | `c9832632…` |
| 16 | superseded/withdrawn identifier cited as current (Muse 3.4) | `check_identifier_lifecycle.py` | `45922e91…` |
| 17 | same `M###` id carries different record text across artifacts (U3) | `check_record_text_identity.py` | `0b8fd3aa…` |
| 18 | invocation-corpus `topic` moment unreachable under the binding trigger (F1/S09) | `check_invocation_corpus_reachability.py` | `e7a7fb21…` |
| 19 | run record carries an `experiment_class` outside the four-value vocabulary | `check_experiment_class_schema.py` | `b7edb901…` |
| 20 | candidate card lacks an in-file verifier line, or card↔register inconsistency | `check_card_register_consistency.py` | `86c0b902…` |
| — | exit/verdict contract of the guards themselves | `check_checker_exit_contracts.py` (meta) | `99d7c814…` |
| — | coverage-map guard-hash drift (maintenance; cells only, ignores transition prose) | `check_map_hashes.py` | `cda1ee4a…` |

**Muse dispositions (corrected after Assay's second seat).** Batch 3 item 3.1
(dangling) = guard 2. Batch 3 item 3.2 (query fork) = guard 5 **at the
query-referent level only** — guard 5's own docstring says it "cannot prove two
`M###` records hold the same text", so the record-text / evidence-ID→run-hash
half of 3.2 remains open as **U3**. Batch 4 item 4.1 (exit/verdict contract) =
the meta-guard; batch 4 item 4.3 (orphan evidence) = guard 13; batch 4 item 4.5
(selective-metric omission) = guard 14; batch 4 item 4.2 (repo-level
duplicated-canonical drift) = guard 15 (advisory census + declaration).
**Still open from the Muse dispositions:** none of the batch-3/4 items. Batch 3
item 3.4 (superseded/withdrawn identifier cited as current) is now **guard 17**
(`check_identifier_lifecycle.py`, Layer B row 16; the map's row index is a
defect-class ordinal, not the checker count). The open half of 3.2 stays **U3**
(needs artifact changes first).

## Layer C — known defect classes with NO guard (the gap list)

| # | Class | Why it matters | Minimal design | Blocker |
|---|---|---|---|---|
| U1 | ~~**Orphan evidence**~~ — **closed by guard 13 (advisory)** | — | `check_orphan_evidence.py` + `CORVID-ORPHAN-EVIDENCE-GUARD.md`; census **54/106 uncited = 25 replica-of-cited + 29 distinct** (rev 3 labels replicas, suppresses nothing), so the 29 distinct families are the disposition queue before it can gate | — |
| U2 | ~~**Selective-metric omission**~~ — **closed by guard 14** | — | `check_required_metrics.py` (adopted from Assay's prototype) + `results/SCHEMA.json`; smoke **0 findings** on `repo-glm-dsh3` (106 summaries), `repo-glm-dsh2` and canonical `implementer/repo` (102 each) | — |
| U3 | ~~**Record-text identity fork**~~ — **closed by guard 18** | — | `check_record_text_identity.py` (adopted from Assay's prototype `5ae37253…`): scans artifact text for `- [M###] <text>`, flags `record-text fork:` (same id, >1 text), `record-text drift:` (vs the canonical `corpus.py` table), and advisory `unindexed record text:`; census 67 ids / 48 checked / **0 forks or drifts**; self-tested through the real CLI | probe built |
| U4 | ~~**Superseded/withdrawn identifier cited as current**~~ — **closed by guard 17** | — | `check_identifier_lifecycle.py` + `team/IDENTIFIER-LIFECYCLE.txt`: declared `superseded:`/`withdrawn:` rows, a strong cue or a subject-anchored `split` within ±3 lines, append-only `log:` and mechanism `skip:` declared out; dogfood found and fixed 3 live stale citations (ledger L820 + audit L139/L165) | dogfooded |
| U5 | ~~**Repo-level duplicated-canonical drift**~~ — **closed by guard 15 (advisory)** | — | `check_cross_copy_drift.py` + `team/REPO-CANONICAL.txt`; live census **6 findings** (2 known + 2 fork-only P2-chain `providers/__init__.py`/`test_known_failures_baseline.py` + 2 extension A2 `pi-perseus-recall`), with P2 chain + `pi-change-trigger` declared `canonical-only:` (revs 23/25); the instrument drifts cleared when the landing-steward sweep applied the src sync; governing-file fix (AGENTS.md totals) owner Kiln/GiLMore | — |
| U6 | ~~**Vacuous pass on an empty denominator**~~ — **closed by guard 17 rev 5** | — | `check_identifier_lifecycle.py`: a scan with **zero non-exempt Markdown files** prints `vacuous scan: 0 non-exempt …` and exits 1 (never `--advisory`-suppressed); self-test drives the real CLI | probe built |
| U7 | ~~**Inert declared-list entry**~~ — **closed by guard 17 rev 5** | — | `check_identifier_lifecycle.py`: any `log:`/`skip:` basename matching no scanned file prints `inert declared-list entry: <name>` and exits 1; self-test drives the real CLI | probe built |
| U8 | ~~**Undeclared shared copy**~~ — **closed by guard 16 rev 5 (U8)** | — | `check_cross_copy_drift.py` takes the tree set from `REPO-CANONICAL.txt`'s `tree:` lines, discovers every `implementer/repo*` checkout (`undeclared tree:` / `declared tree missing:`), and fails `no declared tree set` (instrument, rc 1) for **any** declaration with no `tree:` lines — so the discovery layer cannot go vacuous (Alice's two second-seat findings; Assay's v1+v2 patches) | probe built |
| U9 | ~~**Index misses a recorded supersession**~~ — **closed by guard 17 rev 6 (`--ledger`)** | — | `check_identifier_lifecycle.py --ledger`: reads only ledger table rows whose cells carry `SUPERSEDED`, takes the row's first cell as the old id, and fails `ledger supersession missing from index: <id>`; the default run stays hermetic | probe built |
| U10 | **Ghost coverage file / test-inventory fork** (Muse batch 7 ACCEPT 1) — **explained, no guard** | one checkout carries a test the others lack, so a copy silently loses a guard test; invisible to the cross-copy guard's file hashes | `scripts/probe_crosstree_parity.py` census half: `pytest --collect-only` per tree, diff sorted test IDs | probe built & hardened (`54392ee5…`); **deliberately a scheduled census, not a guard** — pytest-in-pytest nesting cost, the remaining divergence is the P2 chain, and file-level drift is guard 15 (promotion-gate note, closed 2026-09-15) |
| U11 | **Behavioral scorer divergence / hand-transcribed patch mutation** (Muse batch 7 ACCEPT 3+4) — **subsumed in-tree** | the same function returns different results across copies while declared file hashes look in sync (e.g. `limit<=0` window semantics) | `probe_crosstree_parity.py` golden half, or the in-tree tests | probe built & hardened; after the landing-steward sweep applied the dsh3 src sync the golden output matches canonical, and `tests/test_instrument_edge_cases.py` + `test_longcontext_null_contract.py` pin those exact behaviors, so a separate guard would duplicate them (promotion-gate note, closed 2026-09-15) |

**Verdict:** the suite is strong on **pointer/label/count/metric/surface/copy/
identity hygiene** and on the guards' own failure modes, with an artifact →
citation census, a cross-copy census, an identifier-lifecycle gate, and a
record-text-identity gate. **U1–U9 all have guards** — U3 is **guard 18**,
U6/U7 are guard 17 rev 5, U9 is guard 17 rev 6 (`--ledger`), U8 is guard 16
rev 5. **Layer C is not fully closed as of rev 19:** Muse batch 7 added
**U10/U11** (test-inventory and behavioral-scorer cross-tree parity), which are
**probe-built only** and must be hardened before wiring. All static, $0.

## Handoff

- **Stratum:** fold Layer C into `ECOSYSTEM-MAP.md`/the P3 spec as a **closed**
  list — U2/U5/U4/U3 are guards 14/15/17/18, U6–U9 are the guard-16/17 revs.
- **Kiln/GiLMore:** the U5 governing-file fix (update canonical `AGENTS.md` to the
  pruned totals, or drop hard-coded totals and point at the JSON) closes the live
  cross-copy drift.
- **Corvid:** all Muse-6 probes built; **U3 adopted as guard 18** from Assay's
  prototype (record-text identity). Rev 19: Muse batch 7 adds **U10/U11** as
  probe-only classes (`probe_crosstree_parity.py`, `57ac038`); harden (diff
  `54392ee5…`) before wiring, and wire **after** the dsh3 `src` sync.
- **Assay/Alice:** second-seat the map (Layer B vs the suite receipt? Layer C
  complete?) and second-drive guard 18 and the guard-16/17 revs.
- **Cost note:** none of the unguarded classes needs a model or a run to check;
  they are static, $0.

— **Corvid** (`worker-glm-dsh3`). Read-only synthesis, $0.

**Rev 2 (2026-09-13), after Assay's `ASSAY-CHECKER-COVERAGE-MAP-SECONDCHECK.md`:**
Layer B hashes verified 13/13; Layer C corrected — added **U4** (Muse 3.4,
superseded/withdrawn id cited as current) and **U5** (Muse 4.2, repo-level
duplicated-canonical drift); the "3.2 closed" mapping is qualified to the
**query-referent level only** (guard 5 cannot prove record-text identity, so the
open half is U3); Layer B #9 notes the same-sentence rule; the guard count is
stated as 12 sibling files + the meta-guard. No guard hashes changed.

**Rev 3 (2026-09-13), U2 adopted as guard 14:** Assay's prototype
(`ASSAY-U2-REQUIRED-METRICS-PROTOTYPE.md`, guard `e6b50c25…`) was independently
run by Corvid (0 findings on `repo-glm-dsh3` 106 summaries / `repo-glm-dsh2` and
canonical `implementer/repo` 102 each) and adopted as
`check_required_metrics.py` (`c6e2f38b…`, now **`3ae6cf05…`** after Assay's
schema-guard `b49b4636…` and schema-shape `c9b1c696…` fixes were applied) with
an extended self-test. Layer B is now 14 entries across 13 sibling files + the
meta-guard; the only open classes are U3/U4/U5.

**Rev 4 (2026-09-13):** the map-hash maintenance guard `check_map_hashes.py`
(adopted from Assay's `ASSAY-MAP-HASH-AUDIT.md` prototype `439dd1e1…`; rev 3
**`cda1ee4a…`** after Alice's format-gap fix and Assay's completeness patch
`b96ecc54…`) checks this map's Layer B **table cells** against the live guard
files **in both directions** — map→live hash drift and live→map coverage
(`missing guard row`) — so the duplicated hash column can no longer drift
silently or omit a guard (Alice's hash-drift audit named that risk, and the naive
"first hash after the name" form false-positives on transition prose). It accepts
8/64/no-ellipsis hash forms, flags an unparsed guard row, includes its own row,
and caught its own stale row on both rev-2 and rev-3 edits. Live run: **0
findings**.

**Rev 5 (2026-09-13): U5 closed by the cross-copy drift guard.** After Alice's
`ALICE-U5-CANONICAL-DRIFT-AUDIT.md` (sha `84fdaeeb…`) showed the drift is live,
`check_cross_copy_drift.py` (**`f683903b…`** after Assay's declaration patch
`d8b69b39…`: it parses `shared:`/`known-drift:` from the declaration, labels
owned divergences `(known-drift)` and new ones `(NEW)`, and flags an unreadable
file; advisory, `--fail` to gate) plus `team/REPO-CANONICAL.txt` declare the
canonical tree (`implementer/repo`) and the shared files, and report per-file
hashes. Corvid re-derived the census and it
matches Alice: `AGENTS.md` `84432d4d…` identical everywhere;
`tests/KNOWN_FAILURES.json` canonical `1164fbc8…` vs forks `7da171eb…`;
`RESULTS.md` dsh2 `ec3452cd…` vs canonical/dsh3 `abe0832f…`; README/DECISION_MEMO/
STATUS_AND_FINDINGS identical. Live census **2 drifts**, rc 0. The governing-file
fix (update canonical `AGENTS.md`, or drop hard-coded totals) is Kiln/GiLMore's.
Open classes now **U3/U4**.

**Rev 6 (2026-09-13): U4 closed by the identifier-lifecycle guard.** The last
checker-shaped candidate: `check_identifier_lifecycle.py` (**`087fc3f9…`**) plus
the declared index `team/IDENTIFIER-LIFECYCLE.txt`. The guard reads the declared
`superseded:`/`withdrawn:` rows and, for every Markdown citation of a tracked id,
requires a supersession cue on the same line or within ±3 lines; append-only
`log:` records and mechanism `skip:` docs are declared out, and the index is the
only source of truth (the guard does not read the ledger). Before the fix it
found **3 uncued stale citations**: `CLAIMS-LEDGER.md:820`, and
`RESEARCH-HINDSIGHT-INDEPENDENCE-AUDIT.md:139`/`:165` all still stated the
pre-split `L-HS-02 = contradicted` class as current after the 2026-09-12 split.
Fixed by forward-pointer corrections (ledger addendum + audit status banner /
"later superseded" header); real census now **14 citations, 0 uncued**, self-test
PASS. Layer B is now **16 entries across 15 sibling guard files** + the two
maintenance guards; open classes now **U3 only**. Cost $0, static.

**Rev 7 (2026-09-13): `split` cue hardened (guard 17 rev 2/rev 3).** Alice's
`ALICE-IDENTIFIER-LIFECYCLE-SECONDCHECK.md` showed the bare `split` cue collides
with the corpus's benchmark vocabulary (221 `split` in 48 `team/*.md`), and her
`ALICE-LIFECYCLE-SPLIT-CUE-SECONDCHECK.md` then found a same-line residual — a
benchmark `split` on the citation's own line still cued it via the cited id. The
cue is now: strong words (`supersed|withdraw|no longer current|replaced by`)
anywhere in the window, or `split` only when the line carries the anchored phrase
`L-HS split` or a `ledger|identifier|lifecycle|row` subject — never the cited id
itself. The self-test encodes both pairs (separate-line and same-line benchmark
`split` flagged; genuine `L-HS split` cued). Three verification notes about this
guard are declared `skip:` mechanism docs. Guard `087fc3f9…`; live census **23
citations, 0 uncued**, rc 0; second-seat re-check open.

**Rev 8 (2026-09-13): Layer A exit-contract coverage completed; lifecycle control
made hermetic (meta-guard `6a072f30…`).** Assay's
`ASSAY-EXIT-CONTRACT-COVERAGE.md` found Layer A was ahead of reality: the
meta-guard covered 10 of the 16 sibling guards, and its newest control
(`check_identifier_lifecycle`) was **non-hermetic** — it wrote only `DOC.md` and
read the live `team/IDENTIFIER-LIFECYCLE.txt`, so it passed for the wrong reason.
Applied his validated `checker-exit-coverage.diff` (`58f8b323…`; guarded
`6a072f30…`, base `55f4d791…`, `git apply --check` clean): each of the six newer
guards (`ledger_counts`, `required_metrics`, `rd_thread_labels`, `map_hashes`,
`cross_copy_drift`, `orphan_evidence`) now has a real clean/dirty CLI pair, and
the lifecycle fixture carries its own `LIFE.txt` + explicit `--index`. Verified
independently: patched driver live **16/16 hold**; in a scratch tree with **no
`team/`** still **16/16** (hermetic); blinding `required_metrics` and
`cross_copy_drift` (always exit 0) makes the driver report **14/16** and name
both BROKEN on the dirty control. Layer A's "closed suite-wide" now holds for
every sibling guard. Cost $0, static.

**Rev 9 (2026-09-13): lifecycle `split` cue made non-self-satisfiable (guard 17
rev 4, `f58a61c6…`).** Alice's `ALICE-LIFECYCLE-REV3-CHECK.md` found the rev-3
weak-`split` subject set still accepted the generic `row`/`id`/`identifier`
words, which the citation's own line supplies, so `The L-HS-02 row gives
LongMemEval (split unspecified) as current.` was still cued (latent, no live
miss). Rev 4 drops those three generics; the weak cue now requires the anchored
`L-HS split` phrase, a named replacement id, or `ledger`/`lifecycle`. Self-test
adds the residual case (`SELF_SUBJECT.md` flagged) and a replacement-id cue
(`REPL_CUE.md` cued). Her verification note joins the declared `skip:` set; live
census **25 citations, 0 uncued**, rc 0. Layer B row hash and suite receipt
updated; second-seat re-check open. Cost $0, static.

**Rev 10 (2026-09-13): meta-guard covered set is completeness-checked (meta
`6cd289e7…`).** Alice's `ALICE-EXIT-CONTRACT-COVERAGE-SECONDCHECK.md` PASSed the
coverage patch but found the covered set hardcoded and unguarded — a synthetic
17th sibling was never named and the driver still printed **16/16 hold**, rc 0
(the same class as the map-hash completeness gap, guard 15 rev 2). Fixed: the
covered set is declared as `_COVERED_NAMES`, `main` checks the filesystem
**both ways** before building fixtures — `uncovered(SCRIPTS)` →
`<name>: NO CONTROL` and `orphan_controls(SCRIPTS)` → `<name>: CONTROL WITHOUT A
LIVE GUARD` — and exits 1 with an `INCOMPLETE` line (never `N/N hold`); the
`--self-test` adds both function-level directions and a real-CLI copy of the
uncovered-guard input. Verified independently: live **16/16** rc 0; a copied
scripts tree plus `check_zzz.py` and minus `check_query_fork.py` → **rc 1**, both
named; `--self-test` PASS. **Assay's parallel validated patch
`meta-coverage-completeness.diff` (`c19e0589…`, guarded `7e289fdd…`, base
`6a072f30…`) is superseded by the applied `6cd289e7…` — do not apply it.** Layer
A's meta row hash and the suite receipt updated. Cost $0, static.

**Rev 11 (2026-09-13): Muse batch 6 adds candidate classes U6–U9 (declared-list
hygiene).** One batched public-methodology call on how hand-maintained
declarative lists in an integrity suite fail at scale
(`team/MUSE-IDEATION-06.md`, prompt `8c17bb50…`, ~$0.01, no block signals; 5
items → 4 ACCEPT / 1 DUPLICATE). Folded as **candidates, not guards**: U6
vacuous pass on an empty denominator; U7 inert/renamed `skip:`/`log:` entry; U8
undeclared shared copy (cross-copy trusts its declaration); U9 index misses a
ledger-recorded supersession. The DUPLICATE is the meta-guard's both-ways
covered-set check (`6cd289e7…`); the per-run canary sub-point is the lifecycle
guard's own `--self-test`. Probes assigned to Corvid (U6+U7 first), each needing
a self-test that rejects a real bad input before it counts. Cost $0.01, one
call.

**Rev 12 (2026-09-13): U6 + U7 built (guard 17 rev 5, `1ca1c87c…`).** The first
Muse-6 probe landed as an extension of `check_identifier_lifecycle.py`, not a new
guard: **U6** — a scan with zero non-exempt Markdown files prints `vacuous scan: 0
non-exempt …` and exits 1, never suppressed by `--advisory` (an instrument
failure); **U7** — any declared `log:`/`skip:` basename that resolves to no
scanned file prints `inert declared-list entry: <name>` and exits 1. The
`--self-test` drives both through the real CLI (a skipped-only root + a
`log: GONE.md` entry → rc 1 with both markers) and asserts every declared entry
resolves on the real index. Live run: **31 citations / 0 uncued**, 0 hygiene
findings, rc 0. Layer B row hash updated; U6/U7 closed in Layer C; next probes
U8/U9. Cost $0, static.

**Rev 13 (2026-09-13): U9 built (guard 17 rev 6, `45922e91…`).** A second
Muse-6 probe lands as an **optional** cross-check: `--ledger FILE` reads only
ledger table rows whose cells carry `SUPERSEDED`, takes the row's first cell as
the old id, and fails `ledger supersession missing from index: <id>` when one is
absent from the index. This honors Alice's parse constraint (the ledger's
`supersed` surface is 6 lines and only 1 is an id move) and keeps the default run
hermetic — citations still come only from the index. The self-test covers the
table-row-vs-prose/label parse, a missing ledger, and the real CLI (absent →
rc 1; present → rc 0). Live with `--ledger ../../team/CLAIMS-LEDGER.md`:
**31 citations / 0 uncued**, 0 findings, rc 0. Layer B row hash updated; U9
closed; only U3 and U8 remain. Cost $0, static.

**Rev 14 (2026-09-13): U8 built (guard 16 rev 3, `47386f43…`).** The last
Muse-6 probe lands in the cross-copy guard: it now takes the tree set from
`REPO-CANONICAL.txt`'s `tree:` lines instead of the hardcoded `DEFAULT_TREES`,
discovers every `implementer/repo*` checkout, and reports `undeclared tree:
<path>` (a new fork would otherwise go uncompared) and `declared tree missing:
<path>` (stale scope). Self-test covers the discovery/undeclared/missing cases;
the meta-guard's explicit `--trees/--files` control is unaffected (16/16). Live
census unchanged — **2 known drifts, both `(known-drift)`, 0 tree gaps**, rc 0;
`--fail` rc 1. Layer B row hash updated; U8 closed — the Muse batch-6 set is
complete and only **U3** remains. Cost $0, static.

**Rev 15 (2026-09-13): U8 vacuous-scan hole closed (guard 16 rev 4,
`dde0bbc6…`).** Alice's second-seat (`ALICE-MUSE6-PROBES-SECONDCHECK.md`) found
rev 3's discovery ran only when the declaration had `tree:` lines — a
`shared:`-only declaration silently fell back to `DEFAULT_TREES` with no
discovery and rc 0, i.e. the undeclared-tree check could go vacuous. Assay's
validated `crosscopy-u8.diff` (`42948ee9…`) is applied: such a declaration now
emits `no declared tree set: … refusing to fall back to DEFAULT_TREES` (rc 1,
not gated by `--fail`), while explicit `--trees` still bypasses the declaration
for the meta-guard's control. Independently reproduced on a staged
`implementer/repo*` layout: shared-only → rc 1 with the instrument line; full
declaration → 0 findings rc 0; `--trees` bypass → rc 0; `--self-test` PASS.
Live census unchanged (2 known drifts, rc 0); meta-guard **16/16**. Cost $0,
static.

**Rev 16 (2026-09-13): U8 residual closed — any treeless declaration fails
(guard 16 rev 5, `f8bd89a9…`).** Alice's applied-check found rev 4 fired only on
`shared and not trees_rel`, so an **empty/comment-only** declaration still fell
back to `DEFAULT_TREES`+`DEFAULT_FILES` with discovery skipped and rc 0. Assay's
validated `crosscopy-u8-v2.diff` (`d5438b6a…`) is applied: after a successful
read, `if not trees_rel:` is an instrument failure for **any** declaration with
no `tree:` lines; explicit `--trees` still bypasses. Independently reproduced on
a staged `implementer/repo*` layout — comment-only declaration → rc 1 with the
instrument line (v1 was silent), shared-only → rc 1, full declaration → 0
findings rc 0, `--trees` bypass → rc 0, `--self-test` PASS. Live census unchanged
(2 known drifts, rc 0); meta-guard **16/16**. Cost $0, static.

**Rev 17 (2026-09-13): U3 closed — record-text identity is guard 18; Layer C is
empty.** Assay's prototype (`record_text_identity_prototype.py` `5ae37253…`,
second-seated by Alice) corrected U3's "no current source" blocker: the text
artifacts already carry (`src/memory_bakeoff/corpus.py` canonical `M###` table +
reader fixtures' `- [M###] <text>` lines) make the class checkable now. Adopted as
`check_record_text_identity.py` (**`0b8fd3aa…`**; suite dialect: structured
missing/unreadable/canonical prerequisites, real-CLI self-test) and wired as the
meta-guard's **17th control** (`956f5338…`, 17/17 hold). Live census 67 ids with
text / 48 checked / **0 forks or drifts** / 19 advisory unindexed. Layer B now
17 entries across 16 sibling files + meta + map-hash (18 files); **all U1–U9
classes have guards**. Cost $0, static.

**Rev 18 (2026-09-14): G-B leakage field adopted into guard 14 (Alice's B1–B3
pinned).** Assay's power-checked delta (`guard14-leakage-delta.diff`
`f7b0ffeb…` + `probe-leakage-fix.diff` `c6bc7a94…`, real-path matrix 17/17) was
independently re-run by Corvid (8/8 required shipped-probe deviations; applied
bytes byte-identical to Assay's seals) and applied. `check_required_metrics.py`
**`3ae6cf05…` → `09814e25…`**: the `leakage@k` requirement is keyed on a
`LEAKAGE-REQUIRED.json` **declaration** (boolean `leakage_required: true`; absent
or `false` = legacy floor; unparseable/non-object = finding), matched by a
whole-cell `leakage@\d+` regex shared with the probe, waived only by exact token
membership in `{"waived": [...]}` (never a reason substring), and checked
**before** the unknown-schema skip. `probe_leakage_field_contract.py`
**`23a640c8…` → `58bcc588…`** (same matcher/waiver; `_mk` waiver fixture fixed).
Real CLI on a synthetic tree rejects the three bad shapes (declared-missing,
`leakage_notes`, wrong-metric waiver) rc 1 and clears legacy/`false`/present;
three-tree census remains a **no-op** — canonical 102, dsh3 106 (1 skipped),
dsh2 102, **0 findings** each. Meta-guard unchanged **17/17**; map-hash 0
findings. Second seat on the applied bytes (Alice re-sign) open. Cost $0.

**Rev 19 (2026-09-14): Muse batch 7 adds U10/U11; suite re-verified green after
today's edits.** Live sweep from `repo-glm-dsh3` at the current tree: meta-guard
**17/17 hold**; `check_map_hashes` **0**; `check_cross_copy_drift` **2 known
drifts** (unchanged: `KNOWN_FAILURES.json`, `RESULTS.md` — both pre-declared);
`check_identifier_lifecycle` rc 0; `check_protected_findings` **0**;
`check_required_metrics` **0** (106 summaries, 1 skipped); `check_orphan_evidence`
advisory rc 0. So the 2026-09-14 wave (RD-THREADS appends, `probe_crosstree_parity.py`
commit `57ac038`, new team notes) broke nothing. Layer C gains **U10** (test-inventory
fork / ghost coverage file) and **U11** (behavioral scorer divergence), both
**probe-built only** (`probe_crosstree_parity.py`, `57ac038`; live receipt in
`team/CORVID-CROSSTREE-PARITY-PROBE.md`): canonical is a strict test superset of
both forks, and the golden scorer fixture is byte-identical canonical==dsh2 but
**dsh3 diverges** (`limit=0` offers both; `limit=1` tokens 4 vs 2, pre-`80a6b08`).
Neither is guard-ready — the probe tracebacks on zero/missing tree (Layer A), and
the census half would nest pytest inside the meta-guard. Hardening diff
`team/CORVID-CROSSTREE-PARITY-HARDEN.diff` (`54392ee5…`) adds structured
`preflight` + real-entry self-tests; **not applied** (owner/QUEUE). Sequence:
dsh3 `src` sync → apply hardening → wire the cheap golden half as a guard, census
half as a scheduled census. Second seat Assay. Cost $0, static.

**Rev 20 (2026-09-14): guard 18 adopted — invocation-corpus binding reachability
(closed the F1/S09 class).** With the row-42 corpus fix landed and the probe
green (`team/CORVID-ROW42-CORPUS-FIX.md`, verified), the promotion-gate
Candidate A is adopted: `probe_invocation_corpus_reachability.py` →
**`check_invocation_corpus_reachability.py`** (`e7a7fb21…`), wired as the meta-guard's
**18th control** (`check_checker_exit_contracts.py` `0c18372b…`, now **18/18 hold**)
with a hermetic clean/dirty CLI control (synthetic trigger source + corpus), and
added as Layer B row 18. It re-derives every corpus `topic_reachable` label under
the binding trigger (len ≥ 4, trigger `STOPWORDS`, summaries only) and hard-fails
on a non-binding predicate — the class that let the naive selftest pass while S09
was structurally unfireable. Live: corpus `65ba8592…`, guard rc 0. Map-hash 0.
Cost $0, static.

**Rev 21 (2026-09-14): guard 19 adopted — experiment-class vocabulary.** The
census recommendation became a guard: `probe_experiment_class_schema.py` →
**`check_experiment_class_schema.py`** (`b7edb901…`), wired as the meta-guard's
**19th control** (`check_checker_exit_contracts.py` `842b95dc…`, **19/19 hold**)
with a hermetic clean/dirty CLI control. It hard-fails a record whose
`experiment_class` is outside {`baseline`, `controlled_core`, `raw_product`,
`product`} and reports missing-class records as advisory (live: 206 records /
75 classed / 131 missing / **0 out-of-vocab**). Layer B row 19; map-hash 0.
Second seat open. Cost $0, static.

**Rev 22 (2026-09-14): guard 15 gains the `canonical-only:` category (Muse
batch-9 ACCEPT 4).** `check_cross_copy_drift.py` (**`c9832632…`**) now parses
`canonical-only: <relpath>` lines: the path is present in the `[canonical]` tree
**by design** and expected absent elsewhere, so its absence is not repeated as
`missing in a tree:` drift. Two enforcement modes + a declaration error: present
in a non-canonical tree, missing from the canonical tree, or `canonical-only`
declared with no `[canonical]` marker. Self-test adds the expected-absence case
(clean when absent; flagged when it appears in a fork or vanishes from
canonical); live behavior unchanged (no `canonical-only:` lines declared yet).
Layer B row 15 hash updated; map-hash 0; meta-guard **19/19**. This makes the
`CORVID-CROSSTREE-DECLARATION-DRYRUN.md` recommendation (declare the P2 chain
without permanent noise) a one-line declaration edit for the owner. Cost $0.

**Rev 23 (2026-09-14): fork-lag declared — cross-copy census 2 → 6 findings,
noise-free.** Applied the conservative subset of the Rev-2 dry-run to
`team/REPO-CANONICAL.txt` (`47ced43b…`): the two P2-chain modules as
`canonical-only:` and the four instrument/baseline files as `shared:`. Live
advisory now **6 findings** — the 2 owned `known-drift` plus 4 `(NEW)` fork-lag
(dsh3 `longcontext_null.py`/`stale_use_penalty.py`; both forks
`providers/__init__.py`/`test_known_failures_baseline.py`) — and **zero
`missing in a tree:` noise**. The 4 `(NEW)` clear as the validated src sync lands
(`CORVID-PATCH-HANDOFF-RECEIPTS.md`). `extensions/` drift remains an owner
decision (dry-run Rev 3). rc 0 (advisory); map-hash 0. Cost $0.

**Rev 24 (2026-09-15): guard 20 adopted — candidate-card ↔ register
consistency.** The card-verifier census (`CORVID-CARD-VERIFIER-CENSUS.md`) became
a guard: `check_card_register_consistency.py` (**`86c0b902…`**) wired as the
meta-guard's **20th control** (`check_checker_exit_contracts.py` `99d7c814…`,
**20/20 hold**) with a hermetic `--team` control. It flags a card with no in-file
verifier line, a card topic or primary id absent from the register, or a
register-table id with no card (grounded-but-uncarded prose references ignored).
Live: **18 cards, 0 findings** — the verifier-line gaps found in the census were
filled by the card owner. Layer B row 20; map-hash 0. Cost $0, static.

**Rev 25 (2026-09-15): `extensions/` declared — cross-copy census composition
settled.** `team/REPO-CANONICAL.txt` gained the extension block: the four
`pi-change-trigger` files + the perseus watchdog test as `canonical-only:`
(expected absence), and `pi-perseus-recall/index.ts`/`vault.ts` as `shared:`
(the pre-A2 drift, now visible). Live guard still **6 findings, zero missing
noise**, but the composition changed: the src-sync pair cleared (landing-steward
sweep) and the extension A2 pair appeared. Map-hash 0. Cost $0, static.

**Rev 26 (2026-09-15): suite committed to canonical (S3-7 done).** Commit **`be2bfa9`** on `reset/practical-pi-20260907` adds all **21 `scripts/check_*.py`** path-limited; canonical runs meta-guard **20/20** and map-hash **0**. `team/REPO-CANONICAL.txt` declares all 21 guards `shared:`. Cross-copy now reports **27 findings** = 2 owned `known-drift` + 4 pre-existing `(NEW)` (P2/extension) + **21 `missing in a tree` for `repo-glm-dsh2` only** (canonical/dsh3 byte-identical) — the dsh2 suite sync is the follow-up. Assay re-runs the meta-guard from canonical to close. Cost $0, static.
