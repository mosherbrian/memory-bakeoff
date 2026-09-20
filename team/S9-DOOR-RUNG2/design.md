# S9-DOOR-RUNG2 design — rung 2: the load competes for relevance

Row S10-1 (admitted from BACKLOG-NEXT rank 6, 2026-09-18). Author: kiln-flash,
2026-09-18. Gate: S10-1G (plumb-fable, written from the row text alone),
VERIFIED PASS by corvid-dsh 13:12 PDT (`team/CORVID-S10-1G-VERIFY.md`); build
claimed 13:57 PDT. Everything below was fixed before any run; `declare.py`
writes the declaration exactly once before the runner executes, and every run
row carries the declaration's sha256.

## Why rung 2 exists (the row's own words, restated)

Rung 1 (`team/S8-DOOR`) held at its declared 20,000-byte competing load. The
post-run fact that makes "held" honest is narrow: rung 1's ten chunk families
(file trees, backup logs, DNS tables, CI matrices, metrics, tickets, cache
stats, access logs, config dumps, queue snapshots) shared no vocabulary with
any item's query, so no tool chunk reached any adapter's top-k. Rung 1 showed
"this pressure never reached the door"; it must not be read as "pressure never
matters". Rung 2 changes exactly one declared thing — the load — and
re-measures the same cells so the door's first result cannot stand in for a
claim about relevance competition generally.

## Prior measurement (re-measurement rule, cited before the run)

`team/S8-DOOR/results.jsonl` and `team/S8-DOOR/verdict.json`, VERIFIED PASS
2026-09-18: bm25 presence 1.00 -> 1.00, irrelevant bytes 0 -> 0;
pi_lcm_toollevel 0.20 -> 0.20, 0 -> 0; claude_mem_chroma_lsa_no_recency
1.00 -> 1.00, 125.6 -> 115.2. Rung 2 quotes those cells verbatim (the gate
compares them against the prior file itself) beside rung 2's own, recomputed
from the delivered text. Nothing blended: both numbers per cell, everywhere.

## What may change: only the load

Byte-identical to rung 1, asserted at declare time and by the gate: the five
frozen items (`items.jsonl` copied byte for byte; sha pinned into both the
rung-1 declaration and this one), the three adapters in the same order, the
600-character budget, the scoring rules, the composition rule, the ingest
order (base records first, tool chunks after), the adapter invocations (bm25
top-1, pi_lcm_toollevel top-5 with reset/close, claude_mem top-3), and the
record conventions (RECORD_TS uniform, session_id `sess-<item_id>`). The
unloaded condition must reproduce rung 1's `normal` cells or the harness —
not the load — moved.

## The declared load (fixed before any run)

Ten tool-output records per item, same scale as rung 1: each chunk padded to
a 2,050-character floor (lines repeated verbatim, rung 1's `_fill` rule;
pure ASCII, so chars equal bytes), giving every item at least 20,500 bytes
against rung 1's declared 20,000. `declare.py` computes each item's exact
byte total, declares the minimum of them as `pressure.tool_output_bytes`
(the guaranteed per-item floor; each pressure row carries its own item's
exact total as `competing_bytes`), and pins the chunk file by sha256.

Query-adjacency is by construction, not by hope: each item's ten chunks come
from ten families that hard-code that item's query vocabulary, with only
numbers, hosts, identifiers and states drawn from a seeded RNG
(`sha256("door-rung2|<item_id>|<family>")`, fully deterministic):

- sel-001 (staging / port / service / listen / tenant): staging-service
  inventory, port allocation ledger, service config dump, listening-socket
  audit, port-scan log, nginx upstream blocks, k8s Service manifests, listener
  re-point tickets, port-check probes, firewall rules — tenants t-2xx, ports
  9443/9444/9445/7443/8480. Port 8443 and "tenant 100" appear nowhere in the
  load.
- sel-002 (runner / pool / approved / deploy / pipeline): runner inventory,
  pipeline YAML, approval logs, dispatch logs, pool capacity, policy dumps,
  heartbeats, pool-move tickets, approval audits, executor logs — pools
  runners-pool-a/c/d/e only. "runners-pool-b" and "self-hosted" appear
  nowhere in the load.
- sel-003 (staging / artifact / files / after / build): artifact-store
  listings, prune cron logs, publish logs, retention config, sync logs, disk
  usage, publish-step YAML, checksum manifests, prune tickets, download
  audits — stores /srv/artifacts/qa, /srv/artifacts/dev,
  /srv/artifacts/archive. "/srv/artifacts/staging" appears nowhere.
- sel-004 (signs / queue / worker / rollout): approval matrix, queue
  snapshots, rollout waves, worker heartbeats, rollout tickets, worker
  config, signoff audits, deploy-gate YAML, status pages, rollout checklists
  — approvers amara/viktor/josie/ren. "Priya" appears nowhere.
- sel-005 (maximum / request / body / size / public / accepts): gateway
  config, 413 access logs, endpoint limit tables, changelogs, config dumps,
  size telemetry, upload tickets, WAF rules, API doc snippets, load-test
  logs — limits 2m/4m on edge/preview gateways. "1 MiB" appears nowhere.

The pointed absence in every bracket above is deliberate: the load competes
with each query for top-k space on that query's own vocabulary, and by
construction it cannot hand the model the answer. The same pre-run assertion
as rung 1 is recomputed twice (declare time and run time), per chunk, against
every item's helpful evidence, whitespace-collapsed and case-blind; the run
aborts before writing anything if any chunk contains any item's evidence
string. Adjacency itself is also asserted pre-run under the gate's own
mechanical rule (every chunk shares at least two query words of four letters
or more with its item's query), and byte totals are asserted at or above the
declared floor.

## Scoring, reach, and the finding

Scoring is rung 1's, imported from `team/S8-DOOR/check.py` by the gate so the
two rungs cannot drift: presence = every helpful string in the delivered text
(whitespace-collapsed, case-blind), mean over items; irrelevant bytes =
delivered bytes minus helpful bytes counted once, floored at 0, mean over
items. Reach is the gate's own re-derivation, mirrored in the runner so the
verdict says the same thing the gate will check: a 40-character window of a
chunk found in the delivered text means the load reached the door on that
item. Where the load reached the door on no item for an adapter, the finding
says so in those words — "held" without reach is "the load never got there",
not "pressure does not matter".

## Chain of custody

`declare.py` (once, before any run): copies rung-1 `items.jsonl` bytes and
verifies them against the rung-1 pin; generates the chunk file; asserts
adjacency, evidence-freeness and byte floors; writes `pressure_chunks.jsonl`,
then `declaration.json` (declared_at, rung-1 budget/scoring/adapters/items
pin, exact load floor, chunks sha) — the declaration text says nothing of the
run. `run_door.py` (after): re-asserts every pin and the evidence-freeness of
the frozen load, runs the 30 cells in rung-1 order, binds every row to the
declaration sha, writes `results.jsonl` then `verdict.json` with rung-1 cells
quoted from the prior and rung-2 cells recomputed. Neither `items.jsonl` nor
`pressure_chunks.jsonl` nor `declaration.json` is touched after the run; any
edit breaks every row's hash and the gate says so. No number moves backwards
into the declaration.

## Limits, stated on purpose

Ten families per item is a sample of "query-adjacent tool output", not a
census; whether the declared load competes HARD ENOUGH is the named
verifier's call (corvid-dsh, at build verification). The budget binds exactly
as rung 1. The normal condition exists to show the harness stood still: only
the load is new, so any rung-2 delta on the pressure cells is attributable to
the load by declaration and by the gate's ONLY-THE-LOAD-MAY-CHANGE check.
