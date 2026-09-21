"""Replay-safe FAKE dispatch. No agents, no wake/stop/Signal, no timers.

An action is durably started (ledger START event) before the fake executor
runs. Crash-after-start reconciles the SAME action id: acknowledge it or
interrupt it — never a new worker attempt. Acknowledged vs intended delivery
are recorded distinctly.
"""
from __future__ import annotations


class FakeExecutor:
    """Deterministic stand-in for agent execution.

    ``run(action)`` returns canned artifacts keyed by action_id. It records
    nothing itself; the caller commits ledger events.
    """

    def __init__(self, artifacts=None):
        self.artifacts = artifacts or {}
        self.runs = []  # action_ids executed (for no-duplicate assertions)

    def run(self, action):
        self.runs.append(action["action_id"])
        return self.artifacts.get(action["action_id"],
                                  {"output_hash": "sha256:fake-" +
                                   action["action_id"]})


def dispatch(store, action, executor, budget=None, now=""):
    """Durable-start-then-run fake dispatch.

    If ``action_id`` already has an acknowledged START, this is a redelivery:
    return ("redelivered-same-action", True) without re-running.
    """
    status = store.acks.get(action["action_id"])
    if status == "acknowledged":
        return "redelivered-same-action", True
    start = {"event_id": action["action_id"] + "-start",
             "question_id": action["question_id"],
             "revision": action.get("revision", 1),
             "type": "start",
             "actor": {"seat": "cairn", "role": "duty"},
             "at": now or action.get("at", ""),
             "deadline": action["deadline"],
             "action_id": action["action_id"],
             "acknowledged": False}
    outcome, dup = store.append(start, budget)
    if dup:
        return outcome, True
    artifacts = executor.run(action)
    # Acknowledgement is delivery bookkeeping on the same action id: it
    # marks the durable start acknowledged without emitting any new
    # lifecycle event (hence no new attempt, ever, on redelivery).
    store.set_ack(action["action_id"], "acknowledged")
    return {"start": outcome, "artifacts": artifacts}, False


def reconcile_after_crash(store, action):
    """Crash after durable start, before acknowledgement.

    Returns the same action for re-drive; the ledger already holds the
    START, so re-drive redelivers rather than creating attempt+1.
    """
    if action["action_id"] + "-start" in store.seen_events:
        return {"action": action, "attempt_delta": 0,
                "note": "same-action-redelivery"}
    return {"action": action, "attempt_delta": 0, "note": "never-started"}
