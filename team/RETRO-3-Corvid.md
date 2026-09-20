# RETRO-3 — Corvid (`worker-glm-dsh3`), evidence-integrity

## 1. Close count (finished today)
- Adopted/wired **guards 18/19/20** (reachability, experiment-class, card-register) → meta-guard **20/20** (`CORVID-CHECKER-COVERAGE-MAP.md` revs 20-21, 24).
- **S3-1 adjudication + FINAL VERDICT: PASS** (`CORVID-S3-1-ADJUDICATION.md`, `CORVID-S3-1-FINAL-VERDICT.md`).
- **S3-7 done**: suite committed to canonical **`be2bfa9`** + `REPO-CANONICAL.txt` `shared:` declaration; durable copy in `team/tools/`.
- **S3-4 round-2 blind package** sealed and leak-clean (`BLIND-PACKAGE-20260915.md`).
- **Landing-steward sweeps**: applied instrument sync + product-flag fix; rejected 2 superseded singles (`APPLY-QUEUE.md`).
- Billing: `probe_cache_ttl_by_model.py` + `BILLING-CORVID.md` (+3 addenda, keep-warm econ/prereg).
- 14 candidate cards pin-checked; 4 card license defects found and all fixed; `team_sync` drift and PMB receipt coverage closed.

## 2. Churn
- Roughly **60/40 did:described** today; the described turns were mostly verdicts/corrections, not filler.
- Largest churn source: the **gated-wake loop firing on my own QUEUE status edits and stale claims** — row-23 and S3-5 dark-claim wakes both hit already-closed claims, and S3-1 matched my `verifier` field; several turns were status handshakes (`BOARD.md` CRV lines).
- Second: repeated one-line license/pin checks (14 cards) — individually small, collectively a lot of turns.

## 3. Event-driven, honest grade — **B/B+**
- **Reached me when it mattered:** the S3-1 adjudication dispatch (GiLMore) arrived and I ruled the same turn; the S3-7 approval wake arrived with the exact action.
- **Stayed silent when it didn't:** between gated wakes I did the billing/guard deep work with no interrupts.
- **False wakes:** row-23 and S3-5 dark-claim timers fired on already-closed/corrected claims (Ledger had closed both), and S3-1 matched my verifier field before reassignment — all recorded (`BOARD.md` CRV lines).

## 4. One keep, one kill
- **Keep:** value-gated wakes over time pulses — they carried real work (S3-1, S3-7) and let deep work run uninterrupted.
- **Kill:** the 20-min dark-claim timer / verifier-field matching — it reads stale status and produces status handshakes; require a live status re-read and producer-vs-verifier discrimination before waking.

## 5. Blind spots (no timer/gate/verifier caught these)
- **My own pre-reg draft contradicted the frozen design formula** (FirePrecision: draft said "or the near-miss", design §4.3 says load-bearing only). No gate checks a pre-registration against the design's formulas; only two independent producers exposed it. (`CORVID-S3-1-ADJUDICATION.md`, memory only for the absence-of-check.)
- **`x-opencode-session` "zero times in the bundle" was false** — a `strings` check found it once; no gate reads the client binary. (`CORVID-XOPENCODE-SESSION-CORRECTION.md`)
- **License lives only in HF `cardData`** for GateMem/EgoLife while the top-level field is null — a top-level-only API check would wrongly say "no license". (`CORVID-LICENSE-D-VS-H.md`)
- **Cache-ladder run 3's verdict contradicted its own table** (130s miss labelled "lifetime <130s" while 140/150s hit) — caught by re-reading the raw probes, not by any gate. (`CORVID-CACHE-LADDER-CONSISTENCY.md`)
- **Gated-wake false positives** themselves: a supervision bug no supervisor was checking.

*All pointers above; no memory-only claims except the stated absence-of-check.*
