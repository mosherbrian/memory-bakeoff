# CORVID-S11-1-VERIFY — build verification, row S11-1 (BM25 margin-rule abstention)

verified: corvid-dsh 2026-09-18 17:59 PDT (clock read at write) — VERIFIED PASS

Artifact: team/S10-BM25-ABSTAIN2/ (declaration.json, run_margin_rule.py,
results.jsonl, verdict.json, design.md + gate check.py). Builder: kiln-flash
(claimed 17:39, done 17:49 PDT). I authored neither the gate (plumb-fable,
verified separately 17:07, team/CORVID-S11-1G-VERIFY.md) nor the build.

Evidence, this pass:
1. Gate bytes unchanged since my pre-build verification: sha256(check.py)
   = e6f92bdf55df63282bb2b12132ef53eb6be9a750e9bd11e856dff0ac268725c3 —
   identical to the sha pinned in CORVID-S11-1G-VERIFY.md.
2. Declared check: `python3 team/S10-BM25-ABSTAIN2/check.py` → rc 0, clean:
   mechanism-fails at declared threshold 1.0 (abstain_correct 2,
   retrievals_lost 1), grid of 3 recomputed, priors recomputed s6 5/0,
   prefilter 4/0 (retrieve/abstain).
3. Pre-registration ordering: declaration.json declared_at
   2026-09-19T00:44:07.393371Z (= 17:44:07.393 PDT) precedes results.jsonl
   mtime 17:44:07.395226 PDT. Declaration first, run second.
4. Corpus pin: sha256(S6-SELECTIVITY/corpus.jsonl)
   = 5a8668f73383ea1acc4806a31df9240cc0eb9186a7be69385a8f23e8be2024be —
   matches the sha the row and design.md pin (S6's frozen bytes, read in place).
5. results.jsonl: 20 rows, two arms exactly — bm25-nofilter (control) and
   bm25-margin (declared mechanism). No third arm, no token-filter arm.
6. Substance resting on the VERIFIED gate: the S11-1G verification proved the
   gate recomputes margin, abstention, both sides and the full grid from the
   rows' scores, trusting nothing in verdict.json, and rejects six on-disk
   corruption classes by named markers. The gate's recomputed summary above is
   therefore independent of kiln's prose; verdict.json's mechanism-fails claim
   (2 of 5 rejected, sel-005 lost at z 0.985 below two abstain cases) is the
   gate's own finding, and an honest refutation is a result per the gate.

Dispositions (verdict, not defects): the declared rule fails at every declared
threshold (0.5 → 0/0, 1.0 → 2/1, 1.5 → 5/2); rejections never separate from
losses. This refutes the read-the-scores abstention family on this corpus the
way S7-1 refuted token filtering. Both sides were measured as the row required.

verifier: corvid-dsh (did not author artifact or gate)
