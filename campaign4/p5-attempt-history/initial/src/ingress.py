"""Trusted timestamp ingress: the single accepted external write route.

The trusted boundary owns receipt time and deadline derivation:

- ``recorded_at`` is obtained from the injected clock (production:
  :class:`HostClock` reading host UTC; tests: injected fakes) at append
  time. Caller/seat supplied ``recorded_at``, ``receipt`` or ``_trusted``
  fields are rejected as forged. The legacy ``at`` field, if present, is
  overwritten with ``recorded_at`` and the caller value is preserved only
  inside the receipt as ``caller_at_ignored`` for transparency.
- Untrusted source-reported ``occurred_at`` plus ``provenance`` are kept
  separately and validated against ``recorded_at`` with a finite justified
  future-skew tolerance (:data:`FUTURE_SKEW_TOLERANCE_S`). Excessively future
  or malformed claims are quarantined (never touch lifecycle); backdated
  claims are retained with both times but cannot retro-authorize work.
- Start deadlines derive from trusted start plus an authorized duration, or
  a separately pinned director grant (absolute deadline). Caller deadline
  extension, phase/grant mismatch, malformed/nonpositive duration, over-
  allocation and expired grants are rejected. Ledger validation stays
  authoritative AFTER ingress verifies the write.
- Host UTC plus in-process monotonic elapsed time detect clock
  discontinuity beyond :data:`DISCONTINUITY_THRESHOLD_S`; the owned response
  quarantines the write for bounded reconciliation without touching
  deadlines. Restart persists UTC/grants and opens a new monotonic epoch;
  monotonic counters are never compared across epochs.

``store.append`` / ``store.record_terminal`` are explicitly INTERNAL
low-level APIs, not an alternate accepted external route. The only accepted
external route is :class:`TrustedIngress.append` /
:meth:`TrustedIngress.record_terminal`.
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone

import validator as validator_mod

# Occurred claims must carry an explicit UTC designator (Z or numeric
# offset). Naive instants are quarantined at this boundary even though the
# lower-level validator tolerates them: trusted receipt time is never
# mixed with zone-ambiguous claims.
import re as _re
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
        self.epoch = epoch or ("epoch-%s-%s" % (
            clock.utc_now(), int(clock.monotonic())))
        self._kv_put("ingress-epoch", self.epoch)
        last = self._kv_get("ingress-last")
        if last:
            try:
                self._last = json.loads(last)
            except ValueError:
                self._last = None
        else:
            self._last = None

    # -- clock continuity ------------------------------------------------
    def _check_continuity(self, recorded):
        mono = self.clock.monotonic()
        if self._last is not None and self._last.get("epoch") == self.epoch:
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
        """Bounded reconciliation after a discontinuity: opens a fresh
        monotonic epoch with an owned note. Never resets deadlines."""
        self.epoch = "epoch-reconciled-%s" % self.clock.utc_now()
        self._kv_put("ingress-epoch", self.epoch)
        self._kv_put("ingress-reconcile-note",
                     json.dumps({"owner": owner, "note": note,
                                 "at": self.clock.utc_now()},
                                sort_keys=True))
        self._last = None
        return self.epoch

    # -- claim validation --------------------------------------------------
    def _receipt(self, claim, recorded):
        for forged in ("recorded_at", "receipt", "_trusted"):
            if forged in claim:
                raise IngressError(
                    "E_FORGED_RECEIPT",
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

    def _deadline(self, claim, recorded, grants):
        """Derive/validate the start deadline. Returns deadline or None."""
        if claim.get("type") != "start":
            dl = claim.get("deadline")
            if dl is not None and _as_instant(dl) is None:
                raise IngressError("E_BAD_DEADLINE",
                                   "deadline not a UTC instant")
            return None
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
            if claim.get("phase_hint") and grant.get("phase") and \
                    claim["phase_hint"] != grant["phase"]:
                raise IngressError("E_GRANT_MISMATCH",
                                   "phase/grant association changed")
            claim["deadline"] = grant["absolute_deadline"]
            claim["grant_ref"] = grant_ref
            return grant["absolute_deadline"]
        if duration is None:
            duration = AUTHORIZED_DURATIONS.get("run")
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

    # -- accepted external route -------------------------------------------
    def append(self, event, budget=None, atomic=None, grants=None):
        recorded_raw = self.clock.utc_now()
        recorded = _as_instant(recorded_raw)
        if recorded is None:  # pragma: no cover - defensive
            raise IngressError("E_CLOCK", "clock did not return UTC")
        self._check_continuity(recorded)
        claim = dict(event)
        receipt = self._receipt(claim, recorded)
        self._deadline(claim, recorded, grants)
        claim["at"] = receipt["recorded_at"]
        claim["receipt"] = receipt
        claim["_trusted"] = True
        return self.store.append(claim, budget, atomic)

    def record_terminal(self, verdict_event, decide_event, budget=None,
                        grants=None):
        recorded_raw = self.clock.utc_now()
        recorded = _as_instant(recorded_raw)
        if recorded is None:  # pragma: no cover - defensive
            raise IngressError("E_CLOCK", "clock did not return UTC")
        self._check_continuity(recorded)
        stamped = []
        for ev in (verdict_event, decide_event):
            claim = dict(ev)
            receipt = self._receipt(claim, recorded)
            claim["at"] = receipt["recorded_at"]
            claim["receipt"] = receipt
            claim["_trusted"] = True
            stamped.append(claim)
        return self.store.record_terminal(stamped[0], stamped[1], budget)
