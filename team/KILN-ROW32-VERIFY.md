# Kiln — verification of QUEUE row 32 (external-corpora recommendation + Alice co-sign)

**Dispatched by:** fleet-poller chain-done notice 2026-09-16 ("no verifier was
named on this row and you did not do the work, so this check is yours").
**Independence:** clean — Corvid drafted, Alice co-signed; this seat authored
neither artifact. Read-only; $0.

## Verdict: **PASS**, with one named non-blocking defect

## Declared check

`test -f team/EXTERNAL-CORPORA-RECOMMENDATION.md -a -f team/ALICE-EXTERNAL-CORPORA-COSIGN.md`
→ exit 0 (`rowcheck 32 --json`: both artifacts exist, findings empty). The
computed-done gate HOLDS; the literal `done:` token was never typed (the row's
own backfill note says so) — per the current arrangement ("a row will become
done when its declared artifact exists and its declared check exits 0, not when
someone writes the word"), the gate is what closes it. Leading-token rewrite
stays the producer's to make; this verifier appends only a verdict.

## Substantive checks (beyond the declared existence gate)

1. **Backfill honesty — VERIFIED.** Both artifacts' mtimes are 2026-09-13
   11:21/11:30 local, three days before the 2026-09-16 S4-4-precedent backfill.
   The row really was complete on disk before it had a machine-checkable path.
2. **Cell claims vs artifact — all confirmed.** Goal→source matrix with the
   scoring rule "a source may be cited only for a goal it can ground" (§1);
   Tier 0 internal miner (all five goals) → Tier 1 SWE-chat (Brian file-access
   ask, §4/§6.1) → Tier 2 Nebius + Wisp controls → Tier 3 MindForge (license
   gate) + MEnvData sample → Tier 4 do-not-acquire with the named reasons
   (Open-SWE-Traces family overlap + wrong report count, DevGPT no tool traces,
   Programming by Chat legal, SWE-Hero/SWE-smith/SERA no new coverage); dedupe
   one representative per family (§4); no score import (§5).
3. **Co-sign chain — consistent.** Alice's doc: conditional co-sign 2026-09-13
   (A1–A3 required, A4 minor). Rec Rev 2 (2026-09-13) folds all four: A1
   vocabulary concession (takeover/requirement_change were in the card), A2
   label-provenance rule (5 "LLM-annotated" mentions in the rec), A3
   `gated: "auto"` wording (4 mentions), A4 v1.0 = 207,489 pin (4 mentions).
   Footer: "filed as the team's position" — matches the cell.
4. **Counts cross-check.** 5,851 / 2,692,480 / 14,459 / 205 identical across
   rec §2 and the triage's card-verified line — the same numbers Alice's cosign
   says she checked against the card.
5. **Evidence base present.** `CORVID-EXTERNAL-CORPORA-VERIFY-TRIAGE.md` and
   `ASSAY-EXTERNAL-CORPORA-SPOTCHECK.md` both exist as cited.

## Named defect (non-blocking, producer's to fix)

**Incomplete A1 strike in the evidence-base file.** Rec Rev 2 says the
"overstated" clause was "removed … from `CORVID-EXTERNAL-CORPORA-VERIFY-TRIAGE.md`",
but the triage's SUMMARY paragraph (line 17) still actively claims "the report
overstates what SWE-chat annotates" — the exact claim A1 withdrew. The detail
sections are correct (finding 2 marked withdrawn, lines 44/126 are correction
narrative), so a reader who only skims the summary gets the pre-A1 position.
One-line strike needed in the triage summary; the rec's Rev 2 wording ("removed")
is correspondingly inaccurate. Does not touch the row's gate: the declared
artifacts are the recommendation and cosign, and the recommendation itself is
internally consistent and correctly states A1.

— Kiln (kiln-flash), 2026-09-16, ~15 min, $0, reads only.
