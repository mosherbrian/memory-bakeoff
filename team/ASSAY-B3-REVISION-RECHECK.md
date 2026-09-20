# Assay second-seat re-check — revised invocation-benchmark B3

**Verifier:** Assay (`worker-glm-dsh2`), independent · **Date:** 2026-09-13 · **Cost:** $0, synthetic probe only
**Target:** `team/DESIGN-INVOCATION-BENCHMARK.md` Addendum B3/G7, revised after
`team/ASSAY-INVOCATION-B3-REVIEW.md` (Corvid; design sha `963d0367…` →
**`999abdcc…`**).
**Verdict: PASS / AGREE** — the revision implements the mechanism-owning
predicate my probe required, closes F1–F5, and leaves §4.1/§4.2 untouched —
plus **one low residual (F3b)** in how the written predicate tests `reason`.

## What I checked

1. **The predicate matches the required observer.** Revised B3 now reads:
   `channel=="memory" ∧ mechanism=="proactive_topic" ∧ "topic" ∈ reason ∧
   covering_id ∈ record_ids (exact canonical id) ∧ seq < action_seq`, with
   presence-only demoted to `CBMR`/corroboration and out-of-band arms reporting
   `unmappable`. That is exactly the `strict` observer from my 10:22 probe.
2. **No formula change.** §4.1's `FBMR_topic = |{ m ∈ L : a proactive_topic
   event with at ≤ deadline(m) }| / |L|` and §4.2's companion block read
   identically to the pre-revision text I recorded in my 10:22 review. Addendum
   B3 is now an *observer contract*, consistent with Addendum B's "no formula
   change" header.
3. **The new edge semantics hold.** Re-ran an extended 12-system driver
   (`b3_revision_recheck.py`); all 12 reproduce:

| synthetic system | naive (old draft) | literal `∈` | **strict (B3)** | persist |
|---|---:|---:|---:|---:|
| true topic fire + present at action | 1.0 | 1.0 | **1.0** | 1.0 |
| true topic fire, evicted before action | 1.0 | 1.0 | **1.0** | **0.0** |
| context dump | 1.0 | 0.0 | **0.0** | 0.0 |
| fresh-only | 1.0 | 0.0 | **0.0** | 0.0 |
| explicit-call answer | 1.0 | 0.0 | **0.0** | 0.0 |
| user text mentions id | 1.0 | 0.0 | **0.0** | 0.0 |
| post-action injection | 0.0 | 0.0 | **0.0** | 0.0 |
| **exact tie (`seq == action_seq`)** | 0.0 | 0.0 | **0.0** | 0.0 |
| **out-of-band (`channel != memory`)** | 1.0 | 1.0 | **0.0** | 0.0 |
| **reason = bare string `"nontopic"`** | 1.0 | **1.0** | **0.0** | 0.0 |
| **multi-reason `{topic, fresh}`** | 1.0 | 1.0 | **1.0** | 0.0 |
| substring collision (`R1` in `R1EXTRA`) | 1.0 | 0.0 | **0.0** | 0.0 |

   The strict column recovers the old draft's only true positive and rejects
   every control; the tie rule (strict `<`) and the channel requirement both
   bite; `FBMR_persist` cleanly separates "fired then evicted" (topic 1.0,
   persist 0.0), closing F5.

## Residual F3b (low) — `"topic" ∈ reason` is a substring test if `reason` is free text

The revision writes the membership in prose as `"topic" ∈ e.reason`. If the
harness emits `reason` as a **bare string** rather than a controlled token set,
`in` becomes a substring check: `"topic" in "nontopic"` is **True**, so the
`nontopic` row above false-fires `literal=1.0` while `strict=0.0`. This is the
same substring class F3 closed for ids, now on the reason field.

**Minimal fix (one sentence in B3):** `reason` is emitted as a set/list drawn
from a frozen vocabulary (`topic`/`fresh`/`gap`/…); the check is exact token
membership, not a substring of a description string. The probe's `strict`
observer already encodes that (`_tokens(reason)`).

## Limits

- Synthetic observer probe; bounds the predicate, not a real corpus/adapter.
- I did not have sealed pre-revision bytes for §4.1/§4.2; the "unchanged" check
  compares against the text quoted in my 10:22 review, which is the same text.
- No runs, no model calls, no transcript content.

## Receipts

- Re-check: `implementer/repo-glm-dsh2/scripts/verify-20260913-assay-b3-observer/b3_revision_recheck.py`
  sha256 `757c5adbaa8f138883181b2b4863cf7e5ef9474b90278c9a10031e5a19e450da`
- Result: `.../revision_result.json` sha256 `46b5768f3e0c27873983f99516cdddd8df0ce2865b77509a9142372776ce179e`
- Prior probe (F1–F5): `.../b3_observer_power_check.py` (`dc145b52…`, result `2e7f2959…`)
- Reviewed: `team/DESIGN-INVOCATION-BENCHMARK.md` §4.1–4.2, Addendum B3, G7

— **Assay** (`worker-glm-dsh2`). No tree modified.
