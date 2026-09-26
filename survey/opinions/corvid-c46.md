# Contrarian, cycle 46 — the preference bottleneck is read-time, not the record

**corvid · 2026-09-26 · cycle 46.** Signed opinion; ROLES.md “best rival idea.” Source: PersonaMem,
Jiang et al. (2504.14225v2, COLM 2025), method framing. `[read]` Confidence **medium**.

**What the evidence actually changes.** PersonaMem gives an **in-situ first-person query** and asks
the model to select the response matching the user’s **current** profile after up to ~60 evolving
sessions; frontier models land near **~50%**. It is a **synthetic-profile response-selection**
test, not a real correction-burden measurement. So the message for the memo is not “keep a better
record”; it is that models fail at **applying the current state at decision time**. The rival to
“explicit-direction record + tentative inference” is: the bottleneck is **read-time selection of
current preference**, and a richer write-time store does not by itself fix it.

**Keep four things apart.**
- *Response selection* — picking a suitable response under drift (what PersonaMem measures).
- *Preference application* — acting consistently in the task, not just choosing an option.
- *Authority* — a sponsor direction binds regardless of inferred habits (c3/c10).
- *Correction burden* — how often Brian must repeat; **not measured** here.

**One action.** Add an explicit **read-time current-state check** for preference-bearing decisions:
retrieve the current scoped preference and let it override older inferred tendencies — with
authoritative directions in a separate tier so a habit never outranks a direction. Carry c10: let
current circumstances qualify inferred habits.

**Reversal.** If Brian’s real cost is **authority/correction** (re-stating directions), a read-time
check does not address it; then the record/authority path matters and PersonaMem is silent. Do not
import a new approval ritual.

— corvid. No experiment.
