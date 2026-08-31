from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import asdict
from pathlib import Path
from typing import Iterable
import pandas as pd

from memory_bakeoff.corpus import build_corpus, learning_stream, learning_training_cases
from memory_bakeoff.metrics import aggregate, score_case
from memory_bakeoff.models import FeedbackEvent
from memory_bakeoff.providers import PROVIDERS
from memory_bakeoff.providers.base import ProviderUnavailable


def run_provider(name: str, mode: str="raw", top_k: int=5, distractors: int=0) -> dict:
    provider=PROVIDERS[name]()
    probe=provider.probe()
    if mode=="raw" and not provider.capabilities.raw_ingest:
        return {"provider":name,"mode":mode,"top_k":top_k,"distractors":distractors,"status":"ineligible","reason":"provider does not expose a supported raw/no-LLM ingestion path","probe":probe.to_dict(),"details":[],"summary":{}}
    if mode=="product" and not provider.capabilities.product_ingest:
        return {"provider":name,"mode":mode,"top_k":top_k,"distractors":distractors,"status":"ineligible","reason":"provider does not expose product-mode ingestion","probe":probe.to_dict(),"details":[],"summary":{}}
    if not probe.available:
        return {"provider":name,"mode":mode,"top_k":top_k,"distractors":distractors,"status":"unavailable","reason":probe.reason,"probe":probe.to_dict(),"details":[],"summary":{}}
    records,cases=build_corpus(distractors=distractors)
    try:
        provider.ingest(records,mode=mode)
        details=[]
        case_metrics=[]
        for case in cases:
            result=provider.retrieve(case,top_k=top_k)
            cm=score_case(case,result,k=top_k)
            case_metrics.append(cm)
            row=cm.to_dict(); row["retrieved_ids"]=result.ids[:top_k]; row["relevant_ids"]=list(case.relevant_ids); row["prohibited_ids"]=list(case.prohibited_ids)
            details.append(row)
        summary=aggregate(case_metrics, k=top_k)
        return {"provider":name,"mode":mode,"top_k":top_k,"distractors":distractors,"status":"ok","reason":"","probe":probe.to_dict(),"details":details,"summary":summary}
    except ProviderUnavailable as e:
        return {"provider":name,"mode":mode,"top_k":top_k,"distractors":distractors,"status":"unavailable","reason":str(e),"probe":probe.to_dict(),"details":[],"summary":{}}
    except Exception as e:
        return {"provider":name,"mode":mode,"top_k":top_k,"distractors":distractors,"status":"error","reason":f"{type(e).__name__}: {e}","probe":probe.to_dict(),"details":[],"summary":{}}


def run_learning_diagnostic(name: str="toy_adaptive_diagnostic", epochs: int=8, top_k: int=5) -> list[dict]:
    provider=PROVIDERS[name](); records,eval_cases=learning_stream(); train_cases=learning_training_cases(); provider.ingest(records,"raw"); rows=[]
    for epoch in range(epochs+1):
        # Report only held-out query wording. Feedback is generated from a separate
        # training paraphrase set so the curve cannot improve merely by memorizing the
        # exact evaluation prompts.
        scored=[]
        for case in eval_cases:
            res=provider.retrieve(case,top_k); scored.append(score_case(case,res,top_k))
        agg=aggregate(scored, k=top_k); rows.append({"epoch":epoch,"eval_split":"heldout_paraphrase",**agg})
        if epoch < epochs and provider.capabilities.supports_feedback:
            for case in train_cases:
                res=provider.retrieve(case,top_k)
                provider.feedback(FeedbackEvent(query_id=case.id,retrieved_ids=tuple(res.ids),useful_ids=case.relevant_ids,harmful_ids=case.prohibited_ids,verified=True,reward=1.0))
    return rows


def write_results(results: list[dict], outdir: Path) -> None:
    outdir.mkdir(parents=True,exist_ok=True)
    (outdir/"run.json").write_text(json.dumps(results,indent=2,default=str))
    summary_rows=[]; detail_rows=[]
    for r in results:
        summary_rows.append({"provider":r["provider"],"mode":r["mode"],"top_k":r.get("top_k",5),"distractors":r.get("distractors",0),"status":r["status"],"reason":r["reason"],**r.get("summary",{})})
        for d in r.get("details",[]): detail_rows.append({"provider":r["provider"],"mode":r["mode"],**d})
    pd.DataFrame(summary_rows).to_csv(outdir/"summary.csv",index=False)
    detail_df=pd.DataFrame(detail_rows)
    detail_df.to_csv(outdir/"detail.csv",index=False)
    if not detail_df.empty:
        numeric=["hit_at_k","recall_at_k","precision_at_k","reciprocal_rank","all_relevant_at_k","prohibited_at_k","prohibited_count","useful_before_harmful","returned_chars","returned_words","latency_ms"]
        cat=(detail_df.groupby(["provider","mode","category"],dropna=False)[numeric].mean(numeric_only=True).reset_index())
        cat.to_csv(outdir/"category_summary.csv",index=False)
    ks=sorted({int(r.get("top_k",5)) for r in summary_rows})
    label_k=ks[0] if len(ks)==1 else "k"
    lines=["# Memory bake-off results","",f"| Provider | Mode | Status | Hit@{label_k} | MRR | All relevant@{label_k} | Prohibited@{label_k} | Useful>harmful | Mean ctx chars | Notes |","|---|---|---:|---:|---:|---:|---:|---:|---:|---|"]
    for row in summary_rows:
        rk=int(row.get("top_k",5))
        def f(key):
            v=row.get(key); return "—" if v is None else f"{float(v):.3f}"
        notes=(row.get("reason") or "").replace("|","/")
        lines.append(f"| {row['provider']} | {row['mode']} | {row['status']} | {f(f'hit@{rk}')} | {f('mrr')} | {f(f'all_relevant@{rk}')} | {f(f'prohibited@{rk}')} | {f('useful_before_harmful')} | {f('mean_context_chars')} | {notes} |")
    (outdir/"summary.md").write_text("\n".join(lines)+"\n")


def probe_all() -> list[dict]:
    return [PROVIDERS[name]().probe().to_dict() for name in PROVIDERS]
