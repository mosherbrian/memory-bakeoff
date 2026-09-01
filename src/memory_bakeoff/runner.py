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
from memory_bakeoff.repro import capture_execution_environment


RESULT_SCHEMA_VERSION = 2


def _publishability(provenance: dict | None, *, status: str) -> dict:
    if status != "ok" or provenance is None:
        return {
            "status": "not_applicable",
            "publishable": False,
            "reasons": [f"run status is {status}"],
        }
    publishable = bool(provenance.get("publishable"))
    return {
        "status": "publishable" if publishable else "non_publishable",
        "publishable": publishable,
        "reasons": [] if publishable else [provenance.get("reason", "source provenance was not verified")],
    }


def _run_row(provider, name: str, mode: str, top_k: int, distractors: int, status: str, reason: str, probe, *, details=None, summary=None, provenance=None) -> dict:
    return {
        "schema_version": RESULT_SCHEMA_VERSION,
        "provider": name,
        "mode": mode,
        "experiment_class": provider.experiment_class(mode),
        "top_k": top_k,
        "distractors": distractors,
        "status": status,
        "reason": reason,
        "probe": probe.to_dict(),
        "provenance": provenance,
        "publishability": _publishability(provenance, status=status),
        "provider_configuration": provider.configuration(),
        "execution_environment": capture_execution_environment(),
        "details": details or [],
        "summary": summary or {},
    }


def run_provider(name: str, mode: str="raw", top_k: int=5, distractors: int=0) -> dict:
    provider=PROVIDERS[name]()
    probe=provider.probe()
    if mode=="raw" and not provider.capabilities.raw_ingest:
        return _run_row(provider,name,mode,top_k,distractors,"ineligible","provider does not expose a supported raw/no-LLM ingestion path",probe)
    if mode=="product" and not provider.capabilities.product_ingest:
        return _run_row(provider,name,mode,top_k,distractors,"ineligible","provider does not expose product-mode ingestion",probe)
    if not probe.available:
        return _run_row(provider,name,mode,top_k,distractors,"unavailable",probe.reason,probe)
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
        provenance=provider.provenance_report()
        return _run_row(provider,name,mode,top_k,distractors,"ok","",probe,details=details,summary=summary,provenance=provenance)
    except ProviderUnavailable as e:
        return _run_row(provider,name,mode,top_k,distractors,"unavailable",str(e),probe)
    except Exception as e:
        return _run_row(provider,name,mode,top_k,distractors,"error",f"{type(e).__name__}: {e}",probe)
    finally:
        provider.close()


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


def write_results(results: list[dict], outdir: Path, *, allow_overwrite: bool = False) -> None:
    if outdir.exists() and not allow_overwrite:
        raise FileExistsError(
            f"result directory already exists: {outdir}; choose a new directory or pass --allow-overwrite for development/debug only"
        )
    outdir.mkdir(parents=True,exist_ok=allow_overwrite)
    (outdir/"run.json").write_text(json.dumps(results,indent=2,default=str))
    summary_rows=[]; detail_rows=[]
    for r in results:
        summary_rows.append({"provider":r["provider"],"mode":r["mode"],"experiment_class":r.get("experiment_class"),"publishability":r.get("publishability",{}).get("status"),"top_k":r.get("top_k",5),"distractors":r.get("distractors",0),"status":r["status"],"reason":r["reason"],**r.get("summary",{})})
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
    lines=["# Memory bake-off diagnostic results","","This table includes all attempted runs. Only rows in `leaderboard.md` are authoritative/publishable.","",f"| Provider | Class | Mode | Publishability | Status | Hit@{label_k} | MRR | All relevant@{label_k} | Prohibited@{label_k} | Useful>harmful | Mean ctx chars | Notes |","|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|"]
    for row in summary_rows:
        rk=int(row.get("top_k",5))
        def f(key):
            v=row.get(key); return "—" if v is None else f"{float(v):.3f}"
        notes=(row.get("reason") or "").replace("|","/")
        lines.append(f"| {row['provider']} | {row.get('experiment_class')} | {row['mode']} | {row.get('publishability')} | {row['status']} | {f(f'hit@{rk}')} | {f('mrr')} | {f(f'all_relevant@{rk}')} | {f(f'prohibited@{rk}')} | {f('useful_before_harmful')} | {f('mean_context_chars')} | {notes} |")
    (outdir/"summary.md").write_text("\n".join(lines)+"\n")

    authoritative=[row for row in summary_rows if row["status"] == "ok" and row.get("publishability") == "publishable"]
    pd.DataFrame(authoritative).to_csv(outdir/"leaderboard.csv",index=False)
    board=["# Authoritative publishable results","","Rows with fuzzy/subtext or unmapped source provenance are excluded.","",f"| Provider | Class | Mode | Hit@{label_k} | MRR | Prohibited@{label_k} |","|---|---|---|---:|---:|---:|"]
    for row in authoritative:
        rk=int(row.get("top_k",5))
        def bf(key):
            value=row.get(key)
            return "—" if value is None else f"{float(value):.3f}"
        board.append(f"| {row['provider']} | {row.get('experiment_class')} | {row['mode']} | {bf(f'hit@{rk}')} | {bf('mrr')} | {bf(f'prohibited@{rk}')} |")
    (outdir/"leaderboard.md").write_text("\n".join(board)+"\n")


def probe_all() -> list[dict]:
    rows=[]
    for name in PROVIDERS:
        provider=PROVIDERS[name]()
        row=provider.probe().to_dict()
        row["experiment_classes"]={
            "raw":provider.experiment_class("raw"),
            "product":provider.experiment_class("product"),
        }
        rows.append(row)
    return rows
