#!/usr/bin/env bash
# Publish Linux work to the Mac and to origin, in the one order that cannot diverge.
#
# Linux cannot push to GitHub, so work travels Linux -> bundle -> Mac -> origin.
# Every divergence in this repo has had the same cause: the Mac merged a bundle
# and did NOT push, so the next bundle was built against a stale origin/main and
# the fast-forward merge on the Mac refused. The fix is ordering, not cleverness -
# the Mac publishes FIRST, every time, before Linux builds anything.
#
# Usage: scripts/sync-mac.sh
set -euo pipefail

MAC=${MAC:-bmosher@brians-macbook-air.local}
MAC_REPO=${MAC_REPO:-/Users/bmosher/source/repos/memory-bakeoff}
BRANCH=${BRANCH:-main}

mac() { ssh "$MAC" "export PATH=/opt/homebrew/bin:\$PATH; cd '$MAC_REPO' && $1"; }

# 0. Refuse to run from a different branch than the one being synced.
#
#    The first version took the Mac's branch from $BRANCH but built the bundle
#    from whatever Linux HEAD happened to be. Run from a feature branch, it
#    shipped that branch's commits and fast-forwarded MAIN onto them - which is
#    how the work-trigger-canary commit landed on main and auto-closed its own
#    PR as merged. The branch you are on must be the branch you are syncing.
here=$(git rev-parse --abbrev-ref HEAD)
if [ "$here" != "$BRANCH" ]; then
    echo "refusing: on branch '$here' but syncing '$BRANCH'." >&2
    echo "check out $BRANCH first, or run: BRANCH=$here $0" >&2
    exit 2
fi

# 1. The Mac publishes anything it is holding. The omitted step, made mandatory.
mac "git checkout -q $BRANCH && git fetch -q origin && git merge --ff-only origin/$BRANCH -q && git push -q origin $BRANCH"

# 2. Replay local work on top of what the Mac just published.
git fetch -q origin
git rebase -q "origin/$BRANCH"

# 3. Nothing to send is a normal outcome, not a failure.
if [ "$(git rev-parse HEAD)" = "$(git rev-parse "origin/$BRANCH")" ]; then
    echo "in sync at $(git rev-parse --short HEAD)"
    exit 0
fi

# 4. Ship it, merge it, publish it.
bundle=$(mktemp -u /tmp/sync-XXXXXXXX.bundle)
git bundle create "$bundle" "origin/$BRANCH..HEAD" >/dev/null
scp -q "$bundle" "$MAC:$bundle"
mac "git fetch -q '$bundle' HEAD:sync-incoming && git merge --ff-only sync-incoming -q \
     && git branch -q -D sync-incoming && git push -q origin $BRANCH"
rm -f "$bundle"
mac "rm -f '$bundle'"

# 5. Prove all three agree. A sync that reports success without checking is the
#    failure mode this script exists to remove.
git fetch -q origin
linux=$(git rev-parse HEAD)
remote=$(git rev-parse "origin/$BRANCH")
macsha=$(mac "git rev-parse HEAD" | tr -d '\r')
if [ "$linux" != "$remote" ] || [ "$linux" != "$macsha" ]; then
    echo "NOT IN SYNC  linux=${linux:0:7} origin=${remote:0:7} mac=${macsha:0:7}" >&2
    exit 1
fi
echo "synced at ${linux:0:7}"
