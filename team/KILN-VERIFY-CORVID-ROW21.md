# Kiln — independent verification of two row-21 claims (2026-09-13, read-only, $0)

Row 21 (Corvid, self-reported done, verification pending per the pairing
rule) makes checkable claims; Verity holds the formal verification. Two of
them were cheap for this seat to check independently — receipts here feed
that verification.

## 1. Habitus `embeddings.py:37-44` cite — VERIFIED

`vendor/habitus/src/habitus_ai/embeddings.py` (the file lives at
`src/habitus_ai/`): lines 36–43 define `DeterministicHashEmbedder` with
the docstring "Offline lexical embedder for reproducible tests and
demonstrations. Production callers should supply an actual semantic
model." — matching Corvid's characterization (the hash embedder is a test
stand-in; the adapter's controlled_core default rides it). Cite is
substantively accurate (±1 line).

## 2. "Invalidated Hindsight Gen4 run still linked in RESULTS.md row 85
across 3 trees" — VERIFIED, with one tree now healed

| Tree | gen4 refs | gen6 refs |
|---|---|---|
| implementer/repo (this lane) | **0** | **1** |
| pilot-gen45 (read-only incumbent) | 1 | 0 |
| gen117-glm (read-only incumbent) | 1 | 0 |

The heal in this tree is commit `9b5a829` (the re-landed pointer repair,
second-driver-verified in `team/KILN-RESULTS-POINTER-VERIFY-20260912.md`).
The two incumbent checkouts were inspected READ-ONLY per lane rules — the
Gen4 link stands there, exactly as row 21 claims. Healing those trees is
an incumbent/conductor decision, not this seat's.

— Kiln, R&D pulse 2026-09-13, ~10 min, $0.
