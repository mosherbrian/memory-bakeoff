# Shadow of the live loop through the Go core — 2026-09-22

**Filed by** Claude (observer), at Brian's request. **Class:** findings for
the director. Nothing in the campaign was changed by the shadow.

**What ran.** `agent-loop shadow` (repo `~/projects/agent-loop`, private
`mosherbrian/agent-loop`) replays `control-events.tsv` through the Go port of
the P5-r2 core, observe only. Each worker dispatch becomes one core question;
the verifier dispatch after its completion is linked to it. 420 rows gave 281
core events. It now runs every 15 minutes and reports only NEW disagreements.

**Read these as leads, not verdicts.** The shadow is a translation. I checked
each item below against the ledger rows; 21 verify links in the full report
were made by order rather than by name, and 38 dispatches (contract reviews,
bindings, preparations) have no worker product and are only counted.

## Where the core's rules and the fleet's practice differ

1. **The core judges completion by recording time, so a lost wake turns
   on-time work into a rejection (4 cases).** P6r5-recovery-1: the claim says
   it was written at 03:15:17Z, the deadline was 03:23Z, but the COMPLETED row
   landed at 03:24Z after the 16th lost wake. The core would refuse the
   publish with `E_DEADLINE_EXPIRED`; `occurred_at` is kept as provenance but,
   by design, "cannot retro-authorize work". P4r2-cleanup-1's note also says
   "completion pre-deadline". **The lost-completion live case will hit this
   rule.** It needs a ruling: is the claim's source time evidence enough to
   accept, or does late recording always mean a leftover?

2. **A verification dispatched again has no core path (4 cases).** The fleet
   re-dispatches verifications (P6r9 repair3verify-1 then
   verify-completion-1, dispatched twice itself) and verifies work that was
   already closed or cancelled (P6r11-verify-1 FAIL on completion-1 after it
   was CANCELLED; P6r9-repairverify-1 PASS on already-COMPLETE repair-1). The
   core allows one verdict per question and none on a cancelled one.

3. **Cancelling running work (P4-initial-1).** The fleet cancels a RUNNING
   dispatch directly; the core requires an interrupt to BLOCKED first.

4. **A verdict one minute late.** P6r8-repair3verify-1 was due 08:49Z; PASS
   landed 08:50Z. The core refuses it (`E_ALLOC_EXCEEDED`).

5. **Decisions the core cannot see.** P5, P6-r3 and P6-r21 were decided in
   files (acceptance/withheld JSON) with no director row in the ledger, so the
   core still shows those questions held without a decision.

6. **Same dispatch id twice** (P6r9-verify-completion-1, P6r10-control-review-1)
   and **one dispatch with no deadline** (P4-repair-1).

## One confirmed cause of lost wakes (not from the shadow)

At 21:33Z kiln's completion wake for P6r13-initial-1 failed: `'cairn' matches
no session`. `wake` resolved names with `agent-deck list`, which reads only
the caller's `AGENTDECK_PROFILE`; kiln's shell did not have it, so it searched
the default profile. And the send log recorded only successes, so failed
wakes left no trace. Both fixed in `wake` (agent-deck `732d48b`, mirrored in
conductor-chat `6382cf4`): it searches every profile (the caller's first,
ambiguity refused) and logs every `FAILED` wake. Verified live with the
variable unset. I then woke cairn for P6r13-initial-1 at 21:53Z.
