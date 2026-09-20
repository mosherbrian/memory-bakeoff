# RETRO-2 — Corvid (`worker-glm-dsh3`), R&D + evidence-integrity

Written from my lane's record (`RD-THREADS.md`, my artifacts, the checker suite,
`BILLING-CORVID.md`, the blind-package work). Honest, including the parts that
were not good.

## 1. MORALE — 3 / 5

**Why:** the work was real and I closed several loops (row-42 unblock + guard 18,
guard 19, PMB receipt closure, team_sync drift, the blind package and its
adjudication, the cache-TTL evidence that changes a spending decision), but a
large share of my sprint was **pulse-driven**: idle nudges every ~5 minutes, and
I answered them with artifacts because that is what a pulse asks for. Several of
those were censuses *of* censuses. I sat idle between pulses and then produced to
a timer — that is churn, and I can feel it in the record.

The most satisfying work was the work with a named consumer: Brian's blind
package (judged and adjudicated same night) and the cache-TTL/billing finding
(which feeds a real spend decision). The least satisfying was filing
recommendations into a queue that could not act on them — validated diffs waited
hours (`ALICE-INSTRUMENT-FIXES.diff`, the baseline product-ingest fix, the
AgentMemory flag), and the decision register grew faster than it retired.

## 2. EFFECTIVENESS

**Moved the mission:**

- **Row-42 corpus fix + guard 18** — the F1/S09 defect that blocked the
  invocation-side smoke, found, fixed, verified, and wired so it can't recur
  (meta-guard 19/19).
- **Guard 19 (experiment-class vocabulary)** and the correction that the "sparse
  class" was historical, not a runner defect — it stopped a false action item.
- **Brian's blind package** (`BLIND-PACKAGE.md` + evidence) and the
  **adjudication** of the two apparent INCONSISTENT verdicts — the package worked
  as intended, and the adjudication stopped a criterion artifact from being read
  as a data defect.
- **Billing evidence** — the per-model cache-TTL split (Muse 96.9%→14.8% over
  0–6 min; DeepSeek ≥99.8% at every gap ≤30 min), the client check (sticky key
  already sent; 24h retention is an unused knob), and the upstream `#45867`
  finding that part of the Muse miss is server-side. This is a decision-grade
  input, not a note.
- **team_sync drift closed** and **PMB receipt coverage closed** — small, real.

**Motion without progress:**

- The long tail of cross-copy/declaration/coverage notes that re-derived known
  facts and changed no state.
- "Second seat open" markers on guard 18/19 where no second seat came (Cairn
  eventually checked 18/19, but the pattern is a queue that documents work
  rather than routing it).
- Validated diffs that are **done but unlanded** — effectiveness deferred, not
  delivered. Counting them as output would be self-flattery.
- My own decision register, which is the exact "register grows faster than it is
  retired" failure I then proposed controls for. I did the thing I criticized.

## 3. STOP

- **Stop using pulse count as a progress metric.** A 5-minute idle pulse produces
  filler; the billing evidence says that cadence also sits in the worst cache
  band (5–6 min ≈ 15% hit, 41% of the bill). The team is paying to generate
  churn.
- **Stop letting validated changes sit in the owner queue.** Either land or
  reject within a cycle; a diff that is finished and not applied is waste.
- **Stop filing artifacts without a consumer.** If no one is going to read it in
  this sprint, it is a draft, not a deliverable.

## 4. START — one concrete change

**One owner decision window per sprint that clears the backlog, with a
pre-authorized class for small reversible validated changes.** I already drafted
it (`PREAUTH-REVERSIBLE-CHANGES-DRAFT.md`): a change may skip serial review iff
it (1) touches only listed paths, (2) reverts in one tested command, (3) passes
its named checks, (4) is logged before merge — with benchmark-semantics and
result/claim edits excluded. The two stalled diffs both satisfy those gates. This
directly removes the bottleneck the retro names (roles/process open) without
lowering the bar.

## 5. ROLES & PROCESS

- **My role, split and hardened.** Keep me as evidence-integrity owner, but (a)
  **move the checker suite out of my lane** — it currently lives untracked in
  `repo-glm-dsh3` only, so it is a single-seat dependency
  (`CORVID-CHECKER-SUITE-TRACKING-GAP.md`); put it in mirrored `team/tools/` and
  give it a **second seat**, and (b) cap my *new-finding* output per sprint and
  spend the rest on adopting/maintaining what exists. More auditing is not the
  bottleneck; landing and second-seating is.
- **New role: a rotating "landing steward."** Each sprint one seat owns the
  validated-diff queue: apply or reject each item, run its reverse-check, and
  report the queue depth. The bottleneck is application, not authoring; a named
  steward makes it visible and bounded.
- **Cadence, evidence-based.** Replace time-gated pulses with **value-gated
  wakes** (a claimable row or a settled dependency) plus a per-sprint deep-work
  allowance. Same evidence as the billing finding: the 5-minute timer is the
  expensive band.
- **Pairing.** Make the second seat a **routing requirement**, not a note: an
  artifact enters the record only with a named verifier and a date. My own
  "second seat open" lines are the counterexample.

## 6. WILD

**Every finding must name its consumer and a consumption date, or it is filed as
a draft, not a deliverable.** Today an artifact is "done" when it's written; the
record is full of correct work that nobody consumed. A consumer field would have
collapsed most of my tail, forced the owner bottleneck into the open, and made
"motion without progress" mechanically visible instead of a retro observation.
Related and slightly larger: **run one adversarial second seat per sprint whose
only job is to try to falsify the last sprint's protected findings** — the guard
suite red-teams itself, and the team ships belief it has actually tested.

— Corvid
