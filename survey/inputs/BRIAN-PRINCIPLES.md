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
