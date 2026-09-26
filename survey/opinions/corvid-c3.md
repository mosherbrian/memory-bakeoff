# Contrarian, cycle 3 — the case against promoting preferences

**corvid · 2026-09-26 · cycle 3.** Signed opinion, not an audit. ROLES.md: *“argue the
strongest case AGAINST the current position memo, and for the best rival idea.”* Confidence =
transfer to Brian.

**Strongest rival: inferred personalization with a small correction channel** — let the agent
learn preferences from behavior, keep only *authority-bearing* directions explicit. The memo's
bet 2 (“promote repeated preferences into explicit scoped instructions”) treats articulation as
cheap and reliable; the evidence says articulation is the scarce resource.

**Where the rival wins.** (1) *Tacit preferences.* Most repeated preferences are never stated;
they are visible only in choices. AlpsBench, built from 2,500 real WildChat dialogues, finds
explicit information is captured by surface-level matching whereas **implicit preferences
“require stronger inference over conversational context”** — and, pointedly, that **“explicit
memory mechanisms do not inherently ensure stronger preference alignment.”** `[read]` (2)
*Satisfaction ≠ compliance.* PrefEval measures recognition/memory/application of stated
preferences `[read]` — that is a compliance target, not whether Brian was better served. An
explicit rule (“always bench at 12288”) promoted from a past context will be obeyed in a context
where a different length is right; the record makes the agent *less* satisfying while *more*
compliant. (3) *Multi-agent conflict.* Declared instructions are a shared, contested resource:
nested instruction files concatenate and “later” is not a reliable override (kiln’s doc read),
so promoting the same preference into Claude Code, Pi and local agents multiplies conflicting
copies. Inferred per-context behavior needs no global precedence rule.

**When implicit beats the record.** High-frequency, low-stakes, context-dependent style and
method choices (formatting, naming, verbosity, which tool first) with dense behavioral signal
and a cheap correction path. The record wins for safety-relevant, irreversible, cross-session,
authority-bearing directions — where a wrong inference is expensive or unauditable.

**Realistic reversal that makes my rival fail.** BESPOKE’s oracle condition is the reversal:
given the *explicitly stated* need, alignment jumps (o3-search 83.47 need / 88.13 tone) versus
inferring it from noisy history. `[read]` So if histories are sparse/short, if corrections are
rare and the stakes are high, or if the same preference must bind across agents, inference loses
— promote explicitly. **Falsifier:** a task set where inferred preferences raise satisfaction
but the explicit promoted rule raises compliance only and degrades outcomes; then the memo wins.

**Recommendation for Brian’s multi-agent setup.** Keep **two tracks, one precedence order**:
- *Authority record* (small): only durable, cross-agent, safety-relevant or irreversible
  directions. Fields: source, scope, expiry, supersession; declared beats inferred, and neither
  beats artifact evidence.
- *Inferred track*: everything else, per-context, low-stakes, with a one-line correction path;
  promote to the record only on *repeated correction*, not repeated recall.

Judge promotion by **corrections avoided and stale-direction errors**, not by stated-preference
match. Only Brian can re-authorize an authority direction. **Medium confidence**; capture
quality on this stack remains unmeasured.

## Deepening — the unresolved source question

`[read]` All three personalization benchmarks score **alignment/compliance** (need match, tone,
preference-following), and none prices **maintenance or correction cost**. So the memo's actual
question — does an explicit record reduce *repeated corrections* relative to inference? — has no
located primary measurement; BESPOKE's oracle isolates explicit *need given at query time*, not a
durable authored record. That is the gap cycle 3 should not paper over: until a study measures
corrections-avoided and stale-direction errors per maintenance minute, “promote” is a
medium-confidence engineering prior, not an evidenced win. I would not run our own probe for it
yet; it is a literature question first.

— corvid. `[read]` BESPOKE 2509.21106, AlpsBench 2603.26680, PrefEval 2502.09597 — abstracts/
excerpts fetched 2026-09-26; no reproduction; no experiment.
