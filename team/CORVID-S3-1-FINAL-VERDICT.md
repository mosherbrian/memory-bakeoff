# S3-1 FINAL VERDICT — PASS (standard tier, single system, descriptive)

**Verifier of record:** Corvid (`worker-glm-dsh3`) · **Date:** 2026-09-15
**Row:** QUEUE S3-1 — full firing benchmark, standard tier, validated harness.
**Producers:** assay-dsh / muse-drafter (reassigned row), same frozen corpus.
**Cost:** $0 · **No score import.**

## VERDICT: **PASS**

The standard-tier firing run is verified as a valid **single-system descriptive**
result at the `standard` tier. It is not a cross-system headline and no vendor or
system number is imported.

## Checklist result (each item from `CORVID-S3-1-VERIFY-CHECKLIST.md`)

| # | check | result |
|---|---|---|
| 1 | tier + corpus: standard, 60 moments (10/family), corpus `2fa0694b…`; binding-reachability guard **0 findings**; selftest green; no S09-class unfireable moment | **PASS** |
| 2 | shipping definitions: `FalseFire = fired(topic)` on `filler_plain` only (0/60), fresh/gap reported beside; `NearMissFire` 24/24 separate, never folded into FalseFire; `FBMR_topic` 30/30 den 30; **`FirePrecision` corrected to 30/150** (adjudication; 54/150 set aside) | **PASS, with correction** |
| 3 | controls separate: `fire-never` 0/30 & 0/60; `fire-always` 30/30 & 60/60 | **PASS** |
| 4 | determinism: normalized per-turn rows identical 180/180, volatile fields (`at`, `gap_minutes`) excluded | **PASS** |
| 5 | provenance: corpus/manifest/extension/runner hashes, runtime (Py 3.14.6, bun pi 0.84.4), per-scenario isolation, link-never-copy | **PASS** |
| 6 | no score import: rates descriptive only; no cross-system comparison arm | **PASS** |

**Reject conditions: none triggered** (no unfireable labeled moment; no near-miss
folded into FalseFire; no fresh/gap in FalseFire; control separation present;
every rate carries its denominator).

## The one adjudicated item

`FirePrecision` **ships as 30/150** — numerator = topic fires on labeled
load-bearing moments only; the near-miss is credited by `NearMissFire`
(`team/CORVID-S3-1-ADJUDICATION.md`). The conflicting 54/150 traced to a drafting
error in my own pre-registration draft, now corrected; neither producer erred.

## Reporting rule bound to this verdict

Cite `FirePrecision` with its fired-turn strata (30 topic + 60 fresh + 24
near-miss + 18 stale + 18 anachronism = 150) — the number is
corpus-composition-sensitive and must not travel alone.

— **Corvid** (`worker-glm-dsh3`). $0, local.
