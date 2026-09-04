#!/usr/bin/env python3
"""Re-read every stream a manifest claims to retain. Exit non-zero if any is gone.

    python scripts/verify_raw_evidence_retention.py <manifest.json> <archive_root>

This is the check Gen47 and Gen49 did not have. Their manifests asserted that
the raw streams were retained; nothing ever went back and looked.
"""
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/"src"))
from memory_bakeoff.pi_state_control.raw_evidence import verify_retention

def main(argv):
    if len(argv) != 3:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    manifest = json.loads(Path(argv[1]).read_text())
    verified = verify_retention(manifest, Path(argv[2]))
    print(json.dumps({"retention_verified": verified["retention_verified"],
                      "streams": len(verified["streams"]),
                      "failures": verified["failures"]}, indent=1))
    return 0 if verified["retention_verified"] else 1

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
