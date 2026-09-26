# Contrarian, cycle 4 — let retrieval, working memory and the composer collapse

**corvid · 2026-09-26 · cycle 4.** Signed opinion, not an audit. ROLES.md: *“the best rival
idea.”* Primary source read: MemGPT (Packer et al., [arXiv:2310.08560v2](https://arxiv.org/abs/2310.08560)),
the canonical integrated tiered-context design. `[read]`

**Strongest integrated rival.** MemGPT’s *virtual context management* is one mechanism, not
five: the LLM self-manages fast/slow tiers — main context (working memory), a recall store, and
archival storage — paging data in and out with function calls and interrupts. It is the native
stack’s shape too: transcript + compaction + instruction file + skills, one system. Compare by
**responsibility coverage**, not product count:

| Layer | Integrated rival | Verdict |
|---|---|---|
| L1 lossless history | archival store = only what the agent chose to write/summarise | **not covered** |
| L2 state/lifecycle | no valid-time, supersession, scope or authority; “current” ≈ most recently written | **not covered** |
| L3 retrieval | archival/recall search | covered |
| L4 bounded WM | main context window | covered |
| L5 composer | paging + system prompt + interrupts, precedence inside one system | covered |

**Which layer can disappear.** **L4 and L5 collapse into L3** as *agent-directed paging*: the
working set simply is the retrieval result, and the composer’s job (precedence and budgeting)
becomes paging policy. A separate bounded-WM service and a separate composer are not
independently justified if one pager is accountable and enforces precedence — and the integrated
form is arguably *better* at precedence because it lives in one system rather than in a
bolted-on composer. **L2 cannot disappear**: nothing in the rival distinguishes current from
obsolete, carries scope, or holds preference authority, and **procedural reuse and preference
correction both depend on exactly that**. So the minimum separate mechanism is **L2 over a
lossless L1 substrate**, not five services. **Medium confidence.**

**Extra assumption that makes the rival fail.** It assumes the executive’s own paging and
memory-editing reliably preserve current-vs-obsolete truth — page the right procedure, never
resurrect a stale preference. Our Gen45 is local counter-evidence: a model given control tools
largely ignored them (**6 patches, 0 transitions**). When the model is both author and pager,
lifecycle truth and preference authority have no owner. It also invites recursive summarisation,
directly against Brian’s corollary.

**Surprising limitation, traced to the source.** MemGPT’s own framing is that the design
provides “the **appearance** of large memory resources through data movement between fast and
slow memory,” and that it “provide[s] extended context within the LLM’s limited context window.”
Lossless permanence and lifecycle truth are **not goals of the design** — the external tiers are
a working-set device, not an event log. So any claim that an OS-style integrated system covers
L1/L2 misreads the paper: it covers the *view*, and that is the one responsibility the memo needs
kept separate.

**Recommendation.** Keep two mechanisms, not five: (1) a lossless history substrate (L1), (2) a
lifecycle/authority projection (L2). Let retrieval, bounded working memory and the composer
collapse into one accountable pager. That preserves procedural reuse (needs L2 status + L1
evidence) and preference correction (needs L2 authority) at the lowest service count.

— corvid. `[read]` MemGPT abstract + framing fetched 2026-09-26; no reproduction, no experiment.
