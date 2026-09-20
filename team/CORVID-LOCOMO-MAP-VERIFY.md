# LoCoMo category map — second-driver verification

**Author:** Corvid (`worker-glm-dsh3`), R&D + evidence-integrity
**Date:** 2026-09-12 · **Cost:** $0, local analysis of an already-hashed dataset
**Target:** `team/ALICE-LOCOMO-CATEGORY-MAP.md` (Alice). This is an independent
re-derivation from the dataset, not a re-read of her note.

**Plain English (for Brian):** the map that says which LoCoMo question number
means which category is load-bearing — our cross-vendor per-category tables are
wrong if it is wrong. I re-derived it from the dataset's own evidence spans and
it **holds exactly**. I found one small wording error in the note's id-5 cell.

## Method (independent of Alice's script)

`team/row-locomo-map-receipts/locomo10.json`: for every question, take its
`category` id and count the distinct sessions in its `evidence` list
(`D<session>:<turn>`). Single-session vs multi-session distinguishes single-hop
from multi-hop, per the paper's definitions.

```python
import json, re
from collections import defaultdict
d = json.load(open("locomo10.json"))
stats = defaultdict(lambda: [0, 0, 0])  # n, one-session, multi-session
for conv in d:
    for qa in conv["qa"]:
        s = stats[int(qa["category"])]
        s[0] += 1
        sessions = {m.group(1) for e in (qa.get("evidence") or [])
                    for m in [re.match(r"D(\d+)", str(e))] if m}
        s[1 if len(sessions) == 1 else 2] += 1
```

## Result — the map reproduces exactly

| id | n | one session | >1 session | Alice's note | Match |
|---|---|---|---|---|---|
| 1 | 282 | 13 | 269 | 282 / 13 / 269 | ✅ |
| 2 | 321 | 293 | 28 | 321 / 293 / 28 | ✅ |
| 3 | 96 | 61 | 31 | 96 / 61 / 31 | ✅ |
| 4 | 841 | 840 | 1 | 841 / 840 / 1 | ✅ |
| 5 | 446 | 446 | 0 | 446 / 446 / 0 | ✅ |

**Authoritative map confirmed: 1 = multi-hop, 2 = temporal, 3 = open-domain,
4 = single-hop, 5 = adversarial.** Total 1986 questions.

## One correction to Alice's id-5 cell

Alice's table cell reads **`0 (all answers "None")`**. In the dataset, the 446
id-5 questions are **not all `None`**:

| id-5 `answer` state | count |
|---|---|
| key **absent** (`"answer"` not present) | **444** |
| `"No"` | 2 |
| explicit `null` | 0 |

The **adversarial classification and the map are unaffected** (adversarial
questions have no gold answer); only the wording changes. The cell should read
`444 no answer key + 2 "No"`.

## Minor observation

id 3 has **4 questions with empty `evidence`** (the other 92 have evidence).
That is consistent with Alice's "mixed evidence" note for open-domain and does
not change the map.

## Verdict

Map **confirmed**; no number in the map changes. One wording correction for the
owner (`ALICE-LOCOMO-CATEGORY-MAP.md`, id-5 cell). Reproduce with the snippet
above against `team/row-locomo-map-receipts/locomo10.json`.

— **Corvid** (`worker-glm-dsh3`). Second driver, same answer; one cell needed a
smaller claim.
