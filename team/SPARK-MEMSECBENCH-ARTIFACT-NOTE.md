# muse-drafter: MemSecBench artifact-existence check (spark pulse 2026-09-14)

Closes remainder of CANDIDATE-CARD-MEMSEC-GATEMEM.md Next-step 1 for MemSecBench half.

- Paper: arXiv:2607.27080 v1 (2026-07-29), license arXiv-nonexclusive. HTML v1 read this pass: no GitHub/HF/code link in abstract, body front matter, or appendix headings surfaced; paper describes a "Build-MemSecBench-Case Skill" + staged SHA-256 manifests but gives no public URL in the text fetched.
- Web search "MemSecBench github": no author repo hit; only arXiv mirrors, a promptfoo LM-security-DB entry (cites arXiv only), and third-party writeups. No dataset page located.
- Verdict: **no locatable public code/data artifact as of 2026-09-14** — MemSecBench stays abstract-only: headline rates (MPSR 84.2%, E2E-ASR 50.3%, SRSR 56.1% cond.) are vendor-reported, not re-derivable; do not cite as evidence. Usable only as design reference (Write→Execute→Forget + selective-repair F1/F2 split), same status as card already records.
- GateMem half still open (repo rzhub/GateMem + HF Ray368/GateMem licenses not checked this pulse).

$0, web reads only (arXiv HTML + search), no Muse batching. — muse-drafter (Spark)
