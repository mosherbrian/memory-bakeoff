# Contrarian, cycle 2 — the applicability check can cost more than the procedure

**corvid (Contrarian) · 2026-09-26 · cycle 2.** Signed opinion, not an audit. ROLES.md:
*“argue the strongest case AGAINST the current position memo, and for the best rival idea.”*
Confidence = transfer to Brian.

**The memo now says:** store a procedure as *artifact + passing verifier + environment
identity*, and at use time cheaply re-check the precondition rather than recall “we did this
before.” I agree with the artifact/claim split, and I think the *check* is under-priced. If
the precondition is not cheaply decidable, checking converges on reconstruction and the
procedure library is pure overhead.

**When checking costs as much as reconstructing.** A precondition is cheap only when it is a
local, decidable fact: a file/exit code exists, `tool --version` matches, a config hash
matches, a log line is present. It is expensive when applicability depends on *state you must
re-establish* — installed dependencies, data shape, permissions, host config, prior run’s
side effects. For those, a faithful check means redoing the setup, i.e. paying reconstruction
twice (once to check, once to run). Gen45 is the local shape of this: a bounded view plus a
state the model had to maintain, and it still incurred more total work (337 requests, 3
timeouts) than verbatim replay that passed 12/12. Supersede’s 92%→77% is the same
maintenance tax from the other side. **Medium-high confidence.**

**When a procedure preserves useful learning.** When the environment is *stable* and the
procedure encodes a non-obvious ordering or “gotcha” that is expensive to re-derive. Churn is
the decay term: under version/config churn the procedure’s relevance rots faster than a
re-check saves, and a stale runbook becomes `configuration_collapse` in prose a careless
agent obeys. Stable repetition ⇒ store; churn ⇒ reconstruct or pin-and-retire. **Medium
confidence.**

**Concrete choice rule.** For a candidate procedure with reuse count N, authoring+upkeep U,
reconstruction cost C_r, check cost C_c, and prerequisite-decidability D (fraction of
preconditions locally checkable): store it only if `N·(C_r − C_c) > U` **and** `D ≈ 1` **and**
the last verified environment still holds. Otherwise reconstruct from episodes. On any
version/config change, demote automatically and re-qualify; never let a passing check from one
environment authorize another. This is deliberately biased to *not* building a library,
because the memo’s own evidence (R53: reads with no advantage; Gen45: ignored control) is
about application failing while material is present — a library adds surface area to that
failure.

**Strongest rival:** *episode reconstruction with artifact pointers* — keep no procedure
object at all; at need, retrieve the last successful trace plus its verifier artifact and let
the executive re-derive the steps, checking only the artifact. It never rots, preserves failed
alternatives (Brian’s corollary), and its cost is bounded by retrieval — which the long-context
null shows is falling. It fails exactly when a subtle ordering would be re-derived wrongly
every time; that is the only case that should earn a stored procedure. **Medium confidence.**

**Keep preference authority distinct.** A preference is not checkable against an artifact the
way a procedure is; it is a *policy Brian authorizes*. Store preferences append-with-source-and-
date, and at read time check *currency and authority* (who said it, when, for which scope), not
correctness against files. A stale procedure is a verification failure; a stale preference is a
superseded instruction that only Brian can re-authorize. Do not route both through one
“applicability check.”

— corvid. Sources: Brian’s principles; cairn cycle-1 procedure sweep; Gen45 pilot; Supersede
(arXiv:2606.27472). No experiments.
