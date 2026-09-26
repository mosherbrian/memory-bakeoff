# Contrarian, cycle 27 — no checker means candidate, not authority

**corvid · 2026-09-26 · cycle 27.** Signed opinion; ROLES.md “best rival idea.” Existing sources;
no new sweep. Confidence **medium**.

**Strongest recommendation without an affordable ground-truth checker.** Keep the **raw episode**
(transcript/log/report) as evidence, and at most a **tentative candidate note** — never promote
guidance to authoritative on the strength of a coarse judge. At use time, **reconstruct from the
episode and read**, rather than trusting a remembered success. This does not wait for an oracle and
does not charge Brian for labels.

**Compare the three.**
- *Episodic reconstruction* — default when nothing is checkable. Verbatim, no judge needed; the
  cost is reading and selection, not supervision.
- *Cautious agent-owned guidance* — allowed only with an explicit **candidate/unverified** status
  and applicability conditions. C26 correction stands: a **local check establishes only its tested
  property** — a `--version` probe confirms the version, not that throughput is correct — so a
  passing check is not outcome success and is not an artifact oracle.
- *Coarse judging* — usable to **rank which episodes are worth reconstructing**, not to certify.
  Its errors propagate (experience-following/error propagation); treat a coarse score as a
  retrieval cue, never as truth or authority.

**The uncertainty that changes an action:** whether the procedure has **any cheaply decidable
property that correlates with success**. If yes, gate promotion on that property check. If no, do
**not** promote to authoritative guidance at all — keep a candidate note plus the episode and
reconstruct at use.

**Rare/difficult procedures:** no checker + low use means keep archived with source, marked
tentative; do not retire, do not auto-promote, and do not demand a labeled set (no blanket
~300-label rule; labels only when a specific high-stakes procedure earns them).

— corvid. Based on cycles 15–26 readings; no experiment.
