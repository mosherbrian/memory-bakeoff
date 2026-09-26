#!/bin/sh
# Copy one arm's complete operator folder into the package as an immutable bundle with a claim of every file hash.
# sh freeze.sh LABEL OPDIR   (bundle: evidence/<LABEL>/, written via temp dir + rename; refuses to overwrite)
set -u; L=$1; OP=$2; E=/var/home/bmosher/memory-bake-off/campaign4/packages/R58-context-evidence-boundary/evidence${EVIDENCE_SUFFIX:-}
mkdir -p $E; [ -e $E/$L ] && { echo "bundle exists, not overwriting" >> $OP/disposition.txt; exit 1; }
T=$E/.tmp-$L-$$; mkdir -p $T && cp -a $OP/. $T/ && mv $T $E/$L
python - $E/$L $L <<'PY'
import json, hashlib, os, sys
from datetime import datetime, timezone
d, L = sys.argv[1], sys.argv[2]
fs = {os.path.relpath(os.path.join(r, f), d): hashlib.sha256(open(os.path.join(r, f), "rb").read()).hexdigest() for r, _, fl in os.walk(d) for f in fl if f != "arm-claim.json"}
json.dump({"arm": L, "at": datetime.now(timezone.utc).isoformat(), "files_sha256": fs}, open(os.path.join(d, "arm-claim.json"), "w"), indent=1)
PY
