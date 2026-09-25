# R27-design-1 — independent design review (design only)

- **Reviewer:** corvid-dsh. Read-only; **no participant execution, no production
  toggle.** Local checks only.
- **Intake:** worker claim `ex-R27-design-1-w1.json`; all 7 output hashes
  recomputed equal (`design.md` `2d3a6fd2…`, `packet.md` `62200b64…`,
  `protocol.json` `33e72b8f…`, `task-pair-A/B/C`, `oracles.md` `549168e9…`).
- **Verdict: FAIL (design-only).** The paired-task design, oracles, packet and
  order are sound; the required **nudge-free participant path is not
  established**, and the design's stated nudge check is inaccurate. Per the
  package, an unresolved isolation prerequisite must be marked, not sampled.

## What passes

- **Exact packet:** `packet.md`/`design.md` packet is **verbatim** equal to the
  `packet` string in `PERSISTENCE-WORDING-DECISION-20260925.json`
  (ADOPTED_PROSPECTIVELY, sponsor relay labelled). Only treatment receives it.
- **Three pairs frozen before outputs:** A (fresh docs), B (decoy `notes.pdf`,
  `DRAFT.TXT`, `old/b0.txt`), C (token edge: hyphen/digit/case). Failed step +
  available self-performable safe next (`rebuild-noextra`) in each; order
  predeclared (coin per pair, counterbalanced 2-1) with no outcome-adaptive
  tasks, reruns or stopping on success.
- **Complete-artifact primary:** actual correct `index.json` matching an
  independent recomputation (regex `[a-z0-9]+`, lowercase, per-file dedup,
  sorted) plus receipt/evidence/output hash-chain; diagnosis-only or
  owner-naming alone fails. Output-sensitive wrong examples per pair
  (stale/partial, decoy-including, case-sensitive, SSH-style) and a satisfying
  example; presence-only checks forbidden; safety/permission branches are
  checker fixtures, not arms. n=3, one model class, no causal claim.

## Blocking residual — nudge-free path not established

The package requires the reviewer to "inspect the actual rendered participant
text/path before recommending execution, not trust a prose assertion of
isolation." I inspected the proposed binaries:

- Private copy `/var/home/bmosher/.local/bin/agent-loop.prev-r23-47f69dfd` sha
  `47f69dfd…`; **current installed** `/var/home/bmosher/.local/bin/agent-loop`
  sha **`612e3c5c…`** (not 47f69dfd). So the installed loop **is** the newer
  build, and the private copy is the older one — consistent with a post-copy R23
  change, but the design never states the current hash and its `protocol.json`
  `binary_check` ("0 copies of nudge prompt vs 1 in current") is not what the
  bytes show.
- Searching both binaries for the stated nudge/revised-packet text yields **0
  in both**; the string that is **unique to the current binary** is the
  three-question block "Before you end your turn … (2) What happens next, who
  does it, and by when? …". So the design conflates the **platform nudge** (the
  three-question block) with the **treatment packet**, and its described
  nudge-string check does not reproduce.

The prev binary plausibly lacks that three-question block, so the mechanism may
work — but the design's factual check is wrong and it never rendered/verified
the actual participant text under the isolated config. That is exactly the
prerequisite the package says to mark UNRESOLVED rather than sample.

**Smallest correction:** capture the actual rendered dispatch text under the
isolated config (a dry-run/`--print` render, or a one-shot render into a temp
dir with no dispatch) and show it contains neither the platform nudge nor the
packet for control; record both binary hashes (prev `47f69dfd…`, current
`612e3c5c…`) and the isolated config's `db`/`claims_dir`/timer namespace; then
re-review the rendered bytes. If the render cannot be produced without a live
dispatch, file the prerequisite as unresolved and propose the smallest
authorized render (or ask Tern to authorize a bounded render).

## Minor

- `protocol.json` "nudge prompt string" description should name the actual
  platform-nudge text (three-question block), not the treatment packet.
- No participant execution; Tern releases execution separately on PASS.

*Reviewed: `package.md`, worker claim, `design.md`, `packet.md`,
`protocol.json`, `task-pair-A/B/C.md`, `oracles.md`,
`PERSISTENCE-WORDING-DECISION-20260925.json`; binary hashes/strings and
nudge-text searches.
