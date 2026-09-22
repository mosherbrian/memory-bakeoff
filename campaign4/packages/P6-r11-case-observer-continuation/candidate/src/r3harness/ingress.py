"""Trusted timestamp ingress: the single accepted external write route.

The trusted boundary owns receipt time, actor attribution and deadline
derivation:

- ``recorded_at`` is obtained from the injected clock (production:
  :class:`HostClock` reading host UTC; tests: injected fakes) at append
  time. Caller/seat supplied ``recorded_at``, ``receipt`` or ``_trusted``
  fields are rejected as forged. The legacy ``at`` field, if present, is
  overwritten with ``recorded_at`` and the caller value is preserved only
  inside the receipt as ``caller_at_ignored`` for transparency.
- D1: actor attribution is bound at this boundary from an independently
  supplied trusted context (the ``actor`` argument passed by the calling
  adapter, never the event claim). Any ``actor`` key inside the claim —
  including ``record_terminal`` and atomic subevents — is rejected as
  forged attribution. This is a trust-boundary rule, not OS identity
  isolation.
- D2: every new execution or decision/handoff deadline is derived from or
  checked against an explicit authorized duration or pinned grant, using
  the actual phase/action read from authoritative ledger state — never
  optional caller hints (``phase_hint`` claims are rejected). No permissive
  fallback substitutes for explicit authorization. A distant deadline
  covered by a real pinned grant is valid, never occurrence skew.
- Untrusted source-reported ``occurred_at`` plus ``provenance`` are kept
  separately and validated against ``recorded_at`` with a finite justified
  future-skew tolerance (:data:`FUTURE_SKEW_TOLERANCE_S`). Excessively future
  or malformed claims are quarantined (never touch lifecycle); backdated
  claims are retained with both times but cannot retro-authorize work.
- D3: host UTC plus in-process monotonic elapsed time detect clock
  discontinuity beyond :data:`DISCONTINUITY_THRESHOLD_S`; the owned response
  quarantines the write for bounded reconciliation without touching
  deadlines. Every ingress lifetime opens a genuinely new epoch (unique
  token plus persisted boot counter); monotonic counters are never compared
  across epochs. Restart reuses persisted UTC/grants; backward UTC at reopen
  requires bounded owned reconciliation (no silent extension, no invented
  certainty).
- Ledger validation stays authoritative AFTER ingress verifies the write.

``store.append`` / ``store.record_terminal`` are explicitly INTERNAL
low-level APIs, not an alternate accepted external route. The only accepted
external route is :class:`TrustedIngress.append` /
:meth:`TrustedIngress.record_terminal`.
"""
from __future__ import annotations

import json
import re as _re
import secrets
import time
from datetime import datetime, timezone

import validator as validator_mod
import lifecycle as lifecycle_mod

# Occurred claims must carry an explicit UTC designator (Z or numeric
# offset). Naive instants are quarantined at this boundary even though the
# lower-level validator tolerates them: trusted receipt time is never
# mixed with zone-ambiguous claims.
_EXPLICIT_ZONE_RE = _re.compile(r"(Z|[+-]\d{2}:?\d{2})$")

# Finite justified tolerances (see interface.md for justification).
# 120 s bounds honest NTP offset (<1 s typical) plus provisioning and
# delivery latency (seconds); the observed 32-minute future-dating exceeds
# it 16x, so real skew passes while manual future stamps are caught.
FUTURE_SKEW_TOLERANCE_S = 120
# 60 s wall-vs-monotonic divergence catches manual clock steps and large NTP
# corrections while tolerating ordinary drift and scheduling jitter.
DISCONTINUITY_THRESHOLD_S = 60

# Authorized per-action durations (seconds) for deadline derivation.
AUTHORIZED_DURATIONS = {
    "run": 3600,
    "verify": 1800,
    "handoff": 1800,
    "decision": 86400,
}

# Bound for nested/future deadlines without an explicit covering grant:
# a full day covers every legitimate rehearsal window while the 2099 probe
# (decades out, grantless) is rejected. Distant deadlines with a real
# pinned grant are always allowed.
NESTED_DEADLINE_CAP_S = 86400

# Independently trusted actor contexts (seats/roles the boundary accepts
# from its calling adapter — never from the event claim).
TRUSTED_SEATS = ("tern", "corvid", "kiln", "cairn")
TRUSTED_ROLES = ("director", "reader", "worker", "verifier", "duty")

TERMINALS = ("COMPLETE", "EXHAUSTED", "TERMINATED", "SUPERSEDED")

# Event type -> allowed actual ledger phases (authoritative state).
_PHASE_FOR = {
    "admit": {"__absent__", "DRAFT"},
    "reject": {"DRAFT"},
    "authorize": {"ADMITTED"},
    "start": {"REGISTERED", "REPAIR_ALLOWED"},
    "publish": {"RUNNING"},
    "verify_pass": {"CHECKING"},
    "verify_fail": {"CHECKING"},
    "accept": {"COMPLETE"},
    "withhold": {"COMPLETE", "CHECKING"},
    "alloc_repair": {"REPAIR_ALLOWED"},
    "interrupt": {"RUNNING", "CHECKING"},
    "resolve": {"BLOCKED"},
    "defer": {"BLOCKED"},
    "terminate": {"BLOCKED"},
    "exhaust": {"BLOCKED"},
    "recover": {"BLOCKED"},
    "decide": set(TERMINALS),
    "decision_task": set(TERMINALS),
}

# Grant phase binding: which grant phase authorizes which deadline route.
_GRANT_PHASE_FOR_ROUTE = {
    "start": (None, "run"),
    "verify": ("verify",),
    "handoff": ("handoff",),
    "hold": ("verify", "decision"),
    "decision": ("decision",),
}


class IngressError(Exception):
    def __init__(self, code, detail="", owner="cairn"):
        super().__init__("%s: %s" % (code, detail))
        self.code = code
        self.detail = detail
        self.owner = owner


class Quarantined(IngressError):
    """Owned quarantine evidence: the claim never touched lifecycle."""

    def __init__(self, code, detail, evidence, owner="cairn"):
        super().__init__(code, detail, owner)
        self.evidence = evidence


class HostClock:
    """Production clock adapter: reads host UTC time. No clock change."""

    def utc_now(self):
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    @property
    def now(self):
        """Read-only view for driver code paths that read clock.now."""
        return self.utc_now()

    def monotonic(self):
        return time.monotonic()


class FakeTestClock:
    """Injected test clock: explicit UTC instant plus monotonic seconds."""

    def __init__(self, start="2026-09-21T12:00:00Z"):
        self.now = start
        self.mono = 1000.0

    def utc_now(self):
        return self.now

    def monotonic(self):
        return self.mono

    def advance(self, utc_seconds=0, mono_seconds=None):
        import datetime as _dt
        cur = validator_mod._instant(self.now)
        nxt = cur + _dt.timedelta(seconds=utc_seconds)
        self.now = nxt.strftime("%Y-%m-%dT%H:%M:%SZ")
        self.mono += utc_seconds if mono_seconds is None else mono_seconds
        return self.now


def _as_instant(value):
    return validator_mod._instant(value)


def _skew_s(occurred, recorded):
    return (occurred - recorded).total_seconds()


class TrustedIngress:
    """Single accepted external write route into the ledger store."""

    def __init__(self, store, clock, kv_put, kv_get, epoch=None):
        self.store = store
        self.clock = clock
        self._kv_put = kv_put
        self._kv_get = kv_get
        try:
            boot = int(self._kv_get("ingress-boot") or "0") + 1
        except (TypeError, ValueError):
            boot = 1
        self._kv_put("ingress-boot", str(boot))
        # Genuinely new epoch per ingress lifetime: unique token plus a
        # persisted boot counter. Same clock values never reproduce it, so
        # cross-process monotonic values are never comparable — and never
        # compared.
        self.epoch = epoch or ("epoch-%d-%s" % (boot, secrets.token_hex(8)))
        self._kv_put("ingress-epoch", self.epoch)
        self._ambiguous = None
        last = self._kv_get("ingress-last")
        if last:
            try:
                prev = json.loads(last)
            except ValueError:
                prev = None
            if prev:
                self._check_restart_continuity(prev)
        self._last = None  # in-epoch tracking starts empty every lifetime

    # -- restart continuity (persisted UTC facts only) ---------------------
    def _check_restart_continuity(self, prev):
        now_raw = self.clock.utc_now()
        now, then = _as_instant(now_raw), _as_instant(prev.get("utc"))
        if now is None or then is None:
            self._ambiguous = {
                "owner": "cairn", "previous_utc": prev.get("utc"),
                "current_utc": now_raw,
                "response": "unreadable persisted clock fact; bounded "
                             "reconciliation required; deadlines unchanged"}
        elif now < then:
            # Backward UTC at reopen: ambiguous continuity. Writes wait for
            # bounded owned reconciliation; nothing is extended or reset.
            self._ambiguous = {
                "owner": "cairn", "previous_utc": prev.get("utc"),
                "current_utc": now_raw,
                "response": "backward UTC at reopen; bounded "
                             "reconciliation required; deadlines unchanged"}
        # Forward UTC (even a large gap) proceeds: elapsed wall time never
        # extends ledger deadlines, and overdue work stays overdue.

    def _require_continuity(self):
        if self._ambiguous is not None:
            raise Quarantined("E_AMBIGUOUS_RESTART",
                              "ambiguous restart clock continuity",
                              dict(self._ambiguous))

    # -- in-epoch clock continuity -----------------------------------------
    def _check_continuity(self, recorded):
        mono = self.clock.monotonic()
        if self._last is not None:
            # Same lifetime by construction (fresh _last per epoch): the
            # comparison below is always within one process epoch.
            prev_utc = _as_instant(self._last["utc"])
            wall = (recorded - prev_utc).total_seconds() \
                if prev_utc else 0.0
            drift = abs(wall - (mono - self._last["mono"]))
            if drift > DISCONTINUITY_THRESHOLD_S:
                raise Quarantined(
                    "E_DISCONTINUITY",
                    "wall-vs-monotonic drift %.1fs exceeds %ds" %
                    (drift, DISCONTINUITY_THRESHOLD_S),
                    {"owner": "cairn", "epoch": self.epoch,
                     "wall_delta_s": wall,
                     "mono_delta_s": mono - self._last["mono"],
                     "response": "bounded reconciliation required; "
                                 "deadlines unchanged"})
        self._last = {"epoch": self.epoch, "utc": recorded.strftime(
            "%Y-%m-%dT%H:%M:%SZ"), "mono": mono}
        self._kv_put("ingress-last", json.dumps(self._last, sort_keys=True))

    def reconcile_clock(self, note, owner="cairn"):
        """Bounded reconciliation after a discontinuity or ambiguous
        restart: opens a fresh epoch with an owned note. Never resets or
        lengthens deadlines."""
        self.epoch = "epoch-reconciled-%s-%s" % (
            self.clock.utc_now(), secrets.token_hex(4))
        self._kv_put("ingress-epoch", self.epoch)
        self._kv_put("ingress-reconcile-note",
                     json.dumps({"owner": owner, "note": note,
                                 "at": self.clock.utc_now()},
                                sort_keys=True))
        self._last = None
        self._ambiguous = None
        return self.epoch

    # -- D1: attribution binding -------------------------------------------
    def _bind_actor(self, claim, actor, where):
        if "actor" in claim:
            raise IngressError(
                "E_FORGED_ATTRIBUTION",
                "caller actor claim rejected at %s; authority comes only "
                "from the trusted adapter context" % where,
                owner="tern")
        if not isinstance(actor, dict) or \
                actor.get("seat") not in TRUSTED_SEATS or \
                actor.get("role") not in TRUSTED_ROLES:
            raise IngressError("E_UNTRUSTED_ACTOR",
                               "adapter must supply a trusted seat/role")
        return {"seat": actor["seat"], "role": actor["role"]}

    # -- D2: authoritative phase -------------------------------------------
    def _actual_phase(self, qid, revision):
        rec = self.store.revisions.get((qid, revision))
        if rec is None:
            return "__absent__"
        return rec.get("phase")

    def _check_phase(self, typ, qid, revision):
        allowed = _PHASE_FOR.get(typ)
        if allowed is None:
            return  # unknown types fail later, ledger-authoritatively
        if typ == "amend":
            return
        actual = self._actual_phase(qid, revision)
        if actual not in allowed:
            raise IngressError(
                "E_PHASE_MISMATCH",
                "%s not allowed in actual phase %s" % (typ, actual))

    # -- claim validation ----------------------------------------------------
    def _receipt(self, claim, recorded):
        for forged in ("recorded_at", "receipt", "_trusted", "phase_hint"):
            if forged in claim:
                raise IngressError(
                    "E_FORGED_RECEIPT" if forged != "phase_hint"
                    else "E_FORGED_HINT",
                    "caller may not supply %s; actual phase comes from "
                    "authoritative ledger state" % forged
                    if forged == "phase_hint" else
                    "caller may not supply %s" % forged,
                    owner="tern")
        occurred_raw = claim.pop("occurred_at", None)
        provenance = claim.pop("provenance", None)
        occurred = None
        skew = None
        if occurred_raw is not None:
            occurred = _as_instant(occurred_raw)
            if occurred is None or not _EXPLICIT_ZONE_RE.search(
                    str(occurred_raw).strip()):
                raise Quarantined(
                    "E_BAD_OCCURRED",
                    "occurred_at is not a supported UTC instant "
                    "(explicit zone required)",
                    {"owner": "cairn", "claimed": occurred_raw})
            skew = _skew_s(occurred, recorded)
            if skew > FUTURE_SKEW_TOLERANCE_S:
                raise Quarantined(
                    "E_SKEW_EXCEEDED",
                    "claimed occurrence %.0fs in the future exceeds %ds" %
                    (skew, FUTURE_SKEW_TOLERANCE_S),
                    {"owner": "cairn", "claimed": occurred_raw,
                     "recorded_at": recorded.strftime(
                         "%Y-%m-%dT%H:%M:%SZ")})
        caller_at = claim.pop("at", None)
        receipt = {
            "recorded_at": recorded.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "occurred_at": occurred.strftime("%Y-%m-%dT%H:%M:%SZ")
            if occurred else None,
            "provenance": provenance,
            "skew_s": skew,
            "epoch": self.epoch,
        }
        if caller_at is not None:
            receipt["caller_at_ignored"] = caller_at
        return receipt

    def _grant_cover(self, route, deadline_instant, recorded, grants,
                     grant_ref):
        """A nested deadline is authorized iff inside the cap or covered by
        a pinned grant whose phase binds that route. Distant pinned
        deadlines are valid; grantless far-future ones are not."""
        import datetime as _dt
        if deadline_instant is None:
            raise IngressError("E_BAD_DEADLINE",
                               "deadline not a UTC instant")
        if deadline_instant < recorded:
            raise IngressError("E_BAD_DEADLINE",
                               "deadline before trusted receipt")
        if deadline_instant <= recorded + _dt.timedelta(
                seconds=NESTED_DEADLINE_CAP_S):
            return None
        grant = (grants or {}).get(grant_ref or "")
        if grant is None:
            raise IngressError(
                "E_DEADLINE_UNAUTHORIZED",
                "deadline beyond the authorized window needs a pinned "
                "covering grant")
        gdl = _as_instant(grant.get("absolute_deadline"))
        if gdl is None or gdl < deadline_instant:
            raise IngressError("E_DEADLINE_UNAUTHORIZED",
                               "covering grant does not cover the deadline")
        if grant.get("phase") not in _GRANT_PHASE_FOR_ROUTE[route]:
            raise IngressError("E_GRANT_MISMATCH",
                               "grant phase does not bind route " + route)
        return grant_ref

    def _nested_deadline(self, claim, recorded, grants):
        """Check every nested new deadline on non-start claims (verify /
        handoff). Caller deadlines are never extended silently: they must
        be well-formed, unexpired, and authorized."""
        v = claim.get("verify")
        if isinstance(v, dict) and v.get("deadline") is not None:
            dl = _as_instant(v["deadline"])
            self._grant_cover("verify", dl, recorded, grants,
                              claim.get("verify_grant_ref"))
        hd = claim.get("handoff_deadline")
        if hd is not None:
            dl = _as_instant(hd)
            self._grant_cover("handoff", dl, recorded, grants,
                              claim.get("handoff_grant_ref"))

    def _start_deadline(self, claim, recorded, grants, qid, revision):
        grant_ref = claim.pop("grant_ref", None)
        duration = claim.pop("duration_s", None)
        if "deadline" in claim:
            raise IngressError("E_DEADLINE_FORGE",
                               "caller may not supply a start deadline",
                               owner="tern")
        if grant_ref is not None:
            grant = (grants or {}).get(grant_ref)
            if grant is None:
                raise IngressError("E_GRANT_UNKNOWN",
                                   "no such pinned grant")
            gdl = _as_instant(grant.get("absolute_deadline"))
            if gdl is None:
                raise IngressError("E_GRANT_MALFORMED",
                                   "grant deadline malformed")
            if gdl < recorded:
                raise IngressError("E_GRANT_EXPIRED",
                                   "grant deadline already past")
            if grant.get("phase") not in _GRANT_PHASE_FOR_ROUTE["start"]:
                raise IngressError("E_GRANT_MISMATCH",
                                   "grant phase does not authorize a start")
            claim["deadline"] = grant["absolute_deadline"]
            claim["grant_ref"] = grant_ref
            return grant["absolute_deadline"]
        # No permissive fallback: a start needs explicit authorization.
        if duration is None:
            raise IngressError("E_NO_AUTHORIZATION",
                               "start needs an explicit duration_s or "
                               "pinned grant_ref")
        if not isinstance(duration, int) or duration <= 0:
            raise IngressError("E_BAD_DURATION",
                               "duration positive integer seconds")
        cap = (grants or {}).get("__allocation_cap_s__", 7200)
        if duration > cap:
            raise IngressError("E_ALLOC_EXCEEDED",
                               "duration exceeds allocation")
        import datetime as _dt
        dl = recorded + _dt.timedelta(seconds=duration)
        claim["deadline"] = dl.strftime("%Y-%m-%dT%H:%M:%SZ")
        claim["duration_s"] = duration
        return claim["deadline"]

    # Exactly one supported atomic operation per call. Any other shape —
    # mixed hold+decide in any key order, unknown keys, empty form,
    # non-dict or malformed values — is rejected here, before any
    # lifecycle/event mutation, so downstream code can never prefer a
    # different subevent than the one this boundary validated.
    _ATOMIC_FORMS = (frozenset(("hold",)), frozenset(("decide",)))

    def _check_atomic(self, atomic, recorded, grants, atomic_actor):
        if atomic is None:
            return None
        if not isinstance(atomic, dict):
            raise IngressError("E_BAD_ATOMIC",
                               "atomic must be a supported operation object")
        keys = frozenset(atomic.keys())
        if "hold" in keys and "decide" in keys:
            raise IngressError("E_MIXED_ATOMIC",
                               "mixed hold+decide is not a supported atomic "
                               "form",
                               owner="tern")
        op_keys = keys - frozenset(("grant_ref",))
        if op_keys not in self._ATOMIC_FORMS:
            raise IngressError("E_BAD_ATOMIC",
                               "unsupported atomic form: %s" % sorted(keys))
        if "hold" in atomic:
            if atomic_actor is not None:
                raise IngressError("E_FORGED_ATTRIBUTION",
                                   "atomic hold attribution is store-fixed",
                                   owner="tern")
            dl = _as_instant(atomic["hold"])
            self._grant_cover("hold", dl, recorded, grants,
                              atomic.get("grant_ref"))
            return None
        sub = atomic["decide"]
        if not isinstance(sub, dict):
            raise IngressError("E_BAD_ATOMIC", "decide malformed")
        if "actor" in sub:
            raise IngressError("E_FORGED_ATTRIBUTION",
                               "atomic decide actor must come from the "
                               "trusted context",
                               owner="tern")
        if atomic_actor is None:
            raise IngressError("E_UNTRUSTED_ACTOR",
                               "atomic decide needs a trusted actor")
        self._bind_actor({}, atomic_actor, "atomic decide")
        return sub

    def _stamp_atomic_decide(self, sub, recorded, atomic_actor):
        """Stamp an atomic decide subevent: trusted attribution and trusted
        timestamping, same write instant — no unstamped subevent bypass."""
        stamped = dict(sub)
        stamped["actor"] = self._bind_actor({}, atomic_actor,
                                            "atomic decide")
        receipt = self._receipt(stamped, recorded)
        stamped["at"] = receipt["recorded_at"]
        stamped["receipt"] = receipt
        stamped["_trusted"] = True
        return stamped

    def _check_atomic_pair(self, verdict_claim, stamped_sub, recorded,
                           budget):
        """Validate an atomic verdict+decide pair: matching package/revision
        and decide type, and the disposition validated against the
        POST-verdict phase (simulated via the pure core, read-only). A
        verdict that does not land terminal cannot carry a disposition;
        invalid pairs are rejected before any write, so no partial rows."""
        if stamped_sub.get("type") != "decide":
            raise IngressError("E_BAD_ATOMIC",
                               "atomic subevent must be type decide")
        for field in ("question_id", "revision"):
            want = verdict_claim.get(
                field, 1 if field == "revision" else None)
            if stamped_sub.get(field, 1 if field == "revision" else None) \
                    != want:
                raise IngressError("E_BAD_ATOMIC",
                                   "atomic pair package/revision mismatch")
        post = self._simulate_post_phase(verdict_claim, recorded, budget)
        if post is None:
            return  # simulation failed; store rejects ledger-authoritatively
        if post not in TERMINALS:
            raise IngressError(
                "E_PHASE_MISMATCH",
                "atomic disposition needs a terminal post-verdict phase, "
                "verdict lands %s" % post)

    def _simulate_post_phase(self, verdict_claim, recorded, budget):
        """Read-only post-verdict phase via the pure core, or None if the
        verdict itself would not apply (left to authoritative rejection)."""
        try:
            qid = verdict_claim.get("question_id")
            rev = verdict_claim.get("revision", 1)
            base = self.store.revisions.get((qid, rev))
            if base is None:
                base = lifecycle_mod.new_revision(qid)
                base["revision"] = rev
            b = budget or {"attempts": 1, "repairs": 1, "verifier_s": 1800,
                           "passes": {"verify": {"max_s": 1800},
                                      "controller_recovery": {"max_s": 600}}}
            new_rec, _ = lifecycle_mod.apply(
                dict(base), dict(verdict_claim),
                verdict_claim.get("at"), b)
            return new_rec.get("phase")
        except lifecycle_mod.TransitionError:
            return None

    # -- accepted external route -------------------------------------------
    def _stamped(self, event, recorded, grants, actor, where, atomic_actor):
        claim = dict(event)
        bound = self._bind_actor(claim, actor, where)
        receipt = self._receipt(claim, recorded)
        typ = claim.get("type")
        qid, rev = claim.get("question_id"), claim.get("revision", 1)
        self._check_phase(typ, qid, rev)
        if typ == "start":
            self._start_deadline(claim, recorded, grants, qid, rev)
        else:
            self._nested_deadline(claim, recorded, grants)
        claim["actor"] = bound
        claim["at"] = receipt["recorded_at"]
        claim["receipt"] = receipt
        claim["_trusted"] = True
        return claim

    def _now(self):
        recorded = _as_instant(self.clock.utc_now())
        if recorded is None:  # pragma: no cover - defensive
            raise IngressError("E_CLOCK", "clock did not return UTC")
        return recorded

    def append(self, event, budget=None, atomic=None, grants=None,
               actor=None, atomic_actor=None):
        self._require_continuity()
        recorded = self._now()
        self._check_continuity(recorded)
        if event.get("event_id") in self.store.seen_events:
            # Idempotent replay of an already-recorded event: identical
            # outcome to the store's own duplicate path, with no
            # re-validation and no re-stamp. (A forged replay of a seen id
            # changes nothing, so there is nothing to authorize.)
            return "duplicate-ignored", True
        sub = self._check_atomic(atomic, recorded, grants, atomic_actor)
        claim = self._stamped(event, recorded, grants, actor, "append",
                              atomic_actor)
        if sub is not None:
            stamped_sub = self._stamp_atomic_decide(sub, recorded,
                                                    atomic_actor)
            self._check_atomic_pair(claim, stamped_sub, recorded, budget)
            atomic = dict(atomic, decide=stamped_sub)
        return self.store.append(claim, budget, atomic)

    def record_terminal(self, verdict_event, decide_event, budget=None,
                        grants=None, actor_v=None, actor_d=None):
        self._require_continuity()
        recorded = self._now()
        self._check_continuity(recorded)
        verdict = self._stamped(verdict_event, recorded, grants, actor_v,
                                "terminal verdict", None)
        decide = self._stamped_decide(decide_event, recorded, grants,
                                      actor_d)
        # The disposition closes the POST-verdict phase: simulate the pure
        # core read-only. A standalone decide from a non-terminal phase
        # still fails its own phase check inside _stamped_decide.
        post = self._simulate_post_phase(verdict, recorded, budget)
        if post is not None and post not in TERMINALS:
            raise IngressError(
                "E_PHASE_MISMATCH",
                "terminal disposition needs a terminal post-verdict phase, "
                "verdict lands %s" % post)
        if decide.get("question_id") != verdict.get("question_id") or \
                decide.get("revision", 1) != verdict.get("revision", 1):
            raise IngressError("E_BAD_ATOMIC",
                               "terminal pair package/revision mismatch")
        return self.store.record_terminal(verdict, decide, budget)

    def _stamped_decide(self, event, recorded, grants, actor):
        # Paired decide: bound + timestamped here, phase-validated by the
        # caller against the POST-verdict phase. (A standalone decide goes
        # through _stamped, which keeps the current-phase terminal check.)
        claim = dict(event)
        bound = self._bind_actor(claim, actor, "terminal decide")
        receipt = self._receipt(claim, recorded)
        claim["actor"] = bound
        claim["at"] = receipt["recorded_at"]
        claim["receipt"] = receipt
        claim["_trusted"] = True
        return claim
