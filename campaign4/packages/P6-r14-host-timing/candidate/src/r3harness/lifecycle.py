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
RECOVER = "recover"           # overseer incident-recovery pass (bounded)
EXHAUST = "exhaust"           # row 14: BLOCKED -> EXHAUSTED, budget spent

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
    TERMINATE: ("duty", "director"), EXHAUST: ("duty", "director"),
    AMEND: ("director",),
    DECIDE: ("director",), DECISION_TASK: ("duty", "director"),
    RECOVER: ("duty",),
}

# Hard per-pass ceiling from director-decisions.md: controller recovery is at
# most 10 minutes per pass. No budget, cumulative ceiling, or campaign total
# may exceed it. A recorded 20-minute recovery pass (the P2 r2.1
# archive-recheck deviation shape) is rejected here.
HARD_RECOVERY_MAX_S = 600


def _parse_instant(value):
    """Strict aware UTC instant (stdlib-only, pure core).

    Accepts `Z` or numeric `±HH:MM` offsets plus optional fractional
    seconds; equivalent encodings map to the same instant. Naive values
    (no zone), non-strings and malformed fields return None (never raise)
    so callers reject deterministically instead of crashing or falling
    back to lexicographic comparison.
    """
    import datetime as _dt
    import re as _re
    if not isinstance(value, str):
        return None
    m = _re.match(r"^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})"
                  r"(\.\d+)?(Z|[+-]\d{2}:?\d{2})?$", value.strip())
    if not m:
        return None
    zone = m.group(8)
    if not zone:
        return None
    try:
        base = _dt.datetime(int(m.group(1)), int(m.group(2)),
                            int(m.group(3)), int(m.group(4)),
                            int(m.group(5)), int(m.group(6)),
                            int(float(m.group(7) or 0) * 1000000))
        if zone == "Z":
            return base.replace(tzinfo=_dt.timezone.utc)
        digits = zone[1:].replace(":", "")
        if len(digits) != 4:
            return None
        oh, om = int(digits[:2]), int(digits[2:])
        if oh > 23 or om > 59:
            return None
        off = _dt.timedelta(hours=oh, minutes=om)
        res = base - off if zone[0] == "+" else base + off
        if zone[0] not in ("+", "-"):
            return None
        return res.replace(tzinfo=_dt.timezone.utc)
    except (ValueError, OverflowError, ArithmeticError):
        return None


def _passes(budget):
    """Per-pass ceilings with defaults. Fail closed on malformed budget."""
    p = (budget or {}).get("passes", {}) or {}
    try:
        v = int(p.get("verify", {}).get("max_s", 1800))
        r = int(p.get("controller_recovery", {}).get("max_s",
                                                     HARD_RECOVERY_MAX_S))
    except (TypeError, ValueError):
        raise TransitionError("E_BAD_ALLOCATION", "passes ceilings malformed")
    if v <= 0 or r <= 0:
        raise TransitionError("E_BAD_ALLOCATION", "passes ceilings positive")
    return {"verify_max_s": v, "recovery_max_s": r}


def _check_verifier_spend(event, budget):
    """Enforce per-pass verifier allocation. Returns nothing; raises."""
    caps = _passes(budget)
    el = event.get("elapsed_s")
    if not isinstance(el, int) or el < 0:
        raise TransitionError("E_BAD_ALLOCATION",
                              "verifier events need integer elapsed_s")
    cap = event.get("pass_budget_s", budget.get("verifier_s", 1800))
    if not isinstance(cap, int) or cap <= 0:
        raise TransitionError("E_BAD_ALLOCATION", "pass_budget_s malformed")
    if cap > caps["verify_max_s"]:
        raise TransitionError("E_ALLOC_EXCEEDED",
                              "pass budget exceeds per-pass ceiling")
    if el > cap:
        raise TransitionError("E_ALLOC_EXCEEDED",
                              "verifier pass spent beyond its budget")


def _check_grant(value, budget):
    """Validate a new_allocation grant shape. Returns grant seconds."""
    caps = _passes(budget)
    if not isinstance(value, dict):
        raise TransitionError("E_BAD_ALLOCATION",
                              "new_allocation must be an allocation object, "
                              "not free-form")
    g = value.get("grant_s")
    if not isinstance(g, int) or g <= 0:
        raise TransitionError("E_BAD_ALLOCATION", "grant_s positive integer")
    if value.get("granted_by") != "tern":
        raise TransitionError("E_BAD_ALLOCATION",
                              "grants require an attributed director decision")
    if g > caps["verify_max_s"]:
        raise TransitionError("E_ALLOC_EXCEEDED",
                              "grant exceeds per-pass ceiling")
    return g


class TransitionError(Exception):
    def __init__(self, code, detail=""):
        super().__init__("%s: %s" % (code, detail))
        self.code = code
        self.detail = detail


def _require_distinct_verifier(st, event):
    """Author-is-not-verifier invariant (finding #11).

    The producing principal is the seat bound at PUBLISH from trusted
    provenance. Equality is principal identity (seat only): relabelling
    role worker->verifier never defeats the rule, and no caller-supplied
    worker_seat override is consulted. A missing producer identity fails
    closed — it is recoverable only via replay of authentic prior ledger
    events (which re-run PUBLISH), never silently allowed.
    """
    producer = st.get("producer_seat")
    if producer is None:
        raise TransitionError("E_UNKNOWN_PRODUCER",
                              "no authentic producer identity for this "
                              "attempt; verdict refused")
    if event.get("actor", {}).get("seat") == producer:
        raise TransitionError("E_SELF_VERIFY",
                              "producer may not verify own artifacts")


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
        "flight": None,           # outstanding bounded action (worker, then
                                   # verifier) — never a completed attempt
        "producer_seat": None,      # authentic producing principal of the
                                   # CURRENT published attempt, bound at
                                   # PUBLISH from the trusted-ingress actor
                                   # provenance (never a caller-supplied
                                   # worker_seat claim, which is ignored)
        "handoff": None,          # CHECKING awaiting verifier dispatch:
                                  # {owner, deadline}, always bounded
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
            st["flight"] = {"action_id": event.get("action_id"),
                            "owner": event.get("actor", {}).get("seat"),
                            "deadline": event["deadline"]}
            st["handoff"] = None
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
        # Deadline ordering uses validated instants (offsets/fractions
        # normalized); naive/malformed values reject deterministically.
        # Boundary convention preserved: strictly-after expires, equal
        # does not.
        now_i, dl_i = _parse_instant(now), _parse_instant(st.get("deadline"))
        if now_i is None or dl_i is None:
            raise TransitionError("E_BAD_DEADLINE",
                                  "publish needs valid aware instants")
        if now_i > dl_i:
            # Late artifacts are leftovers, not completions (precedence).
            raise TransitionError("E_DEADLINE_EXPIRED", "publish after deadline")
        if not event.get("artifact_hashes"):
            raise TransitionError("E_MISSING_ARTIFACTS", "no hashes")
        # The worker attempt ends here: its flight never survives into
        # CHECKING. Either the verifier's own bounded action is recorded,
        # or an explicitly owned bounded handoff — unbounded silence (an
        # ACTIVE claim with null owner/deadline) is unrepresentable.
        st["flight"] = None
        st["handoff"] = None
        v = event.get("verify")
        if v is not None:
            if not isinstance(v, dict) or not v.get("action_id") or \
                    not v.get("owner") or not v.get("deadline"):
                raise TransitionError("E_BAD_ALLOCATION",
                                      "verify needs action_id/owner/deadline")
            st["flight"] = {"action_id": v["action_id"], "owner": v["owner"],
                            "deadline": v["deadline"]}
        else:
            hd = event.get("handoff_deadline")
            ho = event.get("handoff_owner", "duty")
            if not hd or ho not in ("duty", "director"):
                raise TransitionError(
                    "E_BAD_ALLOCATION",
                    "publication without a dispatched verifier needs an "
                    "explicitly owned (duty/director) bounded handoff")
            st["handoff"] = {"owner": ho, "deadline": hd}
        st["phase"] = "CHECKING"
        st["published"] = event["artifact_hashes"]
        # Producer identity binds here, from the trusted-ingress actor
        # provenance of the actual artifact-producing event. Any
        # caller-supplied worker_seat field is ignored, never trusted.
        # Each publish (including repair re-publish) rebinds its own
        # producer; a new revision starts with None via new_revision.
        st["producer_seat"] = event.get("actor", {}).get("seat")
        return record("checking")
    if typ == VERIFY_PASS:
        if phase != "CHECKING":
            raise TransitionError("E_BAD_TRANSITION", typ)
        _require_distinct_verifier(st, event)
        _check_verifier_spend(event, budget)
        st["verdict"] = "COMPLETE"
        st["finding"] = event.get("finding", "positive")
        st["phase"] = "COMPLETE"
        return record("complete")
    if typ == VERIFY_FAIL:
        if phase != "CHECKING":
            raise TransitionError("E_BAD_TRANSITION", typ)
        _require_distinct_verifier(st, event)
        _check_verifier_spend(event, budget)
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
            if event.get("new_allocation") is not None:
                g = _check_grant(event["new_allocation"], budget)
                st["remaining_verifier_s"] = g
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
    if typ == EXHAUST:
        # Row 14: BLOCKED -> EXHAUSTED, budget/question spent.
        if phase != "BLOCKED":
            raise TransitionError("E_BAD_TRANSITION", typ)
        st["verdict"] = "EXHAUSTED"
        st["why_ended"] = event.get("reason", "budget-spent")
        st["phase"] = "EXHAUSTED"
        return record("exhausted")
    if typ == RECOVER:
        # Overseer incident-recovery pass: bounded per pass, hard-capped.
        # Records only; moves nothing and grants nothing by itself.
        if phase != "BLOCKED":
            raise TransitionError("E_BAD_TRANSITION", typ)
        el = event.get("elapsed_s")
        cap = event.get("pass_budget_s")
        if not isinstance(el, int) or el < 0 or \
                not isinstance(cap, int) or cap <= 0:
            raise TransitionError("E_BAD_ALLOCATION",
                                  "recover needs integer elapsed_s and "
                                  "pass_budget_s")
        if cap > HARD_RECOVERY_MAX_S:
            raise TransitionError(
                "E_ALLOC_EXCEEDED",
                "controller-recovery pass budget exceeds the 10-minute "
                "per-pass ceiling; no cumulative ceiling overrides it")
        if el > cap:
            raise TransitionError("E_ALLOC_EXCEEDED",
                                  "recovery pass spent beyond its budget")
        return record("recovery-recorded")
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
        # The attribution itself must be authoritative: a decision without
        # a reference and reason cannot be recorded — the projection may
        # never supply missing decision data later.
        if phase not in TERMINALS:
            raise TransitionError("E_BAD_TRANSITION", typ + " before verdict")
        # First valid terminal disposition is immutable in a revision:
        # a distinct later DECIDE rejects deterministically BEFORE any
        # mutation (zero state/row change). Existing AMEND behavior is
        # retained (separate branch); exact same-event replay stays
        # idempotent via the store's seen-event path, never reaching here
        # as a new decision.
        if st.get("disposition") is not None:
            raise TransitionError("E_ALREADY_DECIDED",
                                  "terminal disposition immutable; distinct "
                                  "later decide rejected")
        disp = event.get("disposition") or {}
        if disp.get("kind") not in ("successor_opened", "question_answered",
                                    "budget_spent", "blocked"):
            raise TransitionError("E_MISSING_DISPOSITION", "enumerable kind?")
        for field in ("decision_ref", "reason"):
            if not isinstance(disp.get(field), str) or not disp[field]:
                raise TransitionError("E_MISSING_DISPOSITION",
                                      "attributed decision needs " + field)
        st["disposition"] = disp
        st["decision_task"] = None
        return record("closed-" + disp["kind"])
    raise TransitionError("E_UNKNOWN_EVENT", typ)
