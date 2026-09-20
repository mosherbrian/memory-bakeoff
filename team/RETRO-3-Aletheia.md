# RETRO-3 — Aletheia (Alice), `worker-glm-dsh`

**Seat:** verifier — independent sign-off on built-but-unapplied poller/sprint
deliverables. **Method:** hermetic harnesses (stub `wake`/registry, no live
sends) + re-run of committed suites, from my own turns today.

## 1. Close count (what I finished, not pulses)
- **§11 sprint-close detector — SIGN-OFF, then caught a real defect:** the spend read ran
  `meters.budget()` (3 live HTTPS endpoints) every 60 s, not on close; fix re-verified by
  call-counting (0 calls steady-state). Final verdict delivered to Brian. (`RD-THREADS.md`)
- **S3-3 adapters — VERIFIED PASS:** 6 adapters + 10 adapter tests reproduced, suites 39 green,
  ACM deferral confirmed. Receipt `team/ALICE-S3-3-VERIFICATION.md`.
- **§9 completion-chaining — re-affirmed PASS** on the 17:54 revision (pipe fix, hop cap, ghost
  fallback, backfill); **§10 verdict-due clock — new SIGN-OFF PASS**. (`RD-THREADS.md`)
- **§8 conductor exemption — SIGN-OFF PASS** + one finding (exemption log repeats every sweep). (`RD-THREADS.md`)
- **S3-9 — scope note:** items 1–2 PASS; item 3 partly enabled by §11; Signal path still absent.

## 2. Churn
- Roughly **1 describing : 11 doing** — every turn ran a harness or re-ran suites, not prose.
- Largest churn source: **ambiguous dispatch labels.** "section-9" could mean poller §9, poller §10,
  or QUEUE row S3-9, so I verified all three to be safe. One artifact, one name, please.
- Second: re-verifying stale sign-offs after each new revision (revision moved 16:21 → 17:46 → 17:54 →
  18:50 today); a revision hash on the sign-off would let a verifier skip a no-op re-read.

## 3. Event-driven, honest grade
- **No gated wake reached me today** — my work arrived as direct conductor messages, so I can cite
  **none** in either direction (memory only, no wake log read).
- What I can vouch for is the mechanism: the §9/§10/§11 clocks I verified key on *transitions*, and
  re-sweeps of an unchanged state are silent (harness-proven) — pulse would have been noise.
- Grade **B, unproven for my own seat:** I verified the gates but was not woken by them, so I cannot
  claim first-hand that they reached me "when it mattered."

## 4. Keep / kill
- **Keep:** hash-pinned verification receipts that **re-derive from source**. Every real bug today
  (double-dollar, 60 s spend read, exemption log repeat) was found this way, at $0.
- **Kill:** code comments that assert unenforced behavior — *"zero tokens"*, *"logs once instead of
  every sweep"*. Both were false; both had already been trusted in a prior sign-off. In this fleet
  the comment is where the next finding hides.

## 5. Blind spots (no timer/gate/verifier would have caught these)
- §11's spend read: looked local, was live network every sweep — only reading `meters.budget()` caught it.
- S3-3: 10 green tests hid that the adapters are **not wired into `mine.py`** — green ≠ integrated.
- §8 exemption: the log contradicts its own "logs once" comment — a gate watches wakes, not log volume.
- S3-3's "39 passed" includes 5 unrelated row-30 tests — arithmetic that only a second seat re-counts.

**Who answered:** Aletheia (Alice), `worker-glm-dsh`. Cost: existing turns, $0 pipeline spend.
