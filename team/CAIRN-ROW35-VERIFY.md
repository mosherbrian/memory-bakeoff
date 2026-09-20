# CAIRN-ROW35-VERIFY — verdict on row 35 (DIGEST-V2 curation pass)

Verifier: Cairn (worker-pi) — the row's named verifier; not a producer
(GiLMore dispatched; producer worker-glm-2, later kiln-flash). Filed
2026-09-17 ~14:0x PDT in answer to the chain-verdict nudge. The
verification itself was done 2026-09-14 and is fully recorded in
`team/CAIRN-DIGEST-V2-SPOTCHECK.md` (all 32 seed rewrites read, not the
20 the gate asked for).

## Verdict: VERIFIED FAIL — the seed list as written is not vault-ready

- The curation pass is real: 318 rows classified, deterministic local
  classifier, three tightening passes, no vault writes. I did not
  re-derive the 318-way split; my gate covered the seed list.
- The 32-row seed list FAILS the vault-ready gate as written: 27 of the
  32 seeds demote (I concur with Kiln's self-audit on all 27), 5 remain
  and each needs a qualifier before any vault write — #110 subject,
  #134 framing, #159 framing, #228 my dissent (first-person n=1), #288
  as-of date. Net: ~5/318, not 32/318.
- The corrected shape (5 qualified seeds + 27 demotions) was served to
  Brian 2026-09-14; the artifact file itself still carries the
  uncorrected 32-row list.

Fix (owner kiln-flash, cheap): apply the 27 demotions and the 5
qualifiers to the seed section of `team/DIGEST-V2.md`, or mark that
section superseded by the served correction. Re-verify is mine.

— Cairn
