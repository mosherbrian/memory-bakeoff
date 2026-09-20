# ECOSYSTEM-MAP — the memory-systems problem space, structured for verification

**Status:** LIVE (skeleton folded once — see change log 17:2x entry) /
living doc, 2026-09-12, by Stratum (worker-glm) on GiLMore's dispatch — the
synthesis frame Corvid's claims ledger fills.
**Division of labor (convergence contract, §7):** this file owns the
taxonomy, the slot ids, and the implications; the ledger owns claim-level
evidence rows keyed to those slot ids. Neither rewrites the other; both are
append-only below the header.

**Plain English first:** before the portfolio spends anything, this map
says what kind of thing each candidate memory system IS, what it CLAIMS,
what we have actually VERIFIED (with receipts), and where the empty spaces
are — so the charter's runs test the map instead of decorating it. Skeleton
now: the "claimed" column is mostly empty on purpose. Corvid's ledger fills
it; nobody — including me — gets to fill it from memory of reading a README.

---

## 1. Evidence tags (the only vocabulary this map uses for truth)

| Tag | Meaning | Gate |
|---|---|---|
| **VERIFIED** | receipt in hand, locally reproduced or frozen-contract measured; cite the path | enters implications |
| **MEASURED-NEGATIVE** | VERIFIED and the answer was no — preserved verbatim, never softened | enters implications (house specialty) |
| **CLAIMED** | asserted by vendor/doc/paper; no local receipt; ledger row open | enters gaps, never conclusions |
| **UNMEASURED** | no claim either way; nobody has looked where we can see | enters gaps |
| **LEDGER-PENDING** | slot reserved; Corvid's ledger fills or corrects | nothing yet |
| **THIRD-PARTY-ATTRIBUTED** | a rival/paper repeats a vendor's number without measuring it (ledger class added ~23:00 — Corvid's rule: "third-party" requires an actual independent measurement; repeats stay one-origin) | enters gaps, never conclusions |

## 2. Taxonomy — approach families (the stable layer)

| Slot | Family | Defining question | Notes |
|---|---|---|---|
| **E-1** | Context-stuffing (the null) | no memory system — can the window hold the history? | the arm the field under-runs (EvoMemBench per intake); row 4's instrument |
| **E-2** | Lexical/statistical retrieval | cheap index, no semantics | bm25, tfidf_cosine, dense_lsa, hybrid_rrf |
| **E-3** | Dense/vector stores | embed, store, cosine back | mem0's store side; hindsight's base |
| **E-4** | Hierarchical/layered stores | layers, tiers, promotion paths | membukkit; Perseus vault T0/T1 tiering; letta core/archival blocks |
| **E-5** | Graph / temporal KG | entities + edges + time | Zep/Graphiti (stretch, charter #17); graphiti schema modules already in `src/memory_bakeoff/` |
| **E-6** | Agentic/procedural | memory operations by an agent loop (decide-what-to-remember) | a_mem, langmem, letta, memobase, memos |
| **E-7** | Conflict/supersession-first | what happens to the OLD truth | Perseus EXPLICIT_LINEAGE, hindsight STATE_TRANSITION, agentmemory PRODUCT_DECIDES (row 2's three mechanisms) |
| **E-8** | Session/compaction continuity | lossless session store + summaries across a conversation | pi-lcm + LCM variants |
| **E-9** | Native/built-in capture | the runtime's own remember/admission | pi native remember chain (measured inert — see S-04) |

**Cross-cutting axes** (every system gets a position on each, ledger-filled):

- **A. Write path:** who confirms capture — pipeline-internal / agent-confirmed / human-confirmed (our T0/T1 tiering is the only tiered answer we know of — VERIFY in ledger, we may be surprised).
- **B. Serve path:** how memory reaches the model — tool-call / auto-inject / prompt-transform / nothing (R2-lineage finding: serve path is where systems silently fail — F1 0/8 vs F2 8/8 vs f4 automation).
- **C. Conflict mechanism:** none / timestamps / explicit lineage / product-decides / state-transition (row 2: they are incommensurable — results diverge completely; the map does not sum them).
- **D. Delivery honesty:** does the system measure what the model actually RECEIVED (delivered-level) or what was stored/streamed? Field default: stored (our standing instrument rule 2 exists because of this).

## 3. Solution clusters — the charter systems, slotted

Slot ids S-nn follow the charter candidate table numbering (§3 there).
Evidence tags are TODAY's; the ledger corrects, this table yields.

| S-nn | System | Family | One-line mechanism | Tag today | Ledger slot |
|---|---|---|---|---|---|
| S-01 | pi-lcm (store reader) | E-8 | lossless per-project SQLite+FTS5, cross-session read tool | VERIFIED in-orbit (R2-lineage, 12/12 unit); P2-entry MEASURED: tool-level dynamic Hit@3 0.2227 (row 28 second-driven) | none — our own line (unit receipts only) |
| S-02 | pi-lcm tool variants | E-8 | within-conversation recovery tools vs raw store | VERIFIED within-conversation only; P2-entry A/B MEASURED: raw-without-relaxation 0.0 vs tool-level 0.2227 — the relaxation layer is worth +0.22 by itself (row 28 second-driven) | none — our own line |
| S-03 | Perseus vault | E-7 + E-4 | explicit lineage, tiered capture (T0/T1), delivered-level recall | VERIFIED: best conflict mechanism (48/48 row-2; Hit@3 0.434) — MEASURED-NEGATIVE: still <44% absolute | none — our own line |
| S-04 | native capture (pi remember) | E-9 | runtime remember + admission chain | MEASURED-NEGATIVE: demotes active→proposed, admission chain inert, CLI-write only activation path | none — our own line (probe receipts) |
| S-05 | mem0 | E-3 + E-6 | extract-and-embed memory operations | VERIFIED on benchmark (0.419); row-2 mechanism unclear/absent in pinned profile | supernode rows (2f/2h/2r) (+ P1 license) |
| S-06 | habitus | E-4 | working-memory + graph layers, dependency-free core | VERIFIED core5 (Useful>harmful 0.923 at lowest ctx chars — efficiency novelty); memconflict UNMEASURED | L-S06-01 (+ P1 license) |
| S-07 | agentmemory | E-7 | product-decides supersession at write | MEASURED-NEGATIVE: falsely retired 92.9% of stress memories; 12/48 row-2 | L-LME-01 (+ P1 license) |
| S-08 | hindsight | E-3 + E-7 | state-transition supersession | MEASURED-NEGATIVE: 0/48 row-2 — mechanism present, never asked, didn't work | independence audit + AMB rows (2l/2o) (+ P1 license) |
| S-09 | membukkit | E-4 | layered store | VERIFIED core5 (Hit@5 0.958 / MRR 0.525 — finds it, ranks it badly) | L-LME-02 (+ P1 license) |
| S-10 | claude_mem | E-8 | session summarizer memory | VERIFIED core5 only | none yet — license receipt only (P1) |
| S-11 | bm25 / tfidf / lsa / rrf | E-2 | lexical/LSA baselines | VERIFIED, frozen (bm25 = the anchor: 0.226 dynamic, 0.917+ Hit@5 static) | none — home-grown |
| S-12 | letta (MemGPT) | E-6 + E-4 |paged core/archival memory blocks | CLAIMED (upstream harness shipped, never run here) | L-S12-01..03 |
| S-13 | langmem | E-6 | LangChain memory SDK | CLAIMED | L-S13-01..02 |
| S-14 | a_mem | E-6 | agentic memory (paper system) | CLAIMED | L-S14-01..02 |
| S-15 | memobase | E-6 | user-profile extraction | CLAIMED | L-S15-01..03 |
| S-16 | memos (MemOS) | E-4 | "memory operating system" layering | CLAIMED | L-S16-01..03 |
| S-17 | Zep / Graphiti | E-5 | temporal knowledge graph | CLAIMED (vendor-published; charter parks it) | L-S17-01..02 |
| S-18 | long-context null | E-1 | history in window, no retrieval | RUN (P2 entry 2026-09-13: dynamic Hit@3 0.0 on n=2,631 — row 28 second-driven); chronologically-first units essentially never rank ≤3 | none — instrument (row 4) |
| S-19 | Chronos | E-3 | AMB top external row (0.956 LongMemEval); tracked for AMB provenance, not a charter candidate | LEDGER-PENDING (Alice check filed) | none yet |
| S-20 | SmartSearch | E-6 | AMB external-row source; de facto LongMemEval protocol documented | LEDGER-PENDING (Alice check filed) | none yet |
| S-21 | TiMem | E-6 | AMB external-row source (5 rows incl. the MemOS measurement) | LEDGER-PENDING (Alice check filed) | none yet |
| S-22 | Supermemory | E-6 | OmniMemEval-table entrant; largest self-vs-independent gap (95.0 self vs 66.07 reproduced), cited source dangling, judge provider-overridable (`ALICE-SUPERMEMORY-CLAIM-CHECK.md`) | LEDGER-PENDING | none yet |

**Cluster read (skeleton-level):** the field's center of gravity is E-6
(agentic capture) + E-3 (vector serve) with E-7 bolted on or absent; our own
line is the outlier — E-7/E-4 with delivered-level serve discipline, and the
only MEASURED-NEGATIVE column in the table. The ledger will tell us whether
the center of gravity has any verified conflict results at all.

## 4. Verified-vs-claimed landscape (the ledger fills this section)

**VERIFIED core (receipts cited; portable across the portfolio):**

1. Every engine measured co-returns the superseded record alongside the
   current one — 192/192, four cores (DECISION_MEMO row 1, CLOSED).
2. Supersession mechanisms are incommensurable: EXPLICIT_LINEAGE 48/48
   removes stale; STATE_TRANSITION 0/48; PRODUCT_DECIDES 12/48 (row 2,
   CLOSED). The map does not sum across them (axis C).
3. On memconflict's held-out slice: dynamic conflict is the discriminator —
   perseus 0.434, mem0 0.419, bm25 0.226; static conflict lands within
   seven points of bm25 (row 3, CLOSED, needs extension = this campaign).
4. Long-context baselines remain competitive; baselines surface stale
   evidence at prohibited@5 = 0.125 (`results/BASELINE_FINDINGS.md`).
5. Delivery, not storage, is where serve fails (F1 0/8 spontaneous → F2
   8/8 nudged → f4 automation; standing instrument rule 2).

**CLAIMED (ledger-pending — none of these may enter implications until the
ledger lands a receipt). [SUPERSEDED 2026-09-12: this skeleton list is
historical — the operative wording is the re-issued v2 list in addendum 2;
several items here were retired as never-vendor-claims.]:** letta's hierarchical blocks beat flat recall;
langmem's write-time extraction is production-viable; a_mem's agentic
curation beats passive stores; memobase's profiles survive drift; MemOS's
layering is a real OS-level abstraction; Zep/Graphiti's temporal KG wins on
temporal reasoning; habitus's efficiency holds outside core5; every ❓
license in charter §3.

**UNMEASURED everywhere we can see:** stale-use penalty (FAMA) applied to
anything (row 6's metric is BUILT, never applied — the field gap and our
opportunity are the same gap); tiered-capture burden vs auto-capture
burden; demand-side capture (re-derivation detection) — no system in the
table even claims it.

## 5. Gaps and interesting novelties (skeleton; ledger may fill/refute)

- **The stale-use penalty is the unclaimed hill.** Row 1 says every engine
  returns poison; row 6's metric scores what happens next; nobody in the
  table claims to have applied anything like it. Whoever scores delivery
  harm owns the only ranking that matters for trust.
- **Long-context null is the control the field skips** (EvoMemBench per
  intake) — and it is our cheapest arm.
- **Mechanism incommensurability (row 2) means "supersession support" is
  not one column** — three mechanisms, three incompatible semantics; any
  leaderboard that sums them is measuring marketing.
- **Serve-path honesty (axis D) may dominate architecture.** Our line's
  failures were delivery failures (admission inert, 0/8 look, receipt-vs-
  state); the R2 habit arm tests the serve side no benchmark touches.
- **Novelties from our own record worth mapping as claims-to-verify:**
  query relaxation as a delivery mechanism (f3, n=2 suggestive); tiered
  human/agent confirmation (T0/T1); blind-adjudication harness pattern
  (R2H/row-9); re-derivation detector (demand-side capture, RETRO-1 WILD —
  unowned anywhere).
- **Efficiency novelty:** habitus's Useful>harmful at the lowest context
  cost in core5 — if it holds on memconflict, "small and accurate" is a
  cluster the taxonomy under-names.

## 6. Implications for our own line

- **Perseus:** the verified best-in-class conflict mechanism that still
  loses 56%+ of dynamic conflicts — the lineage idea is exportable (and the
  portfolio should test lineage semantics as a removable module, not a
  product). Tiering (T0/T1) remains unclaimed by any other system.
- **pi-lcm:** its gap is serve-side and proven (admission inert, capture is
  the hole) — the ecosystem's E-8 cluster is strong on fidelity, silent on
  conflict; pi-lcm + Perseus lineage is the obvious hybrid the map exists
  to notice.
- **Trial design as export:** delivered-level counting, harm columns, blind
  adjudication, drop-by-name — our instrument rules are not in any external
  system's claims; exporting them to the portfolio is how the fleet's
  methodology becomes a result in itself.
- **The recursion:** a fleet of amnesiac workers is itself an E-8/E-9
  stress test with receipts (Cairn's canary findings). The map should keep
  a one-line pointer to it: we are a data point in our own taxonomy.

## 7. Convergence contract with Corvid's claims ledger

1. **Keys:** ledger rows cite this file's slot ids (S-nn, E-nn, axis A–D).
   The map never renumbers; new systems get the next S-nn by edit here
   first, ledger second.
2. **Direction of truth:** the ledger moves systems between tags
   (CLAIMED→VERIFIED, CLAIMED→MEASURED-NEGATIVE) with a receipt path per
   move; the map's cluster/implication sections update only on ledger
   moves, cited by ledger row id. No tag changes from this file's side.
3. **Claim text is verbatim:** the ledger stores the source's own words for
   CLAIMED rows (house rule: negatives preserved verbatim, claims too).
4. **Disputes:** a ledger row that contradicts a VERIFIED core fact (§4)
   goes to the BOARD as `re:` this file, not into the map — GiLMore
   adjudicates, then the map changes with a change-log line.
5. **Cadence:** map updates ride the ledger's updates; no scheduled
   rewriting. Skeleton sections stay marked SKELETON until first ledger
   landing.

## Change log

- 2026-09-12: skeleton (this entry). Slot ids S-01…S-18 allocated (charter
  §3 numbering reused); families E-1…E-9; axes A–D; evidence tags defined;
  §4 VERIFIED core cited, CLAIMED left deliberately empty of conclusions.
- 2026-09-12 (builder-claude, discovery): the seven §4 CLAIMED items now
  have ledger rows in `CLAIMS-LEDGER.md` § "Claims DISCOVERY". Rows are all
  `vendor-only`, and no tags are changed. Pointer table below; Corvid
  classifies next.
- 2026-09-12 ~17:28 (Stratum, fold): classification landed (Alice, row 17).
  No S-table tag moved; §4 CLAIMED re-issued v2 in addendum 2 below (four
  real vendor claims, three items retired as never-vendor-claims, license
  item closed green); six portfolio-shape flags filed in addendum 2; header
  status SKELETON → LIVE.
- 2026-09-12 ~17:55 (Stratum, second fold): rows 20/21 + builder provenance
  folded (addendum 2a) — Mem0 supernode named; habitus class settled
  controlled_core; L-LME-01/02 non-comparability receipted; MemOS
  self-conflict recorded; disclosure checklist adopted as the map's
  CLAIMED-row completeness rule. Still no tag moved.
- 2026-09-12 ~18:08 (Stratum, third fold): collision register folded
  (addendum 2b) — first ledger class amendment (L-S14-02 → vendor-only
  narrowed); Mem0 supernode and MemOS self-contradiction receipted at
  commit level; same-label collision evidence filed for the P3 checklist.
- 2026-09-12 ~18:14 (Stratum, fourth fold): Assay's second-driver
  re-derivation folded (addendum 2c) — S-07's 92.9% verified from raw rows,
  3/3 runs, independent of summary fields; denominator caveat
  (418/450 vs 418/418=1.0) bound to every future citation.
- 2026-09-12 ~18:22 (Stratum, fifth fold): Wayback pins + row-22 checker
  pass folded (addendum 2d) — all four blog sources pinned, "pin before
  citing" conditions satisfied; today's R&D batch second-seat checked 4/4;
  demo citation correction filed same turn.
- 2026-09-12 ~18:30 (Stratum, sixth fold): Habitus pointer AMENDED per
  Ledger's FIND (addendum 2e) — ambiguous path, not bad; 0.955 is our own
  repo receipt; upstream-README negative unchanged. Corvid's invalidated-
  pointer checker folded as the ready closure gate for the RESULTS.md
  defects (mismatch-class, 1 uncued per tree).
- 2026-09-12 ~18:42 (Stratum, qualifier fix): Corvid's LongMemEval qualifier
  census flagged discovery-table lines for MemOS 89.20 and Zep +18.5% —
  split/framework qualifiers added in place (no numbers touched); the map
  now passes the qualifier check.
- 2026-09-12 ~18:55 (Stratum, seventh fold): Alice's memobase raw-row
  re-derivation folded (addendum 2f) — 75.78/85.05 exactly reproduce from
  shipped fixtures (class: vendor-only, arithmetic recomputed);
  question-weighted-overall trap recorded as a P2 protocol note; Memobase's
  own Zep correction (75.14 vs copied 65.99) receipts the first supernode
  staleness casualty.
- 2026-09-12 ~19:07 (Stratum, integrity pass): S-table Ledger-slot column
  refreshed (18 rows; L-pending → actual row ids / none-yet) after the day's
  ledger landings; supersession marker added to the skeleton §4 CLAIMED
  list (operative wording = addendum 2 v2). Qualifier and change-log checks
  clean.
- 2026-09-12 ~19:20 (Stratum, eighth fold): Alice's MemBukkit check +
  Assay's S5 population-drift folded (addendum 2g) — L-LME-02 stays
  vendor-only (recipe published, run unshipped; repro ≈$9 > envelope);
  second null-side vendor agreement (full-context 60.2); Zep collision
  count to four; Corner 7 receipts at two.
- 2026-09-12 ~19:32 (Stratum, ninth fold): Mem0 supernode completed +
  S5 freeze tool folded (addendum 2h) — 92.5 headline untraceable to any
  shipped artifact (docs' own rows aggregate to 90.23/86.80); shipped
  91.56 exact; Corner 7 fix loop closed same-day.
- 2026-09-12 ~19:45 (Stratum, tenth fold): category collision resolved
  against the dataset (addendum 2i — labeling collision, new class; Memobase
  labels wrong; temporal the only safe pairing); Habitus 0.955 saga closed
  (do-not-cite-as-upstream; ours is our own repo receipt); Mem0 series
  triply disposed.
- 2026-09-12 ~19:58 (Stratum, eleventh fold): GiLMore's four-question ruling
  folded (addendum 2j) — MemBukkit repro declined (L-LME-02 permanently
  vendor-only unless re-ruled); Patch 4's off-peak table confirmed as the
  counter's price source (peak draft to be redone before applying).
- 2026-09-12 ~20:40 (Stratum, twelfth+thirteenth folds): addendum 2k pointer
  (vendor transparency register = operative evidence-status layer); addendum
  2l — Hindsight "independently reproduced" resolved to co-authorship
  (third-party stays empty; marketed 94.6 vs report 91.4), habitus
  provenance re-run corroborates frozen scores + receipts the class
  mislabel.
- 2026-09-12 ~20:49 (Stratum, fourteenth fold; time corrected same turn —
  had copied Assay's future-running header label): Gen38 anchor triple
  second-driver-verified (addendum 2m) — 0.434 / 0.419 / 0.226 reproduce
  from derived counts with rank arithmetic and pins exact; tags unchanged,
  weight upgraded.
- 2026-09-13 ~00:2x (Stratum, catch-up fold absorbed): slots S-19/S-20/S-21
  allocated (AMB-sourced vendors); THIRD-PARTY-ATTRIBUTED mirrored into §1;
  S-16's independent contradiction recorded via
  ECOSYSTEM-MAP-CATCHUP-2315.md (filed after a lane write-decline window
  23:15–00:1x). Formal S-16 class move remains Corvid/Alice's.
- 2026-09-13 ~14:08 (Stratum, S-table refresh): S-18 tag BUILT-not-run → RUN
  (P2 entry: dynamic 0.0, row-28 second-driven); S-01/S-02 gained their
  P2-entry measured numbers (0.2227 tool-level; 0.0 raw A/B). First S-table
  tag-relevant moves since the folds began — from our own entry run, not a
  vendor claim.
- 2026-09-13 ~09:35 (Stratum, custodian pass): **guard 15 (map hash guard)
  accepted** — this file's own guard-hash cells are now checked against the
  live scripts (born from a real map/receipt drift; Assay prototype, Corvid
  rev 3, Alice audits). The custodian runs it before each map pass. Also
  noted: the P2/P3 evidence gate card (14 guards, operational when/what/red)
  now exists to ride the P2-entry turn with the riding-set checklist; and
  the 2j envelope row's "ruled" wording amended to track the ruling state
  precisely (account-$25 settled; campaign-$5 → Patch 5 open).
- 2026-09-13 ~01:00 (Stratum): P2-entry state folded — MemConflict
  materialized (c30e8fa), eight checker guards green at the new HEAD, frozen
  indices 0-drift; my 91.4 qualifier gap fixed in place per Corvid's
  canonical-team census.
- 2026-09-12 ~20:55 (Stratum, fifteenth fold): 2l reframed by Alice's
  recompute (addendum 2n) — Hindsight marketed numbers reproduce exactly
  (version split, not fabrication); non-independence finding unchanged.
  Off-map: Assay second-drove the R2H freeze (6/6 hashes, schedule
  re-derived) before Brian's day 1.
- 2026-09-12 ~21:05 (Stratum, sixteenth fold): addendum 2o — Hindsight
  independence double-confirmed by two seats separately; AMB table receipted
  (2 measured + 23 paper-sourced, self-labeled unverified; higher rival
  omitted by marketing).

## §4 addendum — CLAIMED items, ledger pointers (discovery pass)

Append-only under §7: this table points at ledger rows. It changes no tag
and no conclusion.

| §4 CLAIMED item | Slot | Ledger rows | What the source actually says (short) | Discovery flag |
|---|---|---|---|---|
| letta's hierarchical blocks beat flat recall | S-12 | L-S12-01..03 | MemGPT paper: tiered virtual context, no flat-recall number. Letta blog: flat **filesystem** agent 74.0% LoCoMo | wording stronger than source |
| langmem's write-time extraction is production-viable | S-13 | L-S13-01..02 | vendor gives no numbers; competitors report 58.10 LoCoMo judge, p95 ≈60 s | no vendor source |
| a_mem's agentic curation beats passive stores | S-14 | L-S14-01..02 | "superior improvement against existing SOTA baselines", six models (NeurIPS 2025) | wording stronger than source; numbers unsourced |
| memobase's profiles survive drift | S-15 | L-S15-01..03 | vendor claims 75.78 LoCoMo judge and <100 ms online; no drift claim found | no source → UNMEASURED candidate |
| MemOS's layering is a real OS-level abstraction | S-16 | L-S16-01..03 | MemCube with provenance/versioning; README LoCoMo 88.83 / LongMemEval 89.20 (own OmniMemEval framework; split unspecified) | metric unknown; comparative % unsourced |
| Zep/Graphiti's temporal KG wins on temporal reasoning | S-17 | L-S17-01..02 | DMR 94.8 vs 93.4; LongMemEval up to +18.5% accuracy, −90% latency (split unspecified) | parked; competitor table has Zep temporal 49.31 |
| habitus's efficiency holds outside core5 | S-06 | L-S06-01 | README is qualitative only ("zero-external-runtime-dependency", "Zero Eviction") | our hypothesis, not a vendor claim |

— Stratum. Skeleton built from receipts I already hold (cited inline);
everything else waits for the ledger, which is the point. Corvid: the keys
are yours to fill — S-nn/E-nn/axis — and §4 is where your rows land.

---

## §4 addendum 2 — CLASSIFICATION FOLD (ledger classification landed; row 17)

**When/who:** 2026-09-12 ~17:28 PDT, Stratum (map owner), on GiLMore's
synthesis dispatch. **What landed:** `CLAIMS-LEDGER.md` §CLASSIFICATION
(Alice, QUEUE row 17) over §"Claims DISCOVERY" (builder-claude) — the seven
§4 CLAIMED items now carry verification classes, attribution receipts
(`team/row17-claims-fetches/MANIFEST.md`), and per-row dispositions.
**Contract compliance (§7):** no S-table tag moved (nothing crossed
CLAIMED→VERIFIED/MEASURED-NEGATIVE; `vendor-only` ≡ CLAIMED with an
attribution receipt attached). §4's CLAIMED list is re-issued below because
the ledger directed exactly that ("the map owner should reword to match the
sources" — L-S12-01, L-S16-01 notes; L-S06-01 note). Zero `contradicted`
rows → no §7-contract-4 dispute exists; §4's VERIFIED core stands untouched.

### The fold, per slot

| Slot | System | Ledger rows | Class now | What the vendor actually says (short) | Disposition in map |
|---|---|---|---|---|---|
| S-12 | letta | L-S12-01..03 | vendor-only ×3 | Tiered "virtual context management" (paper v2, **no head-to-head number**); vendor blog: **flat filesystem agent 74.0% LoCoMo**; disputes Mem0's MemGPT-on-LoCoMo run | CLAIMED (reworded — old wording was ours, not theirs); blog unpinned |
| S-13 | langmem | L-S13-01..02 | vendor-only; competitor-published | Capability phrases only; **no vendor number exists**. The 58.10 is Mem0's paper number copied into Memobase's table — one origin | §4 "production-viable" retracted as our wording; slot is CLAIMED-capability/UNMEASURED-numeric |
| S-14 | a_mem | L-S14-01..02 | vendor-only; one **unsourced** | "Superior improvement against SOTA baselines", six models (paper v11, verbatim). Six-fold/85–93% figures: no primary located | CLAIMED (reworded to the abstract's sentence); unsourced row not citable |
| S-15 | memobase | L-S15-01..03 | vendor-only; drift item **no-claim** | 75.78 LoCoMo judge (v0.0.37) is its own run; **all rival rows pasted from Mem0's paper**; temporal 85.05 outlier; drift claim: none found | §4 "profiles survive drift" → **UNMEASURED** (was never claimed) |
| S-16 | memos | L-S16-01..03 | vendor-only; one **unsourced** | MemCube provenance/versioning (paper v4, verbatim — nearest thing to E-7 in the batch); README numbers use its own OmniMemEval, judge/metric absent | CLAIMED (architectural only); 88.83 uncomparable until metric known |
| S-17 | Zep/Graphiti | L-S17-01..02 | vendor-only | DMR 94.8 vs 93.4 (1.4 pts); "up to +18.5%, −90% latency" with unspecified baselines; abstract says cross-session synthesis, **not "temporal reasoning" by name** | CLAIMED (reworded); park unchanged |
| S-06 | habitus | L-S06-01 | **verified-by-us (negative)** | Pinned README (sha `8449b7e7…`, 173 lines) contains **no numeric claim** — §4 "efficiency holds" was our hypothesis, not a vendor claim | Moves out of §4 CLAIMED → UNMEASURED/novelty (our hypothesis, our run to make) |

### §4 CLAIMED list, re-issued (v2 — supersedes the skeleton list, per ledger)

Real vendor claims, corrected wording, citable as CLAIMED with row ids:
1. **letta (S-12):** tiered virtual context management exists as architecture; the vendor's own headline run is a *flat* filesystem agent at 74.0% LoCoMo (L-S12-01, L-S12-02).
2. **a_mem (S-14):** "superior improvement against existing SOTA baselines" across six foundation models (L-S14-01).
3. **memos (S-16):** memory-as-OS-resource with MemCube provenance/versioning (L-S16-01).
4. **Zep (S-17):** DMR 94.8% vs 93.4%; "up to +18.5% accuracy, −90% latency" vs unspecified baselines (L-S17-01/02).

Retired from CLAIMED (they never were vendor claims): langmem "production-viable" (no vendor number, L-S13-01), memobase "profiles survive drift" (no-claim → UNMEASURED, L-S15-03), habitus "efficiency holds outside core5" (our hypothesis, L-S06-01). Also closed: "every ❓ license in charter §3" — resolved green by row 15's five pinned-blob receipts plus row 11's four engine receipts. **The license dimension of this map has no open items.**

### Portfolio-shape flags (the actual point of this fold)

1. **For these seven systems, we are the only evidence that will exist.**
   0/16 substantive claims verified, 0 third-party, and both apparent
   cross-confirmations dissolved to single origins (58.10 = one eval, two
   pages; Memobase's rival rows = Mem0's paper, pasted — flags 1–2 of row
   17). P2 triage should therefore rank upstream harnesses by *reproduction
   value*, not vendor signal. **Memobase's temporal 85.05** (27-point
   outlier, the only row in its table it actually ran) is the single
   highest-value bounded reproduction target in the batch.
2. **The null gains a vendor concession.** Letta's own blog reports a flat
   filesystem agent beating its tiering story (74.0% LoCoMo, vendor-only,
   unpinned). BAR A ("does anything beat the long-context null") already
   locked the null as control; the P4 report may now cite the field's own
   data point on the null's side — pinned before citing.
3. **Zep: no independent number exists anywhere in our record.** Both
   headlines are vendor-only with unspecified baselines; every third-hand
   Zep figure traces to Mem0's paper. The G0 park stands, now with a better
   reason: re-opening requires an independent reproduction, not a citation.
4. **Habitus survey pointer is bad (owner: Corvid, his file).**
   `RESEARCH-4-ENGINES-SURVEY.md` cites `README.md:134-139` for "22
   non-as-of positives Hit@5 0.955"; the pinned README has no such number
   and points benchmarks to `DEVELOPMENT.md`. Same defect class as the
   three RESULTS.md mislinks — a pointer fix, not a retraction; habitus's
   local receipts and cleared license stand.
5. **Upstream-number citation rule for P3/P4 (owner: Verity's rule pass; my
   caveat-travel duty).** Mem0's LoCoMo reads 66.88 (paper) / 68.5%
   (Letta-cited) / 92.5% (live blog) across mutable pages, and its
   MemGPT-on-LoCoMo run is formally disputed by Letta (L-S12-03) — never
   cite it as a Letta number. Rule: an upstream benchmark number is cited
   only with source + date + pin, or not at all.
6. **Cluster read, updated on ledger evidence:** the skeleton asked whether
   the E-6/E-3 center of gravity has any verified conflict results. Answer:
   **it has none.** The agentic cluster (E-6) produced the weakest claim set
   in the batch — no numbers, a no-source drift claim, unsourced
   multipliers — while the batch's two strongest leads are a null-side
   result (flag 2) and a single bounded outlier (flag 1). §4's VERIFIED
   core remains the only verified set in the record, and it is ours.

---

## §4 addendum 2a — SECOND FOLD: rows 20/21 + builder provenance (17:5x)

**When/who:** 2026-09-12 ~17:55 PDT, Stratum, R&D pulse item 1. **What
landed since addendum 2:** `CLAIMS-LEDGER.md` — Alice's provenance chase
(row 20: "ten origins, not twelve"), Corvid's LongMemEval-S audit (rows
L-LME-01/02) and Habitus class settlement, and the builder provenance
update (17:41). **Contract:** still no S-table tag moved ("nothing promoted
off `vendor-only`"); the fold records provenance and interpretive frame.
Corvid's new disclosure checklist (split + metric + reader + judge + encoder
+ backend + top-k + context size, or the row is marked incomplete) is
adopted here as the completeness rule for any future CLAIMED row in this
map.

| Slot | New ledger fact | Effect on the map |
|---|---|---|
| S-05 mem0 | The Mem0 paper is the **single origin behind four "independent" vendor numbers** (58.10 and the rival halves of Memobase's table) | Flag 1 of addendum 2 gets its name: **the Mem0 supernode**. More copies add no evidence; only a local reproduction would |
| S-06 habitus | Experiment class **settled: `controlled_core`** — upstream's own docstring calls the evaluated embedder a test/demo stand-in; written evidence pages were correct; the adapter default is the defect (fix owner: implementer/build) | S-06 receipts stand, now with an honest frame: our habitus numbers measure a controlled-core configuration, not a product. The survey's gap item (1) is closed |
| S-07 / S-09 | L-LME-01 vs L-LME-02: agentmemory's 95.2 is **retrieval recall, no judge** (and it explicitly disclaims the QA reading); MemBukkit's 92.6 is **judged answer accuracy** — different metrics, **not comparable** | Upstream headline non-comparability is now receipt-backed. Reinforces shape flag 1: reproduction value, not vendor signal, orders P2 |
| S-14 a_mem | L-S14-02 traced (builder): "six-fold" = Multi-Hop, one model, **ROUGE-L** 27.23 vs 4.68 (word-overlap, not accuracy); "85–93%" is aggregator arithmetic from the token sentence | Even the sourced E-6 number is narrower than repeated. Sharpens flag 6; class stays `unsourced` until Alice/Corvid move it |
| S-16 memos | L-S16-02 sharpened (Alice): 88.83 is **not in any paper version** and conflicts with the vendor's own text (92.34); L-S16-03's first appearance is an **author-side HF comment** (name-match only, not paper text) | MemOS numbers remain uncitable for any comparison until OmniMemEval's metric is resolved |
| cluster read | Provenance-proven: **ten origins, not twelve**; one supernode (Mem0) + one self-conflicting vendor (MemOS) | No family restructure needed — E-6's evidence vacuum is now measured, not asserted |

**Re-cluster check:** no drift in the family table; taxonomy stable. The
skeleton's question is answered more strongly than addendum 2 stated it —
the E-6/E-3 center of gravity now has **provenance-level** evidence of
having no independent conflict results.

---

## §4 addendum 2b — THIRD FOLD: collision register class moves (18:0x)

**When/who:** 2026-09-12 ~18:08 PDT, Stratum, R&D pulse. **What landed:**
`ALICE-LEDGER-COLLISION-REGISTER.md` (Alice, RD-THREADS thread 3) — the
ledger's first class amendments plus duplicate/collision registers.
**Contract:** this fold is made *on* a ledger move (§7.2): L-S14-02 changed
class. Still no S-table tag moved — `vendor-only (narrowed)` ≡ CLAIMED.

| Slot | Ledger move / register fact | Effect on the map |
|---|---|---|
| S-14 a_mem | **L-S14-02: `unsourced` → `vendor-only (narrowed)`** (+ `derived-not-stated` on the %): "six-fold" is one model, one category, ROUGE-L 27.23 vs 4.68; "85–93%" is aggregator arithmetic. Amended ledger counts: 13 `vendor-only` · 1 `verified-by-us` · 1 `unsourced` · 1 `no-claim` | §4 re-issued v2's a_mem entry can now cite the narrowed number as a real vendor claim — with its scope attached. The E-6 pattern holds: even the *sourced* numbers shrink on inspection |
| S-05 mem0 | **D1:** the whole rival half of Memobase's table = L-S13-02 = one Mem0-paper measurement; count it **once**. D2: Letta's "68.5%" is `unresolved-attribution` (paper says 68.44) | The Mem0 supernode is now register-receipted, not just asserted: four-to-five ecosystem numbers, one origin |
| S-16 memos | **The ledger's one true self-contradiction:** LoCoMo 88.83 (table) vs 92.34 (prose) in the same file at the same commit `40f8e832` — silently edited in a later README | S-16's "uncitable until metric known" is now receipted at commit level; a vendor that silently edits its own benchmark prose is scored in the map's axis D (delivery honesty), not just flagged |
| cross-slot | **"LongMemEval" has five referents, one name** (recall@K / judged QA / unknown / relative delta / survey slogan); "LoCoMo" has seven numbers with no shared protocol | Corner 6 of `DESIGN-CORNERS-1.md` (disclosure checklist in the P3 spec) is no longer a proposal from analogy — it is the map's own registered evidence that the label carries no protocol |

---

## §4 addendum 2c — FOURTH FOLD: S-07's anchor number gets a second driver (18:1x)

**When/who:** 2026-09-12 ~18:14 PDT, Stratum, R&D pulse. **What landed:**
`ASSAY-SECOND-DRIVER-AGENTMEMORY-418.md` — Assay re-derived 418/450 from the
raw lifecycle rows (native id → canonical id → source observations, corpus
builder as the authority), all three runs byte-agreeing, **without using the
summary's `false_supersession_count` or rate fields. Verdict: AGREE —
92.89% ≈ the cited 92.9%; every core record survives; all 418 losses are
distractors.**

**Effect on the map:** S-07's MEASURED-NEGATIVE — the single most
load-bearing negative in the portfolio (it is charter Patch 2's scored
dimension) — moves from single-receipt to **second-driver-verified**. No tag
change; the tag was already right. Two things travel with the number from
now on, per caveat-travel duty:

1. **The denominator is part of the number:** 92.9% = 418 / **450 stress
   distractors**. The same lifecycle file also carries
   `false_supersession_rate_of_retired = 1.0` (= 418/418) — a different,
   also-true quantity. Side by side they read as a contradiction; any table
   that prints one must print the denominator (P3/P4 table builders: this
   means you).
2. **Limits:** the re-derivation covers the *stored* lifecycle counts of the
   controlled-lifecycle arm; the product/service path remains unrun (the
   separate arm with the service-health preflight).

---

## §4 addendum 2d — FIFTH FOLD: the pins close; the loop closes (18:2x)

**When/who:** 2026-09-12 ~18:22 PDT, Stratum, R&D pulse. **What landed:**
`ALICE-MUTABLE-SOURCE-PINS.md` + `team/row-pin-receipts/` (4 Wayback
snapshots, sha256, all cited strings present in snapshot bytes), and QUEUE
row 22 — Alice's second-seat check of today's R&D batch: **4/4 PASS**,
including this seat's SPRINT-1-DEMO (14/14 cited paths exist; one citation
omission found — S3's 11/8 figure lives in `ROW9-BLIND-HARNESS.md` —
corrected in the demo the same turn).

| Fold item | Effect on the map |
|---|---|
| All four mutable blog sources now pinned (Letta snapshot 1 day after publication; Zep same-day; Mem0 +1 mo; LangChain +15 mo) | Addendum 2's "pin before citing" conditions are **satisfied**: S-12's 74.0% flat-files claim and S-17's vendor-copy numbers are citable as CLAIMED with frozen bytes. The last open provenance gap from row 17 is closed |
| Mem0 snapshot arrived gzip-encoded; the first grep falsely read "claims absent" | Recorded as the newest member of the house collection: *an instrument's first pull can lie about absence* — same class as the S6 v1 false-fire and the scrubber's compact-date miss. Raw bytes + hash travel, or the negative didn't happen |
| Row 22 = today's R&D batch is second-seat checked (Corvid probe, Assay B7 + second-driver, Stratum demo) | The rule-1 gap the scoreboard flagged at 17:45 is closed for this batch. The demo is the first artifact through the full loop — written → cold-read → second-seat checked → correction filed — which is the whole governance stack working on one document |

---

## §4 addendum 2g — EIGHTH FOLD: membukkit's recipe vs its missing run; a second null-side agreement (saved 19:18 per mtime)

**When/who:** 2026-09-12 ~19:20 PDT, Stratum, R&D pulse. **What landed:**
`ALICE-MEMBUKKIT-926-CHECK.md` (+ `team/row-membukkit-receipts/`) and
`ASSAY-SECOND-DRIVER-S5-SAMPLE.md`.

| Slot | Fact | Effect on the map |
|---|---|---|
| S-09 membukkit | 92.6% is stated **consistently** (8 mentions, one setup: reader gpt-5.4, official gpt-4o judge, embedder, named config, repro command, ±3 band) — the best recipe in the batch — **but the run is not shipped**: `results/bench/longmemeval-*` absent at the pin. L-LME-02 stays `vendor-only`; the docs' own repro estimate (~60M input tokens + metered judge) prices at **≈$9 on deepseek off-peak — over the whole campaign envelope** (Patch 4 line) | Moving L-LME-02 is **not envelope-compatible**; it would need its own Brian ruling or rides as "recipe published, result self-attested." Best citation until then: `vendor-only (full recipe, run unshipped)` |
| cross-slot (E-1) | MemBukkit's candid judge table — where full-context reads **60.2 under the official judge** — matches the Zep paper's gpt-4o full-context score exactly (row 20). Two unrelated vendors agree on the null | **Second null-side data point** (after letta's flat-files, addendum 2). BAR A's control now has two independent vendor-side confirmations that the unwindowed baseline is a real competitor. Strengthening shape flag 2 |
| S-17 Zep | Zep now has **four published benchmark numbers, none comparable** (own paper: DMR-style margin and a relative gain; Mem0-paper copies; MemBukkit-table row — splits unspecified throughout) | The collision register's Zep row was an understatement; park reason unchanged and tripled |
| campaign plane | Assay's S5 second-driver: headline byte-identical on re-run, but **population drifts** — `--window-end` bounds turn *start*, not completion, so late-completing turns enter the bounded set (classes moved 3/1→4/1 at n=1); RUN-RECEIPT's "reproducible" claim needs the population frozen before close | Corner 7 (population honesty) now has **two live receipts** (Cairn's diet artifact, Assay's drift). The S5 close must freeze inputs — pinned copies or per-file sha256 — before any number is cited |

---

## §4 addendum 2h — NINTH FOLD: the Mem0 supernode is complete; the freeze tool exists (19:3x)

**When/who:** 2026-09-12 ~19:32 PDT, Stratum, R&D pulse. **What landed:**
`ALICE-REDERIVE-MEM0-LOCOMO.md` (+ `team/row-mem0-locomo-receipts/`) and
`ASSAY-S5-FREEZE-INPUTS.md`.

| Slot | Fact | Effect on the map |
|---|---|---|
| S-05 mem0 | The **shipped** top_200 run reproduces exactly (1410/1540 = 91.5584%; top_50 = 82.6623%, both gpt-5 answerer + judge). But the **current documented headline 92.5 traces to no shipped artifact** — the docs' own category rows aggregate to 90.23 weighted / 86.80 unweighted, neither 92.5 | **The Mem0 supernode is now complete:** all five rival numbers (single-origin, one stale), mem0's own series (drift 66.88→92.5), and now the headline-vs-artifact gap — every number in the block has a provenance disposition. The citation rule (source + date + pin, addendum 2f) has its second demonstrated failure case: a live vendor headline that outlives its own raw data |
| campaign plane | Assay shipped `s5_freeze_inputs.py` same-day: snapshots the live session tree + per-file sha256 manifest, refuses overwrite, positive control verified | Corner 7's loop is closed end-to-end inside one day: drift found (2g) → freeze mechanism built → verified. The S5 close can now cite frozen inputs |

---

## §4 addendum 2i — TENTH FOLD: the category collision is resolved against the dataset; the 0.955 saga ends (19:4x)

**When/who:** 2026-09-12 ~19:45 PDT, Stratum, R&D pulse. **What landed:**
`ALICE-LOCOMO-CATEGORY-MAP.md` (+ `team/row-locomo-map-receipts/`, LoCoMo
paper + dataset fetched), the survey's pointer-correction addendum, and
Corvid/Kiln closure receipts.

| Slot | Fact | Effect on the map |
|---|---|---|
| cross-slot (collision class) | **LoCoMo category-id collision RESOLVED against the dataset** (Alice): same question sets, permuted labels — memobase calls id 1 (282q) `single_hop` while the Mem0 harness calls it `multi-hop`; id 3 (96q) and id 4 (841q) likewise swapped; only temporal (id 2, 321q) agrees. A new collision class, distinct from duplicate and contradicted: **a labeling collision that corrupts cross-vendor comparison while every number is "true"** | Upgrades addendum 2b's "LoCoMo: seven numbers, no shared protocol" with the per-category layer — and the map now exists, checked against the dataset (Memobase's labels are the wrong ones). Only "Memobase temporal 85.05 vs Mem0 temporal 92.83" is a safe cross-vendor pairing; the P3 report pins this map before any per-category table |
| S-06 habitus | The 0.955 saga ends one step further than addendum 2e recorded: at the pin, **neither README nor DEVELOPMENT.md contains it** (DEVELOPMENT.md reports only LLM-free diagnostic trials). Survey correction filed: "Do not cite 0.955" as an upstream-adjacent number; the verifiable Habitus numbers are our own core5/stress receipts | The number Ledger found lives in **our** repo README describing **our** run — so the final disposition: 0.955 is our receipt, never an upstream claim. Class settlement (`controlled_core`) and the artifact half of gap 5 (24,169 IDs canonical across 102 frozen dirs) are confirmed in the survey's own addendum |
| S-05 mem0 | Mem0's LoCoMo series is **triply** disposed: paper 66.88 (two algorithms and two judges old) → shipped current run 91.56 (exact) → docs headline 92.5 (untraceable) | Shape flag 1's citation rule now has a fully worked example — one vendor, three values, one lineage; cite the pin or cite nothing |

**2i postscript (same day, ~20:15):** Alice's completed map gives the
corrected Memobase row assignment — the numbers belong to different names
than the vendor printed: corrected row = single-hop **77.17**, multi-hop
**70.92**, temporal **85.05**, open-domain **46.88** (overall 75.78
unchanged; temporal was always safe). New citing rule for pre-2026 LoCoMo
per-category numbers: **by category number, or not at all** — overall and
temporal columns remain safe. P3's per-category tables pin the map before
shipping.

---

## §4 addendum 2j — ELEVENTH FOLD: the ≈$9 question is ruled; the prices are confirmed (19:5x)

**When/who:** 2026-09-12 ~19:58 PDT, Stratum, R&D pulse. **What landed:**
GiLMore's ruling on the four open questions (relayed via the 19:50 scoreboard
refresh).

| Slot | Ruling | Effect on the map |
|---|---|---|
| S-09 membukkit | **MemBukkit reproduction (~$9): DECLINED.** 92.6% stays a vendor-only claim | Addendum 2g's open question ("needs its own ruling") is closed: L-LME-02's upgrade path is declined, not deferred. Standing citation: `vendor-only (full recipe, run unshipped; repro declined)`. If the number ever matters beyond this campaign, the recipe is published and the band (±3) is the vendor's own — but that is a fresh ruling, not an inference |
| envelope | **Counter prices confirmed = Patch 4's table** (off-peak; peak surcharges recorded separately if they occur). The builder's drafted pricing config used peak rates and must be redone at off-peak before applying | Patch 4 is now the single confirmed price source for the P2-entry arithmetic line; no discrepancy between the relay and the patch. Cap mechanics: reserve-on-claim per the lane-counter design; `meters.py --check` is the stop until built |
| envelope (2026-09-13 04:4x ruling; state tracked) | **Account budget ruled: the paid account counts against a $25 campaign envelope** (real spend ≈$7.51–7.53 pre-top-up; the "$3.84 = 15%" figure first recorded here was an OpenRouter Muse-note reading, not fleet total — corrected per fsync's find, 12:4x); the earlier "77% of $5" was also a wrong measure | Reconciliation for the record: Patch 4's **≤$5 line governs the portfolio campaign's own metered run matrix**; the **$25 envelope governs the fleet account** the live lanes spend against. Two budgets, two scopes. **State (09-13 09:3x):** the account-$25 ruling is settled; whether the campaign line stays at $5 or moves is **open as a proposed Patch 5** — Ledger correctly flags this row's "ruled" wording as covering only the account half |
| envelope caution (12:1x; quantified 12:2x) | **The fleet spend meter is currently unreliable**: after a ~$20 DeepSeek top-up, `budget()`'s max(0,·) clamp forgot $7.51 of real spend (meter reads $0.02; actual ≈$7.53) and will hide the next ~$12.48 (builder 12:07; Assay defect reproduced, fix validated — not applied, budget rule is Brian/GiLMore's) | **Stakes quantified (Ledger-verified):** current code refuses at ~$45.10 real spend; the fix refuses at $25.10. The forgotten $7.51 needs a one-time add-back or an accepted loss. Until applied, the P2-entry arithmetic line's "current spend" term is UNRELIABLE — envelope tracking paused, not passing. Same Corner 8 class: an instrument that cannot say what it saw must say so |





---

## §4 addendum 2e — SIXTH FOLD: Habitus pointer amended (ambiguity, not badness) (18:3x)

**When/who:** 2026-09-12 ~18:30 PDT, Stratum, R&D pulse. **Trigger:** Ledger's
board FIND (17:4x) correcting my own addendum 2. **What it amends:** addendum
2's S-06 row and shape flag 4 said the four-engine survey's Habitus pointer
(`README.md:134-139`, Hit@5 0.955) was **bad**. It was **ambiguous**: the
line resolves in **our** repo README (`implementer/repo/README.md:136`, same
line in repo-glm-dsh2/dsh3), not Habitus's upstream README — the survey
wrote a bare `README.md` with no repo prefix. Fix = prefix it. The notes
that called it bad (row 17's flag 4, my flag 4, Ledger's earlier tick) want
this amendment, not a retraction.

**What survives untouched:** the `verified-by-us (negative)` on L-S06-01
stands exactly as scoped — the pinned **upstream** README makes no numeric
claim. What changes is the story around the 0.955: it is **our own
receipt** (22 positive non-as-of cases, our README), which is *better* than
the survey's framing implied — a number we can actually re-run, not a
vendor slogan. Habitus keeps the map's sharpest upstream-vs-ours contrast:
upstream claims nothing; our README claims 0.955 on 22 cases; neither is
the vendor's.

**Also folded (board, Corvid 18:02/18:24):** the invalidated-evidence-pointer
checker exists (`scripts/check_invalidated_pointers.py`, self-test PASS,
exits 1 until fixed — a ready closure gate). All three trees: exactly **1**
uncued invalidated pointer each (`RESULTS.md:85` → the Gen4 Hindsight run),
0 dangling links — the RESULTS.md defects are *mismatch-class*, not
dead-link-class, which confirms they were citation errors, not missing
artifacts.

---

## §4 addendum 2f — SEVENTH FOLD: memobase reproduces exactly; the supernode's first casualty (18:5x)

**When/who:** 2026-09-12 ~18:55 PDT, Stratum, R&D pulse. **What landed:**
`ALICE-REDERIVE-MEMOBASE-7578.md` + `team/row-memobase-receipts/` —
second-driver re-derivation of Memobase's headline from the vendor's own
shipped per-question judge fixtures (1,540 rows, both versions, pure Python).

| Slot | Fact | Effect on the map |
|---|---|---|
| S-15 memobase | **75.78 / 70.91 reproduce exactly (4 decimals) from the shipped raw rows** — every category, both versions, counts included. Class amended by Alice: `vendor-only` → `vendor-only (arithmetic recomputed from shipped raw rows)` — still not `verified-by-us` (nothing re-measured; judge + predicted answers taken as shipped) | Addendum 2 flag 1 named temporal **85.05** the top bounded reproduction target: it is now offline-verified as internally exact, so a P2 reproduction that misses it is looking at method/judge, not arithmetic. **Protocol note for that reproduction:** the vendor's "overall" is question-weighted (open_domain = 54.6% of 1,540); the unweighted category mean is 70.00, not 75.78 — compute it their way or report both, or the reproduction spuriously "fails" |
| S-17 Zep | Memobase's own README later corrected the Mem0-pasted Zep row to **Zep* 75.14** (after Zep disputed it, upstream issue #101) vs the copied 65.99/49.31 | First concrete evidence that a supernode number is **wrong, not just borrowed** — the Mem0 paper's rival block is stale. Zep's park reason (addendum 2, flag 3) strengthens again: no independent number exists, and the copied ones move |
| S-05 mem0 (supernode) | Supernode accounting after today: of the five rival numbers in Mem0's Table 2 block, **one (Zep 65.99) is shown stale by the borrower itself**; four (langmem 58.10, openai 52.90, mem0 66.88/68.44) still have exactly one measurement behind them | The "count it once" rule (addendum 2b, D1) plus this: borrowed numbers inherit the origin's staleness. Citation rule (source + date + pin) now has a demonstrated failure case |

---

## Addendum index — cold-reader navigation (appended ~20:09, after ten addenda in one day)

Reading order for the §4 fold series: **addendum 2's re-issued v2 CLAIMED
list is the operative wording**; the skeleton §4 list and the discovery
addendum are historical; each later addendum supersedes earlier ones where
they touch the same slot. The S-table's tags and Ledger-slot column are
current as of the ~19:07 integrity pass.

| Section | Date | One-line takeaway |
|---|---|---|
| §4 addendum (discovery) | 09-12 | builder's 16-source discovery table; historical wording |
| §4 addendum 2 | 09-12 ~17:28 | classification fold; **v2 CLAIMED list (operative)**; six shape flags |
| §4 addendum 2a | 09-12 ~17:55 | Mem0 supernode named; habitus class settled; L-LME non-comparability |
| §4 addendum 2b | 09-12 ~18:08 | collision register folded; L-S14-02 class move (first ledger move) |
| §4 addendum 2c | 09-12 ~18:14 | S-07's 92.9% second-driver-verified; denominator caveat bound |
| §4 addendum 2d | 09-12 ~18:22 | Wayback pins close the provenance gaps; row-22 loop closes on my demo |
| §4 addendum 2e | 09-12 ~18:30 | Habitus pointer amended: ambiguous, not bad (supersedes flag 4) |
| §4 addendum 2f | 09-12 ~18:55 | memobase reproduces exactly from raw rows; Zep-copy staleness found |
| §4 addendum 2g | 09-12 ~19:18 | membukkit recipe published, run unshipped; second null-side agreement |
| §4 addendum 2h | 09-12 ~19:32 | Mem0 supernode complete (92.5 untraceable); S5 freeze tool landed |
| §4 addendum 2i | 09-12 ~19:45 | LoCoMo category collision resolved vs dataset; 0.955 saga closed |
| §4 addendum 2j | 09-12 ~19:58 | MemBukkit repro declined by ruling; Patch 4 prices confirmed |
| §4 addendum 2k (pointer) | 09-12 ~20:28 | transparency register = operative evidence-status layer |
| §4 addendum 2l | 09-12 ~20:40 | Hindsight co-authorship; habitus provenance corroborated |
| §4 addendum 2m | 09-12 ~20:49 | Gen38 anchor triple second-driver-verified |
| §4 addendum 2n | 09-12 ~20:55 | Hindsight marketed numbers reproduce (version split) |
| §4 addendum 2o | 09-12 ~21:05 | independence double-confirmed; AMB table 2+23 |
| §4 addendum 2p + S-19..S-21 | 09-13 ~00:2x | catch-up fold absorbed (see ECOSYSTEM-MAP-CATCHUP-2315.md); MemOS independently contradicted; third-party-attributed class mirrored |
| §4 addendum 2q | 09-13 ~00:45 | MemOS merge passed second seat; Supermemory slotted S-22 |
| §4 addendum 2r | 09-13 04:21 | overnight catch-up: Letta harness found; ledger pins self-contradiction (owner Corvid); time-label checker instrumented; Verity down |
| §4 addendum 2s | 09-13 ~21:4x | leakage@k contract ADOPTED+APPLIED+SIGNED (supersedes update 3d's "proposal reviewable"); goal-5 harvest complete (cards 3–4: STALE/Supersede, MemSecBench/GateMem); P2 gate card second-checked AND exec-checked (Rev 4) |
| S-22 Supermemory | 09-13 ~00:45 | slotted: largest self-vs-independent gap (95.0 vs 66.07), dangling source |
| External corpora research | 09-13 (key claims VERIFIED) | Brian-commissioned Deep Research report (`RESEARCH-EXTERNAL-CORPORA-20260913.md`): agent-only trajectories abundant, real human↔agent histories scarce; SWE-chat (5,851 sessions) the standout, gated on Brian's HF account. Verification complete (`ALICE-EXTERNAL-CORPORA-FULLPASS.md`): the remaining numeric claims confirmed from primary sources |
| External corpora recommendation | 09-13 (**FINAL**; amendments applied) | `EXTERNAL-CORPORA-RECOMMENDATION.md` — the team's own position, scoring sources against frozen goals G1–G5 (conflict, supersession, invocation, outcome, continuity) instead of the report's rankings; report = candidate-discovery input only. **All of Alice's amendments applied** (incl. retracting the wrong SWE-chat label claim); most report counts verified, only Open-SWE-Traces wrong. Brian's two asks: accept the SWE-chat HF gate on the team account, and read the transcript-miner pilot |
| Own-corpus supply | 09-13 (`TRANSCRIPT-MINING-FULL.md`) | Brian approved the scale-up (closed-sessions rule, 60-min freshness exclusion): **1,250 closed files, 5,152 operator turns, all local, $0, no model in the loop**. The synthesis: the report called real human↔agent histories the *scarce* corpus class — the fleet's own record is producing exactly that without any gated external source. **Second-driven** (Alice): every headline number reproduces from the local JSONL outputs; one schema finding carried. **Filtered re-run second-driven too** — the precision+macro-filter pass overwrote the dir (noted); Alice's recount AGREEs on all three headlines. **PRIVACY FLAG (Kiln) — filter now BUILT:** the on-machine personal-content filter removed **230 personal turns pre-save** (candidates 909 → 344, now dominated by setup/convention content); a negative test asserts personal turns are never saved; Brian's per-record approval still gates the vault. The correction-events list is unaffected. **Precision pass landed:** post-filter longlist is privacy-safe to display locally and materially denser (344 candidates, now dominated by genuine environment/convention content) — Brian's human curation is the next step |
| **Open rulings queue (consolidated 09-13 ~15:55)** | decision owner | 1. **GiLMore:** S4 value-shape canary adoption — close-gated (no packet to a rater until ruled; patch validated, second-checked). 2. **GiLMore:** amendment A2 — the 3-line vault.ts carry-over fix (frozen lineage). 3. **GiLMore:** parse-iso v2 for the frozen builder (second-checked). 4. **GiLMore/Brian:** budget-meter rebase fix + the forgotten-$7.51 add-back decision. 5. **Brian (sprint-2 asks):** outline sign-off, transcript-mining pilot word, R2 day-0 timing. 6. ~~Corvid: adopt U3~~ **DONE + second-checked** — U3 is guard 18 (`CORVID-U3-RECORD-TEXT-GUARD.md`, Alice PASS on every claim); **Layer C has no open classes** |
| Research intelligence directive | 09-13 (filed; UNVERIFIED details per corpora-report pattern) | `RESEARCH-INTELLIGENCE-DIRECTIVE.md` — frontier snapshot; five priorities (mechanisms before brands; state evolution before static recall; coding experience before chat; formation + use; Pareto frontiers) with "no defensible global SOTA; treat all SOTA claims as protocol-local". **Maps onto this map directly:** priorities 1–5 are the slot taxonomy, E-7/axis C, E-8/E-9, axes A/D, and Corners 1–2 respectively. The directive asks for a live claim→artifact→mechanism→experiment→decision map — this file is that map. **Assessed (Corvid, Alice second-check):** advisory input, no score import, nothing overrides frozen instruments; genuine additions = named-benchmark landscape (MemOps, LongMemEval-V2, StreamMemBench, MemSecBench — new to our ledger) + the Persistent SWE History Suite proposal and evidence-grade/handoff schema; headline numbers verified: Alice checked three (StreamMemBench, MemSecBench, AMA-Agent), Assay five more — all reproduce exactly from primary abstracts. **Sprint-2 goal-5 harvest begun:** candidate cards filed — card 1 MemOps (lifecycle operations, arXiv:2607.12893) and card 2 StreamMemBench (streaming evidence→use→reuse, future-oriented assistance; the "intervening interaction changes later reuse" finding), both discovery only. **Companion artifact:** `CORVID-DISCOVERY-VOCABULARY.md` — the directive's terminology fan-out mapped onto our families/goals, so frontier scans query by mechanism, not by the word "memory" |
| ECOSYSTEM-MAP-CATCHUP-2315.md | 09-13 00:2x | staged fold filed on retry — slots S-19/20/21, vocabulary mirror, MemOS third-party row |

Bottom line for a cold reader: **no S-table tag moved all day** — the day's
verification work deepened and receipted the CLAIMED layer, closed the
license dimension, verified our anchor negative twice, and built the
instrumentation (pins, checkers, freeze tool, meter) that P2 will stand on.

*Update (~20:22):* the checker suite is now **five** guards (added:
query-fork — 0 forked query_ids across all 3 trees / 102 runs, so a cited
query id means the same referent everywhere; this is what lets the map's
cross-run comparisons share rows), consolidated with hashes and verify
commands in `team/CORVID-RD-CHECKER-SUITE.md`, and the three sibling-tree
pointer fixes are packaged as a one-command apply (`apply-pointer-fixes.sh`,
`git apply --check` clean on both). The remaining step for the row-12
defects is execution, not authoring.

*Update (2026-09-13 ~01:00 — P2 entry):* the suite is **eight** guards
(added: Gen38 anchor, MemBukkit parity, protected findings), all green at
the new canonical HEAD `c30e8fa` — Kiln materialized the 182 MB MemConflict
dataset (P1's last build prerequisite) and the 183 MB change **perturbed no
frozen-result index or protected number**. The row-12 pointer defect
remains the one canonical red, one command from closure. A qualifier-census
pass on the canonical `team/` corpus found and fixed 4 ledger lines and 1
map line (this file — the 91.4 split qualifier, fixed same turn); 58
residual lines are working prose, not citable claims.

*Update 2 (2026-09-13 ~05:4x — P2 entry chain double-verified):* Assay
(second-driver, row 27) and Alice (independent reproduction) both PASS
Kiln's P2 entry chain — port parity byte-identical on a clean store, pin
gate receipts as expected, and the chain's one real defect (TS-side
non-idempotence) confirmed with a validated fix pending at the owner.
Method note worth keeping: the focused suite grew 28→30→32 *during*
verification, so both "N passed" claims were snapshots — test counts cite
commits, never turns.

*Update 3 (2026-09-13 ~10:18 — entry run verified):* row 28 closed —
Assay's second-driver of the P2 entry run is **PASS**: deterministic re-run
to a scratch OUT byte-identical, HEAD exactly `40d71e3` with no worktree
diff on the verified paths, raw 0.0 confirmed a retrieval-null. The
baseline floor the external candidates must beat is now second-driven.

*Update 3 (2026-09-13 ~06:00):* the checker suite gained an **orphan-evidence
guard** (rev 2, Alice second-check PASS) — it flags evidence artifacts no
index row cites, which is this map's own failure class: an artifact that
exists but is unreachable through the index is invisible to every cold
reader, including future seats. Slot tables and indexes are now guarded
artifacts, not etiquette.

*Update 3a (2026-09-13 ~12:2x):* Layer C is nearly empty — guard 17 rev 6
adds the ledger supersession cross-check (U9 closed), U6/U7 landed with
rev 5's declared-list hygiene; **only U3 + U8 remain open** (earlier "only
U3" wording corrected). The P2 gate card carries all of it (17 guards,
entry/publication gates, meta-guard INCOMPLETE stop rule). Off-map: the R2H
rev-2 fix is **committed** (1682c4e; canonical = team copy) — this seat's
freeze is settled at the bytes level; re-send to Brian remains the open
step.

*Update 3b (2026-09-13 ~13:12; updated ~15:50):* **U8 closed too** — guard 16
rev 3's declared-tree discovery passed Alice's second-seat probes (real CLI:
undeclared trees named, missing declared trees named, --trees bypass works),
along with U6/U7/U9. **U3 — the last open Layer C class — is now prototyped
and second-checked** (`ASSAY-U3-RECORD-TEXT-IDENTITY.md` + Alice's check:
independent extractor reproduces the clean census); adoption pending Corvid.
When adopted, Layer C is empty. Off-map: Cairn's
lane stays blocked (restart won't fix — the service is stuck inside its own
scan; Kiln must fix the scan or write the pending memory another way).

*Update 3c (2026-09-13 ~13:20; applied-state 13:4x):* U8's fix immediately
drew its own boundary — Assay found a vacuous-scan hole in guard 16 rev 3 (a
declaration with `shared:` but no `tree:` lines silently falls back to
defaults, rc 0); **the fix is now LIVE and second-checked** (Alice: live
guard byte-identical to the guarded file, reverse-apply clean; the fix
note's "not applied" had drifted), one residual carried. Layer C status:
U3 open, U8 **fully closed** (v2 live, second-checked by Alice: residual
closed, nothing else moved).

*Update 3d (2026-09-13 ~20:10):* leakage-guard delta progress — Assay's
power check reproduces all three of Alice's blockers through the real
committed probe, and a candidate delta with B1–B3 pinned passes a 17-case
matrix; a fourth divergence found (the probe's own waiver fixture used a
format guard 14 does not read). Proposal reviewable; owner Corvid. The
design constraint from the fold series stands: the leakage/scope guard must
be declaration/waiver-based, never detail-triggered.

*Update 3a (04:4x second-seat result, noted 06:0x):* Assay's check of the
coverage map verifies Layers A and B (13/13 hashes) but finds **Layer C
incomplete against the Muse dispositions** (two accepted checker classes
missing) and one "closed" mapping overclaiming. My citation above covers
Layers A/B only; Layer C's completion is Corvid's, and the overclaim is a
reminder that "closed" needs the second seat's signature, not the author's.

## §4 addendum 2l — THIRTEENTH FOLD: "independently reproduced" resolved to co-authorship; habitus provenance corroborated (20:4x)

**When/who:** 2026-09-12 ~20:40 PDT, Stratum, R&D pulse. **What landed:**
`ALICE-HINDSIGHT-THIRD-PARTY.md` (+ receipts) and Corvid's habitus
provenance re-run (`RESEARCH-HABITUS-PROVENANCE-RERUN.md`).

| Slot | Fact | Effect on the map |
|---|---|---|
| S-08 hindsight | Hindsight's "independently reproduced by research collaborators at Virginia Tech and The Washington Post" refers to **co-authors of the vendor's own technical report** (arXiv:2512.12818: Vectorize.io + WaPo + VT affiliations). Also: the report's own abstract says **91.4% LongMemEval-S** / 89.61% LoCoMo while the marketing page claims **94.6 / 92.0**; the benchmarks page mislinks "LongMemEval" to Hindsight's own paper, not the benchmark | The ledger's `third-party` class **stays empty ledger-wide** — the one candidate dissolved into vendor-led co-authorship. The marketed 94.6 and the report's 91.4 are different claims; MemBukkit's table already cites 91.4. The survey's "SOTA claim unverified" line is now receipted at the strongest available level: the verification claim itself is authorship, not independence |
| S-06 habitus | Corvid's provenance re-run reproduces the frozen scores (core 0.875/0.750/0.097; stress 0.792/0.025) into new dirs **with** full provenance records (native counts == frozen retrieved_ids counts) — the frozen method is corroborated native at artifact level, and the run itself receipts the `raw_product` class mislabel | S-06's VERIFIED receipts now have provenance records, closing survey gap 5's method half in live runs; the class defect stays an adapter-label defect, receipted |

---

## §4 addendum 2m — FOURTEENTH FOLD: the anchor triple is second-driver-verified (21:1x)

**When/who:** 2026-09-12 ~20:49 PDT, Stratum, R&D pulse. (Time corrected
same turn: the first draft copied Assay's file-header label "~21:1x", which
runs ahead of the clock — STOP-1 again, this time by inheritance.) **What landed:**
`ASSAY-SECOND-DRIVER-GEN38-SCORES.md` — re-derivation of the Gen38 dynamic
Hit@3 anchors from stored derived counts, independent of the summary fields.

| Anchor | Recomputed | Cited | Checks |
|---|---|---|---|
| perseus (S-03) | 1142/2631 = **0.4341** | 0.434 | rank sums == hits; adapter pin `627f812d` exact |
| mem0 (S-05) | 1103/2631 = **0.4192** | 0.419 | same |
| bm25 (S-11, the BAR B floor) | 594/2631 = **0.2258** | 0.226 | same |

Dataset sha `8ef9ec…` identical across all 30 persona files × 3 engines.
**AGREE on all three.** Limit stated inside the receipt: counts/provenance
re-derivation — no raw retrieval replay (the 182 MB corpus is absent by
policy), so the retrieval itself was not re-executed.

**Effect on the map:** the three numbers every bar and comparison leans on —
the S-03 anchor, the S-05 comparison, and the S-11 floor — are now
second-driver-verified at the aggregate, denominator, rank-arithmetic, and
pin level. VERIFIED tags unchanged; their evidentiary weight upgraded.

**Member added (2026-09-13 ~06:1x):** S-09 membukkit's row-9 receipts
(core5 Hit@5 0.9583 / MRR 0.525; stress 0.5833/0.329167) now carry the same
weight — Kiln recounted from the frozen artifact and Alice re-derived from
the per-case `details` rows independently; three trees byte-identical.

**Member added (2026-09-13 ~10:05):** S-06 habitus's core row re-derived
independently by Alice from the 26 per-case `detail.csv` rows — exact,
including the **21/22 = 0.955 positive non-as-of subset**. That closes the
0.955 saga's verification half end to end: the number is ours (2e), lives in
our repo README, and now has an independent per-row re-derivation.

**Member added (2026-09-13 ~10:12):** membukkit's Gen41 product-default row
(stress 0.9167/0.8333, MRR 0.4486; core 1.000/0.958/0.642; fallback-contrast
MRR 0.554) also recounts exactly from the frozen artifact — charter row 9
and the Gen41 row are both fully second-driver-verified.

**Members added (2026-09-13 ~11:34):** S-06 habitus core (0.875/0.750/0.097,
Alice, per-case rows) and — third driver — S-07's 92.9% anchor recounted
independently by Kiln from the per-record trace (store 500 → 82 live
reproduces). Every anchor number in this fold now has at least two
independent derivations.

**Residual closed (2026-09-13 ~11:40):** S-07's reader-correctness counts
(12/14 core, 11/14 stress) reproduce under Assay's independently
re-implemented grading predicate — never calling `score_answer`. Kiln's
residual is closed: the agentmemory anchor is verified at every component
(lifecycle counts, reader counts, provenance pins). **And convergent by
distinct methods:** Kiln's own recount used the reader.json
`grade.pass_answer` fields (a different field path than Assay's
re-implementation) and reproduced both counts exactly, failure pattern
matching the gen17 narrative — including the documented negated-phrase
false positive.

**Update (2026-09-13 01:2x):** Kiln added a **third driver** via a different
aggregation path (rank-bucket sums from the derived JSON, never reading the
headline table) — same three numbers, exact. The anchor triple now has two
independent recomputation paths plus the original receipt; it is the most
verified tuple in the record.

---

## §4 addendum 2n — FIFTEENTH FOLD: hindsight's marketed numbers reproduce; 2l's divergence reframed (20:5x)

**When/who:** 2026-09-12 ~20:55 PDT, Stratum, R&D pulse (clock read).
**What landed:** Alice's Hindsight per-question recompute (relayed in the
20:40+ scoreboard section and logged separately) and Assay's R2H second-driver
(`ASSAY-SECOND-DRIVER-R2H-FREEZE.md`).

**S-08 refinement — amends 2l:** the marketed **94.6 / 92.0 recompute
exactly** from the per-question data Hindsight publishes; the report's 91.4 is
an **earlier, different run**, not a contradiction. So 2l's "marketed vs
report divergence" is a **version split, not a fabrication signal** — the
running caution against citing Hindsight numbers without split/judge
qualification stands, plus two live caveats from the recompute: a small
Google model grades a Google model, and the web page's per-category breakdown
does not match the published run. The **non-independence finding is
unchanged**: co-authorship is still not third-party verification.

**Off-map but on record:** Assay second-drove this seat's R2H freeze — 6/6
hashes recomputed, the ON/OFF schedule independently re-derived from the
committed seed (commit-reveal half holds), no network paths in the shipped
script. The arm that ships to Brian's work machine is now second-seat
verified before day 1.

---

## §4 addendum 2o — SIXTEENTH FOLD: the independence finding double-confirmed; AMB's table receipted (21:0x)

**When/who:** 2026-09-12 ~21:05 PDT (clock read), Stratum, R&D pulse.
**What landed:** `ALICE-AMB-EXTERNAL-ROWS.md` (+ receipts) and Corvid's
`RESEARCH-HINDSIGHT-INDEPENDENCE-AUDIT.md` — two seats reaching the same
co-authorship conclusion **separately** (Alice via the report's affiliation
block; Corvid via the Virginia Tech paper itself, which reports 91.4/83.6 vs
the marketed 94.6).

| Slot | Fact | Effect on the map |
|---|---|---|
| S-08 hindsight | The AMB comparison table behind the marketing page contains **2 AMB-measured rows and 23 paper-sourced rows**, self-labeled "Unverified — not independently reproduced"; and the vendor's own data carries **a higher rival than the marketing page shows** | The marketed comparison is overwhelmingly borrowed, and the omission has a direction. S-08's citation posture tightens to: cite only the technical report's 91.4 (or nothing); never the marketing table |
| cross-slot | The co-authorship (non-independence) finding is now **double-confirmed by two seats working separately** — convergent verification, the strongest shape a negative can take without a new measurement | Shape flag 1 and the citation rule (source + date + pin) are no longer one seat's audit; they are convergent. The `third-party` class staying empty is now a measured fact about the whole batch, not an absence of looking |




*Update (~20:28, addendum 2k pointer):* `ALICE-VENDOR-DATA-TRANSPARENCY.md`
consolidates the day's re-derivations into the **operative per-slot
evidence-status table** — re-derivable / self-attested / one-origin per
vendor, with receipts. Structural findings: exactly **one** headline
(Memobase 75.78) is fully re-derivable offline; agentmemory is partial
(R@20/MRR truncated at 10); a published recipe is not a checkable number
(MemBukkit, Hindsight); the Mem0 2025 paper is a single point of failure for
four rival numbers; and the authoritative LoCoMo id→name map is now pinned
(1=multi-hop, 2=temporal, 3=open-domain, 4=single-hop, 5=adversarial),
completing this map's 2i postscript. The S-table tags above are unchanged by
it — this register is the layer between them and the vendor claims.

---

## §4 addendum 2q — EIGHTEENTH FOLD: the MemOS merge passes second seat; Supermemory slotted (2026-09-13 00:4x)

**When/who:** 2026-09-13 ~00:45, Stratum, R&D pulse. **What landed:**
`ALICE-MEMOS-MERGE-SECONDCHECK.md` (every number and class call in the
MemOS merge reproduces from frozen receipts; one label correction, numbers
unchanged) and `ALICE-SUPERMEMORY-CLAIM-CHECK.md`.

| Slot | Fact | Effect on the map |
|---|---|---|
| S-16 memos | The self-vs-independent merge **passed second-seat check** (Alice re-hashed all four receipt files; transcription accurate) | The S-16 receipt chain is complete: claim (vendor-only, self-conflicted) + independent measurements (69–78/69) + second-seat-checked merge. The formal class call now has nothing left to wait on |
| S-22 supermemory (NEW, allocated above) | Homepage claims "#1 SOTA"; the cited source **does not resolve**; the harness judge is provider-overridable; self 95.0 vs independently reproduced 66.07 — the largest gap in the tables | Slotted for provenance tracking (not a charter candidate). Second confirmed member of the pattern: the loudest self-claims have the weakest artifacts |

---

## §4 addendum 2r — EIGHTEENTH FOLD, CATCH-UP (the 01:29→04:21 overnight session; 04:21)

**When/who:** 2026-09-13 04:21 (clock read), Stratum — consolidated fold for
the overnight wave (invocation-benchmark workstream, metaguard revs 1–3,
Muse batch 5, the Letta hunt, ~45 artifacts). The scoreboard and Assay's
register carry the campaign plane; these are the map-plane items.

| Slot | Fact | Effect on the map |
|---|---|---|
| S-12 letta | Letta's LoCoMo test code **has been found and saved** (the script behind the 74.0% flat-files claim) — we could re-run it ourselves if the portfolio ever decides to | The claim stays `vendor-only` (we have not run it), but it moves from "blog-only" to "re-runnable at will" — the strongest offline status a vendor claim has reached in this batch besides memobase's shipped fixtures. **Same-day completion (04:2x):** the recipe is now **fully commit-pinned** — harness, agent prompt, judge, and dataset at one hashed commit — with Assay's independent re-fetch byte-identical; both open caveats closed. 74.0% is the best-evidenced vendor claim in the batch: located, pinned, second-driven, unrun |
| cross-slot (pins) | The ledger **self-contradicts on source pins**: 8 lines still say four blog sources are unpinned; they were pinned on 09-12 and one ledger line already says so. Owner: Corvid | **RESOLVED same morning** (`CORVID-LEDGER-PIN-STATUS-FIX.md`): all cells now carry the Wayback pins — the pins milestone (addendum 2d) and the ledger's prose agree again. The self-contradiction window was ~9 hours; the checker-suite coverage that would have caught it at write time remains queued. **Second seat: PASS/AGREE** (Assay; one low clarity finding — "4 pins vs 3 blog rows" wants a clause) |
| vocabulary | A **time-label checker** now exists (Corvid), built from the fleet-wide future-label defect class; it immediately found 2 more future-dated entries (Corvid's and Assay's — not this seat's) | This seat's STOP-1/policy-v2 arc is now fleet-instrumented. Labels are estimates; mtimes are timestamps — the map's change log has used mtime-governed entries since 2m |
| campaign plane | **Verity was idle, not down** (fsync's false-empty status reading, corrected 20:1x) — she is wakeable for the A1 design review and the citation-rule pass; the R2 rev-2 fix is committed but unre-sent. **Live-arm blocker (12:5x; sharpened 14:2x):** vault-serve hang — recall works, capture/supersede hangs; internally deadlocked on the scan RPC (transport alive, respawn won't fire). **Write half confirmed down ~12h** (Kiln: 15 entities unchanged since 08:43, zero new records) — the metric that matters for Brian's window read. Recall-side S4/S5 data accumulates. **Post-restart: brand-new services hang too (3/3 tries, watchdog replacing each) — the accumulation assumption is disproven; Cairn stopped retrying.** Timeline (`SERVE-HANG-TIMELINE.md`): the trigger is the **supersede-draft `keyInUse` scan itself** (every hang at that scan, never recall, never cliWrite); **age is not the discriminator** (2 min → 7 h), so the watchdog will be exercised on essentially every supersede draft; post-A1 respawns stable so far (intermittent by evidence). His own serve-age speculation corrected on the record. **REPRODUCER FOUND** (`SERVE-HANG-REPRODUCER.md`): `perseus_vault_scan` issued while `perseus_vault_recall` is in-flight against the **live WAL vault** deadlocks both (36 fds = r2d2 pool materialized, futex-idle — the exact incident signature); each condition alone is clean. **ROOT CAUSE (Cairn, 14:3x; mechanism confirmed by Ledger in code): it was never the serve** — the extension's client `rpc()` (vault.ts) reads replies in ≤64 KB pieces and **discards both parts when a reply spans a boundary** (no carry-over buffer; partial lines hit the catch), so the client waits 30 s for nothing. The scan reply is 69,615 bytes = 2 pieces; recall replies are smaller, which is why recall always worked. Cairn's 3-line carry-over-buffer fix drops the scan to 1 ms — but vault.ts is frozen lineage, so it needs **amendment A2** (second amendment to the extension this window; A1 hashes already with Verity). **CONTRADICTED PAIR → RESOLVED for B** (Alice, `ALICE-SERVE-HANG-ROOTCAUSE-RECONCILE.md`; Kiln withdrew the reproducer): the two accounts were mutually exclusive as primary causes; the byte arithmetic (65,536 + 4,079 = 69,615) explains scan-fails/recall-works exactly, the reproducer's test client was at fault and was withdrawn, and with a corrected client the live database is clean. A2 (the 3-line client fix) is still the required path — vault.ts is frozen lineage. **NEW DISAGREEMENT (16:1x):** Kiln's "final state" re-asserts a serve-internal root cause needing an upstream fix and calls the watchdog "production-proven" — against the accepted client-parse finding (Cairn's evidence, Alice's byte arithmetic, Ledger's code confirmation, this seat's folds). The scoreboard treats the reading-code bug as confirmed; the disagreement is live for GiLMore to adjudicate. **Ledger's verification (16:1x) cuts against "operationally closed":** S1 cycles are NOT accumulating — the pending supersede is unrun (file unchanged since 14:54), the same worker has run ~2h, and its memory service is unreplaced since ~14:30; the quiet fits Cairn having stopped drafting No new memory or S1 cycle until Kiln fixes it. Window closes Tuesday EOD. **Mid-window amendment (GiLMore URGENT, Kiln executing):** watchdog added to the frozen extension lineage; **A2 body exists and is at rev 2, second-checked** (`ASSAY-A2-VAULT-FRAMING-FIX.md` rev 2 + Alice's v2 check: both framing residuals closed; one moderate carried residual — a timed-out call leaks its listeners, same class as v1 — not applied; owner Kiln/Cairn, needs an outside restart; A1's watchdog mitigates the symptom, not the trigger); state-only recovery procedure RUN; amendment A1 (watchdog, commit 2e247bb) deploy ATTEMPTED via worker-pi self-restart — **lane reported DOWN post-restart** (builder 13:40: state.db status=error, no live worker process; restart was run from inside cairn-pi), supersede of record-e0634fb9 per the PENDING record executed before the restart, before/after hashes filed and now **second-driven by Assay** (060d842 → 2e247bb after-hashes match the amendment's claims); one provenance-record defect named: WINDOW-OPENING's block still reads byte-identical — pending fix; the deadlock itself is serve-internal in the pinned binary (scan RPC; 16/16 pool fds materialized) — root cause unidentified, binary unchanged | Map-adjacent only: S4 counting continues but close-time blind adjudication has a staffing gap for GiLMore, and the scan-RPC deadlock points at the S6 scan instrumentation as a hang suspect — the same scan whose empty-result false-violation behavior guard #4's fix addresses |

---

## §4 addendum 2s — NINETEENTH FOLD: leakage closed end-to-end; the goal-5 harvest completes; the gate card is executable (2026-09-13 ~21:4x)

**When/who:** 2026-09-13 ~21:4x PDT (clock read; mtime is the timestamp),
Stratum, R&D pulse. Consolidated fold for the 20:49→21:3x wave plus the two
index gaps this seat found against its own map (cards 3–4 and the leakage
adoption were absent from the addendum index). **No S-table tag moved** —
this wave is the instrument and discovery plane, not the vendor-claim plane.

**1. The leakage/scope arc is CLOSED — supersedes update 3d's "proposal
reviewable; owner Corvid."** The chain, in order: scope audit (Gen76) →
isolation ablation (Gen78: 6/6 → 0/6 on all three engines, not a ranking) →
configuration isolation Gen79–82 (G-C half-closed: a real capability
difference, agentmemory stays 3/3) → Assay's census proved a detail-derived
trigger has zero discrimination (0/102 details carry a scope column, so a
fail-closed guard would red every legacy run) → **contract ADOPTED**
(`CORVID-LEAKAGE-FIELD-CONTRACT.md`): declaration-triggered
(`LEAKAGE-REQUIRED.json`, boolean `leakage_required: true`), legacy floor =
absence alone is never a finding, waiver reuse, advisory on
reported-but-undeclared, malformed declaration fails closed → **delta
APPLIED**: guard 14 `3ae6cf05…` → `09814e25…`, probe `23a640c8…` →
`58bcc588…` → **Alice SIGNED the applied bytes** (`ALICE-LEAKAGE-GUARD-RESIGN.md`,
03:3x UTC): 18/18 independent matrix through the real `check()`/`scan()`,
blockers B1–B3 closed in code, meta-guard 17/17, map-hash 0, coverage-map
row 14 re-hashed. Three-tree census: 102/106/102 runs, 0 declared, **0
findings — adoption is a verified no-op today**; the guard bites only a
future arm that declares leakage-bearing and then omits the column. The
contract's honest limit stands on the record: a run that declares nothing
and reports nothing is structurally undetectable — a green census is not
"no leakage anywhere." Map plane: axis D (delivery honesty) gains its first
required-when-provocable **harm field** (`leakage@k`, reported beside
`prohibited@k`, never folded into recall), and the record now carries three
deliberately distinct senses of "leak" (pipeline de-identification; S4
blinding assurance; memory leakage) — cross-referenced so gate prose cannot
conflate them.

**2. Sprint-2 goal-5 harvest completes in the index (cards 3–4, joining
cards 1–2 from row 634).** All Corvid, Phase-B, abstract-level, **no score
import**, all headline numbers abstract-reproduced by Alice/Assay:
- **Card 3 — STALE + Supersede** (`CANDIDATE-CARD-STALE-SUPERSEDE.md`):
  STALE names a failure class our taxonomy does not carry — **implicit
  conflict** (a later observation invalidates an earlier memory without
  explicit negation; best model 55.2%) — plus Premise Resistance, a probe
  shape we do not measure. Supersede isolates the update gap ("length, not
  compression ratio" scales the failure; 92%→77% under self-maintenance).
  Taxonomy candidate (this seat's proposal, not yet adopted into §2):
  implicit conflict as a sub-class of axis C's conflict mechanisms, pending
  the bounded corpus probe (do implicit conflicts exist in our
  transcript-miner correction events? owner Corvid). CUPMem = an E-7
  mechanism arm reference (write-time revision + propagation-aware search).
- **Card 4 — MemSecBench + GateMem** (`CANDIDATE-CARD-MEMSEC-GATEMEM.md`):
  the security/governance arm we do not have, **with the card's own
  overstatement corrected before it was quoted** (`CORVID-SCOPE-LEAKAGE-GATE-ADDENDUM.md`,
  Alice second-check): single-principal scope isolation is **measured and
  closed** (Gen76/78/80–82), so the net-new axis is **multi-principal
  access control** (principal × role × trust-label across a shared pool) and
  leakage as a first-class harm — the former reserved as P3/P4 design, the
  latter now landed via item 1. MemSecBench's Write→Execute→Forget chain
  (poisoned memory persists 84.2%; repair 56.1%) is the threat-model shape
  for the P3/P4 gate; "selective repair after poisoning" is the one
  genuinely unmodeled class. GateMem's failed active forgetting and
  agentmemory's 418/450 false supersession are the same delete/repair
  failure from two sides — a discriminating E-7 hypothesis.

**3. The P2 evidence-gate card is now second-checked AND executable
(`CORVID-P2-EVIDENCE-GATE-CARD.md`, Rev 4).** Alice's second seat
(`ALICE-P2-GATE-CARD-SECONDCHECK.md`) independently reproduced all **18
entry-gate states** ("one red by design, two advisory") but found the card
unexecutable as written (missing `scripts/` prefix → literal copy-paste gave
18 rc 2s). Corvid's Rev 4 fixed ~24 invocations and closed the 18-vs-17
title question (18 live files = driver + its exact 17 `_COVERED_NAMES`).
Alice's exec-check (`ALICE-P2-GATE-CARD-EXECCHECK.md`, 21:3x) ran every
command as written: **0 `can't open file`, every rc matches its stated
state**; one residual of the same class carried (the bare
`check_rd_thread_labels.py` edit-gate bullet resolves against the tree and
rc 1s as a missing-prerequisite — one-line fix proposed, owner Corvid). The
publication gate Corvid's card describes now includes the adopted
leakage-field check riding guard 14 — it is not a seventh pass/fail check.

**4. Instrument plane, for the owners (map-adjacent).** Assay's
power-check register (`ASSAY-POWERCHECK-REGISTER.md`) is now the one index
of independently exercised instruments: 9 findings (fixes validated or
pending adoption, none silently dropped), positive controls, and named
gaps closing. Its newest entry power-checks the **fleet-poller's own
section-6 QUEUE pulse** (`ASSAY-POLLER-QUEUE-PULSE-POWER.md`): the shipped
predicate has zero power on the real 7-column schema (case-sensitive seat
names; no `| open |` cell exists — the vocabulary is `done:/claimed:/assigned:/open…/draft`),
and the obvious `grep -i` fix would false-wake; a field-aware predicate
fires on exactly the one claimable open row (QUEUE 29, Verity). Fleet-infra,
owner builder/GiLMore — the poller is not a registered session and cannot
fix itself.

**5. Off-map (fleet plane, builder, 21:1x–21:3x):** the flash lanes were
switched to InferX ~04:07Z, erroring at 67% per turn; builder's request-level
dig showed the cause is **rate limiting** on the discounted endpoint under
fleet load (7 of 36 requests in 20 min), and the fleet was reverted to zai
~04:30Z by the switch owner. Two context resets tonight from the
resume-failure path (`acp-worker` discards the resume exception text — his
proposal to print `exc` stands); lane-meter counted through it all, and the
`model_usage`→`session.directory` join now gives per-lane provider spend.
Carry-forward: the 18:00 PDT timer returns to InferX.

Bottom line: the map's vendor-claim layer is unchanged today (no tag moved);
the day went to the **instrument layer** — the guards that keep the map
honest now include the leakage field, the gate card that operationalizes
them is executable and second-checked, and the discovery layer gained four
abstract-level frontier benchmarks pointing at exactly the axes this map
holds open (implicit conflict, multi-principal governance, formation→reuse).
