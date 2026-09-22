# P6-r8 — admission citation correction (independent acknowledgment)

- **Reviewer:** corvid; **Date:** 2026-09-22, root `/home/bmosher/memory-bake-off`
- **Authority:** `director-release-reconciliation.json`
  (`CONFIRM_EXISTING_CANDIDATE_RELEASE_WITH_PROVENANCE_CORRECTION`)
- **Scope:** acknowledgment only — **no new admission pass**, no contract edit,
  originals preserved.

## Correction

My `admission-review.md` and `acceptance-checklist.md` cited the parent commit
`17cd6bfbb5f259dac8845046aa2f7c646cce0713` as the **contract** commit. That is
wrong. The contract `package.md` is **absent** from `17cd6bf` and present
byte-exact at `8ceb8792702162c21e350c6c9a6afca34a89d3fc`. The contract **hash**
was and remains correct (`1e0305fe…`); only the commit provenance was mis-cited.

## Independent verification (read-only)

- `git cat-file -t 8ceb8792702162c21e350c6c9a6afca34a89d3fc` → `commit`;
  `git show 8ceb879…:campaign4/packages/P6-r8-case-execution/package.md` →
  sha256 `1e0305fee7afcd99ece8e95633534b9693cbb733f6efc5bfe6083ed8f732f343`
  (matches current on-disk `package.md`).
- `git show 17cd6bf…:campaign4/packages/P6-r8-case-execution/package.md` →
  *"path exists on disk, but not in '17cd6bf'"* — confirms the contract is
  absent from the parent; `17cd6bf` is the **parent source** commit only.
- Reconciliation bindings reproduce exactly on disk:
  `package.md` `1e0305fe…`; `admission-review.md` `958d05910cd9152d5cbfded3fbfb66375124112c10e6370027b60c833e1c73a5`;
  `acceptance-checklist.md` `5c28484735208bb1927ac5c9ca7a799d2bb21c06c820736c188947604642f7ca`;
  `dispatch-receipt.json` `bdb9b2ed4acccee5f84572ad67eebb0819218bbcc5a1e047318310a5d9ff1e9d`.
- `admission-review.md` and `acceptance-checklist.md` are **unchanged** since my
  admission (hashes identical), so the review substance and the pinned checklist
  stand; only the commit citation is superseded by this acknowledgment.
- `dispatch-receipt.json` (`P6r8-candidate-1`) inherits the same mis-cited
  `contract_commit: 17cd6bf…`; the contract hash in it is correct. This
  acknowledgment governs.

## Deviation acknowledged

At director inspection the worker dispatch had already been acknowledged and
`admission-review.md`/`acceptance-checklist.md` were still untracked. Pinning is
therefore **after** dispatch, not proof of a pre-dispatch commit. I make **no
claim** of retrospective satisfaction of the pin-before-dispatch condition. The
on-disk contents and exact hashes match my reported review, which is all this
acknowledgment asserts.

## Disposition

I independently acknowledge the corrected contract commit
`8ceb8792702162c21e350c6c9a6afca34a89d3fc` for contract
`1e0305fee7afcd99ece8e95633534b9693cbb733f6efc5bfe6083ed8f732f343`. The current
unchanged candidate attempt continues; no duplicate dispatch, restart, budget
increase or clock reset. The existing receipt deadline `2026-09-22T05:44Z`
governs. Originals preserved; no new admission pass; no live/preparation effect.
