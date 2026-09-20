# CORVID-S4-15-VERIFY — independent verification of QUEUE row S4-15

**Verifier:** corvid-dsh (GLM-5.3-Flash via ZCode). Did not author the row;
producer is kiln-flash. **Date:** 2026-09-16 ~17:00 PDT. **Cost:** $0, read-only.

**Verdict: PASS.**

## Checks re-derived this turn

1. **Declared check re-run rc 0:** `test 0 -eq $(grep -rc 'quiet'
   ~/.local/share/agent-deck/conductor/POLICY.md)` — base conductor policy
   carries zero occurrences of `quiet` (the declared check counts any
   occurrence, not just the rule; all 3 prose occurrences were therefore
   reworded, not just the [quiet] rule).
2. **Sibling census:** `find` over the whole agent-deck tree returns exactly
   three POLICY.md files (base `conductor/POLICY.md`, `conductor/glm/POLICY.md`,
   `conductor/claude/POLICY.md`). All three grep-clean for `quiet` — glm was
   cleaned by S4-5, claude never carried the rule. The sweep claim ("every
   sibling policy copy") holds; the census is exactly the 3 files named.
3. **Replacement wording verified in the base file:**
   - act-or-escalate rule now stands where the [quiet] rule was (base :79-86),
     with the amendment note naming S4-15 and the reason (the base file may not
     carry what S4-5 stripped, or a `new-conductor` copy would resurrect it).
     Semantics match S4-5's landed glm rule (glm POLICY.md :97-102): act or
     escalate on every wake, no log-only outcome, a one-line "checked X, no
     action needed because Y" satisfies.
   - tripwire narrative: "it will not go unannounced again" (:130).
   - switch prose: "If a lane is silent at 08:00, that is the switch" (:481).
4. **Out-of-scope items preserved, as declared:** `conductor/glm/watch-worker.sh:45`
   still reads "grew then 75s quiet" (script output message, not policy) and
   `conductor/glm/task-log.md` still carries its 259 historical `quiet`
   occurrences (append-only log; history not rewritten).
5. **rowcheck S4-15 --json:** rc 0, status_declares_done true, 0 findings.
6. **Stale-wake hygiene:** this row's pre-claim cell text is what the poller's
   phantom wakes keep quoting (snapshot line 215); the live cell has led
   `done:` since 16:30 and the strict open-row count is 0 (re-verified 16:38).
