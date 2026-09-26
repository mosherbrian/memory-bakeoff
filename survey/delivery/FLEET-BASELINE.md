# Fleet baseline — frozen seven-day window

Tern ·26 September2026 · Local extraction completed. Window **19September19:55UTC through26September19:55UTC**, excluding the new c85 commissions. [Machine-readable counts and provenance](fleet-baseline-20260926.json), [offline extraction](baseline_fleet.py). This is a snapshot analysis, not another monitoring service.

| Requested metric | Baseline from available records | What the number means |
|---|---|---|
| Manual Claude/Brian interventions | **10 acknowledged recovery wake calls across9 episodes confirmed; total unknown** | Claude tool-use/result records supply this conservative lower bound.2,340 wake records include2,172 with sender missing and168 attributed to Tern; neither category can be counted as manual Brian/Claude interventions. |
| Gap alarms | **18 distinct gap incidents;22 notification events** | Four notifications are additional stages of existing incidents. By question:8 WORK-BENEFIT,6 EVALUATOR-VALIDITY,4 FIELD-SURVEY. These are detector incidents, not independently proven idle failures. |
| Idle minutes | **101,595 inactive lane-minutes /114,726.52 observed lane-minutes (88.55%)** | Integrates the existing30-second activity sampler, holding samples at most60seconds. Includes unavailable/paused/waiting lanes; **avoidable ready-work idle is unknown** without an eligibility/rest join. |
| Same failure class recurring | **4 recurrences across2 operator-reported classes;30 repeat alert fingerprints separately** | Three P12 progress/handoff stalls and three survey unwanted pauses yield two recurrences each. Supervisor reasons support those classes, not independent root-cause proof. The30 alert repeats are a broader, separate proxy. |

Additional observations: all observed lanes were inactive for3,988.63 wall-minutes. Sampling covers10,078 of10,080 window minutes; two minutes unobserved. All18 gap incidents have explicit resolution records, totaling334.34 incident-minutes; this is **not** idle time and overlapping incidents are not summed into fleet downtime.

## Coverage and definitions to carry forward

Wake-send logging begins22September03:44UTC, less than seven days; the escalation ledger begins20September15:56UTC. Fleet history scan covers51 files with events in the window. Additional Claude transcript scan covers224 recently modified files/42,464 windowed records:588 wake-command candidates,38 strong nudge candidates,24 acknowledged candidates reviewed. The utilization log spans the window, but its aggregates lack seat IDs and task-readiness state. Missing evidence is unknown, never zero. The counts include historical regimes and cohorts; compare like regimes and publish denominators rather than calling a raw weekly decline a memory effect.

**Manual intervention:** corrective wake/nudge attributable to Claude or Brian, after a failure to continue/complete; exclude automatic alarms, ordinary new assignments, notifications, and retries of the same intervention. Direct Claude tool-use/result review confirms10 recovery wakes in9 episodes: operator-stop recovery, worker failure, three P12 idle/handoff recoveries, two sends for one authentication recovery, and three survey-idling corrections. The17:49 transcript message duplicates one tool call and is not added again. [Review ledger](manual-intervention-review-20260926.json) records IDs/hashes, not private command text. Automated extraction produces candidates; uncertain attribution stays unknown. An actor ID alone does not prove manual intent.

**Avoidable idle:** an assigned, eligible task exists; its seat is not active; no valid named dependency or quota/availability block explains the interval. Exclude deliberate rest and absent work. Corvid correctly distinguishes activity from registry status and alarms from failures; his suggested “no eligible task” conjunction is reversed here—lack of any eligible work does not establish avoidable idleness. Existing sampler source uses active-turn state, not only the dashboard idle label.

**Recurring failure:** a new causal episode of the same operational class after a prior resolved episode; repeated emissions within one episode count once. Existing alert kinds support the reported proxy, not a complete semantic failure ledger. A false alarm is a detector failure class, not a fleet execution failure. Preserve unresolved classifications separately.

## Delivery use now

Use existing wake, escalation, activity and result logs for Monday summaries; retain these same definitions. First fix attribution at the existing dispatch point when Claude ships the reflector—record sender and intervention-vs-assignment reason, without a new service or Brian form. The log's missing past sender cannot be recovered by guessing. Join existing queue/rest and active-turn intervals where identifiers permit; otherwise publish raw inactive time with its qualifier.

The baseline is now usable for observed gaps and inactivity, and exposes exactly why manual-intervention and causal-recurrence totals cannot yet be asserted. Scoreboard must show both counts and missingness. Success means less intervention and repeated failure with useful deliveries maintained, not fewer alarms achieved by disabling monitors, more busy work, or more notes captured. [Corvid's challenge](c85-metric-challenge.md), [lead disposition](c85-lead-disposition.md).


**Reproduction addendum:** the core extractor covers fleet logs. [Claude wake candidate scan](scan_claude_wakes.py) adds operator provenance from existing local transcripts; [candidate metadata](claude-wake-candidates-20260926.json) and the review ledger separate automated nomination from confirmed intent. Ten is a lower bound, not the total of all588 wake-command candidates.
