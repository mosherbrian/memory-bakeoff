# Assay — S4 leak classification: 3 probable real draft-secret exposures + 5 canary-word hits

**Author:** Assay (`worker-glm-dsh2`) · **Date:** 2026-09-13 · **Cost:** $0, local, structural only
**Follow-up to:** `team/ASSAY-S4-LEAKSCAN-PATH-BUG-FIX.md` (4/19 frozen sessions
flagged once my no-op scan was fixed). **Purpose:** decide whether those flags
are real leaks or detector false positives, and name the mechanism.

**Verdict:** the 8 findings split into **3 non-user entries carrying
`draft-<hex>` value-shaped secret tokens (probable real exposure)** and **5
non-user entries that only mention the bare word `draft_id`** (canary-word hits,
likely false positives). Both are "unredacted non-user" under the shared
predicate; the redaction step simply never treats them as memory traffic.

## Evidence (structural; no packet text printed)

All 8 findings hit only `draft_id`; roles are 6 `assistant` / 2 `toolResult`;
none is from a perseus tool.

| session (short) | packet | entry | role | `draft_id`× | `draft-<hex>` values | chars |
|---|---|---:|---|---:|---:|---:|
| 2026-09-12T15-47-02 | turn-001 | 4 | toolResult | 1 | **3** | 3,217 |
| 2026-09-12T15-47-02 | turn-003 | 3 | assistant | 1 | 0 | 5,410 |
| 2026-09-12T19-19-29 | turn-001 | 47 | assistant | 1 | 0 | 2,540 |
| 2026-09-12T20-56-25 | turn-001 | 4 | assistant | 3 | **1** | 1,634 |
| 2026-09-13T00-48-25 | turn-001 | 17 | toolResult | 7 | 0 | 4,218 |
| 2026-09-13T00-48-25 | turn-004 | 5 | assistant | 1 | 0 | 4,708 |
| 2026-09-13T00-48-25 | turn-004 | 7 | assistant | 1 | 0 | 5,606 |
| 2026-09-13T00-48-25 | turn-004 | 9 | assistant | 2 | **1** | 5,555 |

No entry matched a `draft_id[:=]<value>` assignment; the value-shaped tokens
appear independently of the `draft_id` label. No `key=record-` or
`confirmation_code` in any finding.

## Root cause (builder logic)

`is_memory_traffic(entry)` for **non-user** entries returns true only if the
tool name contains `project_perseus_` or the entry text contains one of the
five memory `SENTINELS` (`[project_perseus_recall]`, `[perseus-write]`,
`[recall-nudge]`, `[change-trigger]`, `project_perseus_`). `draft_id` and
`confirmation_code` live in `DRAFT_SECRET_SENTINELS`, which is applied **only to
user entries**. Therefore a non-user entry that carries a draft id but no memory
sentinel is never classified as memory traffic → never redacted → the leak gate
flags it. That is why the gate fires on these 4 sessions and no sentinel/`key=`
canary fires.

## Recommendations (owner: builder = Kiln/fsync; gate = mine/fsync)

1. **Redaction:** extend non-user memory-traffic detection to secret **value
   shapes** — `draft-[0-9a-f]{6,}`, `confirmation_code` assignments — not just
   the memory sentinels. That closes the 3 probable real exposures.
2. **Canary specificity:** replace the bare `draft_id` leak canary with the
   value shape (`draft-[0-9a-f]{6,}` and/or a required assignment); keep
   `key=record-` and `confirmation_code`. That stops flagging the 5 prose/code
   mentions while still catching real values.
3. **Until then:** the gate is conservative — it over-flags prose but does catch
   at least 3 value-shaped exposures. **Do not hand these packets to a rater**;
   re-run the gated builder at close and stop on nonzero.

## Limits

- Structural/regex counts only; I did not print or quote packet text. A secret
  in a shape other than `draft-[0-9a-f]{6,}` could still be missed, and a
  coincidental hex string could be misread as a draft id.
- The builder gate and my scanner share the mirror predicate, so their agreement
  is "gate + mirror", not two independent detectors; this classification adds
  the value-shape test, which is independent of both.
- Frozen snapshot only.

## Receipts

- Classifier: `implementer/repo-glm-dsh2/scripts/verify-20260913-assay-s4-leak-classify/s4_leak_classify.py`
  sha256 `5e93b4b50a23…`
- Result: `.../result.json` sha256 `1bc9c02c1752…`
- Builder (applied gate): `6616c48e00e5…`
- Prior: corrected readiness `.../sealed-s4-gated-recheck-20260913/readiness_fixed.json` sha256 `9286a1359da9…`

— **Assay** (`worker-glm-dsh2`). No tree modified.
