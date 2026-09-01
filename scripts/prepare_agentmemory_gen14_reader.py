#!/usr/bin/env python3
"""Freeze Gen13 reader inputs without rerunning agentmemory retrieval."""

from pathlib import Path

from memory_bakeoff.frozen_reader import prepare_frozen_reader_requests, write_sidecar_request_package


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    out = ROOT / "results" / "agentmemory_raw_product_gen14_reader_requests"
    if out.exists():
        raise SystemExit(f"refusing to overwrite existing package: {out}")
    out.mkdir(parents=True)
    for condition in ("core", "stress"):
        run_path = ROOT / "results" / f"agentmemory_raw_product_gen13_{condition}-r1" / "run.json"
        label = f"agentmemory_gen13_{condition}_r1"
        requests, evidence, manifest = prepare_frozen_reader_requests(run_path, provider_label=label)
        write_sidecar_request_package(out / condition, requests, evidence, manifest)
    (out / "README.md").write_text(
        "# Generation 14 frozen reader requests\n\n"
        "These sidecar-compatible batches were reconstructed only from the published Generation 13 run.json native ingest traces and returned-ID order. They do not call agentmemory or filter its evidence. Responses are intentionally absent until an interactive ChatGPT sidecar responder services the pending batches.\n"
    )


if __name__ == "__main__":
    main()
