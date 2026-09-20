# Assessment — ChatGPT Deep Research "Research Intelligence Directive" (advisory)

**Author:** Corvid (`worker-glm-dsh3`), R&D + evidence-integrity · **Date:** 2026-09-13
**Second-check:** Alice (requested; see §5). **Cost:** $0 (web spot-check only).
**Precedence:** advisory input, per GiLMore/Brian. Our frozen instruments
(`S4-ADJUDICATION.md`, the P2 entry run, `DESIGN-INVOCATION-BENCHMARK.md`,
`SPEC-OUTCOME-PROTOCOL.md`, the 17-guard gate card) and verified findings take
precedence; **no score import**. Source: `team/RESEARCH-INTELLIGENCE-DIRECTIVE.md`.

## 1. Verdict

The directive's **framing mostly converges with ours** — mechanisms over brands,
state evolution over static recall, formation+use over retrieval, coding over
chat, Pareto over one score — and its main value is a **named-benchmark landscape
and a discovery vocabulary** we had not compiled. Its two real additions are a
*Persistent SWE History Suite* proposal and an *evidence-grade/handoff* schema;
its weaknesses are opaque `turnNNviewNN` citations and unverified headline
numbers. Nothing here overrides a frozen instrument.

## 2. Genuinely new to us

- **Named benchmarks we have not surveyed:** **MemOps** (lifecycle operations:
  remember/forget/update/reflect), **StreamMemBench** (paired commit ablation —
  formation as a separable mechanism), **MemSecBench** + **GateMem** (memory
  poisoning persistence→execution→repair; multi-principal governance),
  **STALE** + **Supersede** (staleness / memory-update gap), **HaluMem** (memory
  hallucination), **EvoMemBench** (long-context stays competitive; no universal
  winner), **Mem2ActBench** (memory-to-action), **LongMemEval-V2** (115M-token
  agent histories, workflows/gotchas), **AMA-Bench/AMA-Agent** (causal graph vs
  similarity retrieval), **Agent Memory Leaderboard** (standard Add/Search;
  textual + coding tracks). *Spot-checked by two seats to exist; the headline
  numbers largely reproduce (see §6). **Two partial touches to credit, per
  Alice:** HaluMem appears only as a MemOS vendor-table column (`L-S16-02`) and
  EvoMemBench as a one-line E-1 intake note — not wholly new; the rest have no
  ledger row or survey entry.*
- **Persistent SWE History Suite** — same-repo SWE-Gym/SWE-smith task sequences
  with injected recurring build commands, conventions, failed fixes, corrections,
  supersessions and cross-project distractors. A concrete asset idea we have not
  written down.
- **Discovery vocabulary / terminology fan-out** — search outside "memory":
  event sourcing, change-data-capture, effective/transaction time, belief
  revision, truth maintenance, case-based reasoning, process mining, experience
  replay, rate–distortion, sufficient statistic, blackboard systems, tainted
  retrieval. Directly usable in the Phase-B harvest.
- **Evidence grade A/B/C/D/S + confidence + lifecycle tag, and the handoff's
  `REVISIT TRIGGER` / "what would make this wrong"** — a sharper formalization
  than our ledger classes alone.
- **Security/scope-leakage as a first-class memory dimension**, and an
  **observer/distiller size study** (capture recall/precision separated from
  downstream use).

## 3. What we already do better (do not regress)

- **Mechanisms before brands** is already our operating model: E-1…E-9 mechanism
  families, `controlled_core` vs `raw_product`, frozen P2 arms — and we *measured*
  mechanism differences (Perseus explicit lineage 48/48, agentmemory
  product-decides **418/450 false supersessions**, hindsight state-transition
  0/48), which the directive only recommends.
- **State evolution / supersession** is our strongest asset: Gen38
  `dynamic_conflict` anchor, S6 sanctioned-supersession, `stale_use` +
  `anachronism` in the invocation benchmark, and the AGENTS rule that false
  merge/supersession is never rewarded.
- **Formation + use** is already instrumented: delivered-level rule,
  `redundant_delivered` vs `available_only`, `CBMR`/`FBMR_topic`, `ExplicitBefore`.
- **Coding experience** is our substrate, not a proposal: the live-arm workflow
  plus the transcript miner (**1,250 files / 4,579 operator turns / 548
  corrections / 909 durable facts**, local-only) — the scarce real
  human↔agent corpus the directive calls for.
- **Long-context null** is already an explicit arm in the invocation design.
- **Evidence discipline / anti-fabrication:** CLAIMS-LEDGER classes, the six-field
  citation rule, provenance pins, the second-driver rule and mandatory second
  seats. We caught the corpora report's Open-SWE-Traces error (511,668 vs
  207,489); the directive's `turnNNviewNN` citations would fail our citation rule.

## 4. What enters the R&D thread pool (candidates, not mandates)

1. **Phase-B candidate cards** for the named benchmarks — MemOps, StreamMemBench,
   MemSecBench/GateMem, STALE/Supersede, EvoMemBench, HaluMem, Mem2ActBench,
   Agent Memory Leaderboard — candidate discovery only, **no score import**
   (extends Sprint-2 goal 5; owner Corvid/Alice). **Cards built:
   `team/CANDIDATE-CARD-MEMOPS.md`** (trace schema
   `trigger/target/scope/state transition/evidence`; G1/G2 design fit) and
   **`team/CANDIDATE-CARD-STREAMMEMBENCH.md`** (two-step commit/no-commit
   ablation template, 27.5→40.6 PDF-verified; G4/G3 design fit) and
   **`team/CANDIDATE-CARD-STALE-SUPERSEDE.md`** (implicit-conflict class,
   premise-resistance probe, CUPMem mechanism arm; G1/G2 fit) and
   **`team/CANDIDATE-CARD-MEMSEC-GATEMEM.md`** (Write→Execute→Forget chain,
   leak targets, multi-principal access control; security/governance arm).
2. **Discovery-vocabulary fan-out** — **built** as
   `team/CORVID-DISCOVERY-VOCABULARY.md` (our E-1…E-9/G1–G5-mapped ontology +
   query/contradiction templates); folds into the Phase-B query set and the
   weekly watchlist delta (owner Corvid).
3. **Persistent SWE History Suite** — design-input assessment against the
   invocation/outcome tracks, checking it does not duplicate the internal miner;
   verify SWE-Gym (Apache-2.0) / SWE-smith (MIT) versions (owner Corvid, design).
4. **Evidence-grade + `REVISIT TRIGGER`** — **built** 2026-09-14:
   `team/CORVID-CITATION-GRADE-CENSUS.md` (probe `86b4027f…`) finds the grade is
   **authored, not derivable** from the ledger (9/16 rows decided; 0 above D/S;
   6 primary-source rows underivable for want of artifact/ablation columns) and
   that no cell carries a revisit trigger; fields 7–8 added to
   `CITATION-RULE-DRAFT.md` **Rev 2**, pending Verity.
5. **Memory security/governance arm** — map MemSecBench/GateMem dimensions
   (poisoning chain, trust labels, selective repair, multi-principal access
   control) onto our P3/P4 gate; candidate for Assay's instrument-power
   register. **Cards + addendum built:** `CANDIDATE-CARD-MEMSEC-GATEMEM.md` and
   `CORVID-SCOPE-LEAKAGE-GATE-ADDENDUM.md` (leakage fields G-A/B/C). The
   addendum **corrects** "scope isolation is absent": Gen76/78 already measure
   and close single-principal scope isolation; only the multi-principal/role
   axis is net-new.
6. **Long-context break-even + observer-size** — extend the existing long-context
   null into the outcome protocol (tokens/latency vs accuracy) and note the
   distiller-size question as an M3/M4 confound.

## 5. Second-check block

- **Corvid:** assessed as above; directive is advisory, converges with our
  framing, adds named benchmarks + vocabulary + two schema ideas. Recommend
  **adopt-as-advisory** with §4 items entering the pool.
- **Alice:** **second-check done, 2026-09-13 21:4x UTC** — agree with the
  assessment. (a) Coverage: **no** named benchmark has a ledger row or survey
  entry; HaluMem appears only as a MemOS vendor-table column (`L-S16-02`) and
  EvoMemBench as a one-line E-1 intake note, so credit those two as partials
  when the cards are written. (b) All three flagged numbers are **CONFIRMED**
  from primary sources: StreamMemBench 27.5→40.6 / +13.1 / paired 160
  trajectories (arXiv `2606.14571` **PDF** — note the HTML full text omits
  them), MemSecBench 310/48 (`2607.27080` abstract), AMA-Agent 57.22 / +11.16
  (`2602.22769` abstract). Detail: `team/ALICE-INTELLIGENCE-DIRECTIVE-SECONDCHECK.md`.
  Adopt-as-advisory stands.
- **Assay:** **second-driver spot-check done** — the five landscape numbers left
  after Alice's pass reproduce **exactly** from primary abstracts: Agent Zero
  Memory 95.60 LongMemEval / 93.60 LoCoMo (`2608.29606`), LongMemEval-V2
  451 / 500 / 115M / AgentRunbook-C 72.5% (`2605.12493`), BEAM 10M / 100 /
  2,000 (`2510.27246`). **Comparability flag:** Agent Zero's 95.60 on
  *LongMemEval* and LME-V2's 72.5 on *LongMemEval-V2* are different benchmarks
  and must not be read as one board (`ASSAY-INTELLIGENCE-DIRECTIVE-SPOTCHECK.md`).

## 6. Verification status (after Alice + Assay)

- **Named benchmarks exist**, AND the directive's flagged numbers now have two
  independent seats: Alice confirmed StreamMemBench (27.5→40.6, +13.1, paired
  160), MemSecBench (310/48), AMA-Agent (57.22, +11.16); Assay confirmed the
  other five exactly. **Method note (Alice):** StreamMemBench's numbers are in
  the **PDF only** — the HTML full text omits them, so a future grep of the HTML
  must not read as fabrication.
- **Comparability flag:** bind each number to its benchmark version before any
  citation (Agent Zero LongMemEval vs LME-V2 LongMemEval-V2).
- **Still unverified:** MemSecBench's numbers beyond the case count, SWE-Gym
  2.4K/11, the Agent Memory Leaderboard's current protocol, Mem2ActBench, and
  every opaque `turnNNviewNN` citation. Recommend a bounded pass when the
  candidate cards are written, not now — matching Alice's advice.

## Rev 2 (2026-09-13) — verification folded; assessment final

Alice's coverage + three-number check and Assay's five-number spot-check are
folded above; the only corrections are the two partial touches (§2) and the
comparability flag. **Verdict unchanged: adopt-as-advisory**; §4 items enter the
pool as candidates, no score import.

— **Corvid** (`worker-glm-dsh3`). Advisory assessment, **final after two second
seats**; $0 (web spot-check only).
