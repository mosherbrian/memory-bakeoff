# CORVID-S13-2G-VERIFY — verdict of record

**Verdict: VERIFIED FAIL — the gate's mechanism inventory over the REAL
EXTERNAL cards yields non-mechanism names and then requires them as per-
mechanism sections, so a correct, narrowly-scoped audit is rejected. Returned
to the gate-writer (gate-batch / astra) for a small fix.**

Verifier: corvid-dsh. I authored neither this gate (gpt-6-astra, via
gate-batch/gate-write, from the row text alone) nor any S13-2 artifact (none
exists). Verified 2026-09-20 16:1x PDT. Gate sha pinned at first read and
unchanged through every run:

```
e0fbfb63e11173af5b10f0f02e204d57399841207a279a6b935db406d9f25b68  check.py
```
(34,348 B, written 15:21 PDT.)

## Declared checks, run from this seat

| probe | command | result |
|---|---|---|
| bare run (absent build) | `python3 check.py` | rc 1, `FINDING[RECEIPT_COUNT] Expected one receipt; found 0.`, no traceback |
| arg contract | `check.py --bogus` | rc 1, `FINDING[GATE_INPUT_ERROR] ValueError: arguments: unrecognized arguments: --bogus` |
| `--selftest` | `check.py --selftest` | rc 0: "29 independent cases, including clean and named-failure assertions" |
| exit contract | direct observation | named `FINDING` on every failing path, no traceback |

The gate is a real, substantive document gate and is not fitted (it predates any
S13-2 artifact; none exists). Its required content is exactly what row S13-2
asks for: retire the tested key-equality protection, state audit-only / no run /
no composite / $0 / local reads, the S11/S7/S10 prior distinctions (native
22/33 vs layer 33/33, 0/13 missed; controlled 0/32 both arms; S10 native 22/33
and 0/13), the G2 / R-PF Gate F / ANSWER Q4 links, a protection-experiment
distinction, per-mechanism update-model / availability / licence / fleet-
evidence sections, and exactly one final disposition.

## Why FAIL: the inventory over the real cards is wrong

`inventory()` (lines 158-219) builds `names` from the BASE mechanisms plus
whatever it finds in `team/EXTERNAL-*.md` via headings, links and filename
fallbacks; `validate()` then requires **exactly one section per name**. Run over
the real cards, it returns 12 names:

```
agentmemory, Hindsight, Mem0, MemPalace, External benchmark, Zep, Letta,
TEAM RECOMMENDATION, External system, Supermemory, MEX-20260919,
Procedural Graphs
```

Four of those are not mechanisms — they are card titles/headings the parser
mistook for candidates:

| name | source | what it actually is |
|---|---|---|
| `External benchmark` | `EXTERNAL-ADEBENCH-20260917.md:1` and `EXTERNAL-KNOWLEDGEDRIFT-20260916.md:1` | heading prefix "External benchmark: adebench …" / "… KnowledgeDrift v1 …" |
| `External system` | `EXTERNAL-ENGRAM-ALPHA-20260917.md:1` | heading prefix "External system: Engram Alpha …" |
| `TEAM RECOMMENDATION` | `EXTERNAL-CORPORA-RECOMMENDATION.md:1` | a recommendation heading, not a mechanism |
| `MEX-20260919` | filename fallback | a card filename, not a mechanism |

Because `validate()` requires a substantive update/supersession model (≥8 words
with an update verb), availability, licence and fleet-evidence line for every
name, a correct audit that covers only the genuine mechanisms is rejected
(`CANDIDATE_SECTION_COUNT`), and the only way to pass is to write four
fabricated "mechanism" sections for a benchmark title, a recommendation heading,
a filename and a heading prefix.

I proved both directions through the gate's own `validate()`:

| probe | result |
|---|---|
| inventory over the real cards | the 12 names above, no `EXTERNAL_INVENTORY_UNRESOLVED` |
| a conforming receipt with sections for all 12 (generic text for the four non-mechanisms) | **CLEAN** — the gate accepts it |
| the same receipt with only the genuine mechanisms (the row's intent) | would be rejected by `CANDIDATE_SECTION_COUNT` for the four names |

So the gate is satisfiable, but only by distorting the artifact the row asks
for. Its 29/29 selftest is green because `make_fixture` writes synthetic cards
whose headings are clean mechanism names — the real cards are not, and the
selftest cannot see the difference. This is the same fixture-vs-real-input class
as the S12-1G finding.

## What the fix needs

1. Filter non-mechanism names in `inventory()`: add the heading prefixes
   ("External benchmark", "External system", and the other `External …` /
   `TEAM …` forms) to `GENERIC`, and drop the filename fallback when the stem is
   a date-coded card id rather than a product name. `names` must be the genuine
   mechanisms the row names.
2. Keep the rest of the gate — it is strong and its content requirements map
   1:1 to the row's text.
3. ADD a selftest case whose external cards carry the REAL heading forms
   ("External benchmark: …", "TEAM RECOMMENDATION — …", a date-coded filename)
   and assert they do NOT become required candidate sections, so this defect
   class cannot pass a green selftest again.

Probe fixture: `/tmp/corvid-s13-2g/probe.py`. — corvid-dsh

---

# ADDENDUM 2 — re-issue re-verified: VERIFIED FAIL (round 2, worse)

**Verdict: VERIFIED FAIL — the re-issue did NOT fix the named defect; its
candidate discovery is now far MORE over-inclusive, and the honest audit is
rejected by 66 missing-section findings instead of four.**

Verifier: corvid-dsh (authored neither gate nor any S13-2 artifact). Gate sha
pinned at first read and unchanged through every run:

```
8c921fbb23fb59aaf440a38f96676200f3569bb72e129e2f925922883ea19817  check.py
```
(40,851 B, written 2026-09-20 17:23:30 PDT — was 34,348 B / `e0fbfb63…`.)

## Declared checks

| probe | result |
|---|---|
| bare run | rc 1, `FINDING[S13-2:RECEIPT_MISSING]`, no traceback |
| `--bogus` | rc 1, `FINDING[S13-2:ARGUMENT_OR_SELFTEST]` |
| `--selftest` | rc 0, "accepted both conforming fixtures; rejected 27 independent non-conforming fixtures with their expected named findings" |

## Why still FAIL: discovery over the real cards explodes

`discover_candidates()` now also harvests filename stems and every level-≤3
heading, and `audit()` requires one substantive mechanism section (update model,
availability, licence, fleet evidence) for **every** discovered name. Run over
the real `team/EXTERNAL-*.md` cards it returns **73 names**, including
non-mechanisms:

```
Application, Caveats, Next step, Our recommendation, TEAM RECOMMENDATION,
GitHub, JavaScript, TypeScript, HuggingFace, ChromaDB, NumPy, ModernBERT,
ADEBENCH-20260917, ENGRAM-ALPHA-20260917, HEIMDALL-20260917, MEX-20260919,
CORPORA-RECOMMENDATION, PROCEDURAL-GRAPHS-20260920, …
```

Probed through the gate's own `audit()` on a temp root holding the REAL cards
and a minimal honest receipt (the four BASE mechanisms, all card filenames
cited, a disposition):

```
discovered candidate count: 73
CANDIDATE_SECTION missing: 66   (plus MECHANISM_SOURCE 4, BITEMPORAL_GRAPH 1, …)
total findings: 89
```

So the gate now demands ~73 substantive "mechanism" sections, including for
"Caveats", "Next step" and "JavaScript". This is not satisfiable as a faithful
audit; it can only be satisfied by fabricating dozens of sections. The previous
version demanded 12 (four of them non-mechanisms); the re-issue is a regression,
not a fix. The 27/27 selftest stays green because its synthetic cards have clean
mechanism headings — the same fixture-vs-real-input class as round 1.

## Fix

1. `discover_candidates()` must return genuine mechanisms only. Stop treating
   filename stems, generic headings ("Caveats", "Next step", "Our
   recommendation", "Application") and technologies/ecosystem names ("GitHub",
   "JavaScript", "TypeScript", "HuggingFace", "ChromaDB", "NumPy") as candidate
   mechanisms. Restrict to the BASE mechanisms plus product identities the card
   itself labels as a system/product (e.g. an explicit "System:"/"Product:"
   label, a bolded product name, or a heading that is a product name), and
   expand the GENERIC/ACRONYM filters to the real heading vocabulary.
2. `CARD_COVERAGE` already requires the receipt to cite every card filename;
   that is the right way to prove the inventory was reviewed — do not also
   demand a mechanism section per card.
3. ADD selftest cards carrying the REAL heading forms and technologies, and
   assert they do not become required candidate sections.

Probe fixture: `/tmp/corvid-s13-2g-r2/probe.py`. — corvid-dsh
