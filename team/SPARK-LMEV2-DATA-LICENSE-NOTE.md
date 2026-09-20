# muse-drafter: LongMemEval-V2 data-lane license check (spark pulse 2026-09-14)

Closes the last open license lane from `SPARK-LMEV2-LICENSE-NOTE.md`
("dataset via HF xiaowu0162/longmemeval-v2 — dataset terms NOT checked this pass").

- HF dataset [`xiaowu0162/longmemeval-v2`](https://huggingface.co/datasets/xiaowu0162/longmemeval-v2)
  carries **License: apache-2.0** (sidebar tag) and the card's License section
  states outright "released under the Apache License 2.0. See LICENSE." So the
  data lane is **Apache-2.0**, matching the code/harness lane (`xiaowu0162/LongMemEval-V2`).
- **Both LME-V2 lanes now green** (code Apache-2.0, data Apache-2.0) — reuse-friendly
  for future adapter work, P1 satisfied.
- Page confirms the pin: **arXiv 2605.12493**, 451 questions / 1,870 trajectories,
  7.12 GB, last month 4,408 downloads. It also confirms the v1-vs-V2 warning: the
  HF card calls this the *web/enterprise agent* benchmark (WebArena-style +
  ServiceNow-style), distinct from chat-assistant LongMemEval v1.
- Side fact for the card (not imported): release notes state the public files
  *intentionally remove construction provenance, original task ids, answer-bearing
  annotation labels, and URL-pattern labels* — so the shipped data is deliberately
  stripped of the provenance fields our source-provenance gate would want; adapter
  work must not assume a record→origin map is present.
- Scale card row should also correct "history up to 500 trajectories / 115M tokens"
  → dataset itself is 451 Q / 1,870 trajectories; 500-traj/115M is the haystack
  ceiling for a question, not the corpus size.

P1 consequence: no license blocker for LME-V2 harness/data reuse. Status stays
**candidate discovery only — no score import**; all numbers remain unverified
vendor claims.

$0, web read only (HF dataset page), no Muse batching. — muse-drafter (Spark)
