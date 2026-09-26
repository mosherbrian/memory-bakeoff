# Evidence note c69 — what actually changes when the actor ignores the saved lesson

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 69.**
Skeleton first; existing reads only (AutoGuide c39, CLIN c41, PAIR c54, Self-Portrait c52,
STALE c68, Laya probe c67, SQuAD-gating intake, keep/replace inventory); **no new primary needed,
no probe/install**. Sponsor counts are observations, different units, not audited incidence.
Question per proposal: mechanism, outcome, or neither — and what changes at the moment the actor
ignores a stored lesson.

*(verdicts + metric design appended below)*

## The commission's crucial question first

**Does any control demonstrate fewer repeated mistakes when capture was already present?**
**No field control exists in the corpus.** The closest is STALE §4.4/§5 `[read]`: both memories
stored, new evidence retrieved in 77.5% of cases — and behavior still fails; adding **write-side
adjudication** (CUPMem) improves outcomes **on their benchmark**. That is the only read where
stored-but-stale content starts governing action because a control was inserted. Supporting
negative evidence: same-backbone memory frameworks mostly **do not beat the plain model**
(17.8 vs 8.7 the only gain); recognition ≠ application (SR 92 → PR 30); CLIN's
stored-but-not-selected; PAIR's persistence complaints with capture nominally working.

## Per-proposal verdicts (mechanism / outcome / neither)

**1. Enforcement hooks (checkable preferences).** **Mechanism: supported** — deterministic
interception is the corpus's own most-attested pattern (mechanical checks caught every false
"done"; the SQuAD test: the string check held hallucination at 5.3%, the model added nothing).
**Outcome for preference compliance: measured nowhere.** If the actor ignores the lesson: the
action is **blocked or rewritten at execution** — the only proposal where ignoring is impossible,
**within encoded paths**; residual judgment = scope definition and path coverage.

**2. Nightly transcript mining.** **Independent trigger: yes** (runs without the actor noticing).
**Judgment: unsupported** — the corpus's mining evidence is weak (rule/LM mining null c42; the
c67 classifier lost to majority on an adjacent typed task; c67 establishes neither direction for
mining specifically). **Outcome: neither.** And it targets supply, while the reported bottleneck
is application — **more stored lessons is the one thing already failing.**

**3. Relevance delivery + mechanical load-cap guard.** **Mechanism: supported twice over** —
109/301 unloaded is arithmetic, not judgment; and STALE shows delivery format matters (retrieval
present, authority absent). **Outcome: unmeasured**; STALE's warning applies exactly: fixing
visibility does **not** confer authority. If the actor ignores the lesson: the excuse "it wasn't
loaded" is removed; ignoring remains possible.

**4. Weekly recurrence count.** **Neither** — no read runs one. Observability only; nothing
changes at the moment of action.

## Fair automatic weekly recurrence measure (no Brian labeling)

**Numerator: violation events, not complaint absence.** A saved checkable preference is violated
when the transcript shows the corrected action performed again — detectable by the **same typed
pattern the hook would check** (verbatim-quote + string check, the corpus's own validated shape).
**Unit: same-scope repeats** — a correction restated for the same entity/action in a **later
session**. **Excluded:** first occurrences of a scope (new instructions), same-session restatements
(quotes), and anything the matcher cannot quote verbatim (audited band, not counted).
**Silence ≠ success:** the count is driven by observable violations; absence of complaints counts
as nothing either way (PAIR: users went silent while persistence failed). Report weekly trend per
lesson, no thresholds, no labels.

**Trigger independence ≠ judgment reliability:** mining's trigger is independent; its
correction-identification is still model judgment — the part with the weakest evidence.

**Ordering the evidence supports:** enforcement and the load-cap guard act **before** the failure
moment; mining and counting act on supply/observation. Default order stands; the honest gap is
that **no read measures hook-based preference compliance — that is the first thing the revised
memo should make observable.**

**Confidence: high on the no-outcome-control survey (searched corpus), high on mechanism
readings for 1/3 (deterministic), medium that violation-pattern detection works for checkable
preferences only (untestable preferences have no typed pattern — residual, stated).**

## Addendum — the one characterizable design required before any build recommendation

Per the binding sponsor refinement: components, contracts, owner, tests — each item an extension
of **one existing mechanism in one place**, not a new script.

**A. Enforcement (host hook facility — Claude Code hooks / pi extension point).**
Components: one hook-config entry per checkable preference. Contract: matching execution is
blocked or rewritten, and a decision line is appended to the hook log; non-matching traffic
untouched. Owner: Brian approves each entry; the agent may only propose from stored lessons.
Tests: fixture commands (the sponsor's four examples) blocked/allowed as specified in a sandbox.

**B. Load-cap guard (the existing index loader, not a wrapper).**
Components: cap constant = host's measured load limit. Contract: an index over cap is refused at
write with an entry-level report — every entry is either loaded or named as unloaded; silent
truncation impossible. Owner: host product. Tests: fixture index > cap → full accounting.

**C. Recurrence metric (extends the existing append-only ledger + computed-rowcheck pattern).**
Components: violation-ledger line = (lesson id, session, verbatim quote, pattern id). Contract:
lines are appended **only by the mechanical string check**, never by model judgment; weekly
figure is computed from the ledger, not authored. Owner: the poller that already runs. Tests:
fixture transcripts → expected counts with first-occurrences and same-session restatements
excluded.

**And the boundary the refinement sharpens: contract tests prove the mechanism conforms; they are
not evidence of fewer mistakes.** A-passing hook suite plus a falling violation trend are two
different claims — the second is exactly what no read measured, and it remains the only outcome
evidence that would justify the build. No new artifacts beyond these three extensions; mining
stays unbuilt (judgment unsupported above).

— cairn. Inputs: BRIAN-PRINCIPLES sponsor section, ROLES.md, both roadmap inputs, COVERAGE.md,
DEPENDABILITY-IMPROVEMENTS.md.