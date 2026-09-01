# Generation 16: sidecar response import blocked by Drive text encoding

Generation 16 received the exact named native Google Drive document
`AGENTMEMORY_GEN15_SIDECAR_RESPONSE_BUNDLE` and exported it with rclone's
plain-text Google Docs export.  The temporary, uncommitted export passed the
requested semantic preflight without examining or modifying answer text:

- `schema_version`: 1;
- `kind`: `memory-bakeoff-sidecar-response-bundle`;
- request-set SHA-256:
  `9e2dd8955ca9d0eb044f415594b1a9c8e83543de1f58a9955c1c671e2bf6ea5d`;
- response count: 28;
- exported byte-stream SHA-256:
  `34d1b3f1101d8cf5bd84f5239e89e1ab5e563c53d1f26cccf4da219c20cb867b`.

## Fail-closed result

The verbatim Drive plain-text export begins with UTF-8 BOM bytes `EF BB BF`
before the JSON `{`.  The Gen15 importer uses the standard JSON parser and
therefore rejected the file as an invalid JSON transport artifact before it
examined any response object:

```text
JSONDecodeError: Unexpected UTF-8 BOM (decode using utf-8-sig)
```

No normal sidecar response file was written: both Gen14 `responses/`
directories remain empty.  No request, fingerprint, prompt, ranked context,
or ChatGPT answer was changed.  No agentmemory retrieval/lifecycle action was
run.

Generation 16 explicitly forbade changing importer validation or manually
normalizing the response bundle after an import failure.  Accordingly, this is
recorded as a **Drive transport encoding blocker**, not repaired locally.

## Required next input

Provide the same complete 28-object response bundle as a stored UTF-8 JSON
file without a byte-order mark (preferred), or through a Drive/native export
mechanism whose bytes begin directly with `{`.  Its request IDs, fingerprints,
order, answer contents, and required sidecar fields must remain exactly the
Generation 15 bundle.  Codex can then rerun the existing importer and grader
unchanged.  Do not rerun agentmemory or regenerate the frozen requests.

The lifecycle-adjusted interpretation remains pending reader grading: Gen13
stress Hit@5 1.000 / all-relevant@5 0.958 occurred after only 82/500 memories
remained live and 418/450 distinct stress distractors were falsely superseded
(92.9%).
