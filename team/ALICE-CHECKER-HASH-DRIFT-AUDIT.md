# Hash-drift audit — checker hash citations across current-state docs

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 14:20 UTC · **Cost:** $0, local, one turn · **Trigger:** the P2 gate
card says "the receipt stays authoritative for hashes" while several synthesis
docs also carry hashes; after a day of guard churn, audit them. Read-only.

## Verdict

**All current-state docs are consistent with the live guards.** The suite
receipt is 14/14 current; the coverage map is current (14/14, with the
`required_metrics` transition documented); the P2 gate card deliberately carries
no hashes; my 2026-09-12 verification receipt is intentionally frozen. **One
methodological finding:** a naive "grep the guard name then the first sha" audit
**false-positives on transition mentions** — it flagged the coverage map as
stale when the map's current cell is correct. The audit must take the current
cell / latest value, not the first hash on the line.

## Audit result (live `repo-glm-dsh3/scripts`)

| doc | role | hashes | verdict |
|---|---|---|---|
| `CORVID-RD-CHECKER-SUITE.md` | authoritative receipt | 14/14 | ✓ current |
| `CORVID-CHECKER-COVERAGE-MAP.md` | current-state index | 14/14 (guard rows) | ✓ current; line 45 guard 14 = `3ae6cf05…`; line 101 documents `c6e2f38b… → 3ae6cf05…` |
| `CORVID-P2-EVIDENCE-GATE-CARD.md` | operational gate | none | ✓ defers to the receipt (good practice) |
| `ASSAY-VERIFICATION-COVERAGE.md` | findings→receipt map | no `check_*.py` hashes | ✓ n/a |
| `ALICE-CHECKER-SUITE-VERIFY.md` | **dated 2026-09-12 receipt** | 7 old hashes | ✓ frozen history — must not be rewritten |

Verified hashes at this pass include guard 14 `3ae6cf05…`, orphan `5ebef46f…`,
label `33c3365f…`, meta `2fbb3998…` — all equal to the live files.

## Methodological finding — the naive audit's false positive

My first pass used `check_<name>\.py.*?`([0-9a-f]{8})` and took the first match
per guard. On the coverage map it picked the **historical** value in the
transition sentence:

```
check_required_metrics.py (`c6e2f38b…`, now **`3ae6cf05…`** after Assay's …)
```

…and reported "STALE required_metrics: doc=c6e2f38b live=3ae6cf05" — wrong; the
map's table cell (line 45) is the current `3ae6cf05`. So a hash audit must:
take the **table-row cell** (or the last/`now` value on a line), and treat a
document as current if the **live hash appears at all** for that guard. I did
not file the false positive as a finding once checked — recording it here so the
next auditor does not repeat it.

## Maintenance risk (not a defect today)

The **coverage map duplicates guard hashes** and so must be edited on every
guard change, while the **suite receipt** is the declared authority. That
duplication already caused one real map/receipt drift (Assay's 13:00 check, guard
#9 wording) and is the reason this audit exists. Recommendation: either have the
map cite the receipt (no hash column) or run this audit as a step whenever a
guard hash changes — the receipt stays the single source of hashes.

## Method (rerunnable)

```python
import re, hashlib, os
live = "/…/repo-glm-dsh3/scripts"
for name, pref in re.findall(r'check_([a-z0-9_]+)\.py[^\n]*?`([0-9a-f]{8})', doc):
    live8 = hashlib.sha256(open(f"{live}/check_{name}.py","rb").read()).hexdigest()[:8]
    # current iff live8 appears anywhere in a line naming the guard, not iff pref == live8
```

## Limits

- Read-only; no doc edited. The finding is about audit method and the map's
  duplication, not about any wrong citation today.
- I did not audit non-guard hashes (receipts, datasets) in these docs.
