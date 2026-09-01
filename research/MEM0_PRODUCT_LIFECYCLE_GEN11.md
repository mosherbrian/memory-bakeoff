# Mem0 product lifecycle inspection: generation 11

Generation 11 inspected the pinned upstream product-ingestion path before any
benchmarking.  No lifecycle sentinel or score was run: this Mac has no
available faithful LLM backend for the `infer=True` call, and a deterministic
substitute would not be a product result.

## Frozen source and intended configuration

- Upstream checkout: `mem0ai/mem0` commit
  `19cb89aff472325c707f64b2f34ae6afdbf7faf7`, package 2.0.19.
- The proposed retrieval/storage portion remains the Gen10 raw-product stack:
  FastEmbed 0.8.0 `thenlper/gte-large` resolved to
  `qdrant/gte-large-onnx` snapshot `770e825c74a004f165b78793f7c8fc4a95280878`;
  ONNX Runtime 1.29.0 CPU; embedded Qdrant 1.19.0; sparse
  `Qdrant/bm25` snapshot `22b8d2af71a76161e18dd432d2cee0eefa66e412`; scope
  `user_id=memory-bakeoff`; threshold 0.1; vector candidates `max(4*k, 60)`.
- The missing first-class component is a real LLM provider/model.  The pinned
  OpenAI configuration accepts `openai_base_url` and defaults to temperature
  0.1 (`external/mem0/mem0/configs/llms/openai.py:12-35`); its client uses
  that configured URL or `OPENAI_BASE_URL` (`external/mem0/mem0/llms/openai.py:39-53`).

## What `infer=True` actually does at this pin

The pinned V3 inference path is an **additive extraction pipeline**, not an
LLM-directed add/update/delete decision engine.

1. It gathers up to ten prior session messages, embeds the new parsed messages,
   and retrieves at most ten existing vectors scoped only by nonempty
   `user_id`, `agent_id`, and `run_id`
   (`external/mem0/mem0/memory/main.py:918-931`).  Other custom metadata does
   not constrain this consolidation lookup.
2. It presents those existing memory texts to one LLM call using
   `ADDITIVE_EXTRACTION_PROMPT` and `generate_additive_extraction_prompt`
   (`main.py:940-962`).  The prompt builder explicitly describes itself as
   “ADD-only”; the JSON response is a root `memory` array whose objects include
   `id`, `text`, `attributed_to`, and optional `linked_memory_ids`
   (`external/mem0/mem0/configs/prompts.py:918-942,1016-1045`).
3. The implementation parses only the response's `memory` array.  Although it
   creates a local integer-to-UUID mapping for existing memories and the prompt
   permits `linked_memory_ids`, neither is subsequently applied to an existing
   vector (`main.py:933-939,971-989,1015-1039`).
4. It embeds each extracted text, then removes only exact MD5 duplicates among
   the ten retrieved candidates and the current batch (`main.py:991-1024`).
   A paraphrase or a duplicate outside the retrieved top ten is not an exact
   dedup hit.
5. Each surviving text receives a new UUID and a copied input metadata payload,
   then is inserted as a new vector (`main.py:1028-1062`).  Its history is
   unconditionally an `ADD` record with no predecessor (`main.py:1064-1084`).

Explicit `_update_memory` and `_delete_memory` implementations do exist:
update preserves the supplied native ID, replaces vector/payload content, and
writes an `UPDATE` history row; delete removes the vector and writes `DELETE`
with `is_deleted=1` (`main.py:2038-2128`).  This `infer=True` pipeline does not
dispatch to either method.  History is stored per native memory ID with old and
new text, event, timestamps, deletion flag, actor, and role
(`external/mem0/mem0/memory/storage.py:150-255`).

## Consequences for the requested sentinel and provenance

If an LLM backend becomes available, a chronological sentinel can faithfully
test additive extraction, exact duplicate suppression, and the visibility of
old versus newly extracted correction text.  It cannot demonstrate automatic
replacement, supersession, or deletion in this source path: a correction may
become another `ADD`, and its old fact remains live unless a caller separately
uses the public update/delete API.

Native `metadata.record_id` is also not a safe one-to-one lineage channel in
this path.  Input metadata is copied to every extracted output
(`main.py:1028-1037`), so one operation that yields several synthesized
memories would stamp all of them with the same input record ID.  The LLM's
optional links are not stored.  A publishable future product evaluation needs
an external, append-only operation trace that records each input operation,
native returned UUID, exact output text, and native history snapshot.  That
sidecar can establish lineage without changing Mem0's decisions; it must not
fuzzy-map generated text to canonical benchmark IDs.  Until that trace is
proven on a real run, full-product scoring remains blocked.

## Faithful backend check and blocker

The host had only PostgreSQL (loopback port 5432) and the macOS `rapportd`
service (port 59885) listening when inspected.  No `ollama`, `llama-server`, or
`lmstudio` executable was installed, and no recognized OpenAI-compatible local
model endpoint was present.  The repository's optional ChatGPT-sidecar is
architecturally compatible with Mem0's configurable OpenAI base URL, but it
requires an active interactive ChatGPT queue responder
(`research/CHATGPT_SIDECAR.md`).  No such proxy/responder is running or
reachable in this Codex session.

We deliberately did not use external credentials, paid APIs, a secret-backed
endpoint, or a deterministic/replayed response.  Therefore the precise Gen11
blocker is: **no real, locally reachable or actively serviced OpenAI-compatible
LLM backend with a named model and reproducible configuration.**  No private
prompt/response, sentinel state, or result directory was created.

## Next prerequisite

Provide or start one real local OpenAI-compatible LLM endpoint, or activate the
interactive ChatGPT-sidecar responder and proxy.  Then freeze its model and
generation controls, run the small chronological sentinel once, retain native
before/after snapshots and history, and decide whether the resulting
additive-only behavior is the product lifecycle arm intended for later scoring.
