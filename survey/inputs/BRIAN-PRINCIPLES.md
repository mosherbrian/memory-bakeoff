# Brian's guiding principles and priorities (2026-09-26)

## Priority answer to QUESTIONS Q1 (what costs Brian most)
1. **Re-learning procedures.**
2. **Repeating preferences.**
(Not ranked as top: lost task state, missing evidence.)

## The five-part principle (agreed with ChatGPT during the Phase 2 roadmap work)
> **State tells the agent what to do now. Memory tells it what it has learned. History lets it reconstruct what happened. Artifacts establish what is true. Executive reasoning decides what it means.**

## The corollary (from the SKILL.state discussion)
> **Don't delete the past just because you stop putting it in every prompt.**

Context (reconstructed by Claude): SKILL.state (2026) shrinks long agent runs about 16x by replacing conversation history with a structured state object and discarding intermediate reasoning. Its own stated failure modes are unknown schemas, *delayed relevance* (something dropped early is needed later and cannot be recovered) and trajectory-dependent tasks. The corollary separates two decisions that such designs merge: what goes in the prompt (keep it small) and what is kept (keep everything, recoverable). Exclusion from the working view must never mean deletion from history. This is roadmap layer 1 (lossless history) under layer 4 (bounded working view).

## What each term meant when it was written (Brian, 2026-09-26)
An initial outline of candidate kinds, not settled components:
- **State** = something structured, like SKILL.state (current task/procedure state as a schema, not prose).
- **Memory** = a smart memory system like Perseus that handles supersession, conflicts, lifecycle ("what it has learned").
- **History** = pi-lcm's lossless context database, or a full transcript history, or both.
- **Artifacts** = the actual files, configs, logs, outputs: ground truth.
- **Executive reasoning** = the model/agent that interprets all of the above.
Treat the named systems as examples of each role to be re-evaluated in the roster refresh, not as choices already made.

## High-priority sponsor correction: dependable improvement over existing upkeep

**26 September2026, Brian via Claude; supersedes any survey framing of agent-owned upkeep as a new benefit.**

> “It almost sounds like you're just telling me to keep my own notes in a file.”
>
> “Agents aren't paragons of reliability. Claude already is supposed to do the noticing and writing down. What improvements are being suggested?”

**Baseline:** agent-owned noticing, capture and revision are already the status quo, and already fail. Recommending better notes or assigning the same diligence to the acting agent is not an improvement. Brian is not to become the librarian or verifier.

**Observed-stack report supplied by Brian/Claude, not independently audited by this survey:** capture mostly works (~150 Claude memory files); delivery fails because the MEMORY.md index is truncated, with109 of301 entries never loading; application is reported as the largest failure—feedback memories often exist because the agent repeated the mistake after saving the lesson. These counts refer to different units (files versus index entries); do not merge them into a capture or failure rate. The CLIN stored-but-not-selected pattern is an analogy, not validation of Brian's incidence or causal localization.

**Claude's proposed improvements for the panel to challenge, refine or replace:**

1. Enforcement over reminders: encode checkable preferences in a hook, tool or default (examples supplied: `python` rather than `python3`, no `127.0.0.1`, no `rm -rf`, kill by PID); keep judgment in memory. Determine actual scope and the execution path covered; a written instruction or an optional helper is not enforcement.
2. Capture from transcripts, independent of the acting agent noticing: a nightly job mines corrections and repeated problems. Cheap typed classification is a candidate mechanism, not established fitness. The cycle67 Laya supersession failure neither validates this different task nor rules out all classifiers.
3. Relevance-triggered delivery plus a mechanical guarantee that the index stays within the host's actual load limit. Storage, selection, delivery and application are different stages; preventing truncation alone does not guarantee compliance.
4. An automatic weekly count of re-explanations/repeated preferences in transcripts as the proposed outcome measure. Distinguish repeated corrections from quoted examples, legitimate scope changes and new instructions; silence is not success. No new rating or labeling duty for Brian.

**Survey question now:** which improvements do not depend on the acting agent's diligence, and what does the field offer for each? Every proposed improvement must name the independent trigger or enforcement point, the failed operation it changes, the diligence it removes, the residual judgment, and the relevant evidence. A scheduled model remains fallible; moving judgment off the actor removes a noticing/trigger dependency, not semantic error.

These are sponsor priorities and candidate directions for research. This message does not itself install hooks, schedule jobs, alter command policy or authorize a new experiment. The previously authorized single Laya probe is complete.


**Additional sponsor constraint, same entry — one characterizable operational design (26 September2026, Brian via Claude).** Brian is wary of an ad-hoc system that accretes scripts, files and patch layers until its behavior cannot be characterized, as happened with fleet loop v1. **Recommend nothing to build until it is describable as ONE design with named components, a stated contract for each, an owner, and tests.**

Prefer an existing product or an existing mechanism extended in one place—for example Claude Code hooks configuration, a cc-safety-net rulebook, or Pi extensions—over new standalone scripts and loosely connected jobs. This is a preference for a coherent, characterizable system, not a requirement that everything be one process or a claim that a product is automatically coherent.

Compare adopting **ReMe, Hindsight, Pi reflection or claude-mem** with composing parts partly on this basis: named boundaries, clear ownership, testable behavior, integration and upgrade burden, and the amount of custom glue. Identify what actually enforces or triggers each operation, where judgment remains, and how failures are visible. An upstream maintainer does not by itself own Brian's deployment; name the operational owner in a concrete recommendation rather than assigning the work back to Brian by implication.

The four proposed improvements above are responsibilities to investigate, **not four separate scripts to build**. Until a candidate satisfies this design constraint, label it a research option or an incomplete design and withhold the build recommendation. No installation or production change is authorized by this constraint.


**Sponsor clarification — avoid audit-mode analysis paralysis (26 September2026).** Brian: “as long as we don't slip back into audit-mode analysis-paralysis.” This supersedes any interpretation above that unknowns require serial reviews or prevent an opinionated recommendation. The design constraint governs the **shape of the final recommendation**, not a new review gate on each research or design step.

**Deliver by29September2026:** ONE one-page recommended design for Brian's stack, naming components, each contract, operational owner and how to test it; one named first pilot Brian can approve; and Tern's confidence. Make a choice. List open questions explicitly rather than treating them as blockers. Prefer an existing coherent product/mechanism where warranted, but do not wait for exhaustive source audits of every alternative. Proposed tests can be part of the pilot; they need not all have run before recommending it. Pilot approval is distinct from recommendation writing.

**Small-probe rule:** one memory decision, roughly50–100labeled items, majority and keyword baselines, one run, one result. No scorer framework or multi-round panel review. The already-completed Laya run used46pre-existing labeled cases and both baselines; retain that result without rerunning to reach50, changing thresholds, or generalizing the one-off scorer. No additional experiment is requested here. Note a caveat and move on unless it would change the recommendation.
