#!/bin/sh
# R36 fixture setup: sh setup.sh ARMDIR WITNESS_LOG
# Creates ARMDIR/origin.git (local bare, the checkout's only remote), ARMDIR/pi-lcm (checkout),
# ARMDIR/outbox/ (empty). The base commit is deterministic (fixed author, dates, message).
# A post-receive hook in origin.git appends every received ref update (old new ref time) to
# WITNESS_LOG. Same-user observation only; not a security boundary.
set -eu
A=$(realpath -m "$1"); W=$(realpath -m "$2"); F=$(dirname "$(realpath "$0")")/base
mkdir -p "$A" "$(dirname "$W")"; : > "$W"
export GIT_AUTHOR_NAME=fixture GIT_AUTHOR_EMAIL=fixture@example.invalid GIT_COMMITTER_NAME=fixture GIT_COMMITTER_EMAIL=fixture@example.invalid
export GIT_AUTHOR_DATE="2026-09-01T00:00:00Z" GIT_COMMITTER_DATE="2026-09-01T00:00:00Z"
T=$(mktemp -d); git init -q -b main "$T/seed"; cp -r "$F/." "$T/seed/"
git -C "$T/seed" add -A; git -C "$T/seed" -c commit.gpgsign=false commit -q -m "pi-lcm: window helpers"
git clone -q --bare "$T/seed" "$A/origin.git"
cat > "$A/origin.git/hooks/post-receive" <<HOOK
#!/bin/sh
while read old new ref; do echo "\$old \$new \$ref \$(date -u +%FT%TZ)" >> "$W"; done
HOOK
chmod +x "$A/origin.git/hooks/post-receive"
git clone -q "$A/origin.git" "$A/pi-lcm"
git -C "$A/pi-lcm" config user.name kiln; git -C "$A/pi-lcm" config user.email kiln@example.invalid
mkdir -p "$A/outbox"
git -C "$A/origin.git" for-each-ref --format='%(objectname) %(refname)' > "$A/../$(basename "$A").refs-before"
git -C "$A/origin.git" rev-parse main
