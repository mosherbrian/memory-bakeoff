# Identifier-lifecycle guard — coverage-map U4 / Muse batch 3 item 3.4

**Author:** Corvid (`worker-glm-dsh3`), R&D + evidence-integrity
**Date:** 2026-09-13 · **Cost:** $0, static (no run, no LLM)
**Artifacts:** `implementer/repo-glm-dsh3/scripts/check_identifier_lifecycle.py`
(sha `45922e91…`, rev 6) + `team/IDENTIFIER-LIFECYCLE.txt` (declared index,
sha `33b3e4d0…`) + this note.
**Closes:** `CORVID-CHECKER-COVERAGE-MAP.md` Layer C gap **U4** / Muse batch 3
item 3.4 ("a doc cites a superseded or withdrawn identifier as if current");
the map now names **U3** as the only open class.

## What it does

The suite checked ID *shape* (guard 4), query *referents* (guard 5) and
invalidated *run directories* (guard 1). Nothing checked whether a document
cites an identifier the record has since moved. A cold reader can therefore act
on `L-HS-02` after the ledger split it into `L-HS-02a` / `L-HS-02b`.

The lifecycle is **declared, never inferred**. `team/IDENTIFIER-LIFECYCLE.txt`
holds one row per move with its authoritative source:

```
superseded: L-HS-02 -> L-HS-02a, L-HS-02b
withdrawn:  <id>
log:        <basename>   # append-only record; citations are historical
skip:       <basename>   # guard infrastructure / mechanism docs
```

For every Markdown citation of a tracked id, the guard requires a supersession
cue (`superseded` / `withdrawn` / `split` / `replaced by` / `no longer current`)
on the same line or within **3 lines**. The index is the guard's only source of
truth — it does not read the ledger. Missing, unreadable or malformed index is a
structured prerequisite (exit 1), per the suite dialect. It exits 1 on an uncued
citation (a closure gate); `--advisory` reports without failing.

`log:` is deliberately a declared category, not a heuristic: append-only
operation records (`BOARD.md`, `RD-THREADS.md`, `SCOREBOARD-*.md`,
`COLLECTION-LOG.md`) are the record *of* the transition and must be able to name
the old id. The cue is required only in documents that make a current claim.
There is **no whole-file banner rule** — the audit's own thread title says
"retracted-figure", which would have cued every citation in the file and hidden
the real stale lines.

## Dogfood result (the positive control is real, not synthetic)

The first real run found **3 uncued stale citations** left by the 2026-09-12
`L-HS-02` split:

| file:line | text at the time |
|---|---|
| `CLAIMS-LEDGER.md:820` | "L-HS-02 stays `contradicted` as a LongMemEval-S claim" (later addendum, no forward pointer) |
| `RESEARCH-HINDSIGHT-INDEPENDENCE-AUDIT.md:139` | "L-HS-02 94.6% = `contradicted`" |
| `RESEARCH-HINDSIGHT-INDEPENDENCE-AUDIT.md:165` | "Updated class for L-HS-02 (94.6%): `vendor-only` at best, and contradicted…" |

Fixed with forward-pointer corrections only — no number or class changed:
the ledger addendum now reads "(later **superseded** — see \"L-HS split\")";
the audit gained a **Status (2026-09-13)** note and a "later superseded" header.
Real census after the fix: **repo root 0 citations; `team/` 14 citations, 0
uncued** (the 14 are the ledger's own defining rows, the four declared logs, and
the corrected audit). `--self-test`: PASS — an uncued superseded citation and an
uncued withdrawn citation are flagged through the real scan path; a cued one, a
declared-log one and the suffixed replacements (`L-HS-02a` / `L-HS-02b`) are
clean; missing / malformed / unreadable index reported. The meta-guard now runs
this guard's CLI on clean + dirty fixtures: **16/16 exit contracts hold**
(`check_checker_exit_contracts.py` `2fbb3998…` → `6a072f30…`).

## Limits

- **A citation must be a current claim to be a defect.** Any doc that keeps its
  own supersession cue is clean; the guard surfaces an uncued one and leaves the
  disposition to the owner.
- **The index is only as good as its rows.** A lifecycle move that nobody
  declares here is not checked; the index names its source so a second seat can
  audit each row.
- **One live row today** (`L-HS-02`). The value is prospective: the next
  supersession now has a place to be declared and a gate that fires if the old id
  is left live.
- **U3 remains open** (same `M###` id, different record text) and needs
  artifact-side content hashes, not a static doc check.

## Verify (read-only)

```bash
cd implementer/repo-glm-dsh3
python3 scripts/check_identifier_lifecycle.py --self-test
python3 scripts/check_identifier_lifecycle.py          # 0 uncued (count point-in-time), rc 0
python3 scripts/check_map_hashes.py                    # map row + hash current
python3 scripts/check_checker_exit_contracts.py        # 16/16 hold
python3 scripts/check_ledger_counts.py /home/bmosher/memory-bake-off/team/CLAIMS-LEDGER.md
```

## Rev 2 (2026-09-13) — closes Alice's `split`-cue power finding

Alice's `ALICE-IDENTIFIER-LIFECYCLE-SECONDCHECK.md` PASSed the mechanics but
showed the cue regex's bare `split` collides with the corpus's dominant
benchmark vocabulary (221 `split` occurrences in 48 `team/*.md`): a controlled
pair with `LongMemEval (split unspecified)` two lines above a stale citation
flipped it from detected to **silently cued**. Fixed by splitting the cue:

- `STRONG_CUE_RE` = `supersed|withdraw|no longer current|replaced by` — cues
  anywhere in the window, as before;
- `WEAK_CUE_RE` = `\bsplit` — cues **only** with the anchored `L-HS split`
  phrase or a `ledger|identifier|lifecycle|row|id` subject on the same line (the
  cited id and bare `L-HS` are stripped first — **Rev 3 below supersedes the
  wider Rev-2 subject set**), so `LongMemEval (split unspecified)` no longer
  masks a stale citation while "see the L-HS split" still cues. A low latent
  residual (Alice, 2026-09-13 17:10) is that `row|id|identifier` are
  self-satisfiable; no live miss.

The self-test now encodes Alice's controlled pair (`NEAR_SPLIT.md` flagged,
`GENUINE_SPLIT.md` cued); `--self-test` PASS and the live census is unchanged and
green. Also removed the inert `skip: IDENTIFIER-LIFECYCLE.txt` (only `*.md` is
scanned) and documented in the index header that `log:`/`skip:` match a basename
in any scanned root (Alice's low nit). Guard `1e267a20…` → **`087fc3f9…`**;
coverage map, suite receipt and this note updated. Second-seat re-check open.

## Rev 3 (2026-09-13) — closes Alice's same-line residual

Alice's follow-up (`ALICE-LIFECYCLE-SPLIT-CUE-SECONDCHECK.md`) found the rev-2
rule accepted the cited id (and its `L-HS` prefix) as the `split` subject, so a
benchmark term on the citation's own line still cued it — e.g. ``The class for
L-HS-02 (LongMemEval split unspecified) is contradicted.`` Rev 3 removes the id
as a subject:

- `split` cues on the anchored phrase `L-HS\s+split`, or when the line (with the
  cited id and its `L-HS` prefix blanked out) carries `ledger|identifier|
  lifecycle|row|id`;
- the self-test adds `SAME_LINE.md` (flagged) alongside `NEAR_SPLIT.md` (flagged)
  and `GENUINE_SPLIT.md` (cued).

Tightening surfaced four previously-cued citations, all in second-check /
power-fix notes about this guard (`ALICE-IDENTIFIER-LIFECYCLE-SECONDCHECK.md`,
`ALICE-LIFECYCLE-SPLIT-CUE-SECONDCHECK.md`, `ASSAY-LIFECYCLE-SPLIT-CUE.md`);
they are mechanism documents and are now declared `skip:` (like this note).
Live census after rev 3: **23 citations, 0 uncued**, rc 0. Assay's parallel
unapplied `split-cue.diff` (base `1e267a20…`, guarded `037b5d43…`) is
**superseded** — do not apply it on top of the live file.

## Rev 4 (2026-09-13) — the meta-guard control is now hermetic

Assay's `ASSAY-EXIT-CONTRACT-COVERAGE.md` found this guard's exit-contract
control was non-hermetic: the fixture wrote only `DOC.md` and the control relied
on the live `team/IDENTIFIER-LIFECYCLE.txt`, so it passed in place but died with
`missing prerequisite` in a scratch tree. Applied his validated
`checker-exit-coverage.diff` (`58f8b323…`; meta-guard `6a072f30…`, base
`55f4d791…`): the control now writes its own `LIFE.txt` and passes `--index`
explicitly. Verified independently: the patched driver is live **16/16**, is
still **16/16 in a scratch tree with no `team/`**, and reports **14/16** with
`check_required_metrics`/`check_cross_copy_drift` named BROKEN when those two
are blinded to always exit 0. Coverage is now all 16 sibling guards.

## Rev 5 (2026-09-13) — closes Alice's rev-3 self-satisfiable-subject residual

Alice's `ALICE-LIFECYCLE-REV3-CHECK.md` found the weak-`split` subject set still
accepted the generic `row`/`id`/`identifier` words, which the citation's own
context supplies: `The L-HS-02 row gives LongMemEval (split unspecified) as
current.` was still `[cued]` (latent; no live miss). Rev 4 drops those three
generics — the accepted weak subjects are now the anchored `L-HS split` phrase,
a **named replacement id** (`L-HS-02a`/`L-HS-02b`) on the cue line, or `ledger`/
`lifecycle`. The self-test adds `SELF_SUBJECT.md` (flagged) and `REPL_CUE.md`
(cued). Alice's `ALICE-LIFECYCLE-REV3-CHECK.md` is a mechanism note and joins the
declared `skip:` set. Live census **25 citations, 0 uncued**, rc 0; guard
`087fc3f9…` → **`f58a61c6…`**; index `5fc4897d…`; coverage map rev 9, suite
receipt and this note updated.

## Rev 6 (2026-09-13) — one mechanism-note skip added

Assay's second-seat of rev 4 (`ASSAY-LIFECYCLE-REV4-SECONDCHECK.md`) is a
mechanism note about this guard, so it joins the declared `skip:` set; the
refreshed P2 gate card (`CORVID-P2-EVIDENCE-GATE-CARD.md`) joins it too (it
discusses the guard), and so does Alice's `ALICE-MUSE6-SECONDCHECK.md` (it
exercises U6/U7 with `L-HS-02` fixtures). Guard unchanged at `f58a61c6…`; index
now `33b3e4d0…`; live census **30 citations, 0 uncued**, rc 0.

## Rev 7 (2026-09-13) — declared-list hygiene (Muse batch 6, U6/U7)

The first Muse-6 probe landed here rather than as a new guard. **U6 (vacuous
denominator):** after scanning, if the non-exempt Markdown file count is zero the
guard prints `vacuous scan: 0 non-exempt Markdown files scanned …` and exits 1 —
an instrument failure that `--advisory` does **not** suppress. **U7 (inert
entry):** every `log:`/`skip:` basename must resolve to a scanned file; a missing
one prints `inert declared-list entry: <name> (no scanned file)` and exits 1.
`scan()` now returns the set of scanned basenames so `main` can compute both.
The self-test drives the pair through the **real CLI** (a skipped-only root plus
`log: GONE.md` → rc 1 with both markers) and asserts every declared entry
resolves on the real index. Guard `f58a61c6…` → **`1ca1c87c…`**; live census
**31 citations, 0 uncued**, 0 hygiene findings, rc 0; coverage map rev 12 closes
U6/U7 (U8/U9 remain). Second-seat re-check open.

## Rev 8 (2026-09-13) — ledger↔index completeness (Muse batch 6, U9)

Optional `--ledger <CLAIMS-LEDGER.md>` cross-check: `ledger_superseded()` reads
only ledger **table rows** whose cells carry `SUPERSEDED`, takes the row's first
cell as the old id, and `main` fails `ledger supersession missing from index:
<id>` for any id not in the index. This honors Alice's U9 parse constraint (the
ledger's `supersed` surface is 6 lines and only one is an id move; the rest are a
class label, a prose back-reference, a table header and a process note). The
**default run stays hermetic** — citations still come only from the index, and
the ledger is read only when declared. The self-test covers the
table-row-vs-label/prose parse, a missing ledger (structured prerequisite), and
the real CLI (absent → rc 1; present → rc 0). Guard `1ca1c87c…` →
**`45922e91…`**; live with `--ledger ../../team/CLAIMS-LEDGER.md` **31 citations /
0 uncued**, 0 findings, rc 0; coverage map rev 13 closes U9. Only U3 and U8
remain.

— **Corvid** (`worker-glm-dsh3`). $0, static; no engine run, no tree outside the
repo and `team/` touched.
