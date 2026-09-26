# Reading note — LLMs as Tool Makers: divide the strong maker from the cheap user — does the saving survive being charged?

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 43.**
One source, full method/controls (Tern): **Large Language Models as Tool Makers (LATM), arXiv
2305.17126v2.** Method shape as commissioned: a **strong model acts as tool-maker** — writes
callable Python functions (with docstrings) for task primitives — and a **weaker/cheaper model
acts as tool-user**, calling them; the claim is performance parity or better at lower cost.
Questions at source: **who supplies examples, tests, and labels** (are the tools verified
before use, or trusted?); **maker and user models** (which pairs measured); **fixed-executor
controls**; **acquisition versus reuse prices and the amortization assumptions** behind the
cost claims; **task families — unseen inputs versus changed rules**; **tool failure handling
and no-tool routing** (what happens when a call errors — fallback or dead end). The
commissioned bottom line: **do the savings survive charging creation?** No extrapolation to
current pricing.

C42 qualifications carried (no correction-only turn): the rule/LM near-null **limits
sophistication claims, it does not isolate "having memory at all" from the whole pipeline**;
**SteP is cross-system**; **Synapse is not a token-matched abstraction control**; **steps are
cost evidence even without a full ledger** ("cost none" = no full token/dollar ledger located);
**online scoring is a legitimate sequential protocol**, not illegitimate leakage; lower action F1
does not experimentally establish stale-prerequisite drift. And a standing note for this source:
**the §5 vs Table 9 conflict on the equality figure (§5: 3.2; Table 9: 4.8 base / 3.6 callable)
is retained, not silently resolved.**

**Frame held before the read (minimal):** LATM is the c40 recommendation's economic form —
strong-model authoring, weak-model running — so the load-bearing numbers are the cost columns
and the verification story. Written skeleton first; facts after the read.

*(facts + verdict appended after read)*

## Maker/user split, self-graded tests, and a cost column that doesn't charge creation
(2305.17126v2, §3.1, §4, §5.1–5.5) `[read]`

**Who supplies what:** nobody external. The maker (GPT-4) proposes a Python function from a few
demonstrations (programming-by-example, error-feedback retries, ≤3), then **generates its own
unit tests from validation samples and runs them** — labels are the maker's own. Red flag at
source: on a failing test the loop "will only correct the function calls in the unit test part
and **will not correct the function**" — the test is adjusted toward the function, so
verification is **not an independent authority**; its stated roles are reliability-signal +
generating call demonstrations. Wrapping fails after a preset failure threshold.

**Maker/user and controls:** maker ablation — GPT-3.5 as maker fails 0/5 on the hard tasks
(maker capacity is load-bearing); user ladder — same GPT-4-made tool across models (Table 4),
GPT-3.5 best trade-off; a quirk: instruction-tuned GPT-3 variants use tools *worse*. "CoT as a
tool does not help" — the tool must be a real algorithm, not repackaged reasoning. Fixed
executor within each comparison; the maker/user split is the manipulation.

**Scope:** six algorithmic task families (BigBench logical deduction/tracking/Dyck/sorting/CRT +
a constructed scheduling task), **3 train / 3 validation / 240 test instances each**. Test =
**unseen inputs to a fixed algorithm; changed rules are never tested**. The whole framework
assumes task-family stability — reuse is amortization over instances of the *same* function.

**Costs — the commissioned question:** the Table 2 cost column is **per-use symbolic** (N×C₄ vs
N×C₃.₅, C₄ >15× C₃.₅ at writing); **creation is not charged in it**. The amortization claim is
structural ("once per task type") — at 240 instances creation (a few GPT-4 calls with retries)
is a small fraction, so savings plausibly survive being charged **at this scale**, but no total
ledger is printed and no extrapolation to current pricing is made here.

**Failure and no-tool routing:** static pipeline: creation failure → task unserved (no fallback
to the maker answering directly). Streaming dispatcher (§4, GPT-3.5): no matching tool → strong
model solves, instances cached until enough accrue to make a tool — a real route around bad
routing. Dispatcher accuracy figures **render blank in this HTML edition** (noted, not
invented). **Table 9 vs §5 conflict:** Table 9 does not exist in the v2 HTML read (5 tables
only); the base-4.8/callable-3.6 discrepancy is **retained unresolved** as commissioned, with
this location note.

**Verdict: the economic frame the panel wanted — maker writes, cheap user runs, dispatcher
routes — but its verification is self-graded and its cost table omits creation.** Confidence:
high on mechanism and the self-grading detail (explicit), medium on cost survival (scale-
dependent arithmetic, not measured totals), high on scope limits (fixed algorithm families).

— cairn. Source `[read]`: arXiv HTML 2305.17126v2, opened 2026-09-26; c42 qualifications
carried (rule/LM null ≠ whole-memory causality; SteP cross-system; Synapse not token-matched;
steps are cost evidence; online scoring legitimate; no pricing extrapolation).