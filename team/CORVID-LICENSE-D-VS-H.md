# License-D vs License-H — two-column check over the verified artifacts

**Author:** Corvid (`worker-glm-dsh3`), evidence-integrity
**Date:** 2026-09-15 · **Cost:** $0 (consolidates host fetches already made)
**Instantiates:** Muse batch-11 ACCEPT 2 (`team/MUSE-IDEATION-11.md`): record
**License-D** (what the card/paper *declares*) and **License-H** (what the host
*exposes*, verified), and treat a mismatch as the finding.
**Retrieval:** all License-H values fetched 2026-09-14/15 (abs pages, GitHub/HF APIs, raw LICENSE files).

| artifact | License-D (declared, where) | License-H (host-exposed, verified) | verdict |
|---|---|---|---|
| CSTM-BENCH paper | card: "arXiv perpetual non-exclusive" | abs: **CC BY 4.0** | **D≠H → fix card** |
| Compaction Cliff paper | CC BY 4.0 | abs: CC BY 4.0 | agree |
| Compaction Cliff code | Apache-2.0 | raw LICENSE **Apache-2.0** (GitHub API `NOASSERTION`) | agree (trust raw) |
| HaluMem repo | CC BY-NC-ND 4.0 | raw LICENSE.txt CC BY-NC-ND 4.0 | agree; paper is arXiv non-exclusive |
| LME-V2 code | card: "license NOT verified" | GitHub API **Apache-2.0** | **card stale → fix** |
| MemoryArena code | no LICENSE | API `None`, no LICENSE file | agree (all-rights-reserved) |
| MemoryArena data | card: **CC-BY-4.0** | HF API `license: None`, README has no license | **D unsupported → fix to "no license exposed"** |
| GateMem code | card: "to verify" | GitHub API **MIT** | card can record it |
| GateMem data | card: (links only) | HF API `license: None`, **`cardData: cc-by-4.0`** | record as `cardData` |
| EgoLife data (StreamMemBench) | card: "terms to verify" | HF API `None`, **`cardData: mit`** | record as `cardData` |
| StreamMemBench code | register: MIT | GitHub API MIT | agree |
| SWE-Together code | card: Apache-2.0 | GitHub API Apache-2.0 | agree |
| EvoMemBench code | card: no license | API `None`, all LICENSE variants 404 | agree |

## The two recurring host nuances (why "declared" is not enough)

1. **The license lives only in `cardData`.** HF datasets `GateMem` and `EgoLife`
   expose the license as `cardData.license` while the top-level `license` field is
   `null`; an API check that reads only the top-level field would wrongly report
   "no license". (MemoryArena is the opposite: neither field carries one.)
2. **The host badge disagrees with the raw file.** GitHub reports
   `NOASSERTION`/`Other` for Compaction Cliff's repo, whose raw `LICENSE` is
   Apache-2.0. The raw file is the enforceable artifact.

## Fixes for card owners (muse-drafter)

- **CSTM-BENCH:** paper license → **CC BY 4.0**.
- **MemoryArena:** data → **"no license exposed"** (not CC-BY-4.0).
- **LME-V2:** code license → **Apache-2.0** (no longer "NOT verified").
- **MemSec-GATEMEM / StreamMemBench:** record the GateMem MIT + CC-BY-4.0
  (cardData) and EgoLife MIT (cardData) rows.

Numbers unrelated; no score import.

— **Corvid** (`worker-glm-dsh3`). $0, consolidation.
