#!/usr/bin/env bash
# Fresh Hindsight raw_product run using the local Homebrew PostgreSQL 17 backend.
set -euo pipefail
[[ $# -eq 3 ]] || { echo "usage: $0 <label> <distractors> <result-dir>" >&2; exit 64; }
label=$1; distractors=$2; out=$3
[[ $label =~ ^[a-z0-9-]+$ && $distractors =~ ^[0-9]+$ && ! -e $out ]] || { echo "invalid label/distractors or existing result directory" >&2; exit 64; }
ulimit -n 8192
lsof -n -iTCP:8891 -sTCP:LISTEN >/dev/null 2>&1 && { echo "port 8891 occupied" >&2; exit 75; }
root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
pg=/opt/homebrew/opt/postgresql@17/bin
db="memory_bakeoff_hindsight_$label"
"$pg/createdb" -h 127.0.0.1 "$db"
model=/private/tmp/hindsight-hf-cache/hub/models--intfloat--multilingual-e5-small/snapshots/614241f622f53c4eeff9890bdc4f31cfecc418b3
log=/private/tmp/memory-bakeoff-hindsight-$label.log
export HINDSIGHT_API_LLM_PROVIDER=none HINDSIGHT_API_EMBEDDINGS_PROVIDER=onnx HINDSIGHT_API_EMBEDDINGS_ONNX_MODEL_ID=intfloat/multilingual-e5-small HINDSIGHT_API_EMBEDDINGS_ONNX_MODEL_PATH="$model/onnx/model.onnx" HINDSIGHT_API_EMBEDDINGS_ONNX_TOKENIZER_NAME_OR_PATH="$model" HINDSIGHT_API_EMBEDDINGS_ONNX_DIMENSIONS=384 HINDSIGHT_API_EMBEDDINGS_ONNX_MAX_TOKENS=512 HINDSIGHT_API_EMBEDDINGS_ONNX_POOLING=mean HINDSIGHT_API_EMBEDDINGS_ONNX_NORMALIZE=true HINDSIGHT_API_EMBEDDINGS_ONNX_QUERY_PREFIX='query: ' HINDSIGHT_API_EMBEDDINGS_ONNX_PASSAGE_PREFIX='passage: ' HINDSIGHT_API_RERANKER_PROVIDER="${HINDSIGHT_RUN_RERANKER_PROVIDER:-rrf}" HINDSIGHT_API_DATABASE_URL="postgresql://bmosher@127.0.0.1:5432/$db" HINDSIGHT_API_HOST=127.0.0.1 HINDSIGHT_API_PORT=8891 HINDSIGHT_URL=http://127.0.0.1:8891 HINDSIGHT_BANK="memory-bakeoff-$label" HINDSIGHT_RAW_LLM_PROVIDER=none HF_HOME=/private/tmp
[[ $HINDSIGHT_API_RERANKER_PROVIDER != local ]] || export HINDSIGHT_API_RERANKER_LOCAL_MODEL=cross-encoder/ms-marco-MiniLM-L-6-v2 HINDSIGHT_API_RERANKER_LOCAL_FORCE_CPU=true
"$root/.venv/bin/hindsight-api" --host 127.0.0.1 --port 8891 >"$log" 2>&1 & pid=$!
cleanup(){ kill -TERM "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true; }; trap cleanup EXIT
for _ in $(seq 1 24); do curl -fsS http://127.0.0.1:8891/health/ready >/dev/null 2>&1 && break; kill -0 "$pid" 2>/dev/null || { tail -80 "$log" >&2; exit 75; }; sleep 5; done
curl -fsS http://127.0.0.1:8891/health/ready >/dev/null
PYTHONPATH=src "$root/.venv/bin/python" -m memory_bakeoff.cli run --providers hindsight --mode raw --top-k 5 --distractors "$distractors" --out "$out"
LABEL=$label OUT=$out DB=$db "$root/.venv/bin/python" - <<'PY'
import json, os
from pathlib import Path
out=Path(os.environ['OUT']); r=json.loads((out/'run.json').read_text())[0]
assert r['status']=='ok' and r['publishability']['publishable'], r
(out/'hindsight_runtime.json').write_text(json.dumps({'experiment_class':'raw_product','run_label':os.environ['LABEL'],'database':{'backend':'external_postgresql','server':'Homebrew PostgreSQL 17.11','database':os.environ['DB'],'vector_extension':'pgvector 0.8.6'},'ingestion':{'llm_provider':'none'},'embeddings':{'provider':'onnx','model':'intfloat/multilingual-e5-small','snapshot_revision':'614241f622f53c4eeff9890bdc4f31cfecc418b3'},'reranker':{'provider':os.environ['HINDSIGHT_API_RERANKER_PROVIDER']},'nofile_soft':8192},indent=2)+'\n')
PY
