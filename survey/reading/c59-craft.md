# Reading note — CRAFT: collect validated solutions, abstract into tools, retrieve at answer time — what do the controls isolate?

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 59.**
One source, identity per commission: **Yuan, Chen, Wang, Fung, Peng, Ji — "CRAFT: Customizing
LLMs by Creating and Retrieving from Specialized Toolsets," arXiv 2309.17428v2 (13 Mar 2024,
ICLR 2024).** Methods, verification/abstraction and retrieval controls only.

C58 corrections carried: acquisition ablations may not isolate library content purely; FRIDAY's
admission included a **reuse-potential score (>8)** beyond the completion verdict; the
package-choice moderator is inferred, not varied; no "largest-in-corpus" or 10-task/8-tool
recipe claims; GPT-4-only results do not measure local-model transfer.

**Frame held before the read (minimal):** CRAFT's pitch fixes FRIDAY's weak seam — tools are
built from **existing solutions already marked successful in the training data** (validation by
label, not critic opinion), then **abstracted** (generalized signatures), deduplicated, and
retrieved by task similarity at answer time. Panel questions: who supplies the success label,
what exactly is checked, is the executor held fixed across comparisons, and are acquisition and
reuse costs priced. Written skeleton first; facts after the read.

*(facts + verdict appended after read)*

## Label-grounded admission, abstraction re-checked, acquisition priced (2309.17428v2, §2.1–2.2, §3.1, §4.1–4.4) `[read]`

**Who supplies validation: the dataset's ground-truth answers.** Tools are built from **train
splits** (TabMWP, MATH-algebra; sampled problems with known answers). Pipeline: **Generation**
(GPT-4 writes code solutions; keep only bug-free ones producing the correct answer — min-max
SimCSE sampling for diversity) → **Abstraction** (GPT-4 generalizes variable names, wraps inputs
as arguments, writes function name + docstring) → **Validation: the abstracted tool must re-solve
the ORIGINAL problem with proper arguments; failures discarded** — validation **after**
abstraction, against labels, not critic opinion → **Deduplication** (group by function name +
arity; GPT-4 keeps the most comprehensive). Lifecycle is **discard-only**: no repair or revision
path is described.

**Retrieval:** the answering LLM "describes what it needs"; multi-view matching over
{problem, function name, docstring}. Ablations (Table 3): removing **any** view hurts; function
names alone cost >6.6 SAcc when dropped — **the name is the retrieval handle**.

**Executor held fixed; maker/user split again:** main runs use a **GPT-3.5 backbone with
GPT-4-created tools** vs same-backbone baselines including ViperGPT (writes code at answer time,
no stored set). §4.3: with a **GPT-4 backbone the gain shrinks** — the authors align with
evidence that models benefit from stronger-model guidance, not their own. Consistent with
LATM/FRIDAY capacity asymmetry; **GPT-3.5 is still not a local model** (c58 correction).

**Held-out and scaling:** evaluation on test splits; toolset-size curve rises monotonically,
**largest jump 0→261 tools**, still trending up.

**Costs — the rare one:** "around **$2,500** in total" for toolset construction (GPT-4 calls
across the four steps); answer-time cost argued cheaper than GPT-4 use; no per-reuse ledger.
First acquisition price-tag in this cycle's family (LATM's creation cost went uncharged in its
table; the ~$14 estimate belongs to AutoManual, c38) — the range, not a recipe.

**Verdict: CRAFT is the best-supervised tool-acquisition read in the panel — labels gate
admission twice (solution correctness, then abstraction re-solve), evaluation is held-out, the
executor is fixed, components are ablated, and acquisition is priced.** Remaining unknowns:
no changed-environment test; discard-only lifecycle (no correction of a near-miss tool); gains
concentrated where user capacity < author capacity, local executors untested. For Brian: the
**pipeline order is borrowable without the harness** — after generalizing a procedure, re-run it
on the original case before saving; dedup by name+arity; name deliberately. That re-check is
exactly the operation FRIDAY's critic gate lacks. Confidence: high on pipeline/ablations/cost
statement (explicit), medium that label-grounded validation transfers to domains without answer
labels (Brian's preferences have none), high that no drift test exists (searched).

— cairn. Source `[read]`: arXiv HTML 2309.17428v2, opened 2026-09-26; c58 corrections carried
(admission-with-score, package-moderator inferred, no largest-in-corpus/recipe claims,
local-transfer unmeasured).

— cairn. Source: arXiv 2309.17428v2, opened today.