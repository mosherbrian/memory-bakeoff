# Local outcome first rung — Brian's scope answers, 2026-09-19

Source: Brian's message in Tern's director thread, headed "stage two requirement, and four answers", explicitly confirming the following answers. Recorded by Tern. This is a decision record, not a run receipt or sprint selection.

It resolves the four questions under "Open questions for Stratum/Brian" in `SPEC-OUTCOME-PROTOCOL.md` §10 for the local first rung only. It does not authorize the private-transcript scale-up or replace the frozen protocol silently; the pilot needs its own scoped preregistration.

| Original question | Confirmed answer | Scope/status |
|---|---|---|
| does design A run on the work machine or the fleet? | "THE FLEET, cairn as subject, your local first rung. His work machine is already running R2 separately." | Resolved for the local pilot. |
| which two systems for design B? | "not needed for the first rung; design A is memory on/off within one worker." | Not applicable to this pilot; no system selection for a later Design B is implied. |
| token budget and n | "yours: two unscored plumbing pairs, then eight scored pairs, 20 task executions, $0 incremental, one to two days of instrumentation." | Pilot envelope confirmed; Tern owns the numeric per-run token/time limits and preregistration. The instrumentation duration is an estimate, not a completion guarantee. |
| whether the scale-up transcript run is authorized before M4 calibration | "NOT YET. That is the one that needs his private transcripts and it can wait; it is the scale-up, not the pilot." | Explicitly deferred; private-transcript access remains unauthorized. |

The authorized pilot is local-only, uses bake-off tasks and no private transcripts, and has $0 incremental API spend. Its serving model and memory treatment must be pinned; the evidence-use check, matched starting states, arm isolation, outcome definitions and stopping rules must be registered before scored work. Operator corrections remain unmeasured unless a valid operator-observation design is separately specified; scripted corrections are instrument checks, not measured human burden.

The prior blanket blocker "Brian's campaign-2 window/scope call" no longer applies to this pilot. Remaining preparation belongs to the fleet, not to an unanswered Brian scope decision. The random-60 index review remains the next checkpoint. This record neither selects the pilot into a sprint nor starts executions.

## Design note — a memory-selection hypothesis from the field (not an M3 rule)

Source: r/LocalLLaMA, "What are you all using for long term project/conversational
memory these days?", https://www.reddit.com/r/LocalLLaMA/comments/1wl3828/what
— commenter `redtortuga19`, read 2026-09-19. No comment permalink was captured in
the PDF Brian supplied; the handle and thread are the provenance available.

> Unverified practitioner anecdote suggests selecting candidate memories by
> anticipated reductions in context use and tool calls; this is a
> memory-selection hypothesis, not an observed saving or an M3 scoring rule.

WHY IT IS FILED HERE AND NOT AGAINST M3 (Tern, 2026-09-19). M3 already has an
operational definition — count rediscovery of facts held at task start, using
canonical identifiers, separating delivered records from available-only ones —
and what is missing is its instrumentation, not its meaning. The anecdote asks a
DIFFERENT question: "what missing memory would have prevented work?" That is a
retrospective counterfactual. M3 asks "was work repeated despite an existing
memory?", which needs observed records and observed behaviour. Attaching the
first to the second would blur the distinction and leave two definitions of one
metric standing side by side.

The commenter's wider setup is recorded only as context, not as a candidate:
Pi with a per-repo SQLite store holding entities, groups, values, notes and
relationships, and the framing "deterministic memory: this term equals this
thing; probabilistic memory: BM25, embedding, reranking."
