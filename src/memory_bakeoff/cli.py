from __future__ import annotations

import argparse, json
from pathlib import Path
from memory_bakeoff.providers import PROVIDERS
from memory_bakeoff.runner import probe_all, run_learning_diagnostic, run_provider, write_results
from memory_bakeoff.llm import LLMMessage, LLMRequest, create_llm_backend, list_pending, write_sidecar_response
from memory_bakeoff.llm.proxy import SidecarOpenAIProxy
from memory_bakeoff.reader_eval import run_reader_eval, write_reader_results
from memory_bakeoff.repro import write_manifest


def main(argv=None):
    p=argparse.ArgumentParser(prog="memory-bakeoff")
    sub=p.add_subparsers(dest="cmd",required=True)
    sub.add_parser("providers")
    pp=sub.add_parser("probe")
    r=sub.add_parser("run"); r.add_argument("--providers",default=",".join(PROVIDERS)); r.add_argument("--mode",choices=["raw","product"],default="raw"); r.add_argument("--top-k",type=int,default=5); r.add_argument("--out",default="results"); r.add_argument("--distractors",type=int,default=0)
    l=sub.add_parser("learning-diagnostic"); l.add_argument("--epochs",type=int,default=8); l.add_argument("--out",default="results/learning.json")

    reader=sub.add_parser("reader-eval",help="Measure whether retrieved context lets an LLM answer correctly")
    reader.add_argument("--providers",default="bm25,dense_lsa,hybrid_rrf")
    reader.add_argument("--mode",choices=["raw","product"],default="raw")
    reader.add_argument("--top-k",type=int,default=5)
    reader.add_argument("--backend",choices=["fake","chatgpt_sidecar","replay","openai_compat","anthropic"],default="chatgpt_sidecar")
    reader.add_argument("--model")
    reader.add_argument("--base-url")
    reader.add_argument("--queue-dir",default=".memory-bakeoff-sidecar")
    reader.add_argument("--replay-dir",default="results/sidecar_reader_trace")
    reader.add_argument("--timeout",type=float,default=900)
    reader.add_argument("--out",default="results")
    reader.add_argument("--distractors",type=int,default=0)

    smoke=sub.add_parser("llm-smoke",help="Issue one request through a configured LLM backend")
    smoke.add_argument("--backend",choices=["fake","chatgpt_sidecar","openai_compat","anthropic"],default="fake")
    smoke.add_argument("--prompt",default="Return exactly OK")
    smoke.add_argument("--system",default="Follow the user instruction exactly.")
    smoke.add_argument("--model")
    smoke.add_argument("--base-url")
    smoke.add_argument("--queue-dir",default=".memory-bakeoff-sidecar")
    smoke.add_argument("--timeout",type=float,default=900)

    pending=sub.add_parser("sidecar-pending",help="Print outstanding ChatGPT sidecar requests")
    pending.add_argument("--queue-dir",default=".memory-bakeoff-sidecar")

    respond=sub.add_parser("sidecar-respond",help="Write one sidecar response (manual/debug helper)")
    respond.add_argument("request_id")
    respond.add_argument("--content",required=True)
    respond.add_argument("--model",default="chatgpt-sidecar")
    respond.add_argument("--queue-dir",default=".memory-bakeoff-sidecar")

    manifest=sub.add_parser("manifest",help="Capture a secret-free reproducibility manifest")
    manifest.add_argument("--out",default="results/repro_manifest.json")
    manifest.add_argument("--llm-label")

    proxy=sub.add_parser("sidecar-proxy",help="Serve a localhost OpenAI-compatible bridge to the ChatGPT file queue")
    proxy.add_argument("--queue-dir",default=".memory-bakeoff-sidecar")
    proxy.add_argument("--host",default="127.0.0.1")
    proxy.add_argument("--port",type=int,default=8765)
    proxy.add_argument("--timeout",type=float,default=900)
    proxy.add_argument("--model",default="chatgpt-sidecar")

    args=p.parse_args(argv)
    if args.cmd=="providers":
        for n,c in PROVIDERS.items(): print(f"{n:26} {c.capabilities}")
    elif args.cmd=="probe": print(json.dumps(probe_all(),indent=2))
    elif args.cmd=="run":
        names=[x.strip() for x in args.providers.split(",") if x.strip()]; bad=[n for n in names if n not in PROVIDERS]
        if bad: raise SystemExit(f"Unknown providers: {', '.join(bad)}")
        results=[run_provider(n,args.mode,args.top_k,args.distractors) for n in names]; write_results(results,Path(args.out)); print((Path(args.out)/"summary.md").read_text())
    elif args.cmd=="learning-diagnostic":
        rows=run_learning_diagnostic(epochs=args.epochs); out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(rows,indent=2)); print(json.dumps(rows,indent=2))
    elif args.cmd=="reader-eval":
        names=[x.strip() for x in args.providers.split(",") if x.strip()]; bad=[n for n in names if n not in PROVIDERS]
        if bad: raise SystemExit(f"Unknown providers: {', '.join(bad)}")
        llm=create_llm_backend(args.backend,queue_dir=args.queue_dir,trace_dir=args.replay_dir,timeout_s=args.timeout,model=args.model,base_url=args.base_url)
        result=run_reader_eval(names,llm,mode=args.mode,top_k=args.top_k,distractors=args.distractors); write_reader_results(result,args.out); print((Path(args.out)/"reader_summary.md").read_text())
    elif args.cmd=="llm-smoke":
        llm=create_llm_backend(args.backend,queue_dir=args.queue_dir,timeout_s=args.timeout,model=args.model,base_url=args.base_url)
        response=llm.complete(LLMRequest(messages=(LLMMessage("system",args.system),LLMMessage("user",args.prompt))))
        print(response.content)
    elif args.cmd=="sidecar-pending":
        print(json.dumps(list_pending(args.queue_dir),indent=2))
    elif args.cmd=="sidecar-respond":
        path=write_sidecar_response(args.queue_dir,args.request_id,args.content,model=args.model); print(path)
    elif args.cmd=="manifest":
        out=write_manifest(args.out,Path.cwd(),llm_label=args.llm_label); print(out.read_text())
    elif args.cmd=="sidecar-proxy":
        sidecar=create_llm_backend("chatgpt_sidecar",queue_dir=args.queue_dir,timeout_s=args.timeout,model=args.model)
        print(f"OpenAI-compatible sidecar bridge listening on http://{args.host}:{args.port}/v1")
        SidecarOpenAIProxy(sidecar,args.host,args.port).serve_forever()

if __name__ == "__main__": main()
