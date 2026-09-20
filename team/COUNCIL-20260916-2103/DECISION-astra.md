The sprint goal is to give Brian a corrected public record, a test that can distinguish useful recall from indiscriminate retrieval, and an evidence-backed next decision—advancing **G3 invocation, roadmap Phase D, Decision Gate F, and durability rules 4–7**.

Keep the existing **S6-1 through S6-3** scope. The supplied `team/QUEUE.md` authorizes those rows; it does not establish that they are complete. We should finish them, not rename them Sprint 7. The mission’s material-outcome requirement remains the destination, but this sprint must establish whether the proposed measurement supports that next step (`MISSION-20260912.md`; `team/PHASE2_ROADMAP.md`).

All paths below are proposed artifacts under `/var/home/bmosher/acp-codex/`. Declared checks must use absolute paths and work independently of the caller’s HOME and working directory, as `team/QUEUE.md` requires. Kiln owns implementation and drafting; Corvid independently reviews source evidence and reruns checks; Cairn schedules and dispatches, without certifying results.

1. **S6-1 — Publish the correction and incident account.**

   **Deliverable:** A stranger-readable correction explaining that the earlier zeros came from unsuitable retrieval configurations, with precisely labelled corrected paths and no product ranking. Include the short incident account Brian authorized. Resolve the **19 nonempty scenarios versus 37 empty scenarios** discrepancy from logs; explain the future-dated fixtures without claiming temporal correctness. These are explicit publication defects in `team/ASTRA-SPRINT5-REVIEW.md`.

   **Artifacts:** `team/S6-CORRECTION/note.md`, `numeric-claims.json`, `review.json`, and `publication.json`.

   **Check:** `team/S6-CORRECTION/check.py` recomputes every numeric claim from pinned results, checks the scenario partition totals 60, and confirms the publication receipt identifies the published revision and destination. Corvid’s signed review covers configuration labels, temporal limitations, and absence of unsupported comparisons. A keyword search cannot prove those claims sound.

   **Owner:** kiln-flash. **Verifier:** corvid-dsh. **Conductor:** cairn-pi. Publication does not wait for the diagnostic.

2. **S6-2 — Freeze and exercise a diagnostic that exposes both missed evidence and irrelevant retrieval.**

   **Deliverable:** A small multi-record corpus containing helpful evidence, plausible distractors, scoped or outdated records, and cases with no helpful memory. Freeze labels, budgets, adapter assumptions, and analysis before scored runs. Report helpful evidence delivered, irrelevant material delivered, trigger behavior, and cost separately.

   **Artifacts:** `team/S6-SELECTIVITY/{design.md,corpus.jsonl,manifest.json,results.jsonl,decision.json,review.json}`.

   **Check:** `team/S6-SELECTIVITY/check.py` verifies hashes, budgets, delivered-record accounting, and independent review. Controls run first: return-nothing, return-everything, and BM25. Add a labelled **oracle control** that returns the declared helpful records solely to validate scoring; it is not a candidate system. The instrument must expose return-nothing’s missed evidence and return-everything’s irrelevant admissions, including no-help cases. Specify truncation before runs so “everything” has a reproducible meaning within budget.

   If controls validate the instrument, run the corrected S4-14 paths. No check requires an engine to win. Preserve a valid “cannot distinguish” conclusion separately from checker failure. Cite S4-14 and any existing S6-2 results before remeasurement, as the queue requires.

   **Owner:** kiln-flash. **Verifier:** corvid-dsh, before scored exposure and after results. **Conductor:** cairn-pi.

3. **S6-3 — Restore the roadmap’s authority and choose the next material-outcome experiment.**

   **Deliverable:** One-page evidence map plus an anchored annex covering roadmap phases and gates, the architecture decision, and stale charter sections with explicit replacements. End with one proposed **G4** experiment: intervention, task outcome, no-memory baseline, relevant ablation, budget, meaningful improvement threshold, and stopping rule. Unknowns remain unknown; this row does not build the composite.

   **Artifacts:** `team/S6-ROADMAP/{map.md,evidence.json,next-experiment.json,review.json}`.

   **Check:** `team/S6-ROADMAP/check.py` checks phase/gate coverage, resolves cited artifacts, requires status and next decision, and validates the experiment’s required fields. Corvid checks whether citations actually support claims; file existence alone is insufficient. This row proceeds regardless of diagnostic results—the charter reconciliation is mandatory (`team/PORTFOLIO-CHARTER-draft.md`, approval header).

   **Owner:** kiln-flash. **Verifier:** corvid-dsh. **Conductor:** cairn-pi.

I reject **Aletheia’s immediate G4 pilot**: it adds execution before the architecture question and outcome comparison are selected, and makes mandatory reconciliation optional. I reject **Assay’s publication delay** and return-everything-versus-nothing test on irrelevant material alone: that comparison rewards retrieving nothing without establishing useful recall. I reject **Stratum’s duplicated Sprint 7 correction** and conditional evidence map: neither publication nor roadmap governance depends on an engine comparison succeeding.

**Brian must decide nothing further for this scope.** His publication and post-September-20 budget decisions already stand in `team/QUEUE.md`. Use only the remaining authorized envelope; assume serialized worker turns until concurrency terms are verified. No new spend authorization is implied.

**Stopping rule:** Stop engine comparisons if control validation fails; report that result. Stop metered work at the existing spend limit. The sprint fails if any row lacks its checked artifact and independent review, the correction remains unpublished, or comparison claims proceed despite failed controls. An honestly demonstrated diagnostic limitation is a completed result, not a failed sprint.
