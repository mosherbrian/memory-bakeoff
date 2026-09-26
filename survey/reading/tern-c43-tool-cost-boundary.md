# LATM: cost model, routing evidence and the helper boundary

Tern · cycle43 · 26 September2026 · primary §§3–5 read; Reader synthesis pending. [LATM v2](https://arxiv.org/html/2305.17126v2). High confidence in protocol; medium practical transfer.

LATM uses three construction demonstrations and three validation samples. Verification repairs the generated test calls rather than the function; proposing has its own error retries. The cached artifact includes code and calling examples. A separate dispatcher selects existing tools or requests construction; the user model translates the query into arguments.

Routing is directly evaluated: existing-tool identification95±2%, construction request96±3%, on small mixtures of task families. This is a concrete addition to our selection evidence. It does not measure ambiguous software applicability or changed-version routing.

The paper gives an asymptotic creation-plus-reuse cost model and historical token rates, not a measured complete amortization ledger. Maker failures and retries matter. Table3 also makes tool-making competence conditional; Table4 shows weak users can fail despite a fixed tool. No present-day price or Brian-specific break-even follows. [Source §§3–5](https://arxiv.org/html/2305.17126v2#S3).

**Opinion:** keep generated helpers alongside textual procedures. A helper can eliminate repeated computation without eliminating extraction, routing or judgment. This is stronger than simply remembering an answer, and consistent with Brian’s artifact/executive distinction. Preserve the editable tool and the reason for using it; do not turn a measured validation sample into a universal correctness promise.

**Practical qualification:** “compute versus perceive” is not a sound division between code and prose. An agent can observe current conditions and pass them to a function; code can also explicitly observe, branch and validate. LATM’s evaluated tasks do not establish those environmental capabilities, but their absence from this evaluation does not exclude helpers from rollout or triage work. Nor do we know that Brian lacks usable examples or checks. The default producer can remain the agent; no human-authorship requirement follows.

**Open for synthesis:** charge construction attempts, labeled-example acquisition, user calls, routing and maintenance. A frozen tool can amortize under stable repeated use while an infrequently reused or frequently changing one may not. These are decision conditions, not a new per-task accounting mandate.

## Continued reading: what would have to amortize

Appendix E’s meeting task is generated from two availability sets and an interval, with an algorithmically computed answer. It is not observed calendar administration or a deployment workflow. Appendix C/D content is not rendered in the HTML inspected; do not claim the prompts or wrapped-code examples have been fully read from that page. [Source](https://arxiv.org/html/2305.17126v2#A5).

**Tern’s accounting model, not a paper result:** let A be creation/validation cost, M expected maintenance, B cost per comparable baseline resolution, and U the helper path including dispatch, argument extraction and execution. Reuse can repay A+M only when U<B and the number of uses exceeds (A+M)/(B-U), at an acceptable outcome quality. Quality and the cost currency must remain explicit; a token saving does not price Brian’s attention. No numeric threshold is justified for his workload from this source.

This favors a practical choice, not an instrumentation project: create the small helper when the reusable computation and likely recurrence are already evident; retain prose and observation for the uncertain parts. The paper supports this division under its task distribution, while real maintenance and changing prerequisites remain open.

## Completed reader synthesis: two corrections that change the conclusion

Cairn’s full piece is now received. Table2 explicitly gives the cheaper-user LATM cost as O(nc+C): creation is represented symbolically, not omitted. Unknown constants, retries, input lengths, supervision and maintenance still prevent a measured break-even claim. Merely having240 test inputs does not establish that creation is a small fraction in this implementation.

The [author toolmaker notebook](https://github.com/ctlllll/LLM-ToolMaker/blob/main/toolmaker.ipynb) resolves label provenance: get_task reads dataset target into answer; the validation prompt includes each Question/Answer and instructs an assertion against the provided answer. The model writes argument parsing and assertion code. This is fallible model-authored verification against supplied labels, not labels invented by the maker. The runner executes generated verification without an independently enforced assertion schema; parsing or test mistakes remain possible. Do not infer measured test weakening from the instruction to fix function calls.

Notebook split detail: get_task allocates first5/next5/rest, while tool_making defaults and the shown invocation use3 training and3 validation examples. The paper’s3/3/240 description should not be silently equated to a six-example consecutive split in this notebook. Read only; nothing executed.

The dispatcher figures are visible in the lead’s HTML read (§5.4), so a renderer gap in another read is not a source-wide absence. Its no-match path handles a recognized missing tool; it does not necessarily catch a wrong positive match. The carried Table9 discrepancy is exclusively AWM/cycle42, not LATM.
