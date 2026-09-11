# PROBE-20260912 FINDINGS — native Perseus capture vs replacement lineage

Planner-directed mechanism inspection (dispatch/PROBE-20260912-native-capture.md).
Binary: the study binary `/var/home/bmosher/perseus-build/src/target/release/perseus-vault`
2.23.2 (9c82920). Scratch vaults only (`/tmp/native-capture-probe/…`); read-only
over the perseus source; no extension/study artifacts touched.

**No STOP condition:** the compiled binary contains the full capture pipeline
(CLI `capture` verb + MCP `perseus_vault_capture`), and the default distiller is
local/deterministic — no uncompiled components, no external keys.

## The planner's exact sequence (run through native capture, CLI and MCP)

1. Fresh scratch vault → capture `"Production deploys with Docker Compose."`
2. Later capture `"Production now uses Helm. Development still uses Docker Compose."`
3. Inspect store; recall `"how do we deploy to production?"`

## Findings

1. **No replacement lineage is derived.** Conversation 1 distilled to note key
   `production-deploys-with-docker-compose`; conversation 2 to a DIFFERENT key,
   `production-now-uses-helm-development-still-uses-docker-compose`. No
   supersede, no link (`links: []` on both rows, sqlite-verified), no status
   change on the earlier record. The two production statements coexist
   undifferentiated. Capture's only merge mechanisms are trigram near-duplicate
   merging and same-headline→same-key in-place update — neither fires here.

2. **The development statement is NOT its own record** in the planner's shape
   (conversation 2 as one paragraph): the distiller produced ONE note containing
   both sentences. Note-splitting is purely structural (blank-line paragraphs /
   JSONL records / `#`-headed sections), not semantic — the labeled supplementary
   dry-run with a paragraph-split conversation 2 yields two notes
   (`production-now-uses-helm`, `development-still-uses-docker-compose`).

3. **Classification is shallow:** both notes typed `takeaway`; the `decision`
   entity type did not fire on either statement.

4. **Capture output never reaches recall.** Captured entities land
   `status="proposed"`, `source="capture"`, `requires_review: true`, writer
   `"capture"`, hash-only provenance. Public readers see none of them:
   `scan` total 0, `history` total 0, `get_entity` "Entity not found", and
   `recall` abstains (`no_match`) despite 4 stored rows (2 notes + 2 raw
   transcripts, all proposed). After the full planner sequence, the production
   query delivers NOTHING. Raw transcript payloads are additionally retained as
   their own proposed `transcript` entities.

5. **The admission chain cannot resolve capture's own proposals as-is.**
   `perseus_vault_admission_decide` requires (a) a registered agent
   (`perseus_vault_agent`), (b) an enforce-mode authority manifest with
   `memory.admission.review` for the exact workspace
   (`perseus_vault_authority_set`), and (c) an `admission` evidence block inside
   the candidate's body. We satisfied (a) and (b) (probe-operator, tier 3,
   manifest `auth-…`); (c) fails — capture's writes never embed admission
   evidence (`capture.rs` has no admission logic; that evidence is produced by
   the remember path's own trust-admission evaluation). Error: **"admission_decide
   candidate has no admission evidence."** The proposals are therefore stuck:
   non-serveable AND non-admissible through the public tool as-shipped.

6. **CLI and MCP capture are the same pipeline** (docs claim it; receipts
   confirm): identical report shapes, identical store state, identical
   downstream behavior.

7. **Convention notes:** capture stores the workspace hash RAW
   (`ws-probe-native` literal — unlike the benchmark write path's
   sha256-of-scope `workspace_for_scope`); the capture report's per-note `id`
   values do NOT match the stored entity ids; bodies are encrypted at rest
   (sqlite body_json is ciphertext; non-encrypted columns readable).

## Answer to the planner's question

In this build, native capture does not identify replacement relationships —
and it does not even deliver its output to recall without an operator
admission flow that, as shipped, cannot admit capture's own proposals.
Replacement lineage in Perseus 2.23.2 remains exclusively the manual
EXPLICIT_LINEAGE path (`perseus_vault_supersede`) our studies already
exercise. Whatever the published benchmark measured from "automatic
capture," it cannot have come from derived replacement lineage in this
pipeline; at most it reflects selective retrieval over separately admitted
content.

Honest failure-mode ledger: total non-delivery (recall abstain) — observed;
dev record lost as a distinct record (embedded) — observed; wrong lineage
link — not observed (no link at all); duplicate production records —
observed in effect (two coexisting undifferentiated notes; no dedup, since
the headlines differ).

## Receipts

`receipts/` (this directory) — raw capture reports (CLI + MCP), pre/post-
admission scans, history, get_entity, recall outputs, admission-chain
transcript (agent register → authority_set → admission_decide), direct
sqlite dump, and the labeled supplementary dry-run. `probe.sh` reproduces
the whole sequence deterministically against fresh scratch vaults.
