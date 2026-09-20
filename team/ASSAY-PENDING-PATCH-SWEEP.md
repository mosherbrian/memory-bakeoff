# Assay — pending-patch sweep + live suite state (close hygiene)

**Author:** Assay (`worker-glm-dsh2`) · **Date:** 2026-09-13 · **Cost:** $0, static
**Thread:** Assay — instrument power checks / close hygiene.
**Purpose:** one page of what is **live vs superseded** among the diffs Assay
produced, verified against the **current bytes**, so no owner applies a stale
patch at close.

## Pending patches — re-checked just now

| patch | current base (sha) | `git apply --check` | owner / status |
|---|---|---|---|
| `builder-receipt-parser.diff` v2 (A2? no — S4 builder) | `6616c48e…` | **APPLIES** | Kiln/fsync; frozen S4 builder, needs an S4 ruling |
| `a2-buffer.diff` v3 (vault RPC framing) | `905f604c…` | **APPLIES** | Kiln/Cairn; frozen live-arm extension, needs A2 apply + outside restart |
| `meters-topup.diff` | `f2d5c8ea…` | **APPLIES** | builder/Brian; budget rule |
| `checker-exit-coverage.diff` | `956f5338…` | **NO — superseded** | Corvid applied a superset (`6a072f30…`→`6cd289e7…`) |
| `meta-coverage-completeness.diff` | `956f5338…` | **NO — superseded** | same applied superset |
| `split-cue.diff` | `45922e91…` | **NO — superseded** | lifecycle rev 4 (`f58a61c6…`) fixed the same class; my patch is also obsolete |
| `crosscopy-u8-v2.diff` | `f8bd89a9…` | **NO — already applied** | Corvid applied it as guard 16 rev 5 |

**Do not apply** the four superseded/already-applied diffs; each has a
`SUPERSEDED`/apply receipt in the RD log or a note of record. The three live
diffs were re-checked against their exact current bases in this pass.

## Live suite state (current bytes)

- **18 guards** in `repo-glm-dsh3/scripts/check_*.py`.
- Meta-guard `check_checker_exit_contracts.py` sha `956f5338…`: `--self-test`
  PASS, live **17/17 hold** (all 17 siblings covered).
- Guard 18 `check_record_text_identity.py` sha `0b8fd3aa…` (adopted from this
  seat's U3 prototype): `--self-test` PASS, including the structured
  missing/directory-canonical cases Corvid/Alice added after adoption.
- Coverage map: Layer C empty (U2/U4/U5/U6/U7/U8/U3 all closed).

## Why this page

Three of my diffs are still unapplied and load-bearing at close (S4 builder
parser, A2 framing, meters budget), and four older ones are dead. A cold reader
or the close runner should read the first table before touching any diff.

— **Assay** (`worker-glm-dsh2`).
