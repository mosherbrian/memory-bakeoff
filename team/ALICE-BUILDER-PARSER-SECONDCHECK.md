# Second-seat — builder S6 receipt-parser fix (Assay) + a silent colon-form regression

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 18:0x UTC · **Cost:** $0, synthetic, one turn.
**Trigger:** standing second-check of `team/ASSAY-BUILDER-RECEIPT-PARSER.md`
(register #6; frozen S4 instrument, pending a GiLMore ruling).
No tree modified.

**Subject:** `builder-receipt-parser.diff` (`92cf3a63…`), guarded
`build_s4_packets.patched.py` (`915c0aa4…`), base `6616c48e…`.
Driver: `row-builder-parser-check/alice_builder_parser_check.py` (`32128efb…`),
result `result.json` (`58a11b5d…`).

## Verdict

**PASS on the fix's target and every claimed case; one low-severity silent
regression on a header form the canonical parser accepted.**

Both hashes match. Driving the real `load_record_sets` on canonical vs patched
with a distinctive file mtime (`1234567890`) and stamp
`2026-09-12T18:05:00Z` (`1789236300`):

| header | canonical | patched |
|---|---|---|
| `# S6 scan-after-write 2026-09-12T18:05:00Z` | 1789236300 | 1789236300 (unchanged) |
| `# S6 scan-after-write 2026-09-12T18:05:00Z (comment)` | **ValueError** | **1789236300** (fixed) |
| `# S6 scan-after-write` | mtime | mtime (unchanged) |
| `# S6 scan-after-write notadate` | **ValueError** | mtime (fixed) |
| `# S6 scan-after-write: 2026-09-12T18:05:00Z` | **1789236300** | **1234567890 (mtime!)** |

**Finding (low–moderate, latent):** the patch slices the literal prefix and
takes `rest.split()[0]`; for a colon-delimited header the first token is `":"`,
so `parse_iso` fails and the new `except ValueError` **silently substitutes the
file mtime** for the real scan timestamp. Canonical parsed this form correctly
(its `split(" ", 3)[3]` returned the ISO), so this is a behavior regression, and
its class is the worst one for this instrument: a wrong ordering timestamp with
no error, instead of a loud failure. **No live impact today** — the shipped
emitter writes the space form (`s6_scan_after_write.sh:71`), so no existing
receipt is affected; the risk is a hand-written or third-party receipt.
**Fix:** `rest = line[len("# S6 scan-after-write"):].lstrip(": \t")` (or accept
the first ISO-shaped token), and add a colon-form case to the power check. If
the intended contract is space-form only, state that in the note and keep the
mtime fallback deliberate.

The other six power-check cases reproduce: nominal byte-identical, trailing
text parsed, short/unparseable fall back to mtime, and the canonical crash is
real (`ValueError` on the trailing-text header).

## Scope and limits

- Synthetic receipts under a temp dir only; the builder's B7 `--self-test` was
  not re-run (Assay's stated limit — the touched function is orthogonal).
- The patch is **not applied** and stays parked for the S4 ruling; this check is
  input to that ruling, not an application.
- I did not scan for colon-form receipts in the wider vault; the emitter source
  (`s6_scan_after_write.sh:71`) is space-form, which bounds the live exposure.
