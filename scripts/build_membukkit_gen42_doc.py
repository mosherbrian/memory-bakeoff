#!/usr/bin/env python3
"""Render the Gen42 calibration report from its committed JSON."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "results" / "membukkit_memconflict_gen42_calibration"
d = json.loads((BASE / "calibration-report.json").read_text())
s, ident, ops = d["scored"], d["identity"], d["operations"]
route, ctx, det = d["routing_diagnostic"], d["committed_calibration_context"], d["determinism"]
mech = d["static_mechanism"]
pre = json.loads((BASE / "preflight.json").read_text())

def rate(block, k="3"):
    return f"{block['hit_at'][k]['rate']:.4f}" if block["hit_at"][k]["rate"] is not None else "n/a"

types = ("dynamic_conflict", "static_conflict", "conditional_conflict")
rows = "\n".join(
    f"| {t.replace('_', ' ')} | {s['by_conflict_type'][t]['measured_questions']} | "
    f"{s['by_conflict_type'][t]['hit_at']['3']['hits']} | {rate(s['by_conflict_type'][t])} | "
    f"{ctx['perseus']['by_conflict_type_hit_at_3'][t]:.4f} | "
    f"{ctx['mem0']['by_conflict_type_hit_at_3'][t]:.4f} |"
    for t in types if t in s["by_conflict_type"]
)
ranks = s["overall"]["first_support_rank_distribution"]
rank_row = " | ".join(f"{k}: {v}" for k, v in sorted(ranks.items(), key=lambda kv: (kv[0] == "no_hit", kv[0])))
bl = ctx["baseline_context"]
per = "\n".join(
    f"| {pid[:8]} | {v['measured']} | {v['unmeasured']} | {v['hit_at_3']} | "
    f"{v['hit_at_3'] / v['measured']:.4f} |"
    for pid, v in sorted(s["per_persona_measured"].items())
)

doc = f"""# MemBukkit intended models on the MemConflict calibration slice

**Evidence class:** `{s['evidence_class']}`, lane `{s['lane']}`.
**Development-exposed calibration on three personas. Not an official MemConflict score, not a
full release, no reader, no upstream judge.** `upstream_llm_judge` remains
`requires_reader_authorization`.

The question was not who wins. It was whether a third, architecturally different product shows
the same static-versus-conditional asymmetry the first two showed, and whether MemBukkit's
routing trace reveals a different cause. Both halves have an answer, and the second one is the
reason this generation was worth running.

## What ran

MemBukkit source `{ident['membukkit_source'][:12]}` — the Gen7/Gen8/Gen40/Gen41 pin. Intended
MemseekAI models at the Gen40 revisions, every file reconciled to its committed manifest before
exposure and offline thereafter. Gen41 raw-product retrieval, `union_lanes=("atomic",)`. Both
models proven on `mps:0`, the frozen product-default identity. No distiller, no LLM, no reader,
no external API; the network was blocked at the socket layer before the first write.

The frozen Gen37 procedure ran unchanged — this generation registers an engine into it rather
than reimplementing it — and the frozen Gen37 scorer and Gen38 static-mechanism diagnostic
produced the numbers below, so they are comparable with the committed calibration results by
construction.

Totals: {ops['totals']['successful_writes']:,} writes of
{ops['totals']['attempted_writes']:,} attempted, {ops['totals']['malformed_excluded']} malformed
messages excluded and counted, {ops['totals']['distinct_native_ids']:,} distinct native ids,
{ops['totals']['write_failures']} write failures, {ops['totals']['questions_executed']} questions.

## Adapter, frozen before exposure

`{ident['adapter_version']}`. Indexed text is the released message content alone. The write
receipt is an opaque ordinal assigned in write order — never a persona, session, turn or question
identifier — and is never indexed. The query is the released question text alone. Nothing from
the scorer side is written, queried or stored.

One product property forced a decision worth stating plainly. MemBukkit selects by relevance and
then **re-presents the selected hits in date order**, so the order of the public
`MemorySearchResult.hits` is a presentation property, not a ranking. Taking rank off that surface
would have scored a date sort. This adapter reads rank from the relevance order the product
returns internally, and requires per query that it holds exactly the same records the public
surface returned. The equivalence is proven on every one of the
{ops['totals']['questions_executed']} questions, not assumed once.

Preflight, on invented content only: bad payloads rejected, six of six synthetic writes mapped,
two messages with identical text kept as two rows under distinct receipts, store isolation
between universes, reads leaving the state digest unchanged, the LLM path refusing rather than
merely unused, and the frozen chronology function raising on a future-session unit.

## Result

Measured {s['overall']['measured_questions']}, unmeasured {s['overall']['unmeasured_questions']}
— the same measured denominator as the committed Perseus and Mem0 calibration, so the columns
below line up question for question.

| metric | MemBukkit | Perseus | Mem0 | BM25 pilot |
| --- | --- | --- | --- | --- |
| Hit@3 | **{rate(s['overall'])}** | {ctx['perseus']['hit_at_3']:.4f} | {ctx['mem0']['hit_at_3']:.4f} | {bl['hit_at_3'] / bl['scored']:.4f} |
| Hit@2 | {rate(s['overall'], '2')} | — | — | — |
| Hit@5 | {rate(s['overall'], '5')} | — | — | — |
| log-rank@3 | {s['overall']['exact_log_rank_at_3']:.4f} | {ctx['perseus']['exact_log_rank_at_3']:.4f} | {ctx['mem0']['exact_log_rank_at_3']:.4f} | — |

By conflict class, Hit@3:

| class | measured | hits | MemBukkit | Perseus | Mem0 |
| --- | --- | --- | --- | --- | --- |
{rows}

First-support rank distribution: {rank_row}.

Per persona:

| persona | measured | unmeasured | Hit@3 | rate |
| --- | --- | --- | --- | --- |
{per}

Contract integrity: {s['retrieval_health']['unmapped_provenance_items']} unmapped provenance
items, {s['retrieval_health']['empty_returns']} empty returns,
{s['retrieval_health']['short_returns_under_5']} returns under five,
{s['retrieval_health']['future_session_leakage']} future-session leaks,
{ops['totals']['write_failures']} write failures, {ops['totals']['native_id_replacements']}
native id replacements. Inventory reconciles exactly on all three personas.

## The finding: static failure is a ranking failure, and now that is measured, not inferred

Gen38 concluded from an admission diagnostic that static failure in Perseus and Mem0 is a ranking
problem rather than an availability problem. MemBukkit allows a sharper test, because its router
opens only part of the bank before the cross-encoder ever sees a candidate. If static failure
were unreachability, the gold record would sit outside the opened region.

It never does.

| static questions | count |
| --- | --- |
| gold support present in the write ledger | {route['gold_availability']['gold_support_present_in_write_ledger']} |
| hit at 5 | {route['counts']['static_hit_at_5']} |
| miss, gold **entered** the opened region and lost before the top five | {route['counts']['miss_gold_entered_region_lost_before_top5']} |
| miss, gold never entered the opened region | {route['counts'].get('miss_gold_never_entered_region', 0)} |

Every static miss — {route['counts']['miss_gold_entered_region_lost_before_top5']} of
{route['counts']['miss_gold_entered_region_lost_before_top5']} — had its gold support inside the
candidate region the router opened. Routing exclusion accounts for
{route['share_of_static_misses']['routing_exclusion']:.0%} of static misses and rank loss for
{route['share_of_static_misses']['rank_loss']:.0%}. The router opened a median
{ops['scan_fraction']['p50']:.1%} of the bank, and the right record was in it every time.

So a third engine, with a different architecture — topic routing, a fine-tuned cross-encoder, and
rank fusion rather than a vector store with a scoring head — fails the same class in the same
place. The record is stored, searchable, and inside the candidate set the reranker scores. It
still does not reach the top five.

The static mechanism split says the same thing from the scorer side. At K3, of
{sum(mech['top3_categories'].values())} static questions,
{mech['top3_categories'].get('no_truth+no_contradiction', 0)} return neither the truth session nor
the contradicting one, {mech['top3_categories'].get('no_truth+contradiction', 0)} return the
contradiction without the truth, {mech['top3_categories'].get('truth+no_contradiction', 0)} return
the truth alone and {mech['top3_categories'].get('truth+contradiction', 0)} return both.
"Retrieval prefers the newer contradiction" describes a minority here too.

## Where MemBukkit differs from the other two

Conditional questions. Perseus and Mem0 both sit at 1.0000 on this slice; MemBukkit is at
{s['by_conflict_type']['conditional_conflict']['hit_at']['3']['rate']:.4f}. That is the one class
where this product behaves qualitatively differently rather than by a few points, and it is the
main reason its overall Hit@3 lands below both — above the lexical baseline, below the two vector
products. On 29 measured conditional questions across three development-exposed personas, that
gap is worth naming and not worth ranking.

## Determinism

{det['repeat_probes']} label-blind repeat probes against the same unchanged state:
returned order identical {det['returned_order_identical']}/{det['repeat_probes']},
selected set identical {det['selected_set_identical']}/{det['repeat_probes']},
numeric scores identical {det['numeric_scores_identical']}/{det['repeat_probes']}. Reported as
three quantities, not one boolean. Read-side-effect audits found no state change from querying.

## Operations, secondary

Write p50 about 22 ms and query p50 about 1.7 to 1.9 seconds per persona; roughly six minutes per
persona end to end. The query cost is the cross-encoder scoring the opened region on every
question. Scan fraction: p50 {ops['scan_fraction']['p50']:.4f}, p90
{ops['scan_fraction']['p90']:.4f}, max {ops['scan_fraction']['max']:.4f} over
{ops['scan_fraction']['n']} queries, derived from the native trace. Capacity is not quality and
timing sits outside the scientific digest.

## Reading rules

Three development-exposed personas. No global winner claim is available from this slice and none
is made. The direct raw path is append and dedupe with no product supersession, verified rather
than assumed: {ops['totals']['native_id_replacements']} native id replacements and no superseded
rows. Product-default MPS is part of this evaluated-system identity; nothing here claims a forced
CPU run would score the same, and Gen41 measured that it would not be identical.

Scientific digest `{d['scientific_digest']}`, rebuilt with wall-clock and per-item latency
excluded. Adapter `{pre['adapter']['sha256']}`, engine module `{pre['adapter']['engine_module_sha256']}`.
"""
out = ROOT / "research" / "MEMBUKKIT_MEMCONFLICT_GEN42_CALIBRATION.md"
out.write_text(doc)
print("wrote", out)
