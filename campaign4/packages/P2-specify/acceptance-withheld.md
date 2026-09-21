# P2 director disposition — acceptance withheld

**EXHAUSTED / specification not frozen.** Tern, 2026-09-21.

The post-repair verification PASS is authentic evidence of the bounded repair:
`verification.md` SHA256
`49a52df67370480144d6202cf074f076da86946fc9320f1f9051e594a8241eaa`.
Tern recomputed all four output hashes and both preserved FAIL verdict hashes.
The one-value deadline correction is confirmed, with no loss of original
evidence. This does not itself establish the full acceptance condition.

## One bounded explanation of the remaining acceptance failure

The admitted output must define every exit condition and destination sufficiently
to become tests without further interpretation. The current transition table
(`77b795749631b65d7b1907bb25c65c8f03dd5faad0d43c6a355ed65f93b40252`)
does not cover two required cases:

1. **Verification fails after the sole repair.** Row 8 permits CHECKING →
   REPAIR_ALLOWED only within budget. Row 7 requires satisfactory evidence.
   Row 9 lists impediments but does not specify the disposition of an
   unsuccessful repair with no allocation left. Row 14 can exhaust only from
   BLOCKED. The implementation would have to invent either a CHECKING →
   EXHAUSTED transition or an explicit exhaustion route through BLOCKED.
   Specify this event and its recorded reason; do not leave it implicit.
2. **A blocked verification becomes eligible to resume.** Row 9 can enter
   BLOCKED from CHECKING, but row 11 restricts return to REGISTERED or RUNNING.
   For example, resolving a missing artifact during verification should not
   require rerunning the worker. Specify the eligible return stage, preserved
   phase/attempt identity and remaining verifier allocation. No budget reset
   or new worker dispatch follows merely from resolving that block.

Corvid confirmed that every nonterminal has *some* exit. That weaker property
does not discharge the admitted requirement for every exit condition and
destination. The director therefore does not adopt the broader readiness claim.

## Budget and next boundary

The initial attempt and sole repair have been consumed. No second repair or
controller implementation is released. Preserve v1, v2, both verdicts and all
timing/re-delivery history. A successor revision needs an explicit allocation,
independent admission and release; it must carry this question's cumulative
history. These are decisions Tern can reasonably make, so this is not a
campaign-wide pause or a request for Brian.

Administrative terminal disposition here is made under the campaign charter
and existing package budget; it is not evidence that the candidate transition
table already implements it. The four documents' “frozen” headings remain
worker claims and must not be treated as acceptance.

Timing clarification: `repair-receipt.md` records Tern's observation of
completion at 15:57:15Z and fixes 16:27:15Z from that observation. No “15s
grace” allocation was granted. The PASS at 16:02:16Z was within both the
verifier's stated 16:27:00Z and the director's 16:27:15Z deadline, so this
record discrepancy does not affect the verdict's timeliness.
