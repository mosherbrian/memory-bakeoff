# Reading note — PAHF feedback protocol: who paid the clarification cost

**cairn (Reader — local Qwen3.8 Flash-Next, free) · 26 September 2026 · cycle 14.**
One source, one question (Tern): in **PAHF (arXiv:2602.16173v1)**, which feedback/clarification
cost was paid by **real participants**, which was **simulated or oracle**, and how transferable
is the reported benefit to **Brian's repeated corrections**? ~250 w target; source section and
confidence reported. Write-first, then the methods read. No sweep, no experiment.

**Provisional frame (before the read).** My c13 finding was that Capture's ask channel is
validated by stored annotations, not humans. If PAHF's feedback loop is the same shape —
preference labels collected once, replayed as oracle — then the whole "ask when uncertain"
family shares one untested assumption: that real users answer, accurately, repeatedly, without
fatigue. If instead PAHF pays real cost somewhere (live clarification in-session, measured
response rates), it is the only price signal in this area and the transfer question becomes:
single-shot corrections vs **repeated** corrections, which is Brian's actual pattern.

*(protocol facts + verdict appended after the read)*

## Protocol facts (PAHF 2602.16173v1, §4.1–4.2, §5, Prop. 1) `[read]`

**Real participants: none.** "Human feedback" is simulated end-to-end. Embodied domain: *"We
simulate the human behavior by employing another LLMs with specific persona"* — the persona LLM
answers clarification and gives post-action feedback; each persona has an "original" and an
"evolved" profile (a clean, complete preference swap). Shopping domain: hybrid — persona LLM for
pre-purchase clarification, **deterministic rule-based judge** for post-purchase verdicts,
returning minimal targeted feedback naming the offending feature. Scale: 40 simulated users × 30
scenarios/phase (embodied), 20 × 45 (shopping); four-phase protocol (learn → test → drift →
test). Feedback is priced only as **Feedback Frequency** (share of tasks using feedback ≥ once)
and via ACPE/success — counts of feedback events, never cost to a human. Proposition 1
idealises further: post-action feedback *reveals the correct action*.

**The one measured mechanism worth transferring:** the Pre-action-Only agent **stops asking once
its memory is confident** — it no longer perceives ambiguity, fails to detect the drift, and in
the embodied domain falls *below the no-memory baseline* in Phase 3 (§5). The ask channel
self-disables exactly when staleness begins; only the reactive post-action channel catches
"confidently wrong" beliefs, and only after a mistake. That is c13's silent-staleness/discovery
failure, demonstrated — in simulation — at the mechanism level.

**Transferability to Brian's repeated corrections.** Structure: high — the dual-channel loop
(ask when memory empty/ambiguous; correct after acted-on staleness; explicit per-user memory)
maps onto his pattern, and the confidence-silencing result argues our hybrid must keep a
reactive channel, never clarification alone. Magnitudes: none — feedback is oracle-quality
(names the right feature), costless (no fatigue, no non-response; contrast our 59/88 expired
confirms), and drift is a clean persona swap, not messy scope change. **Verdict: solid
mechanism evidence, zero attention pricing.** The family conclusion from c13 stands and
strengthens: ask/correct loops are validated with costless users; PAHF doesn't even pay for
real history. Confidence: high (protocol statements are explicit, quoted); medium that the
confidence-silencing effect reproduces with real users. No universal no-study claim: this is my
inventory, not the literature.

— cairn. Source `[read]`: arXiv HTML 2602.16173v1 §3.2–3.3, §4.1–4.2, §5, opened 2026-09-26.