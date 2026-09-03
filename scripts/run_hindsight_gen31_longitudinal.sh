#!/usr/bin/env bash
# Gen31 preflight: what Hindsight v0.9.2's raw/no-LLM temporal surface actually does.
# Unrelated synthetic domain only. Determines semantics; never tunes scoring.
set -euo pipefail
rep=${1:?usage: run_hindsight_gen31_longitudinal.sh <repetition> <out.json>}
out=${2:?usage: run_hindsight_gen31_longitudinal.sh <repetition> <out.json>}
root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
pg=/opt/homebrew/opt/postgresql@17/bin
label="gen31r${rep}$$"
db="memory_bakeoff_hindsight_$label"
port=$((8900 + rep))
ulimit -n 8192
lsof -n -iTCP:$port -sTCP:LISTEN >/dev/null 2>&1 && { echo "port $port occupied" >&2; exit 75; }
"$pg/createdb" -h 127.0.0.1 "$db"
model=/private/tmp/hindsight-hf-cache/hub/models--intfloat--multilingual-e5-small/snapshots/614241f622f53c4eeff9890bdc4f31cfecc418b3
log=/private/tmp/memory-bakeoff-hindsight-$label.log
export HINDSIGHT_API_LLM_PROVIDER=none HINDSIGHT_API_EMBEDDINGS_PROVIDER=onnx \
  HINDSIGHT_API_EMBEDDINGS_ONNX_MODEL_ID=intfloat/multilingual-e5-small \
  HINDSIGHT_API_EMBEDDINGS_ONNX_MODEL_PATH="$model/onnx/model.onnx" \
  HINDSIGHT_API_EMBEDDINGS_ONNX_TOKENIZER_NAME_OR_PATH="$model" \
  HINDSIGHT_API_EMBEDDINGS_ONNX_DIMENSIONS=384 HINDSIGHT_API_EMBEDDINGS_ONNX_MAX_TOKENS=512 \
  HINDSIGHT_API_EMBEDDINGS_ONNX_POOLING=mean HINDSIGHT_API_EMBEDDINGS_ONNX_NORMALIZE=true \
  HINDSIGHT_API_EMBEDDINGS_ONNX_QUERY_PREFIX='query: ' HINDSIGHT_API_EMBEDDINGS_ONNX_PASSAGE_PREFIX='passage: ' \
  HINDSIGHT_API_RERANKER_PROVIDER=local HINDSIGHT_API_RERANKER_LOCAL_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2 \
  HINDSIGHT_API_RERANKER_LOCAL_FORCE_CPU=true \
  HINDSIGHT_API_DATABASE_URL="postgresql://bmosher@127.0.0.1:5432/$db" \
  HINDSIGHT_API_HOST=127.0.0.1 HINDSIGHT_API_PORT=$port HINDSIGHT_URL="http://127.0.0.1:$port" \
  HINDSIGHT_BANK="memory-bakeoff-$label" HINDSIGHT_RAW_LLM_PROVIDER=none HF_HOME=/private/tmp
"$root/.venv/bin/hindsight-api" --host 127.0.0.1 --port $port >"$log" 2>&1 & pid=$!
cleanup(){ kill -TERM "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true; "$pg/dropdb" -h 127.0.0.1 --if-exists "$db" || true; }
trap cleanup EXIT
for _ in $(seq 1 30); do curl -fsS "http://127.0.0.1:$port/health/ready" >/dev/null 2>&1 && break; kill -0 "$pid" 2>/dev/null || { tail -40 "$log" >&2; exit 75; }; sleep 5; done
curl -fsS "http://127.0.0.1:$port/health/ready" >/dev/null
PYTHONPATH="$root/src" "$root/.venv/bin/python" "$root/scripts/gen31_repetition.py" \
  --repetition "$rep" --bank "memory-bakeoff-$label" --db "$db" --port "$port" --pgbin "$pg" --out "$out"
