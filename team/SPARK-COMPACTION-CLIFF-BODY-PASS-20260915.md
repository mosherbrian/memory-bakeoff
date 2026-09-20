# muse-drafter: Compaction Cliff body pass — typed fidelity lanes + a constraint verifier (spark, 2026-09-15)

Body read of delta-#3's top candidate. **Design extraction only — no score
import**, $0. Corrected 2026-09-15 after Corvid's abstract pin check
(`CORVID-COMPACTION-CLIFF-PINCHECK.md`); see Reconciliation at the end.

## Pin

| field | value |
|---|---|
| Title | *The Compaction Cliff in Long-Running AI Agent Memory* |
| Authors / venue | Saber Zerhoudi, Jelena Mitrovic, Michael Granitzer; submitted **2026-08-24**, CIKM 2026, v1 |
| Paper license | **CC BY 4.0** |
| Artifact | **released**: HF `searchsim/AgentArtifactCorpus` (**CC-BY-4.0**, 396,934 configs / 54,628 repos) + reference impl `searchsim-org/cikm26-knowledge-triage` (**Apache-2.0**; GitHub's LICENSE detection reads NOASSERTION) + the classifier |

Both lanes are reuse-green; this is stronger than the "design reference" the
abstract-only pass recorded.

## The two findings (vendor)

1. **The cliff (abstract).** On **20 production agent configurations**, Claude
   Code's `/compact` prompt on **Sonnet 4.6** preserves **53%** of safety rules
   after **one** compaction round and **10% after five**. That is the named
   "Compaction Cliff."
2. **Hierarchical truncation, §4.3.** Truncation — the core of the
   summarize-and-retain pattern — preserves only **50% of safety constraints on
   50 real agent configurations** (a separate study from #1). A 2026 community
   analysis of leaked Claude Code documents the same uniform pattern.

## The mechanism worth stealing: Knowledge Triage

**Three deterministic operators, per-type policies** (the framework is *Knowledge
Triage*, not three lanes):

- **TypeCompact** — compresses without dropping safety rules; internally routes
  items into **three fidelity lanes** (following Adaptive Focus Memory):
  constraints + procedures at **full**, beliefs/preferences at **compressed**,
  episodic at **placeholder**.
- **TypeDecompose** — splits large topics and duplicates rules that span them;
  reported **0% locality violations vs 93%** under uniform partitioning.
- **TypeRetrieve** — returns applicable rules first; reported **100% recall@50 vs
  73%** for the best single-shot LLM retriever.

A **verifier** extracts a canonical form (**negation + object phrase**) from every
constraint, checks it survived, and flags the output **unsafe** otherwise
(restore-or-escalate). Reported: **2–4× more safety rules than the strongest
single-shot compactor at every ratio**, **96% recall over five rounds**; §4.3's
TypeCompact returned **1.00 / 0.95 / 0.80** constraint recall at 50/25/10% on its
50 configs, stabilizing at 0.96 from round two. The guarantee is
**by construction conditional on classifier recall** (a constraint is lost only
if the per-item classifier mislabels it).

## Map to us

- **Direct hit on our compaction/premise concerns:** it names the exact failure
  our stale-instruction / premise-awareness probes care about — a rule and a log
  merged at one rate — and gives a deterministic check (canonical negation+object
  presence) instead of a similarity score.
- **Epistemic-type system:** "typed knowledge model + per-type distortion + three
  fidelity lanes + three operators" is the closest published shape to
  `SPARK-EPISTEMIC-TYPE-SYSTEM-DESIGN-20260915.md` — a concrete prior for the
  type→treatment table, and it ships a corpus + classifier + harness we can run.
- **Reportable field:** "constraint recall at fixed compression" beside
  prohibited-presence; the verifier is LLM-free.

## Cautions

Numbers are vendor and not imported; the method is **classifier-dependent**; the
"production" claim partly rests on a community leaked-doc analysis (claim-class
care). Not a memory benchmark; no coding substrate. The GitHub LICENSE is
Apache-2.0 text but detected NOASSERTION, so cite the LICENSE file, not the badge.

## Next (bounded, owner call)

Feed the type→operator→lane table + canonical-form constraint verifier into the
epistemic-type-system design and the premise-resistance companion (design only).
Unlike most delta-#3 items, the corpus/harness is reusable if a build is funded.

## Reconciliation with `CORVID-COMPACTION-CLIFF-PINCHECK.md` (2026-09-15)

Corvid checked the **abstract**; this note quotes the **body**. Most "card vs
abstract" discrepancies resolve as scope, one is a real correction, one is a
clarification:

| Corvid's class | resolution |
|---|---|
| 50 → 20 configs; 50% → 53%/10% | **both true, different experiments**: abstract = `/compact` on Sonnet 4.6, 20 configs, 53%→10%; body §4.3 = hierarchical truncation, 50 configs, 50%. Now both cited and labelled. |
| attribution `/compact` on Sonnet 4.6, not "hierarchical truncation" | **both appear**; §4.3's 50% is explicitly hierarchical truncation. |
| artifact "none surfaced" | **Corvid right — corrected**: released (HF CC-BY-4.0 + Apache-2.0 repo + classifier). |
| three operators ≠ three lanes (conflation) | **clarified, not conflated**: Knowledge Triage has three operators; TypeCompact itself routes into three fidelity lanes. Both stated. |
| 1.00/0.95/0.80 trio not in abstract | **body §4.3 claim**, now labelled; 0.96 matches. |

Corvid's two added abstract facts (TypeDecompose 0% vs 93%; TypeRetrieve 100% vs
73%) are folded in above. Net: one genuine correction (artifact), one scope
clarification, and a stronger candidate (reuse-green, not design-only).

$0, web/API reads. — muse-drafter (Spark)
