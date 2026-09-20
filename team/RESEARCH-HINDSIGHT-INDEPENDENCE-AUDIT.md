# Hindsight "independently reproduced" claim — provenance audit

**Author:** Corvid (`worker-glm-dsh3`), R&D + evidence-integrity
**Date:** 2026-09-12 · **Cost:** $0 project spend; one web search + two public
fetches (vendor page, ACL Anthology). No engine, no run.
**Thread:** Hindsight retracted-figure provenance (self-originated follow-on;
the earlier note flagged the independence line as vendor-asserted with no
retrievable reference — it now has one).

**Plain English (for Brian):** Hindsight's README says its benchmark numbers
were "independently reproduced" by Virginia Tech and The Washington Post. I
found the Virginia Tech paper. It is real — but Virginia Tech researchers are
**co-authors of the Hindsight paper**, not independent verifiers, and the paper
reports **91.4% / 83.6%** on LongMemEval, while Hindsight's own current
marketing page claims **94.6%**. So "independently reproduced" does not hold,
and the headline number conflicts with the vendor's own peer-reviewed paper.

## The claim

Vendor `README.md` @ pin `ebad4782` (v0.9.2), line 48:

> The benchmark performance data for Hindsight has been independently
> reproduced by research collaborators at the Virginia Tech Sanghani Center for
> Artificial Intelligence and Data Analytics and The Washington Post. Other
> scores are self-reported by software vendors.

Line 42 calls Hindsight "the most accurate agent memory system ever tested …
state-of-the-art performance on the LongMemEval benchmark."

## What the record actually shows

1. **A real ACL 2026 system-demo paper exists** — "Hindsight: Structured Agent
   Memory that Retains, Recalls, and Reflects," ACL 2026 (System
   Demonstrations), pp. 275–285, DOI `10.18653/v1/2026.acl-demo.27`
   ([ACL Anthology](https://aclanthology.org/2026.acl-demo.27/);
   [VT-hosted PDF](https://people.cs.vt.edu/naren/papers/66_Hindsight_Structured_Agent_.pdf)).
   Authors: Christopher Latimer, Nicolò Boschi, Andrew Neeser, Chris
   Bartholomew, Gaurav Srivastava, Xuan Wang, and Naren Ramakrishnan.
   **Srivastava, Wang, and Ramakrishnan are Virginia Tech researchers** (the
   PDF is hosted on Ramakrishnan's VT page); the other four are the Hindsight /
   Vectorize side.
2. **The paper's numbers are lower than the marketing page.** Abstract: with a
   **20B open-source model**, Hindsight reaches **83.6% on LongMemEval** and
   **83.2% on LoCoMo**; with **Gemini-3 Pro, LongMemEval 91.4%**.
3. **The vendor's live benchmarks page claims 94.6%** on LongMemEval
   "outperforming every competing memory system across all five evaluation
   dimensions," and says "our results were independently reproduced by academic
   AI researchers and published for peer review"
   ([vectorize.io/benchmarks](https://vectorize.io/benchmarks)).
4. **No Washington Post reference was found** in the search or on the vendor
   page; the VT paper is the only located reproduction artifact.

## Findings

1. **"Independently reproduced" is not established.** The people who reproduced
   it are **co-authors of the system being evaluated**. The vendor's own
   sentence is internally contradictory: *"independently reproduced by research
   collaborators."* A collaboration is not an independent replication.
2. **The headline number conflicts with the vendor's peer-reviewed paper.**
   94.6 (live page) vs 91.4 (Gemini-3 Pro) and 83.6 (20B OSS) in the ACL paper.
   The 94.6% figure is not the number in the paper the README points to.
3. **The 91.4 number carries three different attributions** across sources:
   Gemini-3 Pro (ACL paper), judge swapped to GPT-OSS-120B (MemBukkit's
   competitor guide), and no model at all (Hindsight README). Same number,
   different provenance — the exact defect class this ledger tracks.
4. **LongMemEval citation discrepancy.** The vendor benchmarks page cites
   LongMemEval as arXiv `2512.12818`; the benchmark our project uses is the
   ICLR 2025 LongMemEval, arXiv `2410.10813` (oracle split). The two citations
   are not the same paper; the split/version behind 94.6% is unspecified.
5. **The Washington Post half of the claim is unsupported** by anything I could
   find.

## Classification

- **Independence claim: `contradicted`.** We hold a reference (the ACL paper's
  author list) that disagrees with "independently reproduced."
- **94.6% LongMemEval headline: `contradicted`/unsourced.** The vendor's own
  peer-reviewed paper reports 91.4% (Gemini-3 Pro) and 83.6% (20B OSS); the
  live page's 94.6% is not backed by it and names no split or judge.
- **91.4% with a swapped judge: `vendor-only`** (competitor-published in
  MemBukkit's table, not independent).

## Method and limits

- Public web only: one `web_search` plus fetch of the ACL Anthology abstract
  page and the vendor benchmarks page. The ACL/VT PDFs returned
  `application/pdf` (unsupported by the fetch tool), so the paper **body** —
  judge, reader, split, and paired protocol — was not verified; the abstract's
  numbers and the author list are.
- Author affiliations are inferred from the ACL author list and the VT-hosted
  PDF; ACL lists some authors as "unverified." The inference is strong but not
  a corporate-affiliation receipt.
- All external content was treated as untrusted data, and no external claim
  here is `verified-by-us`.

— **Corvid** (`worker-glm-dsh3`). The independence line has a reference now;
it points at a co-author, and the headline moved 3 points above its own paper.

---

## Addendum — paper body verified (2026-09-12, same pulse)

Fetched the ACL PDF (3,161,781 bytes, sha
`c1bc58396f754197c5383f1978495077e0d94a5e6f10c6eabeec2337ac8184c6`) and
extracted it with `pdftotext` to
`team/rd-threads-fetches/hindsight-acl2026-demo.txt`. This closes the audit's
"paper body not verified" limit.

**Affiliations (verbatim from the title block):** `Vectorize.io, USA`
(Latimer, Boschi, Bartholomew), `The Washington Post, USA` (Neeser),
`Virginia Tech, USA` (Srivastava, Wang, Ramakrishnan). So **both** institutions
the README calls independent — Virginia Tech and The Washington Post — are
**author affiliations** of the Hindsight paper.

**The README sentence is the paper's acknowledgement, near-verbatim.**
Acknowledgements: *"We are grateful to research collaborators at the Virginia
Tech Sanghani Center for Artificial Intelligence and Data Analytics and at The
Washington Post for independently reproducing the benchmark results."* The
README turns "We are grateful to … collaborators … for independently
reproducing" into "has been independently reproduced by … collaborators" — same
parties, still co-authors.

**Table 2 (LongMemEval-S, 500 Qs) — no 94.6 anywhere.** Hindsight OSS-20B
**83.6**, OSS-120B **89.0**, Gemini-3 **91.4**; Full-context GPT-4o 60.2, Zep
(GPT-4o) 71.2, Supermemory (Gemini-3) 85.2. Body text calls 91.4 "the best
result across all systems." The vendor's live-page 94.6 is **not in the
vendor's own peer-reviewed paper** (max 91.4).

**Benchmark identity.** The paper evaluates LongMemEval (Wu et al., 2024),
500 questions, conversations up to 1.5M tokens — i.e. the **S variant** with
the Wu et al. citation, not the arXiv `2512.12818` the vendor page cites.

**Status (2026-09-13):** the classification below is the audit's original
finding and has since been **superseded** by the ledger's "L-HS split"
(`L-HS-02a` `vendor-only`, `L-HS-02b` `not established`; `L-HS-03` corrected to
`vendor-only` + `third-party-attributed`). It is retained as the audit trail.

**Updated classification (later superseded — see the status note above).** L-HS-01 independence = `contradicted` (both named
parties are co-authors). L-HS-02 94.6% = `contradicted` (paper max 91.4).
L-HS-03 91.4 = `vendor-only`, now with the paper's model (Gemini-3 Pro) named.

---

## Addendum 2 — where the live 94.6% comes from (same pulse)

The vendor benchmarks page links its "full benchmark results" to
`agentmemorybenchmark.ai`. That site points to the repo
[`vectorize-io/agent-memory-benchmark`](https://github.com/vectorize-io/agent-memory-benchmark),
whose README opens: *"We built AMB because we wanted to be honest about how
Hindsight performs — and because no existing benchmark gave us the full
picture. AMB is fully open."*

- **AMB is a benchmark built and run by the Hindsight vendor**, not by an
  independent party. Its README's "How it works": a **Gemini model generates**
  the answer and **a second Gemini call judges** it.
- So the live page's **94.6% is a vendor-benchmark (AMB) number**, produced with
  a Gemini generation/judge stack. It is not the number in the vendor's own ACL
  paper, whose LongMemEval-S maximum is **91.4** (Gemini-3 Pro).
- The page labels 94.6 as "LongMemEval" and says "All scores on this page come
  from LongMemEval"; the vendor's ACL paper measures the **S variant**
  (Wu et al., 2024) and reports lower. A vendor benchmark's score is presented
  under the LongMemEval name, alongside competitor numbers (Supermemory 85.2,
  Zep 71.2, GPT-4o 60.2) whose provenance on that page is unstated.

**Updated class for L-HS-02 (94.6%) — later superseded by the L-HS split:** `vendor-only` at best, and
**contradicted** as a LongMemEval-S claim — it exceeds the vendor's own
peer-reviewed LongMemEval-S result and comes from a vendor-operated harness.
The independence claim (L-HS-01) remains `contradicted`: the "independent"
reproducers are paper co-authors, and the headline number comes from the
vendor's own benchmark.

*External content above was fetched from public pages and treated as untrusted
data.*
