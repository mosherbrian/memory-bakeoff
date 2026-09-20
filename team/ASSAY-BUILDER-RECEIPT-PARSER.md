# Assay — builder S6 receipt-parser fix (register #6) + register rev 3

**Author:** Assay (`worker-glm-dsh2`) · **Date:** 2026-09-13 · **Cost:** $0, static
**Thread:** Assay — instrument power checks.
**Subject:** `build_s4_packets.py` sha256 `6616c48e…` (frozen S4 builder).
**Status:** fix validated, **not applied** — this is a frozen window
instrument, so it needs a GiLMore ruling + re-freeze (S4 rule 3).

## Defect (register #6, still live)

`load_record_sets` reads `# S6 scan-after-write <iso>` headers. The older
`line.split(" ", 3)[3]` IndexError is caught, but the extracted timestamp goes
**whole** to the unwrapped `parse_iso` at line 189. So a header with a trailing
annotation crashes the builder:

- `# S6 scan-after-write 2026-09-12T18:05:00Z (comment)`
  → `ValueError: Invalid isoformat string: '2026-09-12T18:05:00Z (comment)'`.

Reproduced directly against the committed builder. A short header
(`# S6 scan-after-write`) already falls back to the file mtime, so the only live
failure is trailing text. Low severity: the shipped emitter never writes trailing
text; this is a robustness hole, not a live defect.

## Fix

- take only the first token after the literal prefix as the timestamp;
- if that token does not parse, fall back to the file mtime instead of raising
  (the same fallback already used when no stamp is present).

`builder-receipt-parser.diff` sha256 `92cf3a63…`; guarded builder sha256
`915c0aa4…`; `git apply --check` clean on canonical `implementer/repo`.

## Power check

`builder_receipt_parser_power_check.py` sha256 `d7820dcd…`; sealed result
`sealed-builder-parser-20260913/result.json` sha256 `063dc53f…`. **7/7**:

1. canonical trailing-text header → **ValueError reproduced**;
2. canonical normal header → expected epoch;
3. patched normal header → **same epoch** (nominal path unchanged);
4. patched trailing-text header → expected epoch (not mtime);
5. patched short header → mtime fallback, no crash;
6. patched unparseable stamp → mtime fallback, no crash;
7. canonical vs patched on a normal multi-receipt set → identical
   timestamps/basenames/keys.

## Register rev 3

`ASSAY-POWERCHECK-REGISTER.md` gains a **rev-3 refresh** that corrects two stale
rows (the 23:4x table still said `verify_s4` #2 OPEN when it was fixed at 00:33,
and listed #6 OPEN) and folds the afternoon's post-register instruments
(exit-contract coverage + completeness, identifier-lifecycle rev 4, map-hash
completeness, cross-copy drift, required-metrics schema, orphan rev 3,
ledger-count rev 2, RD-thread-labels rev 4, LongMemEval sentence boundary).
Open instrument items at rev 3: **#4** (S6 empty-scan guard, owner decision) and
**#6** (this fix, needs an S4 ruling). Nothing else.

## Limits

One function exercised directly; the builder's `--self-test` (B7 count parity) is
orthogonal and was not re-run. Synthetic receipts only; no tree modified, no
packet built, no live content read.

— **Assay** (`worker-glm-dsh2`).

---

## Rev 2 — closes Alice's colon-form regression

Alice's second seat (`ALICE-BUILDER-PARSER-SECONDCHECK.md`, driver `32128efb…`,
result `58a11b5d…`) PASSed the target cases and found one silent regression in
v1: it sliced the literal prefix and took `rest.split()[0]`, so for the colon
form `# S6 scan-after-write: <iso>` the token was `":"`, `parse_iso` failed, and
v1 substituted the **file mtime** for the real scan timestamp — a wrong ordering
timestamp with no error, and a regression from canonical (whose
`split(" ", 3)[3]` parsed that form). No live impact (the emitter writes the
space form, `s6_scan_after_write.sh:71`), but the worst class for this
instrument.

Fix: `lstrip(": \t")` before taking the first token, so both the space and the
colon forms parse. The mtime fallback remains deliberate for a genuinely
unparseable stamp (same behavior as a missing one), but a valid form no longer
reaches it.

- v2 diff `5a4c39cc…`, guarded `4715558d…`, power check `ba49c25b…`, sealed
  result `61540e31…`; **8/8** (case 8 adds colon-form parity with canonical);
  `git apply --check` clean on base `6616c48e…`.
- v1 (`92cf3a63…` / `915c0aa4…` / `d7820dcd…`) is **superseded**; do not apply.

— **Assay** (`worker-glm-dsh2`).
