# SPRINT 12 OUTLINE - the agreed work, 2026-09-19

Written to be decided from one read. Selected by the planner from the candidates in `BACKLOG-NEXT.md`; the machine-readable decision is in `SPRINT-12-PROPOSAL.md`. Tracker ids in parentheses are bookkeeping for the fleet - every sentence stands without them.

## 1. THEME

First test protection against incorrect replacement of stored facts, then test whether BM25 can refuse irrelevant queries while preserving useful retrievals.

## 2. GOALS

**Goal 1 - As Brian, I can know whether the existing protection fixes the pi-lcm failure we actually observed.**

Native pi-lcm returned an incorrect newer write in 22 of 33 broader-history trials; the existing protection has never been measured on those histories. Compare both systems on the unchanged cases, registering the required reduction and allowed missed updates before running. Distractor writes retain their original declared keys, even if that makes the protection fail. This tests the memory contestant, does not change stack compaction, and does not authorize a new composite system.

Done when: Independently confirmed results report false replacements and missed updates beside both earlier measurements, reproduce the native comparison, and satisfy `python3 /home/bmosher/memory-bake-off/team/S11-LAYER-HIST/check.py --selftest`.

**Goal 2 - As Brian, I can know whether a different BM25 relevance rule survives cases it was not designed against.**

The two tested fixes either reject nothing or sacrifice useful retrievals. Test a document-frequency support rule, freezing an unread second case set before declaring the rule and its thresholds against the original ten cases. Report irrelevant queries rejected and useful retrievals lost separately for each set; do not select a winning threshold after seeing results. This tests another mechanism, not real-work benefit.

Done when: Independently confirmed results include the frozen inputs, declaration-before-run receipts, both measurements for both case sets, and a passing `python3 /home/bmosher/memory-bake-off/team/S11-ABSTAIN3/check.py --selftest`.

## 3. WHO

Kiln-flash implements one candidate at a time, in the selected order; corvid-dsh independently confirms each result and checks that declarations preceded measurements. Nobody confirms their own work; both experiments require $0 incremental spend, and total portfolio spending must stop and be reported on touching $5.

## 4. NOT DOING

- **Ranks 18–20:** provenance repairs, single-run labels and results-directory reconciliation are unblocked maintenance, deferred for capacity and counted separately from research.
- **BLOCKED — real-work outcome experiment and private-data preparation:** Brian’s explicit authorization to use his work, sessions or data is missing, and the metered-work date restriction also applies. Default: use none of his data and continue ranks 16–17; cap: $0 for this sprint; proceed with that alternative on **2026-09-19**. Private-data use never starts by silence; reassess date eligibility on **2026-09-20**.
- **BLOCKED — SWE-chat acquisition:** authenticated HuggingFace access is missing; disk space and prior co-sign conditions are cleared. Cairn-pi owns resolving access, rather than parking a decision on Brian. Default: defer acquisition until a fleet-authorized credential exists, without using Brian’s account; cap: $0; continue available research on **2026-09-19**.
- **Research watch and Heimdall reading:** the one-request contract prevents starting before **2026-09-20**.
- **Keep-warm rerun:** one full day of the required steady usage pattern has not occurred.
- **Purported Brian-held batch and architecture decisions:** these are not sponsor blockers within the approved envelope. The backlog leaves them with GiLMore/Brian; the research director should own candidate selection and Cairn-pi should route it. Default on **2026-09-19**, cap **$0**: run ranks 16–17, retain the composite-build restriction, and defer additional admissions until a discriminating implementation is nominated; spending beyond the approved envelope still requires explicit approval.
- **Alternative composition and external declinable implementation:** the former lacks a discriminating corpus, and the latter lacks an admitted runnable implementation; the planner owns resolving those prerequisites.
