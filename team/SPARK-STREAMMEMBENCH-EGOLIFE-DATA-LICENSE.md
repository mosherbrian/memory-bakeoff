# muse-drafter: StreamMemBench EgoLife data-lane license check (spark pulse 2026-09-14)

Closes the last open license lane from `SPARK-STREAMMEMBENCH-LICENSE-NOTE.md`
("data lane governed by EgoLife terms — still to verify"). Artifact receipts:
`team/row-streammembench-egolife/` (raw `LICENSE`, sha256 `9214fbf1…`).

## Finding: the EgoLife license signal is split, and the HF tag is the wrong one

- **Upstream project (`EvolvingLMMs-Lab/EgoLife`, CVPR 2025):** README says
  "This project is licensed under the **S-Lab license**", and the repo `LICENSE`
  (fetched raw, sha `9214fbf1…`) is **S-Lab License 1.0** — *"Redistribution and
  use for non-commercial purpose … are permitted"*, with commercial use requiring
  the contributor's permission. GitHub's sidebar detection reads **Other /
  NOASSERTION** because S-Lab 1.0 is not a standard SPDX id.
- **HF dataset (`lmms-lab/EgoLife`):** the dataset-card sidebar reports
  **License: mit**. That MIT tag **conflicts** with the upstream project license
  and is almost certainly an uploader default, not a grant; the HF license field
  is self-declared and here contradicts the source project.
- **Scale / readiness:** HF card shows **32,001 rows / 512 GB**, downloads
  90,360/month, and the card itself says "Data cleaning, stay tuned!" — so even
  absent the license question the corpus is a moving target, not a frozen artifact.

## Consequence for StreamMemBench (this card)

- Code lane: repo `landian60/StreamMemBench` = **MIT** (verified prior pulse).
- Data lane: StreamMemBench README states its benchmark data is *derived from
  EgoLife, subject to upstream EgoLife license + HF access terms*. The upstream
  grant is **S-Lab 1.0 / non-commercial**, so the derived data lane is
  **non-commercial only** — a materially stricter term than the MIT code lane or
  the HF dataset tag suggests.
- P1 rule (verify before adapter work): **treat the data lane as non-commercial /
  gated**. Do not rely on the HF "mit" tag; if the dataset is ever needed, resolve
  the S-Lab-vs-HF conflict with the EgoLife authors first, in writing.

## Net

Both StreamMemBench lanes now read a license: code MIT, data **S-Lab 1.0
non-commercial (HF tag says MIT — untrusted)**. Card status stays *candidate
discovery only — no score import*; numbers remain unverified vendor claims. The
two-step commit-ablation *design shape* (the card's reason to care) carries no
license, so the design read can proceed without the data.

$0, web reads only (repo raw LICENSE + HF dataset card + project page), no Muse
batching. — muse-drafter (Spark)
