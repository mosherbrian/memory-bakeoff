# muse-drafter: GateMem code/data license check (spark pulse 2026-09-14)

Closes CANDIDATE-CARD-MEMSEC-GATEMEM.md Next-step 1, GateMem half (MemSecBench half closed in SPARK-MEMSECBENCH-ARTIFACT-NOTE.md).

- Code `rzhub/GateMem`: repo About box reads **MIT license**; raw `LICENSE` (main) fetched this pass = MIT, copyright 2026 Renz. Permissive; no share-alike bar on our design-reference use.
- Data `Ray368/GateMem` (HF): header **License: cc-by-4.0**; 4 subsets (education 540 / household 552 / medical 579 / office 547 checkpoints + episodes), gated rows viewer working this pass. CC-BY 4.0 = attribution only; fine to read/measure against, attribute on any derived citation.
- Grounding note: GateMem ships real artifacts (91 episodes / 2,218 hidden checkpoints per repo page; viewer confirms per-checkpoint utility/privacy/safety rows with leak_targets). Card's "abstract-only" status for GateMem numbers is now stale — numbers still not imported (candidate discovery only), but the harness is inspectable, unlike MemSecBench.

$0, web reads only (repo page + raw LICENSE + HF dataset page), no Muse batching. — muse-drafter (Spark)
