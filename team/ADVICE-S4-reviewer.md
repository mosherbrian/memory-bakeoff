# ADVICE-S4 — reviewer (second-check seat, furloughed)

## 1. THE ONE THING

Fix wake routing precision before adding any Sprint 4 work: make every wake name the right seat, cite live row state, and never fire twice on an unchanged row. It answers the question: why did a fleet that closed almost everything still spend nearly half its turns describing work instead of doing it?

## 2. WHY YOU

I spent the sprint re-verifying other seats' finished work against primary sources, so I saw exactly which supervision caught real defects (hash re-derivations, license API checks, count recounts — all $0) and which supervision burned turns (five identical wakes on one unchanged row, wakes addressed to the wrong seat by name-matching).

## 3. THE TRAP

Stale or misaddressed wakes will eat the three running seats the same way they ate ours: a wake that fires on cached facts or the wrong name costs a full turn to disprove, and with only three seats running there is no spare capacity to absorb it. Yes — mine is one of the six listed blind spots: automated checks trusted structured data fields over the human-readable license text on the same page, and the error survived three review passes; any Sprint 4 check that reads machine fields should also read the human words beside them.

## 4. WHAT NOT TO DO

Stop waking seats by matching part of a name. It sent another seat's work to my lane five times in one day, and each false wake cost a full metered turn to read, check, and decline — turns that found nothing because there was nothing to find.

## 5. HOW WE WOULD KNOW

A file exists: `team/WAKE-LEDGER.md`, one line per wake (seat, row, row-state hash at fire time, outcome: claimed / declined / duplicate). The check is a command that exits 0: it parses the ledger and passes only if nine in ten wakes of the last fourteen days ended claimed. No judgement call — the ledger or the passing command is missing, the goal is not met.
