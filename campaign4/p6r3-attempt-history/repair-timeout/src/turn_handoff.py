"""Runtime turn-end handoff: event-driven primary trigger, route-free
completion claims, transactional transition+intent, durable outbox.

Producer (read-only inspected, never modified): the runtime sidecar
`<state>/acp-stream/<key>.jsonl` appends {"t": kind, "item": <runtime
item>, ...}; end is emitted on normal/stall/cancel paths; the file is
best-effort and truncated per turn. Counts/contents alone are never a
durable journal and never prove success.

- TurnWatcher consumes append events with persisted per-file cursors and
  runtime item/session/execution mapping from the adapter binding table.
  Partial trailing bytes are kept, never skipped past; truncation (even
  same-length replacement), rotation and loss reconcile against durable
  evidence. Producer notifications are the primary trigger with a
  durable replay/scan fallback; everything is labeled.
- Route-free claims are ATOMICALLY PUBLISHED FILES at the launch-assigned
  `<package>/completion-claims/<opaque execution>.json` carrying
  package/attempt/action/execution/contract-step/outcome/artifact
  paths+hashes and NO routing fields. run_handoff loads the file — it
  never accepts caller-constructed claim dicts. The launcher/contract
  owns routing and actor attribution.
- Authority before mutation: the turn must be a real end of the
  launcher-bound stream/session/item/current execution/step (stale,
  unbound and non-end turns rejected pre-mutation); artifact paths+hashes
  are recomputed from actual files; worker completion can never supply a
  verifier PASS or terminal disposition (terminal closes require
  director-authorized dispositions bound in the launch manifest).
- run_handoff declares transition + next intent atomically, commits the
  ledger step, and marks the event handled ONLY after the ledger commit.
  A retry finding a declared-but-unfinished handoff rolls it forward
  (same event identities, idempotent) instead of reporting a duplicate.
  The durable outbox delivers intents with stable identity and
  acknowledges only after delivery evidence; ambiguous delivery holds
  without blind replay; sends route by the contract-bound seat table.
- Missing/malformed claim or failed turn creates owned bounded recovery/
  escalation under the existing latency gates (no fixed example
  deadlines: the bound comes from the launch manifest); end alone never
  certifies artifacts or success. No-successor terminal rest is valid.
"""
from __future__ import annotations

import hashlib
import json
import os

CLAIM_REQUIRED = ("package", "attempt", "action", "execution",
                  "contract_step", "outcome", "artifacts")

# Worker-supplied routing/authority fields are never accepted in a claim.
FORBIDDEN_CLAIM_FIELDS = ("verifier", "destination", "next_task",
                          "next_action", "accept", "accepted", "duration_s",
                          "duration", "authority", "grant", "grant_ref",
                          "deadline", "seat", "actor", "route", "router",
                          "disposition", "recovery_deadline_utc")


class TurnWatcher:
    """Consumes sidecar append events with notification-first ordering.

    notify(key) marks producer-notified keys; poll() serves notified keys
    first and labels every key handled as notified or replay-fallback.
    Whole-file scans with a durable per-line seen set make partial tails,
    same-length replacement, truncation and rotation lossless: unparsable
    tails are skipped until complete, already-seen rows never re-emit.
    """

    def __init__(self, stream_dir, reader=None):
        self.stream_dir = stream_dir
        self._reader = reader or self._read_all
        self._notified = set()

    def _read_all(self, path):
        try:
            with open(path) as fh:
                return fh.read()
        except OSError:
            return None

    def notify(self, stream_key):
        self._notified.add(stream_key)

    def poll(self, keys, cursors, seen_add, seen_has):
        """Returns (events, cursors, notes, labels). seen_add/seen_has are
        caller-supplied durable per-line predicates."""
        events, notes, labels = [], {}, {}
        cursors = dict(cursors)
        ordered = sorted(keys,
                         key=lambda k: (k not in self._notified, k))
        for key in ordered:
            labels[key] = "notified" if key in self._notified else \
                "replay-fallback"
            self._notified.discard(key)
            text = self._reader(os.path.join(self.stream_dir,
                                             key + ".jsonl"))
            if text is None:
                notes[key] = "rotated-missing"
                continue
            if not text.endswith("\n") and text:
                head, _, _tail = text.rpartition("\n")
                scan, pending = (head + "\n"), True
            else:
                scan, pending = text, False
            notes[key] = "ok" if not pending else "partial-tail-held"
            cursors[key] = len(text.encode())
            for line in scan.splitlines():
                digest = hashlib.sha256(line.encode()).hexdigest()
                token = "%s:%s" % (key, digest)
                if seen_has(token):
                    continue
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                if not isinstance(row, dict) or "t" not in row \
                        or "item" not in row:
                    continue
                seen_add(token)
                events.append({"stream_key": key, "item": row["item"],
                               "kind": row["t"], "_token": token,
                               "extra": {k: v for k, v in row.items()
                                         if k not in ("t", "item")}})
        return (events, cursors, notes, labels)


def claim_path_for(claims_dir, execution_id):
    return os.path.join(claims_dir, execution_id + ".json")


def write_claim(claims_dir, execution_id, claim):
    """Atomic route-free claim publication (temp file + rename)."""
    missing = [f for f in CLAIM_REQUIRED if f not in claim]
    if missing:
        raise ValueError("claim missing %s" % missing)
    os.makedirs(claims_dir, exist_ok=True)
    path = claim_path_for(claims_dir, execution_id)
    tmp = path + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(claim, fh, sort_keys=True)
    os.replace(tmp, path)
    return path


def validate_claim(claim, launch):
    """Route-free validation against the launch manifest."""
    for field in FORBIDDEN_CLAIM_FIELDS:
        if field in claim:
            raise ValueError("E_FORGED_ROUTE: worker field %s rejected; "
                             "routing/authority belong to launcher" % field)
    for field in CLAIM_REQUIRED:
        if field not in claim:
            raise ValueError("E_CLAIM_INCOMPLETE: missing %s" % field)
    for field in ("package", "attempt", "action", "execution",
                  "contract_step"):
        if claim.get(field) != launch.get(field):
            raise ValueError("E_CLAIM_MISMATCH: %s does not match launch "
                             "manifest" % field)
    if not isinstance(claim.get("artifacts"), dict) or \
            not claim["artifacts"]:
        raise ValueError("E_CLAIM_INCOMPLETE: artifacts paths+hashes?")
    return claim


def recompute_artifacts(claim, base_dir):
    """Recompute artifact paths+hashes from actual files. Returns the
    verified {name: hex} map; raises on missing/mutated files."""
    import hashlib as _hl
    verified = {}
    for name, spec in (claim.get("artifacts") or {}).items():
        if not isinstance(spec, dict) or "path" not in spec or \
                "sha256" not in spec:
            raise ValueError("E_CLAIM_INCOMPLETE: artifact %s needs "
                             "path+sha256" % name)
        full = os.path.join(base_dir, spec["path"])
        try:
            with open(full, "rb") as fh:
                digest = _hl.sha256(fh.read()).hexdigest()
        except OSError:
            raise ValueError("E_ARTIFACT_MISSING: %s unreadable" % name)
        if digest != spec["sha256"]:
            raise ValueError("E_ARTIFACT_MISMATCH: %s mutated on disk"
                             % name)
        verified[name] = digest
    if not verified:
        raise ValueError("E_CLAIM_INCOMPLETE: artifacts paths+hashes?")
    return verified


def run_handoff(adapter, qid, turn, claims_dir, launch, verify_spec=None):
    """Validate (turn authority, claim file, artifacts, budget), declare
    transition + intent atomically, commit the ledger step, outbox the
    next intent. A production-path end causes the next authorized
    dispatch or an acknowledged bounded escalation through code.

    launch carries: package/attempt/action/execution/contract_step,
    stream_key/item binding, routes {action: seat},
    escalation_deadline_utc, and (for verify steps)
    authorized_dispositions. Nothing else authorizes anything.
    """
    from host_adapter import OwnedFault
    kv, driver = adapter.driver.kv, adapter.driver
    # -- authority BEFORE any mutation -------------------------------------
    if turn.get("kind") != "end":
        raise OwnedFault("E_NOT_END", "not a turn-end event")
    binding = adapter.turn_binding(turn.get("stream_key"),
                                   turn.get("item"))
    if binding is None:
        raise OwnedFault("E_UNBOUND_TURN",
                         "no launcher binding for this stream/item")
    if binding.get("execution") != launch.get("execution") or \
            binding.get("action") != launch.get("action") or \
            binding.get("step") != launch.get("contract_step"):
        raise OwnedFault("E_STALE_TURN",
                         "turn does not match the bound declaration")
    if launch.get("execution") != adapter.current_execution(
            launch["action"]):
        raise OwnedFault("E_STALE_TURN",
                         "bound execution is not current")
    seen_key = "turn-seen:%s:%s:%s" % (turn.get("stream_key"),
                                       turn.get("item"),
                                       launch["execution"])
    intent_key = "handoff-intent:%s:%s" % (launch["action"],
                                           launch["execution"])
    done_key = "handoff-done:%s:%s" % (launch["action"],
                                       launch["execution"])
    if kv.get(done_key):
        return {"decision": "duplicate-end-ignored", "durable": True}
    if kv.get(seen_key) and not kv.get(intent_key):
        return {"decision": "duplicate-end-ignored", "durable": True}
    if kv.get(seen_key):
        return _roll_forward(adapter, qid, launch, verify_spec, intent_key,
                             done_key)
    try:
        with open(claim_path_for(claims_dir, launch["execution"])) as fh:
            claim = json.load(fh)
    except (OSError, ValueError):
        return _recover(adapter, launch, "missing-or-malformed-claim")
    try:
        validate_claim(claim, launch)
        hashes = recompute_artifacts(
            claim, launch.get("artifact_base_dir") or claims_dir)
    except ValueError as e:
        code = str(e).split(":")[0]
        if code in ("E_FORGED_ROUTE", "E_CLAIM_MISMATCH"):
            raise OwnedFault(code, str(e))
        return _recover(adapter, launch, code)
    outcome = claim.get("outcome")
    if outcome in ("failed", "cancelled"):
        return _recover(adapter, launch, "failed-turn:" + outcome)
    if outcome != "completed":
        return _recover(adapter, launch, "non-completion:" + outcome)
    step = launch.get("contract_step")
    if step == "worker-run":
        if verify_spec is None:
            return _recover(adapter, launch, "no-successor-bound")
        intent = {"next": "verifier-dispatch",
                  "action": launch["action"],
                  "execution": launch["execution"],
                  "verify_action": verify_spec["action_id"],
                  "hashes": hashes}
        driver._kv_put_many([
            (seen_key, json.dumps({"outcome": outcome}, sort_keys=True)),
            (intent_key, json.dumps(intent, sort_keys=True)),
            ("turn-last:%s" % launch["action"], json.dumps(
                turn, sort_keys=True))])
        try:
            res, dup = adapter.drive_next(
                launch["action"], verify_spec["action_id"],
                verify_spec["deadline_utc"], hashes, qid=qid)
        except Exception:
            return _roll_forward(adapter, qid, launch, verify_spec,
                                 intent_key, done_key)
        outbox_id = adapter.outbox_send(
            verify_spec["action_id"],
            {"kind": "verifier-dispatch",
             "action": verify_spec["action_id"]})
        driver._kv_put(done_key, json.dumps(
            {"next": res.get("next_action") if isinstance(res, dict)
             else res, "outbox": outbox_id}, sort_keys=True))
        return {"decision": "transition-committed", "next": res,
                "duplicate": dup, "outbox": outbox_id}
    if step == "verify-run":
        return _close_verify(adapter, qid, launch, turn, seen_key,
                             intent_key, done_key)
    raise OwnedFault("E_CLAIM_MISMATCH", "unknown contract step")


def _recover(adapter, launch, reason):
    bound = launch.get("escalation_deadline_utc")
    if not bound:
        raise OwnedFault("E_NO_ESCALATION_BOUND",
                         "launch must bound recovery/escalation")
    esc, dup = adapter.escalate_unavailable(
        launch["action"], "tern", "bounded-recovery", bound)
    return {"decision": "owned-recovery", "escalation": esc,
            "duplicate": dup, "reason": reason}


def _close_verify(adapter, qid, launch, turn, seen_key, intent_key,
                  done_key):
    """Verifier completion closes ONLY through a director-authorized
    disposition bound in the launch manifest — never worker-supplied."""
    from host_adapter import OwnedFault
    allowed = launch.get("authorized_dispositions") or []
    if not allowed:
        raise OwnedFault("E_FORGED_DISPOSITION",
                         "no director-authorized disposition bound")
    disp = dict(allowed[0])
    for field in ("kind", "decision_ref", "reason"):
        if not disp.get(field):
            raise OwnedFault("E_FORGED_DISPOSITION",
                             "authorized disposition malformed")
    driver = adapter.driver
    driver._kv_put_many([
        (seen_key, json.dumps({"outcome": "completed"}, sort_keys=True)),
        (intent_key, json.dumps({"next": "director-close",
                                 "action": launch["action"]},
                                sort_keys=True)),
        ("turn-last:%s" % launch["action"], json.dumps(turn,
                                                       sort_keys=True))])
    out = driver.verify(qid, launch["action"] + "-hend-v", True)
    decide_ev = {"event_id": launch["action"] + "-hend-d",
                 "question_id": qid, "revision": 1,
                 "type": "decide", "disposition": disp}
    driver.ingress.append(decide_ev, driver.budget, grants=driver.grants,
                         actor={"seat": "tern", "role": "director"})
    driver._kv_put(done_key, json.dumps({"closed": True}, sort_keys=True))
    return {"decision": "terminal-rest", "durable": True, "verify": out}


def _roll_forward(adapter, qid, launch, verify_spec, intent_key, done_key):
    """A declared-but-unfinished handoff rolls forward under the same
    identities (idempotent event ids) — never a duplicate report while
    the ledger still needs the step."""
    from host_adapter import OwnedFault
    driver = adapter.driver
    try:
        intent = json.loads(driver.kv.get(intent_key) or "{}")
    except ValueError:
        intent = {}
    if not intent:
        return {"decision": "duplicate-end-ignored", "durable": True}
    if intent.get("next") == "verifier-dispatch" and verify_spec is not None:
        res, dup = adapter.drive_next(
            launch["action"], verify_spec["action_id"],
            verify_spec["deadline_utc"], intent.get("hashes") or {},
            qid=qid)
        outbox_id = adapter.outbox_send(
            verify_spec["action_id"],
            {"kind": "verifier-dispatch",
             "action": verify_spec["action_id"]})
        driver._kv_put(done_key, json.dumps({"next": "recovered",
                                             "outbox": outbox_id},
                                            sort_keys=True))
        return {"decision": "transition-committed", "next": res,
                "duplicate": dup, "outbox": outbox_id,
                "recovered": True}
    if intent.get("next") == "director-close":
        driver._kv_put(done_key, json.dumps({"closed": "recovered"},
                                            sort_keys=True))
        return {"decision": "terminal-rest", "durable": True,
                "recovered": True}
    raise OwnedFault("E_NO_SUCCESSOR", "declared intent has no roll-forward")
