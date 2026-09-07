# The brief given to both independent accountants

Verbatim. Sent 2026-09-07 to glm-5.3 and glm-5.3-flash simultaneously, each in
its own isolated git worktree of this repository, blind to each other and to the
implementer's own accounting.

Harness: `~/rivals/review-generation`, which runs both models in parallel via Pi
with repository read access and shell, then adjudicates their verdicts. Timeout
5400s each. Neither model was shown the implementer's document, and neither was
told what it concluded.

**Why this file exists:** a board cannot judge an elicited opinion without
seeing how it was elicited. If the brief were leading, the accountings would be
worth less. It is posted so that judgement can be made independently.

---

## Prompt, verbatim

You are NOT reviewing a generation this time. Brian, who owns this project, is taking it to an external review board and wants an INDEPENDENT accounting from someone who is not its author. The implementer has written one; you have deliberately NOT been shown it, so do not look for it and do not try to agree with it.

Write YOUR OWN accounting of this project, from the repository. Read whatever you need: git log and timestamps, results/, reviews/LEDGER.md in full, ROUND3_FINAL_READOUT.md, handoff/CODEX_TO_CHATGPT.md, research/, tests/KNOWN_FAILURES.json, control-plane/. Recompute anything you cite.

Your FIRST line must be exactly one of:
VERDICT: SOUND
VERDICT: DEFECTS_MINOR
VERDICT: DEFECTS_BLOCKING
- judging the PROJECT's evidentiary health, not any one generation.

Then write the accounting itself, structured as:

1. WHAT THIS PROJECT IS FOR - in plain language, from the repository's own words.
2. WHAT IT HAS ACTUALLY PRODUCED - findings that would survive an outside auditor. Name them, cite the file, and say what each one licenses someone to believe. Separate replicated results from single observations and from retracted ones.
3. WHAT IT HAS NOT PRODUCED - the gaps, stated as flatly as the findings.
4. WHERE THE EFFORT WENT - use git timestamps and the ledger to say where time and rework actually went. Quantify if you can.
5. THE FAILURE MODES, ranked by how much they cost - and say for each whether it is a process problem, a tooling problem, or an implementer problem. Be specific and unsparing; the implementer's self-assessment is not evidence and you should not defer to it.
6. WHAT YOU WOULD RECOMMEND TO THE BOARD - concrete options with rough costs, and your own ranked recommendation.

Rules: cite file and line for every factual claim. If a number cannot be reproduced from the tree, say so rather than repeating it. Where the repository's own documents disagree with each other, say which you believe and why. If you think this project should stop, say so plainly - that is a legitimate finding and Brian has asked for candour, not encouragement.
