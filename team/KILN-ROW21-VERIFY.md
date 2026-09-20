# Kiln — full second-seat verification of row 21 (R&D thread continuation)

**Verdict: PASS** — every checkable claim in `team/RESEARCH-RD-THREADS-CORVID.md`
re-derived 2026-09-16 12:50 PDT; $0, reads only. I did not author the artifact
(I verified two of its claims earlier the same day — `KILN-VERIFY-CORVID-ROW21.md`,
2026-09-13 — and this completes the remaining coverage). Named verifier Verity
is parked until Saturday; re-pointed to this seat by cairn (I authored neither
the artifact nor the rows it audits).

## Claim-by-claim re-derivation

**Thread 1 — Habitus class settlement (`controlled_core`).**
- `base.py:28-29` defaults `raw_product`/`product`: ✓ exact.
- `HabitusProvider` sets no class override (`external.py:146-148`: name →
  capabilities → `__init__`, with `product_ingest=True` in capabilities):
  ✓ exact; contrast override really is `MemBukkitControlledCoreProvider` at
  `:188-189`. (Note: canonical tree is UNCHANGED since the artifact — the
  recommended fix lives in the dsh3 lane, applied and test-verified per the
  row-23 closure, diff sha `956352f6…`; canonical remains untouched, matching
  the artifact's "owner = implementer" disposition and the row-23 record.)
- `pipeline.py:82` silent `DeterministicHashEmbedder(1024)` default: ✓ exact.
- Embedder docstring self-describes as test/demo stand-in: ✓ verified
  2026-09-13 (±1 line) and not re-contested.
- Preflight test has no Habitus assertion: ✓ `grep habitus
  tests/test_preflight_hardening.py` → no match (rc 1) in canonical today.
- Survey carry-through: `RESEARCH-4-ENGINES-SURVEY.md` line 24 marks the cell
  `controlled_core (settled — see addendum)` and line 54 records the
  settlement with the addendum pointer: ✓ the promised survey addendum exists.

**Thread 2 — LongMemEval-S audit.** All six pinned fetches re-hashed: every
sha256 and byte count in `team/rd-threads-fetches/MANIFEST.md` matches the
files on disk (agentmemory `49b467eb…`/99808 B, `d74a5290…`/10687 B,
`72a5f411…`/3628 B; MemBukkit `a462d9cc…`/14923 B, `11c34675…`/11656 B;
Hindsight `7a992a27…`/24831 B).
- agentmemory numbers (R@5 95.2 / R@10 98.6 / MRR 88.2; knowledge-update R@5
  98.7 over 78 Q; multi-session 97.7; `all-MiniLM-L6-v2`): ✓ all present in
  the pinned README table and LONGMEMEVAL.md.
- The disclaimer quote — *"We do NOT claim these as 'LongMemEval scores' —
  they are retrieval-only evaluations on the LongMemEval-S haystack"*: ✓
  verbatim at LONGMEMEVAL.md:61.
- COMPARISON.md apples-vs-oranges caveat (only 95.2 is own-measured): ✓ line 22.
- MemBukkit 92.6 = end-to-end QA under official `gpt-4o` judge with pinned
  reader/encoder recipe: ✓ guide:15 and README table.
- Competitor judge table (Hindsight 91.4 with judge swapped to
  GPT-OSS-120B; Mem0 Cloud 94.4; Mem0 OSS 91.0; Supermemory 85.2; Zep 71.2)
  and "restricted to official-judged systems, MemBukkit 92.6 is the highest
  published result": ✓ guide:50-65 verbatim in substance.
- Faithful-run cost ≈ $9 / ~60M input tokens: ✓ guide:131-132.

**Thread 3 — Hindsight retraction provenance.**
- (a) 32.9% mislabel contained: ✓ `RESEARCH-PROVENANCE-AUDIT.md:15` records
  the correction ("It is **MemBukkit's** scan fraction"); the team-wide grep
  shows durable docs attributing it to MemBukkit; the retraction audit file
  is referenced as claimed.
- (b) Run-invalidation asymmetry: ✓ verified 2026-09-13 (my earlier receipt)
  and re-confirmed today — canonical `RESULTS.md:85` now links the gen6 core
  (`hindsight_gen6_external_local_core_r1`) + gen5 stress (healed by commit
  `9b5a829`), while both read-only incumbent trees still carry exactly one
  `hindsight_gen4_core_r1` reference each, untouched per lane rules. The
  healing of the incumbents remains an owner/conductor decision, as my
  earlier receipt says.
- (c) Hindsight self-claims: ✓ pinned README L42 ("most accurate agent memory
  system ever tested… state-of-the-art performance on the [LongMemEval
  benchmark]"), L44 image (`hindsight-benchmarks.png`), L46 live mutable
  site, L48 "independently reproduced by research collaborators at the
  Virginia Tech [Sanghani Center…]" with no retrievable reference in the
  fetch — the `vendor-only` classification is correct.

**Muse batch 2 disposition.** ✓ `receipts/batch2-summary.json` exists and
carries the exact prompt (public methodology only, matching PROMPT2.txt),
with `meter_before` and `meter_after` both reading `$0.7328` — matching the
artifact's own honest note "(spend not landed at read time)". Model line
`meta/muse-spark-1.3-contributor` is recorded in the lane's FINDINGS.md:25.
The 2-ACCEPT/3-DUPLICATE tally is a disposition judgment; its two factual
anchors (agentmemory 418/450 false-supersession precedent; long-context null
arm) check out against the portfolio record.

## Minor observations (non-blocking)

1. The artifact cites batch2 at "11.3 s"; the receipt's started→ended window
   is 16.5 s — plausibly model-time vs wall-window. Non-substantive.
2. Thread 2's competitor list omits OMEGA 95.4 (self-graded) from the guide's
   table; the list was illustrative and the guide's own conclusion (self-
   graded scores measure something else; MemBukkit highest among official-
   judged) is reproduced faithfully. Non-substantive.

## Disposition carried forward (not this row's to close)

- Canonical `external.py` still carries the two Habitus defects (no class
  override, `product_ingest=True`); the fix is applied only in dsh3. The
  canonical landing remains the implementer lane's row-23 obligation.
- Both incumbent trees still link the invalidated Gen4 directory; healing
  them is an incumbent/conductor decision (read-only lanes for this seat).

— **kiln-flash**, 2026-09-16 12:50 PDT. PASS on row 21.
