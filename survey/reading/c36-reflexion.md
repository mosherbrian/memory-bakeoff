# Reading note — Reflexion: how much of 91% is learning, and how much is just more tries

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 36.**
One methods/control read (Tern): **Reflexion, Shinn et al., arXiv:2303.11366** — full methods,
upgrading my c1 `[card]` note ("verbal self-critique in an episodic buffer replayed in the
prompt; lesson is a remembered claim with no check" — card-level, now checked at source).
Questions: separate **actor / evaluator / reflection** models per domain (acting, QA, coding);
**true environment signal vs self-generated tests/judgment**; the **exact trial budget and
denominator** behind the headline 91% pass@1 (HumanEval); **what controls isolate reflection
from extra attempts/feedback**; and is **held-out-task reuse of the accumulated buffer**
actually evaluated? One useful idea + unresolved transfer/cost limit. No ReMe re-sweep.

C35 qualifications carried: the access-ablation concerns availability of already-synthesized
reflections, not isolation of a unique online synthesis operation; and — correcting my own
c35 phrasing — believability-only does **not** mean raters necessarily ignore false details;
the defensible claim is the **absence of a separate accuracy metric**.

**Provisional frame (before the read).** Reflexion: trial → binary-ish signal → LLM writes a
verbal self-reflection → buffer (sliding window, last ~1–3) replayed in the next attempt,
same task, up to N trials. The distinction this cycle needs: **current-task retry** (memory
lives only until the task is solved) vs **reusable learning** (buffer persists across tasks).
My card-level expectation: the wins are retry-shaped, the evaluator is often the environment
(unit tests, exact match) but in some QA settings is self-generated, and cross-task reuse is
*not* the measured claim. Written skeleton first; facts after the read.

*(facts + verdict appended after read)*

## How much of 91% is learning (2303.11366v6, §3 actor/evaluator/reflection/memory, §4.1–4.3,
ablation, §5) `[read]`

**Actor / evaluator / reflection are separate model calls** (same base LLM, GPT-4, in headline
runs; a *different* LLM instantiation tested as evaluator in variants). Signal provenance splits
by domain: ALFWorld = environment success (true); HotPotQA = exact-match vs gold (true);
**programming = self-generated unit tests** (CoT-generated suite, AST-filtered, ≤6 tests) — the
headline 91% runs on a self-generated judge.

**The 91% denominator:** HumanEval-PY (full set), pass@1 scored by the **hidden official suite**,
"base strategy is a single code generation sample"; Reflexion = up to a max-trial cap ("a
handful"; loop `while not pass or max trials`), **memory limit = 1 experience** for programming.
80.1 → 91.0. Crucially **not monotone: MBPP-Python 80.1 → 77.1 — Reflexion LOSES there.**

**Table 2 is the paper's most transferable object** — evaluator confusion vs ground truth:
HumanEval-PY self-tests: **FN 0.40** (tests fail, solution correct) but **FP 0.01** (tests pass,
solution wrong). The loop survives massive false-negatives because a retry can keep the code;
false-positives are terminal. MBPP: **FP 0.16** — one in six accepted submissions is wrong →
net loss below baseline. Cleanest quantification in the sweep of what self-judging costs.

**What isolates reflection from extra attempts:** the Rust ablation (50 hardest): base 0.60;
**test-generation-only (retry, no reflection) 0.60 — extra attempts alone add nothing**;
reflection-without-test-generation 0.52 (below base); full 0.68. On that subset reflection
carries the entire gain — but note the subset is the hardest-50, not the headline set.

**Held-out reuse of the buffer? Not evaluated.** The loop is same-task retry; programming memory
is capped at **one** experience; nothing carries across problems. Reflexion is retry-shaping,
not accumulated learning — my c1 card note ("remembered claim with no check") holds and is now
`[read]`-confirmed, with the refinement that the *trigger* in coding is a check — just one the
author wrote for itself.

**Verdict: solid methods paper whose own tables bound its own headline.** Confidence: high on
mechanism and Table 2, high on non-monotonicity (their words: "except MBPP Python"), medium on
trial-budget specifics (cap stated loosely).

**One useful idea:** report the **retry-trigger's FP/FN against ground truth** — red-but-right
is recoverable, green-but-wrong is terminal; any run-until-green loop owes you its FP rate.
**Unresolved limit:** self-written tests inherit the author's blind spots (MBPP loss), and the
per-task buffer amortizes nothing — transfer to Brian's "retry until the checker passes" is
exactly conditional on the checker not being self-authored.

— cairn. Source `[read]`: arXiv HTML 2303.11366v6, opened 2026-09-26; c35 qualifications
carried (access-ablation scope; defensible claim = absence of separate accuracy metric).