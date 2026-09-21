# P2 admission state — Tern, 2026-09-21 14:48Z

**ADMITTED; execution HELD.** Corvid's appended repair-confirmation was read
from disk, and the current contract digest matches the independently reviewed
revision: `30f98fd59e9d4026edfff4a01f81ad1e56c7414d6effb90a51faf32933fed9ec`,
commit `a53a7f5fa7a33e04a64110249e7bdd89fb2fb5fc`.

This disposition supersedes the historical DRAFT/awaiting-confirmation header
in that frozen contract without changing the reviewed bytes. The evidence is
`admission-review.md`, “repair-confirmation pass,” CONFIRMED before 15:07Z.

P1 was separately released at contract commit
`33d9a25a5ab610bb92a4bd6f8283202b36c0ab8e`; that release remains in force.
At this check, P1's capability map and execution receipt are not yet present
in the canonical package directory. Tern has not inferred execution or
completion from admission or a queued dispatch message.

P2 may not start until P1's capability map is independently accepted with its
version/hash recorded and Tern explicitly releases P2. No controller code.

## Release — Tern, 2026-09-21, after P1 acceptance

**P2 is explicitly RELEASED under the unchanged admitted contract.**
P1 v1 was accepted by Tern and committed with verification and acceptance at
`dd15764258317c125adc2cd193a44c57ad5dd6b4`:

- P1 capability map SHA256: `b7279897618c41339e4eca3b6744527b991c7c38d712b62bb5eeb8b1c111eea9`.
- P1 verdict SHA256: `98201be92b898a4e278188c035218710028ef79d98edb99d399e69f0c9cd82c2`.
- P2 contract remains `30f98fd59e9d4026edfff4a01f81ad1e56c7414d6effb90a51faf32933fed9ec`
  at `a53a7f5fa7a33e04a64110249e7bdd89fb2fb5fc`.

The same `dd157642…` commit supplies `director-decisions.md`, closing the two
assigned ownership decisions and recording the trust-boundary interpretation.
Cairn records input versions and hashes before dispatch. Kiln has 60 minutes
for its initial attempt; corvid has 30 minutes for independent verification.
The admitted one-repair/30-minute limit and 30-minute post-repair verification
limit remain unchanged. Preserve all attempt history.

Only the four specified P2 documents are worker outputs. No controller code,
upgrade, migration, research execution or subsequent package is authorized.
Cairn owns dispatch, one-shot deadlines, artifact binding and verification
handoff, and wakes Tern for final acceptance or an owned block. P2's outputs
are not frozen merely because the worker has produced them.
