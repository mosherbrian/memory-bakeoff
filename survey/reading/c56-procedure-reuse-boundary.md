# Reading note — procedure reuse for the model-test/rollout family: one control, one untested claim

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 56.**
Own c41–c45 only; no new paper. Illustrative family (model-test/rollout from c19/c23) — **not**
a claim about Brian's measured incidence. Question: for the worked minimal arrangement (first
successful run → stored conditional procedure → later reuse), which control supports it, and
which changed-condition claim remains untested?

**The one supporting control — LATM's maker/user split (c43)** `[read]`: tools authored by a
strong model executed successfully by a weaker executor. It is the only control in c41–45 that
validates the exact chain the arrangement needs — **write once with capacity, run later without
it** — and it fits Brian's shape (strong authoring pass, local models running the result).
AWM's rule-vs-LM mining near-null (c42) `[read]` is supporting, not load-bearing: it says the
**mining can be dumb** (35.6 vs 35.5), which licenses plain dedup-and-save, but it never tests
the author→executor transfer.

**Separating the three operations:**
- **Writing** — best-evidenced form is CLIN-style (c41) `[read]`: constrained, scope-first rules
  rewritten at trial end; but CLIN's rules were never tested for later reuse, and AWM's online
  arm reused the test stream itself, so **writing is evidenced as feasible, not as valuable**.
- **Selecting** — read-time applicability ("is this the right procedure for this situation?")
  is measured by **none** of c41–45; the c40 unknown stands.
- **Executing** — CaP (c44) `[read]` shows stored reactive code generalizes within attribute
  ranges where imitation collapses, but it is a **within-session artifact**, not accumulated
  reuse; LATM's self-graded tests remain the red flag: a failing check gets its test corrected,
  not the function.

**The untested changed-condition claim:** nothing in c41–45 runs a stored procedure **after the
environment changes** — new model version, renamed config, shifted API. The arrangement assumes
the validation step catches drift; no source measures catch rate, silent misapplication, or who
repairs. CaP's attribute generalization is the closest evidence and it is inside one task family
with the code visible — not drift across months.

**Verdict: the arrangement (strong-author, dumb-mine, local-execute, validate-before-trust)
stands on one real control (LATM transfer) and one permanent gap (selection accuracy), with
drift-catching assumed.** Anyone presenting it as measured should be quoted to these two lines.

**Confidence: high that these are the controls and gaps in c41–45 (re-read of own notes), medium
that LATM transfer extends to config-shaped procedures (LATM's were algorithmic functions).**

— cairn. Built from reading/c41–c45; c55 corrections applied in-file there.