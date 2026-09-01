#!/usr/bin/env python3
"""Export/import the frozen Generation 14 agentmemory reader sidecar batches."""

import argparse
import json
from pathlib import Path

from memory_bakeoff.frozen_reader import grade_frozen_sidecar_responses, write_frozen_reader_grades
from memory_bakeoff.sidecar_transport import export_pending_sidecar_requests, import_sidecar_response_bundle


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "results" / "agentmemory_raw_product_gen14_reader_requests"
EXPORT = ROOT / "results" / "agentmemory_raw_product_gen15_sidecar_transport" / "pending_requests.json"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    export = commands.add_parser("export")
    export.add_argument("--package", type=Path, default=PACKAGE)
    export.add_argument("--out", type=Path, default=EXPORT)
    importer = commands.add_parser("import")
    importer.add_argument("bundle", type=Path)
    importer.add_argument("--package", type=Path, default=PACKAGE)
    grade = commands.add_parser("grade")
    grade.add_argument("--package", type=Path, default=PACKAGE)
    grade.add_argument("--out", type=Path, default=ROOT / "results" / "agentmemory_raw_product_gen15_sidecar_transport" / "reader_results")
    args = parser.parse_args()
    if args.command == "export":
        result = export_pending_sidecar_requests(args.package, args.out)
        print(json.dumps({"out": str(args.out), "request_count": len(result["requests"]), "request_set_sha256": result["request_set_sha256"]}, indent=2))
    elif args.command == "import":
        print(json.dumps(import_sidecar_response_bundle(args.package, args.bundle), indent=2))
    else:
        result = grade_frozen_sidecar_responses(args.package)
        write_frozen_reader_grades(result, args.out)
        print(json.dumps({"out": str(args.out), "conditions": list(result["conditions"])}, indent=2))


if __name__ == "__main__":
    main()
