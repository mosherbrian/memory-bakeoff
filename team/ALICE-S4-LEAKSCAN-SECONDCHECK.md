# Second-seat check — S4 leak-scan retraction reproduced; the `draft_id` canary is a keyword, not a value

**Author:** Alice (`worker-glm-dsh`), verification/provenance seat · **Date:**
2026-09-13 11:51 UTC · **Cost:** $0, local + one counts-only triage over the
frozen packets · **Trigger:** standing second-check of
`team/ASSAY-S4-LEAKSCAN-PATH-BUG-FIX.md` (a retraction + rater-blinding stop
item). **Method note:** I read no packet *text* into the record and printed no
content; the triage below emits only three integers.

## Verdict

**PASS / AGREE on the retraction and the corrected result** — independently
reproduced to the packet: 19 sessions, 134 turns, 376 == 376, `builder_gate_failed=4`,
`leak_scan_verdict=FAIL`, `b7_all_pass=false`, rc 1; power check rc 0. **One
important nuance:** both the builder gate and the scanner match the **bare key
name** `draft_id` (`LEAK_CANARIES` / `SUBSTANCE`), so the 6 flagged packets are
"unredacted non-user entries that **mention** the key", not evidence of a leaked
draft **value**. A counts-only triage finds **17 `draft_id` occurrences, 0 of
them followed by a value** (`=`/`:` + token). The stop item is a **redaction
contract violation**, not a confirmed substance leak.

## Retraction and corrected result — reproduced

| Claim | Check | Result |
|---|---|---|
| fixed aggregator `95d90749…`, power check `3e573dc0…`, power result `9a06b5d1…`, frozen result `9286a135…`, gated builder `6616c48e…` | re-hashed all five | ✓ 5/5 match |
| old harness scanned `out/packets` (nonexistent) → leak PASS by construction | read the new aggregator + ran it | ✓ it now scans `<out>/turn-*.json`; my run scanned **134** turn files |
| fixed frozen run: 19 / 134 / 376==376 / `builder_gate_failed 4` / leak FAIL / rc 1 | re-ran on the frozen snapshot | ✓ exactly; power check **7/7, all_pass true** |
| the 4 failing sessions are real packet producers | read `per_session` + `leaked_packets` | ✓ 4 sessions, 6 packets, `builder_rc=1`/`builder_leak_scan=FAIL` on exactly those |
| old note carries the retraction | grep `ASSAY-S4-READINESS-RECHECK.md` | ✓ 2 retraction markers present |

## The nuance — `draft_id` is matched as a bare substring

`packet_leak_scan.py:26` → `SUBSTANCE = ("key=record-", "draft_id", "confirmation_code")`,
tested as `s in json.dumps(entry)`; the gated builder is the same
(`build_s4_packets.py:40-41`). Synthetic demonstration (no real content):

```python
{"message": {"role": "toolResult", "content": '{"name": "draft_id", "type": "string"}'}}
{"message": {"role": "assistant",  "content": 'I will call the tool with a draft_id parameter.'}}
```

Both are flagged `"unredacted non-user entry carries substance", hits=['draft_id']`
— pure key mentions, no secret. So the canary cannot distinguish a leaked
`draft_id=<value>` from a schema/prose mention of the field name.

**Counts-only triage of the 6 real flagged packets** (regex over the emitted
entries; nothing printed): `draft_id` appears **17 times** — `assistant` 9,
`toolResult` 8 — classified by what follows the token:

| class | count |
|---|---:|
| value-ish (`draft_id` then `=`/`:` + a token) | **0** |
| mention-ish (no value follows) | **17** |

Conclusion: on this frozen snapshot the detector's only hit key is the bare
name, and none is an assignment — so the finding is **"unredacted non-user
entries exist and name the key"**, not **"a draft secret value leaked"**. The
contract violation stands (the scanner reached those entries only because
`is_redacted()` was false); the *blinding* severity is unestablished.

## Recommendation

1. **Reword the stop item** from "emit at least one unredacted non-user entry
   carrying a sentinel/substance marker" to "…carrying the bare key name
   `draft_id` (classification: mention, not a value on this snapshot)". Keep the
   fail-closed behavior.
2. **Tighten the canary** to an assignment shape (`draft_id\s*[=:]\s*\S` or the
   builder's actual secret format) in both the gate and the scanner, or emit a
   `severity`/`class` (`value` vs `mention`) per hit. This is the same
   "predicate matches the wrong thing" family as the S6 empty-scan and the
   blind_pack short-value findings.
3. The underlying question — should *all* non-user entries be redacted, or only
   memory-activity ones — is the owner's contract call; if all, the 4 sessions
   are a genuine builder bug independent of `draft_id`.

## Limits

- The triage is a heuristic classification of the token's immediate syntax; a
  secret in an unusual serialization could be mis-binned. It reports counts, not
  values, and no packet content entered this note.
- Frozen snapshot only; the live window has grown and must be re-run at close.
- Detector-vocabulary limits (a memory string that is neither marker nor canary
  escapes) are unchanged from `ASSAY-S4-B7-LEAK-GATE.md`.
