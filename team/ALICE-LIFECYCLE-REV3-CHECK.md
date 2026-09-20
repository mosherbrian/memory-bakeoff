# Second-seat — identifier-lifecycle guard rev 3 (Corvid) closes my residual; one self-satisfiable-subject residual remains

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 17:1x UTC · **Cost:** $0, static, one turn.
**Trigger:** my `ALICE-LIFECYCLE-SPLIT-CUE-SECONDCHECK.md` residual was folded
into the live guard; independent re-check of the shipped rev 3.
No tree modified.

**Subject:** live `scripts/check_identifier_lifecycle.py` (`087fc3f9…`, rev 3) +
`team/IDENTIFIER-LIFECYCLE.txt` (`2793a64f…`). Driver:
`row-lifecycle-rev3-check/alice_rev3_check.py` (`19ac81f7…`), result
`result.json` (`f3afedde…`).

## Verdict

**PASS on the case I reported.** Rev 3 blanks the cited id and `\bL-HS\b`
before the weak-`split` subject test, so
`The class for L-HS-02 (LongMemEval split unspecified) is contradicted.` is now
**`[UNCUED-ID]`** (was `[cued]` in rev 2). Genuine cues are kept
(`The L-HS-02 split is recorded in the ledger.` / `L-HS-02 was superseded…`),
`--self-test` PASS, and the live census is green (`team/` **27 citations, 0
uncued**; point-in-time). The four `skip:` mechanism docs are this guard's own
second-check/power-fix notes — checked, they do not hide a current claim.

**One residual in the same class (low-to-moderate, latent):** the weak-`split`
subject set is `ledger|identifier|lifecycle|\brow\b|\bid\b`, and `row` / `id` /
`identifier` are words the **citation's own context** supplies. So a stale claim
that names its row/id and carries the benchmark qualifier still cues itself:

| fixture | rev 3 |
|---|---|
| `The class for L-HS-02 (LongMemEval split unspecified) is contradicted.` | **detected** (my case, closed) |
| `The L-HS-02 row gives LongMemEval (split unspecified) as current.` | **cued (miss)** |
| `For id L-HS-02, LongMemEval (split unspecified) is the claim.` | **cued (miss)** |
| `The L-HS-02 identifier is paired with LongMemEval (split unspecified).` | **cued (miss)** |

No live miss today (all 27 live citations are genuinely cued), so this is
prospective. **Principled fix direction:** drop `row` / `id` / `identifier` from
the weak subject set — keep the anchored `L-HS split`, `ledger`, `lifecycle`,
and/or require a **replacement id** from the index — then validate against the
live 27-citation census so no genuine cue is un-cued. This is a narrowing
trade-off, not a defect in the reported case.

## Provenance check of the index row (PASS)

The index names its source; audited it against the ledger:

- `CLAIMS-LEDGER.md:793` (L-HS-02) reads exactly
  **"SUPERSEDED — see \"L-HS split\" … L-HS-02a `vendor-only` (94.6 number),
  L-HS-02b `not established` (superlative)"** — matching the index's
  `superseded: L-HS-02 -> L-HS-02a, L-HS-02b` and its inline source comment.
- The split section is headed "(Corvid + Alice, 2026-09-12)" and line 945 names
  **"the 22:50 L-HS split"**, matching the index's "resolved 2026-09-12 22:50".

One trivial doc nit: the index header's cue list still names `"split"` without
the subject condition the code now imposes; harmless, but it would mislead a
reader re-deriving the predicate.

## Scope and limits

- Read-only over the repo and `team/`; synthetic fixtures under a temp dir only;
  no document bodies printed.
- I did not re-run Assay's sealed rev-2/3 power check; I rebuilt the cue matrix
  independently and added the three self-satisfiable-subject cases it lacks.
