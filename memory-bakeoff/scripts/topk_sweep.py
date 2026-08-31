from pathlib import Path
import argparse
import pandas as pd

from memory_bakeoff.runner import run_provider


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--providers", default="bm25,dense_lsa,hybrid_rrf")
    p.add_argument("--ks", default="1,3,5,8,10")
    p.add_argument("--mode", default="raw", choices=["raw", "product"])
    p.add_argument("--out", default="results/topk_sensitivity.csv")
    p.add_argument("--distractors", type=int, default=0)
    args = p.parse_args()

    providers = [x.strip() for x in args.providers.split(",") if x.strip()]
    ks = [int(x) for x in args.ks.split(",") if x.strip()]
    rows = []
    for k in ks:
        for provider in providers:
            result = run_provider(provider, mode=args.mode, top_k=k, distractors=args.distractors)
            row = {
                "provider": provider,
                "mode": args.mode,
                "k": k,
                "distractors": args.distractors,
                "status": result["status"],
                "reason": result.get("reason", ""),
                **result.get("summary", {}),
            }
            # Normalize k-dependent names for easier plotting/comparison.
            if result["status"] == "ok":
                row["hit_at_k"] = row.get(f"hit@{k}")
                row["recall_at_k"] = row.get(f"recall@{k}")
                row["precision_at_k"] = row.get(f"precision@{k}")
                row["all_relevant_at_k"] = row.get(f"all_relevant@{k}")
                row["prohibited_at_k"] = row.get(f"prohibited@{k}")
            rows.append(row)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(out, index=False)
    print(df[["provider", "k", "status", "hit_at_k", "mrr", "all_relevant_at_k", "prohibited_at_k", "harmful_presence_rate", "mean_prohibited_count", "mean_context_chars"]].to_string(index=False))


if __name__ == "__main__":
    main()
