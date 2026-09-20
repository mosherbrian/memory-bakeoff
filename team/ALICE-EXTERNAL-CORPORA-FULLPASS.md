# External-corpora report — remaining numeric claims verified (completes the named full pass)

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 18:3x UTC · **Cost:** $0, public reads, one turn.
**Duty:** `RESEARCH-EXTERNAL-CORPORA-20260913.md` header: "UNVERIFIED — Alice to
check key claims". Assay spot-checked 5 claims and Corvid triaged; this closes
the numbers neither had. Sources cited inline (fetched this turn).

## Newly confirmed (were unverified)

| Report claim | Primary source | Verdict |
|---|---|---|
| SWE-Hero **34,269** | HF card `nvidia/SWE-Hero-openhands-trajectories` README: "Total Trajectories: **34,269**", `license: cc-by-4.0` | **CONFIRMED** |
| Programming by Chat **11,579 sessions / 74,998 messages / 899 developers** | arXiv [`2604.00436`](https://arxiv.org/abs/2604.00436) abstract: "74,998 developer messages from 11,579 chat sessions across 1,300 repositories and 899 developers … Cursor and GitHub Copilot" | **CONFIRMED** (headline set; the paper's later post-dedupe/CLI-excluded set is 11,655 sessions / 76,231 user messages — a version note, not a contradiction) |
| SERA **>200K synthetic** | arXiv [`2601.20789`](https://arxiv.org/abs/2601.20789) abstract: "generating **200,000+ synthetic trajectories**" | **CONFIRMED** |

## Already established (not re-run here)

- SWE-chat counts (`5,851 / 2,692,480 / 14,459 / 205`): card-verified; the card's
  `prompt_pushback` classes **include `takeover` and `requirement_change`**, so
  the report's field list was right and the earlier "overstated vocabulary"
  correction was withdrawn (`ALICE-EXTERNAL-CORPORA-COSIGN.md` A1).
- Wisp (MIT, n<1K), Nebius SWE-rebench (67,074 / 64.3 turns / cc-by-4.0),
  MEnvData (3,872 / 10 langs / apache-2.0), MindForge counts (1,001 / 181.6 /
  177K) — Corvid's triage.
- **Open-SWE-Traces `511,668 rows / 42.6 GB` is wrong** (card 207,489 v1.0;
  later versions + a 151k filtered count) — Assay/Corvid.

## Still unverified (bounded, no effect on the filed position)

- **Kwai SWE-smith 66k** — no primary count found this pass; Tier 4 scale.
- **MindForge "MIT"** — Corvid found no official release/licence; the search
  surface for the name returns an unrelated mental-health project, so the name
  is ambiguous. Tier 3 remains gated on licence.
- **DevGPT 17,913 prompts** — existence only (Corvid); not re-verified.

## Reading

The report's counts are **mostly accurate**: of the numbers anyone has now
checked, only Open-SWE-Traces is wrong, and its field vocabulary claim is
right. The recommendation's Tier 4 demotions do not rest on any of the three
still-unverified items, so no decision changes. The one substantive correction
stands: SWE-chat access is gated (`gated: "auto"`, data 401) despite the public
ODC-BY card.

## Limits

- Public cards/abstracts only; no dataset files downloaded (SWE-chat data is
  gated; the others were not needed to read a headline count).
- "Confirmed" means the primary source states the number, not that the dataset
  was downloaded and counted.
