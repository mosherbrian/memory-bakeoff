#!/usr/bin/env bash
# Gen31 preflight: what Hindsight v0.9.2's raw/no-LLM temporal surface actually does.
# Unrelated synthetic domain only. Determines semantics; never tunes scoring.
set -euo pipefail
out=${1:?usage: preflight_hindsight_gen31.sh <out.json>}
root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
pg=/opt/homebrew/opt/postgresql@17/bin
label="gen31pre$$"
db="memory_bakeoff_hindsight_$label"
port=8893
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
PORT=$port DB=$db OUT=$out PGBIN=$pg BANK="memory-bakeoff-$label" "$root/.venv/bin/python" - <<'HSPY'
import json, os, subprocess
from hindsight_client import Hindsight

PORT, DB, OUT, PGBIN, BANK = os.environ["PORT"], os.environ["DB"], os.environ["OUT"], os.environ["PGBIN"], os.environ["BANK"]
client = Hindsight(base_url=f"http://127.0.0.1:{PORT}")

def sql(q):
    done = subprocess.run([f"{PGBIN}/psql", "-h", "127.0.0.1", "-d", DB, "-Atc", q], text=True, capture_output=True, timeout=60)
    return done.stdout.strip()

items = [
    ("P001", "Greenhouse bench A humidity target is 55 percent.", "2026-01-10T00:00:00+00:00", "site:greenhouse", "benchA"),
    ("P002", "Greenhouse bench B humidity target is 62 percent.", "2026-01-12T00:00:00+00:00", "site:greenhouse", "benchB"),
    ("P003", "Audit corrected bench A humidity: the valid target was 58 percent, not 55 percent.", "2026-01-20T00:00:00+00:00", "site:greenhouse", "benchA"),
    ("P004", "Recovered log: bench A ran the coarse perlite mix on 2026-01-05.", "2026-01-05T00:00:00+00:00", "site:greenhouse", "benchA"),
    ("P005", "The orchard drip schedule failed without a prewarm cycle.", "2026-01-23T00:00:00+00:00", "site:orchard", "default"),
    ("P006", "The orchard drip schedule succeeded with a prewarm cycle and fixed interval.", "2026-01-24T00:00:00+00:00", "site:orchard", "default"),
]
findings = {"ingest_errors": []}
for marker, content, ts, scope, configuration in items:
    try:
        client.retain(bank_id=BANK, content=content, context=f"memory-bakeoff-preflight; scope={scope}",
                      timestamp=ts, document_id=f"src-{marker}",
                      metadata={"record_id": marker, "scope": scope, "configuration": configuration})
    except Exception as exc:
        findings["ingest_errors"].append(f"{marker}: {exc}")

findings["tables"] = sql("select table_name from information_schema.tables where table_schema='public' order by 1").splitlines()
for table in findings["tables"]:
    if table.startswith(("memor", "chunk", "document", "fact", "entit")):
        findings["count_" + table] = sql("select count(*) from " + table)

def rows(raw):
    got = getattr(raw, "results", None)
    if got is None and isinstance(raw, dict):
        got = raw.get("results") or []
    out = []
    for x in list(got or [])[:5]:
        get = (lambda k: x.get(k)) if isinstance(x, dict) else (lambda k: getattr(x, k, None))
        scores = get("scores")
        if scores is not None and not isinstance(scores, dict):
            scores = {k: v for k, v in vars(scores).items() if not k.startswith("_")}
        md = get("metadata") or {}
        out.append({"text": (get("text") or "")[:60],
                    "document_id": get("document_id") or (md.get("record_id") if isinstance(md, dict) else None),
                    "occurred_start": get("occurred_start"), "mentioned_at": get("mentioned_at"),
                    "chunk_id": get("chunk_id"), "scores": scores})
    return out

def recall(label, **kw):
    try:
        findings[label] = rows(client.recall(bank_id=BANK, max_tokens=4096, **kw))
    except Exception as exc:
        findings[label] = {"error": str(exc)[:200]}
    return findings[label]

def db_snapshot():
    state = {}
    for table in findings["tables"]:
        state[table] = sql("select count(*) from " + table)
    for table in ("memory_units", "chunks", "documents", "memory_links"):
        if table in findings["tables"]:
            state[table + "_digest"] = sql("select md5(string_agg(t::text, '|' order by t::text)) from " + table + " t")
    return state

findings["db_before_reads"] = db_snapshot()
recall("recall_plain", query="bench A humidity target")
recall("recall_as_of_before_correction", query="bench A humidity target", query_timestamp="2026-01-15T00:00:00+00:00")
recall("recall_as_of_after_correction", query="bench A humidity target", query_timestamp="2026-01-25T00:00:00+00:00")
recall("recall_backdated_window", query="perlite mix bench A", query_timestamp="2026-01-08T00:00:00+00:00")
recall("recall_scope_orchard", query="drip schedule prewarm cycle")
recall("recall_negative", query="wind turbine gearbox lubrication schedule")
recall("recall_plain_repeat", query="bench A humidity target")
findings["db_after_reads"] = db_snapshot()
findings["db_changed_by_reads"] = {k: [findings["db_before_reads"][k], v]
                                   for k, v in findings["db_after_reads"].items()
                                   if findings["db_before_reads"].get(k) != v}
findings["reads_return_identical_order"] = ([r["document_id"] for r in findings["recall_plain"]]
                                            == [r["document_id"] for r in findings["recall_plain_repeat"]])
def _drift(a, b):
    out = []
    for x, y in zip(a, b):
        sx, sy = x.get("scores") or {}, y.get("scores") or {}
        if isinstance(sx, dict) and isinstance(sy, dict):
            out.append({k: abs((sx.get(k) or 0) - (sy.get(k) or 0)) for k in sx if isinstance(sx.get(k), float)})
    return out
findings["score_drift_between_identical_reads"] = _drift(findings["recall_plain"], findings["recall_plain_repeat"])

open(OUT, "w").write(json.dumps(findings, indent=2, default=str) + "\n")
print("wrote", OUT)
print(" ingest errors:", findings["ingest_errors"] or "none")
print(" counts:", {k: v for k, v in findings.items() if k.startswith("count_")})
for key in ("recall_plain", "recall_as_of_before_correction", "recall_as_of_after_correction",
            "recall_backdated_window", "recall_scope_orchard", "recall_negative"):
    print(" ", key, "->", json.dumps(findings[key])[:200])
print(" reads return identical order:", findings["reads_return_identical_order"])
print(" db changed by reads:", findings["db_changed_by_reads"] or "no change")
print(" max score drift:", max((max(d.values()) for d in findings["score_drift_between_identical_reads"] if d), default=0))
HSPY
