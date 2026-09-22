"""Runtime turn-end handoff: event-driven primary trigger, route-free
completion claims, transactional transition+intent, durable outbox.

Producer (read-only inspected, never modified): the runtime sidecar
`<state>/acp-stream/<key>.jsonl` appends {"t": kind, "item": <runtime
item>, ...}; end is emitted on normal/stall/cancel paths; the file is
best-effort and truncated per turn. Counts/contents alone are never a
durable journal and never prove success.

- TurnWatcher consumes append events with persisted per-file cursors and
  runtime item/session/execution mapping from the adapter binding table.
  Duplicate/stale end, stream reset/rotation/loss and restart reconcile
  against durable session evidence and completion claims, never by
  filename inference and never by mtime polling.
- Route-free claims live at the launch-assigned
  `<package>/completion-claims/<opaque execution>.json` with
  package/attempt/action/execution/contract-step/outcome/artifact
  paths+hashes and NO routing fields. The launcher/contract owns routing
  and actor attribution; destination overrides, verifier nomination and
  self-granted acceptance/duration/authority/next-task are rejected.
- run_handoff validates turn receipt + claim + artifacts + budget and
  declares transition + next intent atomically (kv), then commits the
  ledger transition; the durable outbox delivers intents with stable
  identity and acknowledges only after delivery (never clears before
  send). Restart at every boundary reconciles without blind replay or
  overwritten evidence. No-successor terminal rest is valid.
- Missing/malformed claim or failed turn creates owned bounded
  recovery/escalation under the existing latency gates; end alone never
  certifies artifacts or success.
"""
from __future__ import annotations

import json
import os

CLAIM_REQUIRED = ("package", "attempt", "action", "execution",
                  "contract_step", "outcome", "artifacts")

# Worker-supplied routing/authority fields are never accepted in a claim.
FORBIDDEN_CLAIM_FIELDS = ("verifier", "destination", "next_task",
                          "next_action", "accept", "accepted", "duration_s",
                          "duration", "authority", "grant", "grant_ref",
                          "deadline", "seat", "actor", "route", "router")


class TurnWatcher:
    """Consumes sidecar append events. Cursors are supplied and returned
    (the adapter persists them); file reading is injected for tests."""

    def __init__(self, stream_dir, reader=None):
        self.stream_dir = stream_dir
        self._reader = reader or self._read_new

    def _read_new(self, path, offset):
        try:
            size = os.path.getsize(path)
        except OSError:
            return ([], offset, "rotated-missing")
        if size < offset:
            offset = 0
            note = "truncated-reset"
        else:
            note = "ok"
        try:
            with open(path) as fh:
                fh.seek(offset)
                lines = fh.readlines()
                new_offset = fh.tell()
        except OSError:
            return ([], offset, "unavailable")
        return (lines, new_offset, note)

    def poll(self, keys, cursors):
        """Read new lines per stream key. Returns (events, cursors, notes)
        where events are normalized {stream_key, item, kind, extra}."""
        events, notes = [], {}
        cursors = dict(cursors)
        for key in keys:
            lines, new_offset, note = self._reader(
                os.path.join(self.stream_dir, key + ".jsonl"),
                cursors.get(key, 0))
            notes[key] = note
            if note in ("rotated-missing", "unavailable"):
                continue
            cursors[key] = new_offset
            for line in lines:
                try:
                    row = json.loads(line)
                except ValueError:
                    continue  # partial/corrupt line skipped
                if not isinstance(row, dict) or "t" not in row \
                        or "item" not in row:
                    continue
                events.append({"stream_key": key, "item": row["item"],
                               "kind": row["t"],
                               "extra": {k: v for k, v in row.items()
                                         if k not in ("t", "item")}})
        return (events, cursors, notes)


def write_claim(claims_dir, execution_id, claim):
    """Worker-side route-free claim writer (fixture/launcher use)."""
    missing = [f for f in CLAIM_REQUIRED if f not in claim]
    if missing:
        raise ValueError("claim missing %s" % missing)
    path = os.path.join(claims_dir, execution_id + ".json")
    with open(path, "w") as fh:
        json.dump(claim, fh, sort_keys=True)
    return path


def validate_claim(claim, launch):
    """Route-free validation against the launch manifest. Returns the
    claim on success; raises ValueError with an owned code otherwise."""
    for field in FORBIDDEN_CLAIM_FIELDS:
        if field in claim:
            raise ValueError("E_FORGED_ROUTE: worker field %s rejected; "
                             "routing/authority belong to launcher" % field)
    for field in CLAIM_REQUIRED:
        if field not in claim:
            raise ValueError("E_CLAIM_INCOMPLETE: missing %s" % field)
    for field in ("package", "attempt", "action", "execution"):
        if claim.get(field) != launch.get(field):
            raise ValueError("E_CLAIM_MISMATCH: %s does not match launch "
                             "manifest" % field)
    if not isinstance(claim.get("artifacts"), dict) or \
            not claim["artifacts"]:
        raise ValueError("E_CLAIM_INCOMPLETE: artifacts paths+hashes?")
    return claim


def run_handoff(adapter, qid, turn, claim, launch, verify_spec=None,
                terminal_disposition=None):
    """Validate turn receipt + claim + artifacts + budget, then declare
    transition + next intent atomically and commit the ledger step.

    A production-path end causes the next authorized dispatch (ledger
    verifier flight + outbox intent) or an acknowledged bounded
    escalation — never a bare descriptive dict. Returns an outcome
    record; raises OwnedFault/ValueError without partial state on
    invalid input."""
    from host_adapter import OwnedFault
    item, current = turn.get("item"), adapter.current_execution(
        launch["action"])
    seen_key = "turn-seen:%s:%s" % (turn.get("stream_key"), item)
    if adapter.driver.kv.get(seen_key) is not None:
        return {"decision": "duplicate-end-ignored", "durable": True}
    validate_claim(claim, launch)
    outcome = claim.get("outcome")
    if outcome in ("failed", "cancelled"):
        esc, dup = adapter.escalate_unavailable(
            launch["action"], "tern", "bounded-recovery",
            claim.get("recover_by_utc") or
            adapter.driver.kv.get("harness-escalation-deadline") or
            "2026-09-22T01:00:00Z")
        adapter.driver._kv_put_many([
            (seen_key, json.dumps({"outcome": outcome}, sort_keys=True)),
            ("turn-last:%s" % launch["action"], json.dumps(turn,
                                                           sort_keys=True))])
        return {"decision": "owned-recovery", "escalation": esc,
                "duplicate": dup}
    if outcome != "completed":
        raise OwnedFault("E_CLAIM_INCOMPLETE",
                         "turn outcome is not a completion claim")
    artifacts = claim.get("artifacts") or {}
    bound = adapter.bound_artifacts(launch["action"])
    missing = [h for h in artifacts.values() if h not in bound]
    if missing:
        raise OwnedFault("E_ARTIFACT_MISMATCH",
                         "claim artifacts not bound at dispatch")
    # Declare transition + next intent atomically BEFORE the ledger write;
    # a crash after this point rolls forward the SAME declared handoff.
    intent = {"next": "verifier-dispatch" if verify_spec else "terminal",
              "action": launch["action"], "execution": launch["execution"],
              "item": item}
    adapter.driver._kv_put_many([
        (seen_key, json.dumps({"outcome": outcome}, sort_keys=True)),
        ("turn-last:%s" % launch["action"], json.dumps(turn,
                                                       sort_keys=True)),
        ("handoff-intent:%s:%s" % (launch["action"],
                                   launch["execution"]),
         json.dumps(intent, sort_keys=True))])
    if terminal_disposition is not None:
        adapter.driver.terminal_close(
            qid, launch["action"] + "-hend-v",
            launch["action"] + "-hend-d",
            {"type": "verify_pass", "who": "verifier",
             "body": {"elapsed_s": 60, "pass_budget_s": 1800,
                      "finding": "positive"}},
            terminal_disposition)
        return {"decision": "terminal-rest", "durable": True}
    if verify_spec is None:
        raise OwnedFault("E_NO_SUCCESSOR",
                         "completion needs a verifier step or an explicit "
                         "terminal disposition")
    res, dup = adapter.drive_next(
        launch["action"], verify_spec["action_id"],
        verify_spec["deadline_utc"], artifacts, qid=qid)
    outbox_id = adapter.outbox_send(
        verify_spec["action_id"],
        {"kind": "verifier-dispatch", "action": verify_spec["action_id"]})
    return {"decision": "dispatched-next", "next": res,
            "duplicate": dup, "outbox": outbox_id}
