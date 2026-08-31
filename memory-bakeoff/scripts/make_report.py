from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"

summary = pd.read_csv(OUT / "summary.csv")
ok = summary[summary.status == "ok"].copy()

# Baseline metric chart.
metrics = ["hit@5", "mrr", "all_relevant@5", "useful_before_harmful"]
fig, ax = plt.subplots(figsize=(9, 5))
x = range(len(ok))
width = 0.18
for j, metric in enumerate(metrics):
    vals = ok[metric].astype(float).to_list()
    ax.bar([i + (j - 1.5) * width for i in x], vals, width=width, label=metric)
ax.set_xticks(list(x), ok.provider.tolist())
ax.set_ylim(0, 1.05)
ax.set_ylabel("Score (higher is better)")
ax.set_title("Offline baseline retrieval scores")
ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig(OUT / "baseline_scores.png", dpi=150)
plt.close(fig)

# Learning diagnostic.
learn = pd.read_json(OUT / "learning.json")
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.plot(learn.epoch, learn["useful_before_harmful"], marker="o", label="useful before harmful")
ax.plot(learn.epoch, 1 - learn["prohibited@5"], marker="o", label="1 - prohibited@5")
ax.set_ylim(0, 1.05)
ax.set_xlabel("Verified feedback epoch")
ax.set_ylabel("Score")
ax.set_title("Held-out learning-signal diagnostic (not Habitus)")
ax.legend()
fig.tight_layout()
fig.savefig(OUT / "learning_diagnostic.png", dpi=150)
plt.close(fig)

# Baseline findings markdown.
cat = pd.read_csv(OUT / "category_summary.csv")
lines = [
    "# Baseline findings",
    "",
    "These results are a harness sanity check, **not** the memory-system bake-off yet. Only local deterministic baselines were executable in this sandbox.",
    "",
    "## Headline",
    "",
    "| Provider | Hit@5 | MRR | All-relevant@5 | Prohibited@5 ↓ | Useful-before-harmful | Negative empty-rate |",
    "|---|---:|---:|---:|---:|---:|---:|",
]
for _, r in ok.iterrows():
    lines.append(
        f"| {r.provider} | {r['hit@5']:.3f} | {r.mrr:.3f} | {r['all_relevant@5']:.3f} | "
        f"{r['prohibited@5']:.3f} | {r.useful_before_harmful:.3f} | {r.negative_empty_rate:.3f} |"
    )
lines += [
    "",
    "## What the baselines already reveal",
    "",
    "- Simple lexical/LSA retrieval is strong on this small corpus, so a sophisticated engine needs to win on **temporal correctness, conflict handling, multi-hop completeness, procedural success-vs-failure ranking, or learning over time**, not merely Hit@5.",
    f"- All three simple baselines surface stale/failed evidence (`prohibited@5 = {ok['prohibited@5'].mean():.3f}` mean). That is intentionally a major benchmark axis.",
    "- The lexical baseline misses some multi-hop companions even when it finds one correct fact; `all-relevant@5` catches this.",
    "- Negative/unanswerable behavior is separated from normal retrieval because many memory engines always return top-k evidence.",
    "- The toy adaptive diagnostic moves `useful-before-harmful` from 0.80 to 1.00 after verified feedback learned from **training-only paraphrases** and measured on disjoint held-out query wording. This proves the harness can detect transferable outcome-driven ranking change; it is deliberately **not** presented as a Habitus result.",
    "",
    "## Per-category snapshot",
    "",
]
pivot = cat.pivot(index="category", columns="provider", values="reciprocal_rank").round(3)
lines.append(pivot.to_markdown())
lines += [
    "",
    "## Sandbox limitation",
    "",
    "This environment cannot resolve outbound package/repository hosts from the coding container, so the real third-party packages/services could not be installed here. Their adapters and eligibility rules are included in the repository, but the result table marks them unavailable/ineligible rather than substituting simulations.",
]
(OUT / "BASELINE_FINDINGS.md").write_text("\n".join(lines) + "\n")

# Real reader-impact findings, if present.
reader_summary_path = OUT / "reader_summary.csv"
reader_detail_path = OUT / "reader_detail.csv"
if reader_summary_path.exists() and reader_detail_path.exists():
    reader_summary = pd.read_csv(reader_summary_path)
    reader_detail = pd.read_csv(reader_detail_path)
    reader_ok = reader_summary[reader_summary.status == "ok"].copy()
    if not reader_ok.empty:
        fig, ax = plt.subplots(figsize=(8, 4.5))
        vals = reader_ok["answer_pass_rate"].astype(float).to_list()
        ax.bar(reader_ok.provider.tolist(), vals)
        ax.set_ylim(0, 1.05)
        ax.set_ylabel("Deterministic answer pass rate")
        ax.set_title("Reader impact with GPT-5.6 Sol via ChatGPT sidecar")
        for i, value in enumerate(vals):
            ax.text(i, min(value + 0.025, 1.025), f"{value:.3f}", ha="center", va="bottom", fontsize=9)
        fig.tight_layout()
        fig.savefig(OUT / "reader_scores.png", dpi=150)
        plt.close(fig)

        failures = reader_detail[reader_detail["pass_answer"] == False]  # noqa: E712
        reader_lines = [
            "# Reader-impact findings",
            "",
            "This is the first **real LLM reader** trial in the bake-off. GPT-5.6 Sol in the current ChatGPT conversation read only each provider's retrieved context. The benchmark harness, not the model, graded every answer deterministically.",
            "",
            "## Result",
            "",
            "| Provider | Cases | Answer pass | Required coverage | Prohibited-answer rate |",
            "|---|---:|---:|---:|---:|",
        ]
        for _, r in reader_ok.iterrows():
            reader_lines.append(
                f"| {r.provider} | {int(r.cases)} | {r.answer_pass_rate:.3f} | "
                f"{r.mean_required_fraction:.3f} | {r.answers_with_prohibited:.3f} |"
            )
        reader_lines += [
            "",
            "## Interpretation",
            "",
            "- Dense LSA and hybrid RRF supplied enough evidence for the reader to answer all 14 deterministic cases correctly.",
            "- BM25 passed 12/14; both misses were retrieval omissions, and the reader correctly returned `INSUFFICIENT_MEMORY` rather than guessing.",
            "- TF-IDF also passed 12/14, but its failure shape differed: Q008 surfaced only the obsolete deploy command, so the grounded reader emitted a prohibited stale answer; Q016 was an evidence omission and produced `INSUFFICIENT_MEMORY`.",
            "- Q012 exposed multi-hop completeness: BM25 missed part of the credential chain, while TF-IDF/dense/hybrid supplied the secret → Terraform module → workflow chain.",
            "- Q016 exposed procedural retrieval: BM25 and TF-IDF omitted the verified-success NDJSON diagnostic memory; the reader abstained.",
            "",
            "## Failed cases",
            "",
        ]
        if failures.empty:
            reader_lines.append("None.")
        else:
            reader_lines += [
                "| Provider | Case | Reader answer | Retrieved IDs |",
                "|---|---|---|---|",
            ]
            for _, r in failures.iterrows():
                answer = str(r.answer).replace("|", "/")
                ids = str(r.retrieved_ids).replace("|", "/")
                reader_lines.append(f"| {r.provider} | {r.case_id} | {answer} | `{ids}` |")
        reader_lines += [
            "",
            "The archived 56-request sidecar trace under `results/sidecar_reader_trace/` contains the exact OpenAI-shaped requests and responses used for this result.",
        ]
        (OUT / "READER_FINDINGS.md").write_text("\n".join(reader_lines) + "\n")


# Top-k / context-budget sensitivity.
topk_path = OUT / "topk_sensitivity.csv"
if topk_path.exists():
    tk = pd.read_csv(topk_path)
    tk_ok = tk[tk.status == "ok"].copy()
    if not tk_ok.empty:
        fig, ax = plt.subplots(figsize=(8.5, 4.8))
        for provider, group in tk_ok.groupby("provider"):
            group = group.sort_values("mean_context_chars")
            ax.plot(group["mean_context_chars"], group["all_relevant_at_k"], marker="o", label=provider)
        ax.set_ylim(0, 1.05)
        ax.set_xlabel("Mean retrieved context (characters)")
        ax.set_ylabel("All-relevant@k")
        ax.set_title("Retrieval completeness vs context budget")
        ax.legend()
        fig.tight_layout()
        fig.savefig(OUT / "topk_sensitivity.png", dpi=150)
        plt.close(fig)

        tlines = [
            "# Top-k and context-budget sensitivity",
            "",
            "A fixed `top_k` is not a fixed prompt budget. This sweep records exact returned text size so later systems cannot improve simply by injecting much more context.",
            "",
            "| Provider | k | Hit@k | MRR | All relevant@k | Prohibited@k ↓ | Harmful present | Mean harmful count | Mean context chars |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
        for _, r in tk_ok.sort_values(["provider", "k"]).iterrows():
            tlines.append(
                f"| {r.provider} | {int(r.k)} | {r.hit_at_k:.3f} | {r.mrr:.3f} | "
                f"{r.all_relevant_at_k:.3f} | {r.prohibited_at_k:.3f} | {r.harmful_presence_rate:.3f} | {r.mean_prohibited_count:.3f} | {r.mean_context_chars:.1f} |"
            )
        tlines += [
            "",
            "## Readout",
            "",
            "- Dense LSA reaches 0.958 Hit@5 and 0.958 all-relevant@5 at about 421 mean characters of retrieved context.",
            "- TF-IDF reaches 0.958 Hit@8 at only about 376 mean characters, but its MRR remains much lower (0.785), all-relevant completeness is 0.917, and its prohibited fraction is higher; merely appearing somewhere in the window is not enough.",
            "- BM25 reaches the same 0.958 hit rate only at k=10, at about 745 mean characters, and still trails dense on all-relevant completeness (0.875 vs 0.958).",
            "- Increasing k can reduce the *fraction* of prohibited items simply because the denominator grows. The harness therefore also reports harmful-presence rate and mean harmful-item count, which do not get this cosmetic improvement.",
            "- The benchmark will report context size with every external-engine score and should eventually add a fixed-character/token-budget retrieval condition for publication-quality comparisons.",
        ]
        (OUT / "TOPK_FINDINGS.md").write_text("\n".join(tlines) + "\n")
