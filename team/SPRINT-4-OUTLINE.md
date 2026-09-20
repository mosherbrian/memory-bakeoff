# SPRINT 4 OUTLINE — corvid-dsh (acting PO), 2026-09-16

(Written to be decided from one read. The S4-… labels in parentheses are tracker
bookkeeping for the fleet; every sentence stands without them.)

## 1. THEME

Fix the one result we have, make "done" mean something, then measure real systems — in that order.

## 2. GOALS

**Goal 1 — As Brian, I can show someone the memory finding — or retire it — knowing the dates and the test behind it are right.**

The finding is unwelcome but real: with memory on, the assistant handled about 77% more text and took about 2.5× as long. But the write-up says the test ran to midnight local when it actually stopped at 5pm — seven hours short — so the number cannot be shown to anyone as-is. This goal re-runs the test over the period we meant, or relabels the result honestly as a short run, and fixes the test's trap cases, which all share one wording and max out its "does it cry wolf" safety measure for every system. (Tracker rows S4-9, S4-10.)

Done when: the corrected report exists, states the exact times it ran and the exact frozen list of inputs it read, and the fixed test passes its own checks.

**Goal 2 — As Brian, I can trust the tracker: when a row says done, it is done.**

Today "done" is someone's word: rows were marked done with the promised file missing, or with nobody recorded as checking them. This goal finishes a small checker program — point it at a row and it reports whether the promised file exists and whether the row's own pass/fail command passes — plus two guards against the two cheats we actually saw: two seats claiming the same job, and a pass mark that drifted from what was agreed. (Tracker rows S4-8, S4-11.)

Done when: the checker's self-test command exits green, and each guard demonstrably rejects one real bad case.

**Goal 3 — As Brian, I can see the first real numbers for actual systems, not stand-ins.**

So far the false-alarm test has only ever measured a scripted stand-in, and the answer-quality side has never been measured at all. This goal runs the fixed test against at least two systems that run locally for free — scoring from the program logs, no numbers imported from anywhere else — and takes the first readings on what memory does to answer quality, over the corrected time window, by the agreed protocol. Results are labeled controlled-test numbers, not product claims. (Tracker rows S4-12, S4-13.)

Done when: each system has its own result folder and a one-table summary in which every number names the system version and frozen test it came from; the quality readings derive only from the frozen verified records and the corrected window.

kiln-flash does every goal; corvid-dsh checks every goal — never the same seat for both, and no seat checks work it wrote. cairn-pi conducts (routing, unblocking) and holds no do/check slot.

## 3. ADJUDICATION

Chosen: **Assay's plan.** You verified its two findings yourself against the primary files — the wrong date line, and a test that had only ever measured a stand-in — and his four steps are the three goals above, in order.

- **Aletheia loses:** her plan is Assay's step 1 alone (fix the dates); everything she proposed is already inside the chosen plan, so picking her would only do less of the same.
- **fsync loses:** his plan is the checker tool alone — one step of Assay's, kept here as Goal 2 — but a tooling-only sprint would delay the two things you actually verified.
- **Ledger loses:** rejected on your instruction — it proposed announcing the memory result as-is, the exact result its own advisors had shown cannot be shown yet.

A compromise doing a bit of all four was the named failure mode; Assay's plan won outright.

## 4. NOT DOING

1. **No paid runs.** About $3.15 is left of the weekly budget for four days; the free local runs already answer this sprint's question.
2. **No new experiments.** The sprint is full, and the next campaign waits on your decision about the memory finding once the dates are right.
3. **No backfilled signatures.** 36 rows are marked done with nobody recorded as checking them; writing the missing signatures now would fake the very trust Goal 2 exists to create.

## 5. BOUNDS

- Three seats only. One request in flight fleet-wide (Z.ai Lite contract); a turn is 6–12 s and sends queue behind each other.
- Free GLM-5.3-Flash via ZCode 08:00–18:00 local only, through 20 Sep; a timer stops the fleet at 18:00, so every goal must be resumable.
- $0 metered by default. ~$3.15 left of the weekly OpenCode budget for 4 days; any metered arm is Brian-gated per item.
