"""Deterministic lifecycle transition core (P3-core-validator).

Pure transition function over explicit events. No I/O, no model calls, no
clock reads: the caller supplies ``now`` (fake clock in tests). All
rejections fail closed with deterministic error codes.
"""
from __future__ import annotations

STATES = ("DRAFT", "ADMITTED", "REGISTERED", "RUNNING", "CHECKING",
          "REPAIR_ALLOWED", "BLOCKED")
TERMINALS = ("COMPLETE", "EXHAUSTED", "TERMINATED", "SUPERSEDED")
PHASES = STATES + TERMINALS
ROLES = ("director", "reader", "worker", "verifier", "duty")

# event types understood by the core
START = "start"               # controller records start before dispatch
PUBLISH = "publish"           # worker publishes artifacts
VERIFY_PASS = "verify_pass"   # verifier receipt: evidence satisfies
VERIFY_FAIL = "verify_fail"   # verifier receipt: defect found
ACCEPT = "accept"             # director acceptance
WITHHOLD = "withhold"         # director acceptance withheld
INTERRUPT = "interrupt"       # deadline expiry / lost process / failed wake
RESOLVE = "resolve"           # recorded resolution of a block
DEFER = "defer"
TERMINATE = "terminate"
AMEND = "amend"               # new revision: old -> SUPERSEDED
ADMIT = "admit"               # reader accepts contract
REJECT = "reject"             # one bounded rejection
AUTHORIZE = "authorize"       # authorization + versioned contract recorded
ALLOC_REPAIR = "alloc_repair"  # repair allocation recorded and launched
DECIDE = "decide"             # director boundary disposition (terminal close)
DECISION_TASK = "decision_task"  # open bounded director-decision task

# who may emit which event (role, not seat identity proof)
PERMITTED = {
    ADMIT: ("reader",), REJECT: ("reader",),
    AUTHORIZE: ("director", "duty"),
    START: ("duty",), ALLOC_REPAIR: ("duty",),
    PUBLISH: ("worker",),
    VERIFY_PASS: ("verifier",), VERIFY_FAIL: ("verifier",),
    ACCEPT: ("director",), WITHHOLD: ("director",),
    INTERRUPT: ("duty", "director"),
    RESOLVE: ("duty", "director"), DEFER: ("duty", "director"),
    TERMINATE: ("duty", "director"),
    AMEND: ("director",),
    DECIDE: ("director",), DECISION_TASK: ("duty", "director"),
}


class TransitionError(Exception):
    def __init__(self, code, detail=""):
        super().__init__("%s: %s" % (code, detail))
        self.code = code
        self.detail = detail


def new_revision(question_id):
    """Initial per-revision lifecycle record."""
    return {
        "question_id": question_id,
        "revision": 1,
        "phase": "DRAFT",
        "attempt": 0,
        "repair_used": False,
        "blocked": None,          # {phase, attempt, remaining_verifier_s or None}
        "verdict": None,          # COMPLETE/... once rows 7/9a/13/14 fire
        "decision_task": None,    # {task_id, owner, deadline}
        "disposition": None,      # director DECIDE payload once committed
        "history": [],            # append-only event ids applied
    }


def _require_role(event):
    allowed = PERMITTED.get(event["type"])
    if allowed is None:
        raise TransitionError("E_UNKNOWN_EVENT", event.get("type", "?"))
    role = event.get("actor", {}).get("role")
    if role not in allowed:
        raise TransitionError("E_UNAUTHORIZED",
                              "%s may not emit %s" % (role, event["type"]))


def apply(state, event, now, budget):
    """Apply one event; return (new_state, outcome).

    ``budget``: {"attempts": 1, "repairs": 1, "verifier_s": int}.
    ``now``: comparable timestamp (ISO string). Fail closed on any violation.
    """
    _require_role(event)
    st = dict(state)
    hist = list(st["history"])
    typ = event["type"]
    phase = st["phase"]

    def record(outcome):
        hist.append(event["event_id"])
        st["history"] = hist
        return st, outcome

    if phase in TERMINALS and typ not in (AMEND, DECIDE, DECISION_TASK):
        # Row 16: terminals have no outgoing execution transition.
        # AMEND bumps the revision; DECIDE/DECISION_TASK commit the
        # boundary (validation-level close, not an execution transition).
        raise TransitionError("E_TERMINAL", phase)

    if typ == ADMIT:
        if phase != "DRAFT":
            raise TransitionError("E_BAD_TRANSITION", typ)
        st["phase"] = "ADMITTED"
        return record("admitted")
    if typ == REJECT:
        if phase != "DRAFT":
            raise TransitionError("E_BAD_TRANSITION", typ)
        return record("rejected-bounded")
    if typ == AUTHORIZE:
        if phase != "ADMITTED":
            raise TransitionError("E_BAD_TRANSITION", typ)
        st["phase"] = "REGISTERED"
        return record("registered")
    if typ == START:
        # Row 4/10: start recorded before dispatch; attempts counted here.
        if phase == "REGISTERED":
            if st["attempt"] >= budget["attempts"]:
                raise TransitionError("E_NO_ALLOCATION", "attempts spent")
            if event.get("deadline") is None:
                raise TransitionError("E_NO_DEADLINE", "start needs deadline")
            st["attempt"] += 1
            st["phase"] = "RUNNING"
            st["deadline"] = event["deadline"]
            return record("running")
        if phase == "REPAIR_ALLOWED":
            st["attempt"] += 1
            st["phase"] = "RUNNING"
            st["deadline"] = event.get("deadline")
            if st["deadline"] is None:
                raise TransitionError("E_NO_DEADLINE", "repair needs deadline")
            return record("running-repair")
        raise TransitionError("E_BAD_TRANSITION", typ)
    if typ == PUBLISH:
        if phase != "RUNNING":
            raise TransitionError("E_BAD_TRANSITION", typ)
        if now > st.get("deadline", ""):
            # Late artifacts are leftovers, not completions (precedence).
            raise TransitionError("E_DEADLINE_EXPIRED", "publish after deadline")
        if not event.get("artifact_hashes"):
            raise TransitionError("E_MISSING_ARTIFACTS", "no hashes")
        st["phase"] = "CHECKING"
        st["published"] = event["artifact_hashes"]
        return record("checking")
    if typ == VERIFY_PASS:
        if phase != "CHECKING":
            raise TransitionError("E_BAD_TRANSITION", typ)
        if event.get("actor", {}).get("seat") == state.get("worker_seat"):
            raise TransitionError("E_SELF_VERIFY",
                                  "worker may not verify own artifacts")
        st["verdict"] = "COMPLETE"
        st["finding"] = event.get("finding", "positive")
        st["phase"] = "COMPLETE"
        return record("complete")
    if typ == VERIFY_FAIL:
        if phase != "CHECKING":
            raise TransitionError("E_BAD_TRANSITION", typ)
        if event.get("actor", {}).get("seat") == state.get("worker_seat"):
            raise TransitionError("E_SELF_VERIFY",
                                  "worker may not verify own artifacts")
        if event.get("eligible_repair") and not st["repair_used"]:
            if st["repair_used"]:
                raise TransitionError("E_NO_ALLOCATION", "repair spent")
            st["phase"] = "REPAIR_ALLOWED"
            return record("repair-allowed")
        # Row 9a: fail with no eligible allocation left -> EXHAUSTED.
        st["verdict"] = "EXHAUSTED"
        st["why_ended"] = event.get("reason", "failed-verification-no-allocation")
        st["phase"] = "EXHAUSTED"
        return record("exhausted")
    if typ == ACCEPT:
        # Director acceptance of a COMPLETE verdict (freeze gate input).
        if phase != "COMPLETE":
            raise TransitionError("E_BAD_TRANSITION", typ)
        return record("accepted")
    if typ == WITHHOLD:
        # Director withholds acceptance -> row 9a exhaustion (r1 shape).
        if phase not in ("COMPLETE", "CHECKING"):
            raise TransitionError("E_BAD_TRANSITION", typ)
        st["verdict"] = "EXHAUSTED"
        st["why_ended"] = event.get("reason", "acceptance-withheld")
        st["phase"] = "EXHAUSTED"
        return record("exhausted")
    if typ == ALLOC_REPAIR:
        if phase != "REPAIR_ALLOWED":
            raise TransitionError("E_BAD_TRANSITION", typ)
        if st["repair_used"]:
            raise TransitionError("E_NO_ALLOCATION", "repair already spent")
        st["repair_used"] = True
        return record("repair-allocated")
    if typ == INTERRUPT:
        # Rows 6/9: deadline expiry, lost process, failed wake.
        if phase not in ("RUNNING", "CHECKING"):
            raise TransitionError("E_BAD_TRANSITION", typ)
        st["blocked"] = {
            "phase": phase,
            "attempt": st["attempt"],
            "remaining_verifier_s": event.get("remaining_verifier_s"),
        }
        st["block_reason"] = event.get("reason", "interrupted")
        st["phase"] = "BLOCKED"
        return record("blocked")
    if typ == RESOLVE:
        if phase != "BLOCKED":
            raise TransitionError("E_BAD_TRANSITION", typ)
        origin = (st.get("blocked") or {}).get("phase", "RUNNING")
        if origin == "CHECKING":
            # Row 11: verification block returns to CHECKING, same attempt,
            # no worker launch. Expired verifier allocation needs a grant.
            rem = (st.get("blocked") or {}).get("remaining_verifier_s")
            if rem is not None and rem <= 0 and not event.get("new_allocation"):
                raise TransitionError("E_NO_ALLOCATION",
                                      "expired verification needs a grant")
            st["phase"] = "CHECKING"
        elif origin == "RUNNING":
            st["phase"] = "RUNNING"
        else:
            st["phase"] = "REGISTERED"
        st["blocked"] = None
        return record("resumed-" + st["phase"].lower())
    if typ == DEFER:
        if phase != "BLOCKED":
            raise TransitionError("E_BAD_TRANSITION", typ)
        return record("deferred-owned")
    if typ == TERMINATE:
        if phase != "BLOCKED":
            raise TransitionError("E_BAD_TRANSITION", typ)
        st["verdict"] = "TERMINATED"
        st["phase"] = "TERMINATED"
        return record("terminated")
    if typ == AMEND:
        # Row 15: old revision -> SUPERSEDED; caller opens the new revision.
        # Budgets continue under question_id; history preserved.
        st["phase"] = "SUPERSEDED"
        st["superseded_by"] = event.get("new_revision")
        return record("superseded")
    if typ == DECISION_TASK:
        if phase not in TERMINALS:
            raise TransitionError("E_BAD_TRANSITION", typ + " before verdict")
        if st.get("disposition") is not None:
            raise TransitionError("E_BAD_TRANSITION", "already closed")
        st["decision_task"] = {
            "task_id": event["event_id"],
            "owner": "director",
            "deadline": event["deadline"],
        }
        return record("decision-pending")
    if typ == DECIDE:
        # Global atomic boundary rule: verdict rows cannot close alone.
        if phase not in TERMINALS:
            raise TransitionError("E_BAD_TRANSITION", typ + " before verdict")
        disp = event.get("disposition") or {}
        if disp.get("kind") not in ("successor_opened", "question_answered",
                                    "budget_spent", "blocked"):
            raise TransitionError("E_MISSING_DISPOSITION", "enumerable kind?")
        st["disposition"] = disp
        st["decision_task"] = None
        return record("closed-" + disp["kind"])
    raise TransitionError("E_UNKNOWN_EVENT", typ)
