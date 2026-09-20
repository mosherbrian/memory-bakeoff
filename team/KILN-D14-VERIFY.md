# kiln-flash second-seat verify — D-14 timestamp-gate verify-receipt excusal

**Verifier:** kiln-flash (sole doer seat) · **Date:** 2026-09-17 · **Cost:** $0, local reads only
**Subject:** the D-14 extension to `team/D-7-timestamps/check.py` (author corvid-dsh;
original gate plumb-fable per the file header), against the row's declared
contract and its own closing bar: **"Both directions proven in --selftest or
the row does not close."**
**Independence:** the row's own constraint — "the gate must not be refitted by
the party it excuses: corvid authors, kiln verifies." Corvid authored the
extension and owns four of the rows it excuses; I authored nothing in the gate,
and I hold no producer stake in any row the excusal touches. The blind this row
demands is the one I am in.

## Declared check

`python3 team/D-7-timestamps/check.py --selftest` → **rc 0**, output matching
Corvid's claim exactly: 5 conforming boards ACCEPTED (clean; **verify-closed by
receipt**; marked-unreliable; corrected-with-original-quoted; machine stamp
with seconds/offset) and 17 defects REJECTED **by name** — the inventory includes
both directions D-14 demands: **a receipt newer than its stamp** (REJECTED) and
**a stale receipt** (REJECTED), beside a future stamp and a silent rewrite.
CLI contract holds in all four hostile/clean subprocess cases (exit codes, no
tracebacks).

## Live board gate

`python3 check.py` (no args) → **rc 0**: 31 stamped rows, 21 compared against an
existing artifact, **4 verify-closed by receipt**, 0 marked unreliable,
0 changed since baseline. Matches Corvid's claimed 15:56 close verbatim. The
four S7-*G verify receipts exist on disk (mtimes 15:24/15:35 PDT) consistent
with the excused count.

## Code review — contract fidelity

The row's contract, mapped clause by clause to the implementation:

| Declared | Code | Verdict |
|---|---|---|
| receipt named `team/CORVID-<ROW>-VERIFY.md` | `queue.parent / f"CORVID-{rid}-VERIFY.md"`, `is_file()` | exact path, no globbing ✓ |
| mtime within tolerance BELOW the stamp → verify-closed | excused iff `timedelta(0) <= stamp − receipt_mtime <= tol` | ✓ (inclusive at the boundary — reasonable) |
| receipt NEWER than the stamp is its own finding | `[RECEIPT-AFTER-STAMP]`, not excused, counted | ✓ |
| stale receipt still flags | falls through to `[STAMP-LEADS-ARTIFACT]` | ✓ |
| still flag every late stamp with no receipt | no-receipt case → `[STAMP-LEADS-ARTIFACT]` | ✓ |
| late-stamp excusal only | receipt path lives only in the `STAMP-LEADS-ARTIFACT` branch; `[FUTURE-STAMP]` ("Never excused", selftest-tested even when marked) and `[SILENT-REWRITE]` are untouched | ✓ |

## Code review — not refitted in the author's favor

The independence question, answered from the code rather than the author's
word: the excusal is **narrow** — it fires only on a late-stamp lead, only when
a file named for a Corvid verify receipt already exists, and only when that
file's mtime sits in the 0–10-minute window below the stamp. Corvid cannot
excuse its own late stamps by gate fiat: a receipt must exist on disk, written
before the stamp. The obvious launder — finishing late, stamping early, then
writing the receipt — is the `[RECEIPT-AFTER-STAMP]` case, flagged, selftest-
proven. The excused count is printed in every clean run ("4 verify-closed by
receipt"), so excusal is visible, not silent. The declaration predates the
implementation in the row text and is quoted in the file header with the 15:42
incident that motivated it.

Semantics sanity: the model is "a reviewer closing later is ELAPSED TIME, not
skew" — artifact mtime ≪ receipt ≤ stamp. That is exactly the four S7-*G
closes (receipts 15:35, stamps 15:36, artifacts earlier) that tripped the
pre-D-14 gate.

## Inherited limits (unchanged by D-14, stated in the gate itself)

mtime is the newest write, so a later edit hides an earlier lead; BASELINE
knows only the stamps that existed 2026-09-17; and in principle any mtime can
be backdated with `os.utime` — the general mtime-trust limit the D-7 charter
already owns ("whether the stated cause is the TRUE cause stays with the named
verifier"). D-14 neither widens nor hides these.

## Verdict

**PASS.** Both directions are proven in --selftest as the row requires, the
live board is clean with excusals visible and receipt-backed, and the
implementation matches the declared contract without widening it in the
author's favor. Row D-14 closes.

— **kiln-flash**, 2026-09-17. $0, one turn, local reads only. Writes confined
to `team/`.
