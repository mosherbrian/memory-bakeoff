# Reading note — what actually prices human attention in memory maintenance

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 13.**
One question, one source family (Capture/PAHF, already in my reading): **what evidence prices
human attention in memory maintenance?** Signed provisional opinion first, then the method
deepening. No broad sweep, no experiment.

**Provisional opinion (~250 w, before the deepening read).**
My cycle-12 claim was that Brian's maintenance attention is the largest unmeasured user cost.
The honest version after re-checking my own evidence: almost all of it is **counted as
something else**. In Capture's D-PrefGuard, the clarifying ask is priced as an *action in a
simulated loop* — a budget (≤1 per 12) and an entropy trigger — and scored against generated
episodes, not against a human paying attention. The genuinely human parts of that paper (the
40-user, 2–3-week study) measure **label agreement**, not seconds or interruptions. TrustMem
prices transitions by a verifier LLM, zero human axis. Memory-R1 prices operations by QA
exact-match, zero human axis. EvoArena prices chains by task success, zero human axis. Our own
lane contributes the only observed human-attention numbers in my inventory, and they are
failure-shaped: 59/88 confirm-drafts expired unconfirmed — attention *withdrawal*, which no
benchmark has a metric for at all. So the field's cost accounting is: tokens (everywhere),
latency (some), **attention (nowhere measured; once starved)**.
Which unmeasured cost most threatens our recommendation? **Correction discovery time** — not
the correction itself: the interval in which a stale or mis-scoped memory silently acts before
anyone notices (outcome-gated correction never reaches what no question revisits). It is
unmeasured by every source I read, and our A+C hybrid's ask-budget only addresses *write-time*
uncertainty, not read-time silent staleness. Confidence: medium-high that the measurement gap is
real across my sources; medium that discovery time, rather than confirm burden, is the top
threat.

*(deepening appended after the method re-read)*

## Deepening — Capture/PAHF methods: the ask is priced symbolically, never paid by a human

Re-read of the primary methods (evaluation design, §6, Appendix B cost table, Theorem-4
assumptions). `[read]`

**Counted as simulated or oracle:** D-PrefGuard is generator-made episodes; win rate is an LLM
judge (87.4% agreement with three human raters on a 600-comparison subset); regret is scored by
a second reward model; safety by a classifier; the ask action's precision/recall/F1 are scored
against generator labels. HorizonBench: 360 **simulated** users, non-interactive — clarify
degenerates to quarantine. **The decisive one: the 40-participant, 2–3-week study is an
oracle-assisted replay.** Histories were collected, frozen, and replayed identically to every
system with six attacks injected that no participant ever saw, and **"when the gate asks the
stored annotation answers… with zero answer error"** — the human is absent at exactly the point
where the attention cost is supposed to land. The authors say the quiet part plainly: Theorem 4
"establish[es] that a bounded-cost query changes the achievable region, **not… evidence about
how accurate real clarification is**"; the query cost *c* is a parameter, and Assumption 5 grants
the ask channel a fixed symmetric-channel accuracy.

**Actually measured:** machine costs only — per-turn latency and tokens (full system 2,480 ms /
3,850 tokens; +17% tokens over their StateMem baseline, −43% vs Full History), plus label
agreement in the user study. Two side findings worth carrying: their **StateMem baseline
(explicit supersession bookkeeping, no authenticity gate) leads the heuristics on win rate and
is close to a Capture ablation** — consistent with "supervision/bookkeeping, not architecture"
(~2.2 pts attributable to the learned gate); and per the commission's caution, the theorem
binds only rules reading recency+provenance — a file store or integrated system may host richer
observations and a learned policy, so it is not a verdict on A or B architectures.

**Sharpened signed opinion.** The field's attention accounting is worse than "unmeasured":
the one design family that explicitly budgets human interruption (**Capture**) validates the
budget against **oracle answers**, so even the 1-per-12 figure my cycle-12 opinion cited is a
design parameter, not a price. The unmeasured cost that most threatens our recommendation is
therefore **the ask channel's real exchange rate**: how often Brian answers, how accurate and
stable his answers are under fatigue, and what an ignored ask does to the ledger — none of
which any source measures, and our lane's 59/88 expired confirms is the only observed exchange
rate, and it is *non-payment*. Recommendation stands (A+C hybrid, budgeted ask) but its budget
must be **instrumented on Brian's actual traffic before it is trusted** — count asks, responses,
latency-to-answer, and expiry, exactly as our confirm ledger already does. Confidence: high on
the oracle-replay facts (quoted), medium-high that no other read source measures attention
(true across c1–c12 inventory), medium on which cost ranks first.

— cairn. Sources: Capture 2609.02265 methods re-opened 2026-09-26 (§4 scoring, §6, App. B
latency/tokens, Thm-4 assumptions, App. A.6); my c3/c5/c11/c12 files.