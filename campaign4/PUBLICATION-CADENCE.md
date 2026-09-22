# Campaign publication cadence

Tern, 2026-09-22. Effective immediately. Charter already authorizes commit AND push;
no new sponsor permission is required. Local commits alone are not publication.
The 27-hour gap was a director omission, not a permission boundary. Brian's delegate
pushed through b3db16b; subsequent completed commits still require publication.

Owner: Tern pushes and verifies the remote. Cairn owns bounded local evidence commits
and reports their full commit IDs; it need not race Tern with independent pushes.

Push the completed commit frontier to origin/fleet/team-corpus:
- at every terminal package disposition, together with any opened successor;
- after a director acceptance, material ruling or release is pinned;
- before ending a director turn that created commits, batching that turn's commits
  into one push. Receipt-only turns with no new commit need no redundant push.

Use ordinary fast-forward push with an explicit ref/commit; never force-push.
Capture the intended local commit first, then verify the remote branch names that
commit or a descendant (another authorized writer may advance it). A successful
local commit or attempted push is not proof of remote publication. Report failed
pushes as publication failures and resolve ordinary conflicts/network issues within
authority; never erase remote work. Keep the local record intact if remote is down.

Push only already-created commits. Do not stage/commit dirty work merely to make the
worktree clean, sweep unrelated paths, reset/stash another seat's work, or stop the
fleet for publication. Dirty paths are unaffected by a push. Existing exact-path
commit discipline remains mandatory. No auto-push daemon, model polling or extra
per-event narrative ledger. Tool receipt + remote commit verification is evidence;
include the published frontier in boundary reports instead of a recursively committed
'push succeeded' file. Future authorized conductor-chat work uses the same cadence
on its actual agreed branch; no blanket push of unrelated repositories/branches.

Control-ledger preservation: at each director publication boundary also capture a
new immutable byte/hash checkpoint per LEDGER-PRESERVATION-20260922.md. Publishing
other files is not preservation of an uncommitted shared ledger. Leave the live TSV
untouched; compare prior snapshot prefixes and report any divergence.
