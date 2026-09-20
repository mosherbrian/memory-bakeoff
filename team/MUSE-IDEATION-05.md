# Muse ideation batch 5 — adversarial stress of the invocation benchmark

**Author:** Corvid (`worker-glm-dsh3`), R&D + evidence-integrity
**Authorization:** fleet-poller R&D pulse 2026-09-13 (standing Muse cadence,
`team/RD-THREADS.md` Corvid thread; original approval Brian via GiLMore
2026-09-12, `PROTOCOL.md`). Public methodology only; no project-specific detail
on the wire.
**Trigger:** row-24 `DESIGN-INVOCATION-BENCHMARK.md` — stress the design before
Stratum integrates it and Assay verifies it.
**Cost:** one batched call; meter read `$3.8375` before and after (openrouter
`used` did not move in the read; batch 4's comparable call was ≈$0.012, and the
meter lags whole-cent balance updates). No block signals. Latency 26.5 s,
2,525 chars.
**Receipts:** `implementer/repo-glm-dsh3/scripts/experiment_20260912_muse_ideation/receipts/batch5-*`
(summary sha `36261eed…`, history `0e5d5046…`, stream `f61e05c7…`,
state `caf9692a…`, pty `bcc395e1…`); prompt `PROMPT5.txt` sha
`56efb7594dd4b7963c971f03b96aada19ef14a2517d64c21d2d9e45e252464b8`, recorded
before sending.

**Plain English (for Brian):** before the new invocation benchmark gets built,
I asked an outside ideation model how that kind of benchmark is usually gamed.
It named five ways, and all five are real for this design: firing on everything;
quietly shrinking the set of moments that count; a trigger log that claims a fire
that never happened; "covering" a moment by dumping the whole store; and winning
by matching the scripted wording rather than generalizing. Each has a cheap
control. I accepted all five as design-strengthening additions (not findings —
none has a probe yet) and folded them into the design as Addendum B.

## Prompt (verbatim, preregistered)

See `PROMPT5.txt` (sha above). Public research question: name five ways a
scripted "proactive memory invocation" benchmark could be gamed, confounded, or
made misleading, with a minimal control for each, deliberately including an
undesirable-behavior reward, a manipulable denominator, and a lying trigger log.

## Muse output (verbatim)

**1. Fire-everywhere alarm — rewards undesirable behavior.** A system that
proactively interrupts on every turn scores 100% on "fraction of load-bearing
moments fired before deadline" while being unusable: alert fatigue, token bloat,
latency. *Control:* fix a fire budget and report precision alongside recall —
false-fire rate on non-covering turns, median injected tokens per turn, and a
penalized score like F1 or recall-at-fixed-fires-per-100-turns.

**2. Denominator shrinkage — load-bearing classification is manipulable.** If
the system, vendor, or a post-hoc adjudicator can dispute/exclude "hard" moments
as not-truly-load-bearing, or if load-bearing status depends on the system's own
behavior, the denominator shrinks to only moments it handles. *Control:*
pre-register and freeze the load-bearing set with covering record IDs before any
system runs; harness owns ground truth; report intent-to-treat recall over the
frozen denominator and require any exclusion to be logged with a sensitivity
analysis.

**3. Phantom-fire logging — the log lies about what happened.** A system can
write "fired at t" to the trigger log while injecting nothing, injecting after
the agent already committed, or backdating the timestamp — programmatically
counted as success. *Control:* never score self-reported logs; the harness
independently observes context assembly with its own clock and verifies the
covering record's content was present in the agent's prompt before the action
deadline.

**4. Dump-the-store retrieval — technically fired but misleading.** A system that
fires by injecting the entire memory store, or a large irrelevant bundle
containing the covering record by accident, counts as a hit without doing useful
retrieval. *Control:* score payload fidelity, not just firing: require the
covering record ID in the injected set, cap context budget/top-k, and report
precision, exact injected size, and performance with the covering record ablated.

**5. Cue-overfitting to synthetic fingerprints — confounded corpus.** If
decision moments share lexical tells ("remember my allergy..."), a system wins by
keyword-matching the scripted phrasing rather than general proactive invocation,
failing on paraphrases. *Control:* hold out a paraphrased/adversarial split with
tells removed, plus a counterfactual check: the deterministic agent must
demonstrably take the wrong action without the memory and the right action with
only the covering record injected.

## Dispositions (Muse proposes, Corvid disposes)

| # | Muse item | Verdict | Reason / where folded |
|---|---|---|---|
| 5.1 | Fire-everywhere alarm | **ACCEPT (narrowed)** | The design already has `FalseFire`/`FirePrecision`/`NearMissFire` and a fire-always control. New: a **fixed fire budget** and `Recall@F` (FBMR at ≤F fires/100 non-moment turns) so a fire-everywhere system cannot top the headline. Folded as Addendum B1. |
| 5.2 | Denominator shrinkage | **ACCEPT (strengthen)** | The design already freezes the manifest and derives `load_bearing` from the OFF control. New vector: a per-system OFF arm can shrink its own denominator; the load-bearing set must be established **once, neutrally, and frozen across arms**, with any cross-arm divergence reported. Folded as Addendum B2. |
| 5.3 | Phantom-fire logging | **ACCEPT (strengthen)** | Real gap: the primary `FBMR_topic` counts a fire from the adapter's own event log. Require **harness-observed** fire evidence (injected context, harness clock, covering-record presence before the action); the system log becomes corroboration, and a dual-source mismatch is an instrument finding. Folded as Addendum B3 — **the literal presence-only form was then rejected by Assay's probe and replaced (see Postscript)**. |
| 5.4 | Dump-the-store retrieval | **ACCEPT (narrowed)** | Mostly covered by `context_dump` mode, `context_tokens`, `CBMR`, and the long-context-null bound. New: an **ablation control** (remove the covering record → the agent must revert to wrong) and exact injected size. Folded as Addendum B4. |
| 5.5 | Cue-overfitting to synthetic fingerprints | **ACCEPT (narrowed)** | Covered in part by held-out templates and pre-registered topic reachability. New: a **paraphrased/tell-removed split** with a necessity-and-sufficiency counterfactual. Folded as Addendum B5. |

**Tally:** 5 ACCEPT (3 narrowed, 2 strengthen) · 0 REJECT · 0 DUPLICATE.

## What I take from it

- **Chase first: 5.3 (phantom-fire logging).** It is the only item that can make
  the *primary* metric wrong while everything else looks healthy; the design's
  delivery-level companion covers the outcome but not the fire claim.
- **5.2 is the subtlest:** the design's OFF-control denominator is per-run, which
  is fine for one system but invites cross-arm denominator drift when comparing
  systems; freeze it once.
- **5.1 and 5.4 are metric-shape fixes**, not new instruments — cheap to add to
  §4/§5.
- **5.5 is a corpus-property fix**; it belongs beside the existing held-out rule.
- Muse remains divergence, not truth: each ACCEPT is a proposal until a probe
  rejects a real bad input.

— **Corvid** (`worker-glm-dsh3`). One batched call, 5/5 accepted as design
hardening; folded into `team/DESIGN-INVOCATION-BENCHMARK.md` Addendum B.

## Postscript (2026-09-13) — 5.3's proposed control was insufficient

The control Muse proposed for 5.3 (and my first fold of it) was **presence of the
covering id in the prompt before the deadline**. Assay's probe
(`ASSAY-B3-REVIEW.md`, `dc145b52…`) showed that literal predicate scores
`FBMR_topic=1.00` for dump-the-store, fresh-only fire, explicit-call answers, a
mere user-text id mention, and an `R1`-inside-`R1EXTRA` substring collision, and
his re-check (`ASSAY-B3-REVISION-RECHECK.md`, `757c5adb…`) added F3b (a bare
string `reason` makes `"topic" in "nontopic"` true). The design's Addendum B3/G7
was therefore revised to a **mechanism-owning** observer
(`channel ∧ mechanism==proactive_topic ∧ exact-token "topic" ∈ reasons ∧ exact
canonical id ∈ record_ids ∧ seq < action_seq`), with presence demoted to
`CBMR`/corroboration and `FBMR_persist` added. Net: item 5.3 was a correct
diagnosis with an insufficient first fix; the probe, not the ideation call,
made it correct. No other disposition changes.
