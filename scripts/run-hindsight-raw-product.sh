#!/usr/bin/env bash
# Run one fresh, configuration-pinned Hindsight raw_product retrieval repetition.
# Usage: scripts/run-hindsight-raw-product.sh <run-label> <distractors> <result-dir>
set -euo pipefail

if [[ $# -ne 3 ]]; then
  echo "usage: $0 <run-label> <distractors> <result-dir>" >&2
  exit 64
fi

label=$1
distractors=$2
out=$3
if [[ ! $label =~ ^[a-z0-9-]+$ ]]; then
  echo "run-label must contain only lowercase letters, digits, and hyphens" >&2
  exit 64
fi
if [[ ! $distractors =~ ^(0|[1-9][0-9]*)$ ]]; then
  echo "distractors must be a non-negative integer" >&2
  exit 64
fi
if [[ -e $out ]]; then
  echo "result directory already exists: $out" >&2
  exit 73
fi

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo_root"
python_bin="$repo_root/.venv/bin/python"
api_bin="$repo_root/.venv/bin/hindsight-api"
if [[ ! -x $python_bin || ! -x $api_bin ]]; then
  echo "expected .venv/bin/python and .venv/bin/hindsight-api" >&2
  exit 69
fi

model_revision=614241f622f53c4eeff9890bdc4f31cfecc418b3
model_dir=/private/tmp/hindsight-hf-cache/hub/models--intfloat--multilingual-e5-small/snapshots/$model_revision
if [[ ! -f $model_dir/onnx/model.onnx ]]; then
  echo "pinned ONNX model snapshot is unavailable: $model_dir" >&2
  exit 69
fi

tmp_dir=$(mktemp -d /private/tmp/memory-bakeoff-hindsight.XXXXXX)
api_log="$tmp_dir/api.log"
api_pid=''
cleanup() {
  if [[ -n $api_pid ]]; then
    kill -TERM "$api_pid" 2>/dev/null || true
    wait "$api_pid" 2>/dev/null || true
  fi
  rm -rf "$tmp_dir"
}
trap cleanup EXIT

export HINDSIGHT_API_LLM_PROVIDER=none
export HINDSIGHT_API_EMBEDDINGS_PROVIDER=onnx
export HINDSIGHT_API_EMBEDDINGS_ONNX_MODEL_ID=intfloat/multilingual-e5-small
export HINDSIGHT_API_EMBEDDINGS_ONNX_MODEL_PATH="$model_dir"
export HINDSIGHT_API_EMBEDDINGS_ONNX_TOKENIZER_NAME_OR_PATH="$model_dir"
export HINDSIGHT_API_EMBEDDINGS_ONNX_DIMENSIONS=384
export HINDSIGHT_API_EMBEDDINGS_ONNX_MAX_TOKENS=512
export HINDSIGHT_API_EMBEDDINGS_ONNX_POOLING=mean
export HINDSIGHT_API_EMBEDDINGS_ONNX_NORMALIZE=true
export HINDSIGHT_API_EMBEDDINGS_ONNX_QUERY_PREFIX='query: '
export HINDSIGHT_API_EMBEDDINGS_ONNX_PASSAGE_PREFIX='passage: '
export HINDSIGHT_API_RERANKER_PROVIDER=rrf
export HINDSIGHT_API_DATABASE_URL="pg0://memory-bakeoff-gen4-$label"
export HINDSIGHT_API_HOST=127.0.0.1
export HINDSIGHT_API_PORT=8891
export HINDSIGHT_URL=http://127.0.0.1:8891
export HINDSIGHT_BANK="memory-bakeoff-gen4-$label"
export HINDSIGHT_RAW_LLM_PROVIDER=none
export HF_HOME=/private/tmp/hindsight-hf-cache

"$api_bin" --host "$HINDSIGHT_API_HOST" --port "$HINDSIGHT_API_PORT" >"$api_log" 2>&1 &
api_pid=$!
for _ in $(seq 1 72); do
  if curl --fail --silent --show-error "$HINDSIGHT_URL/health/ready" >/dev/null 2>&1; then
    break
  fi
  sleep 5
done
if ! curl --fail --silent --show-error "$HINDSIGHT_URL/health/ready" >/dev/null; then
  echo "Hindsight did not become ready for $label" >&2
  tail -n 120 "$api_log" >&2
  exit 75
fi

PYTHONPATH=src "$python_bin" -m memory_bakeoff.cli run \
  --providers hindsight --mode raw --top-k 5 --distractors "$distractors" --out "$out"

RUN_LABEL="$label" RESULT_DIR="$out" MODEL_REVISION="$model_revision" "$python_bin" - <<'PY'
import importlib.metadata
import json
import os
import platform
from pathlib import Path

out = Path(os.environ["RESULT_DIR"])
packages = ("hindsight-api-slim", "hindsight-client", "hindsight-embed", "pg0-embedded", "asyncpg", "onnxruntime", "transformers", "tokenizers")
runtime = {
    "experiment_class": "raw_product",
    "run_label": os.environ["RUN_LABEL"],
    "service": {"package": "hindsight-api-slim", "version": importlib.metadata.version("hindsight-api-slim")},
    "packages": {name: importlib.metadata.version(name) for name in packages},
    "database": {"backend": "pg0-embedded", "namespace": f"memory-bakeoff-gen4-{os.environ['RUN_LABEL']}"},
    "raw_ingestion": {"llm_provider": "none"},
    "embeddings": {
        "provider": "onnx",
        "model": "intfloat/multilingual-e5-small",
        "snapshot_revision": os.environ["MODEL_REVISION"],
        "dimensions": 384,
        "pooling": "mean",
        "normalize": True,
        "max_tokens": 512,
        "query_prefix": "query: ",
        "passage_prefix": "passage: ",
    },
    "reranker": {"provider": "rrf", "learned_reranker_active": False},
    "retrieval_arms": {
        "directly_observed": ["semantic", "keyword"],
        "configured_but_not_validated_through_extracted_source_facts": ["graph", "temporal"],
    },
    "host": {"system": platform.system(), "release": platform.release(), "machine": platform.machine(), "python": platform.python_version()},
}
(out / "hindsight_runtime.json").write_text(json.dumps(runtime, indent=2) + "\n")
run = json.loads((out / "run.json").read_text())[0]
if run["status"] != "ok" or not run["publishability"]["publishable"]:
    raise SystemExit(f"non-publishable run preserved at {out}: {run['status']} / {run['publishability']}")
PY
