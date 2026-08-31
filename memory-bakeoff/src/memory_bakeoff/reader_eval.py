from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
from typing import Iterable, Sequence

import pandas as pd

from memory_bakeoff.corpus import build_corpus
from memory_bakeoff.llm import LLMBackendError, LLMClient, LLMMessage, LLMRequest
from memory_bakeoff.providers import PROVIDERS
from memory_bakeoff.providers.base import ProviderUnavailable


@dataclass(frozen=True)
class AnswerSpec:
    case_id: str
    # Every outer group must match; alternatives inside a group are ORed.
    required_groups: tuple[tuple[str, ...], ...] = ()
    prohibited: tuple[str, ...] = ()
    expect_insufficient: bool = False
    notes: str = ""


@dataclass(frozen=True)
class AnswerScore:
    case_id: str
    provider: str
    answer: str
    required_fraction: float
    prohibited_hits: tuple[str, ...]
    insufficient_ok: bool
    pass_answer: bool
    retrieved_ids: tuple[str, ...]
    request_id: str

    def to_dict(self) -> dict:
        d=asdict(self)
        d["prohibited_hits"]=list(self.prohibited_hits)
        d["retrieved_ids"]=list(self.retrieved_ids)
        return d


# Small, exact-answer set chosen so grading can stay deterministic. The LLM is a
# reader, never the judge. Required strings are intentionally literal identifiers,
# commands, or concise semantic anchors rather than style-sensitive prose.
ANSWER_SPECS: tuple[AnswerSpec, ...] = (
    AnswerSpec("Q003", (("6",),), ("database number 2", "database number 3", "db 2", "db 3")),
    AnswerSpec("Q007", (("strix07",),), ("strix03",)),
    AnswerSpec("Q008", (("shipit release --cluster pdx",),), ("deployctl push --region west",)),
    AnswerSpec("Q010", (("deployctl push --region west",),), ("shipit release --cluster pdx",)),
    AnswerSpec("Q012", (("billing-db-dsn",), ("platform-secrets",), ("secrets-plan",))),
    AnswerSpec("Q013", (("media-repair",), ("media-repair replay --source deadletter",))),
    AnswerSpec(
        "Q014",
        (("source schema", "schema"), ("generator", "generate"), ("generated diff", "inspect the generated diff"), ("package tests",), ("full suite",)),
        ("edit generated go files directly", "edit the generated go file directly"),
    ),
    AnswerSpec(
        "Q015",
        (("-race",), ("synchronization", "ownership boundary"), ("focused race test",), ("whole package",)),
        ("add sleeps", "adding sleeps", "timing sleeps"),
    ),
    AnswerSpec(
        "Q016",
        (("exact frames", "capture exact frames"), ("one json object per line",), ("off stdout", "stderr")),
        ("pretty-print", "multiple lines"),
    ),
    AnswerSpec("Q019", (("release/atlas-2.x",),), ("stable",)),
    AnswerSpec("Q022", (("qa-fixtures-v2",),), (), notes="v1 may be mentioned only if clearly identified as legacy; exact grading focuses on the current bucket."),
    AnswerSpec("Q024", (("stderr",), ("stdout",), ("ndjson", "protocol frames"))),
    AnswerSpec("Q025", expect_insufficient=True),
    AnswerSpec("Q026", expect_insufficient=True),
)


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.casefold()).strip()


def score_answer(spec: AnswerSpec, answer: str, *, provider: str, retrieved_ids: Sequence[str], request_id: str) -> AnswerScore:
    norm=_norm(answer)
    insufficient="insufficient_memory" in norm or "insufficient memory" in norm
    if spec.expect_insufficient:
        required_fraction=1.0 if insufficient else 0.0
        prohibited_hits=()
        passed=insufficient
        insufficient_ok=insufficient
    else:
        matches=[]
        for group in spec.required_groups:
            matches.append(any(_norm(term) in norm for term in group))
        required_fraction=(sum(matches)/len(matches)) if matches else 1.0
        prohibited_hits=tuple(term for term in spec.prohibited if _norm(term) in norm)
        passed=(required_fraction == 1.0 and not prohibited_hits and not insufficient)
        insufficient_ok=not insufficient
    return AnswerScore(
        case_id=spec.case_id,
        provider=provider,
        answer=answer,
        required_fraction=required_fraction,
        prohibited_hits=prohibited_hits,
        insufficient_ok=insufficient_ok,
        pass_answer=passed,
        retrieved_ids=tuple(retrieved_ids),
        request_id=request_id,
    )


def _reader_prompt(case, result) -> str:
    if result.items:
        memories="\n".join(
            f"- [{item.record_id or 'unknown'}] {item.text}" for item in result.items
        )
    else:
        memories="(none)"
    temporal=(f"\nQuestion as-of timestamp: {case.as_of.isoformat()}" if case.as_of else "")
    return (
        "QUESTION:\n"
        f"{case.query}{temporal}\n\n"
        "RETRIEVED MEMORY:\n"
        f"{memories}\n\n"
        "Answer the QUESTION using only RETRIEVED MEMORY. Preserve exact identifiers, commands, "
        "paths, and numbers. Prefer the current/correct/verified memory when the context contains "
        "conflicting or failed alternatives. Do not mention obsolete or failed alternatives unless "
        "the question explicitly asks about history. If the answer is not supported by retrieved "
        "memory, output exactly INSUFFICIENT_MEMORY. Be concise."
    )


def prepare_reader_requests(provider_names: Sequence[str], mode: str="raw", top_k: int=5, specs: Sequence[AnswerSpec]=ANSWER_SPECS, distractors: int=0):
    records,cases=build_corpus(distractors=distractors); case_by_id={c.id:c for c in cases}
    requests=[]; contexts=[]; unavailable=[]
    for name in provider_names:
        provider=PROVIDERS[name](); probe=provider.probe()
        if mode=="raw" and not provider.capabilities.raw_ingest:
            unavailable.append({"provider":name,"status":"ineligible","reason":"provider does not expose a supported raw/no-LLM ingestion path"}); continue
        if mode=="product" and not provider.capabilities.product_ingest:
            unavailable.append({"provider":name,"status":"ineligible","reason":"provider does not expose product-mode ingestion"}); continue
        if not probe.available:
            unavailable.append({"provider":name,"status":"unavailable","reason":probe.reason}); continue
        try:
            provider.ingest(records,mode=mode)
            for spec in specs:
                case=case_by_id[spec.case_id]
                result=provider.retrieve(case,top_k=top_k)
                request_id=f"reader_{name}_{case.id}"
                req=LLMRequest(
                    messages=(
                        LLMMessage("system","You are a strict memory-grounded coding assistant. Never use outside knowledge or guess."),
                        LLMMessage("user",_reader_prompt(case,result)),
                    ),
                    temperature=0.0,
                    request_id=request_id,
                    metadata={"provider":name,"case_id":case.id,"mode":mode,"top_k":top_k,"retrieved_ids":result.ids[:top_k]},
                )
                requests.append(req)
                contexts.append({"provider":name,"case":case,"spec":spec,"result":result,"request_id":request_id})
        except ProviderUnavailable as e:
            unavailable.append({"provider":name,"status":"unavailable","reason":str(e)})
        except Exception as e:
            unavailable.append({"provider":name,"status":"error","reason":f"{type(e).__name__}: {e}"})
    return requests,contexts,unavailable


def run_reader_eval(provider_names: Sequence[str], llm: LLMClient, *, mode: str="raw", top_k: int=5, specs: Sequence[AnswerSpec]=ANSWER_SPECS, distractors: int=0) -> dict:
    requests,contexts,unavailable=prepare_reader_requests(provider_names,mode=mode,top_k=top_k,specs=specs,distractors=distractors)
    responses=llm.complete_batch(requests) if requests else []
    scores=[]
    for ctx,response in zip(contexts,responses,strict=True):
        scores.append(score_answer(
            ctx["spec"],response.content,provider=ctx["provider"],retrieved_ids=ctx["result"].ids[:top_k],request_id=ctx["request_id"]
        ))
    by_provider={}
    for name in provider_names:
        rows=[s for s in scores if s.provider==name]
        if not rows: continue
        by_provider[name]={
            "cases":len(rows),
            "answer_pass_rate":sum(x.pass_answer for x in rows)/len(rows),
            "mean_required_fraction":sum(x.required_fraction for x in rows)/len(rows),
            "answers_with_prohibited":sum(bool(x.prohibited_hits) for x in rows)/len(rows),
            "insufficient_rate":sum("insufficient_memory" in _norm(x.answer) or "insufficient memory" in _norm(x.answer) for x in rows)/len(rows),
        }
    return {
        "mode":mode,
        "top_k":top_k,
        "distractors":distractors,
        "llm_backend":getattr(llm,"name",type(llm).__name__),
        "provider_summary":by_provider,
        "unavailable":unavailable,
        "details":[x.to_dict() for x in scores],
    }


def write_reader_results(result: dict, outdir: str | Path) -> None:
    out=Path(outdir); out.mkdir(parents=True,exist_ok=True)
    (out/"reader.json").write_text(json.dumps(result,indent=2,default=str)+"\n")
    pd.DataFrame(result.get("details",[])).to_csv(out/"reader_detail.csv",index=False)
    summary_rows=[]
    for provider,metrics in result.get("provider_summary",{}).items():
        summary_rows.append({"provider":provider,"status":"ok",**metrics})
    for row in result.get("unavailable",[]):
        summary_rows.append({"provider":row["provider"],"status":row["status"],"reason":row["reason"]})
    pd.DataFrame(summary_rows).to_csv(out/"reader_summary.csv",index=False)
    lines=[
        "# Reader-impact evaluation",
        "",
        f"LLM backend: `{result.get('llm_backend')}`; mode: `{result.get('mode')}`; top-k: {result.get('top_k')}; distractors: {result.get('distractors',0)}",
        "",
        "| Provider | Status | Cases | Answer pass | Required coverage | Answers with prohibited | Notes |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    by=result.get("provider_summary",{})
    unavailable={x["provider"]:x for x in result.get("unavailable",[])}
    names=list(by)+[x for x in unavailable if x not in by]
    for name in names:
        if name in by:
            m=by[name]
            lines.append(f"| {name} | ok | {m['cases']} | {m['answer_pass_rate']:.3f} | {m['mean_required_fraction']:.3f} | {m['answers_with_prohibited']:.3f} |  |")
        else:
            row=unavailable[name]; lines.append(f"| {name} | {row['status']} | — | — | — | — | {row['reason'].replace('|','/')} |")
    (out/"reader_summary.md").write_text("\n".join(lines)+"\n")
