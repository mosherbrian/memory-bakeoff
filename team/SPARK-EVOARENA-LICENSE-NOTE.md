# muse-drafter: EvoArena/EvoMem code/data license check (spark pulse 2026-09-14)

Closes the addendum residual of `CANDIDATE-CARD-EVOMEMBENCH.md` (EvoArena + EvoMem companion paper, arXiv:2606.13681 v1/v2).

- Code `Aiden0526/EvoArena` (26 stars, 13 commits): file listing = 3 EvoMem-* experiment dirs + assets/docs/README, **no LICENSE file**. README License section is explicit: **"The license will be added with the public release. Please check the final repository license before using the code or data in downstream projects."** → treat as **all-rights-reserved** until a license appears. Repo self-describes as "being released progressively" (only PersonaMem-Evo folder currently released; Terminal/SWE folders placeholders).
- Data `Aiden0526/EvoArena` (HF, linked from paper + README): exists as linked; terms not read this pass — covered by the same "check final license" warning.
- Grounding note (paper/HTML + README, not imported): 39.6% avg agent accuracy under evolution; EvoMem patch-history wrapper +1.5 EvoArena / +3.7 chain / +6.1 GAIA / +4.8 LoCoMo (vendor, do not cite). Design reference only — git-like versioned-evidence-trail + chain accuracy stay the takeaways for our lineage/supersession reporting.
- P1 consequence: same posture as EvoMemBench proper (no-license → read-only, no vendoring/adapting code). No score import.

## Re-check 2026-09-15
- Repo page re-read: unchanged — still 26 stars / 13 commits / 2 forks, no LICENSE file, same "license will be added" warning; Terminal-Bench-Evo and SWE-Chain-Evo folders still read "will contain" (placeholders). No movement on the progressive release.
- Verdict unchanged: ARR posture holds.

$0, web reads only (search + repo page + paper HTML), no Muse batching. — muse-drafter (Spark)
