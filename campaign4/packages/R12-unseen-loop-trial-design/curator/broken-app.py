"""The OpenAI-compatible front door.

Users pick a model CLASS (`"model": "deep-coder"`), never a box. The gateway
decides where the request goes (igw.router.engine), forwards it with the
class name rewritten to the backend's model id, streams the answer through,
and learns from the outcome (igw.router.beliefs, igw.router.affinity).

Failover is bounded: each failed attempt excludes that backend and re-decides;
when the engine reports nothing eligible is left, the client gets a structured
error carrying the full decision trace. Never an infinite loop.

Observability: every decision is logged as one structured JSON line
(logger "igw.router"), and every response carries x-igw-* headers naming the
backend, deciding stage, and — critically — which SOURCE identified the
conversation, because "affinity silently never engaged" is the failure mode
this project exists to prevent.

The app never talks to a backend that is not in its config, and tests only
ever configure stub backends on ephemeral ports (AGENT-RULES.md).
"""

from __future__ import annotations

import asyncio
import contextlib
import os
import json
import time
from collections import OrderedDict
import logging
from datetime import datetime, timezone
from typing import Any, AsyncIterator, Callable, Mapping
from urllib.parse import quote

from pathlib import Path

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response, StreamingResponse

from igw.router.affinity import AffinityTable
from igw.router.beliefs import BeliefStore, Outcome
from igw.router.config import RouterConfig
from igw.router.engine import Decision, RouteRequest, decide
from igw.router.gate import PriorityGate
from igw.router.identity import identify
from igw.router.usage import (
    USER_HEADER,
    SseUsageScanner,
    sanitise_user,
    usage_from_payload,
    usage_line,
)
from igw.state import BackendSpec, FleetSnapshot, Pool

logger = logging.getLogger("igw.router")

SnapshotProvider = Callable[[], FleetSnapshot | None]

ORIGIN_BOX_HEADER = "x-igw-origin-box"
#: Comma-separated backends this request must NOT be sent to. The manual
#: escape hatch: "I am sharing a box with somebody and I want off." Without it
#: the only way to move is to change conversation identity and hope the load
#: stage sends you somewhere better - a full re-prefill spent on a guess.
#:
#: Deliberately advisory. It narrows like any other stage and can empty the
#: candidate set, in which case the request is refused with a reason rather
#: than silently routed to an excluded box: a header that is sometimes obeyed
#: is worse than one that is always obeyed or always ignored.
EXCLUDE_HEADER = "x-igw-exclude"
#: (removed) A short "is anyone here right now" window was tried and is wrong.
#: Pausing to read a reply and abandoning a session look identical from outside,
#: so a short window hands your box to somebody else while you are thinking -
#: and with --cache-ram sized for roughly two conversations, a third arriving
#: can evict yours and cost a full re-prefill on return. Load now counts
#: conversations the gateway believes LIVE on a box, over the same window that
#: decides whether to send a returning conversation back: the affinity TTL.

# HTTP statuses from a backend that mean "try another box" rather than
# "the client's request is bad". Anything else passes through unchanged —
# retrying e.g. a 500 elsewhere risks double-computing a prompt-specific
# failure (see BACKLOG-router.md).
_RETRYABLE_STATUS: dict[int, Outcome] = {
    404: Outcome.MODEL_NOT_RESIDENT,
    429: Outcome.QUEUE_REJECTED,
    503: Outcome.QUEUE_REJECTED,
}


class Gateway:
    """Mutable per-process state. All of it is ephemeral actual state."""

    def __init__(
        self,
        config: RouterConfig,
        snapshot_provider: SnapshotProvider,
    ) -> None:
        self.config = config
        self.snapshot_provider = snapshot_provider
        self.affinity = AffinityTable(
            ttl_s=config.affinity_ttl_s, max_entries=config.affinity_max_entries
        )
        self.beliefs = BeliefStore(
            down_ttl_s=config.down_ttl_s,
            not_resident_ttl_s=config.not_resident_ttl_s,
            saturated_ttl_s=config.saturated_ttl_s,
        )
        self.gates: dict[str, PriorityGate] = {
            b.name: PriorityGate(config.npu_max_inflight)
            for b in config.backends
            if b.pool is Pool.NPU
        }
        self.client: httpx.AsyncClient | None = None
        #: Where affinity survives a restart. None = ephemeral, as before.
        self.state_file: Path | None = None
        self._pins_pruned = False
        #: (conversation key, class) -> [first_seen, last_seen, count, backends].
        #: Bounded and ephemeral, like every other actual-state table here.
        self._seen: "OrderedDict[tuple[str, str | None], list]" = OrderedDict()

    def save_affinity(self) -> None:
        """Write pins to disk. Cheap, and a lost write costs only re-prefills."""
        if self.state_file is None:
            return
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.state_file.with_suffix(".tmp")
            tmp.write_text(self.affinity.to_json())
            tmp.replace(self.state_file)  # atomic: never a half-written table
        except OSError as exc:
            logger.warning("could not save affinity to %s: %s", self.state_file, exc)

    def prune_restored_pins_once(self) -> None:
        """Drop restored pins whose box is demonstrably holding nothing.

        Runs once, after the first snapshot: before that we cannot tell an
        empty box from an unseen one, and treating unseen as empty would throw
        away exactly the pins worth keeping.
        """
        if self._pins_pruned:
            return
        snap = self.snapshot_provider()
        if snap is None:
            return
        self._pins_pruned = True
        dropped = self.affinity.drop_pins_for_empty_backends(
            {b.name: b.slots_occupied for b in snap.backends}
        )
        if dropped:
            logger.info(
                json.dumps(
                    {"event": "affinity-pruned", "dropped": dropped,
                     "why": "backend reports no conversations held"},
                    sort_keys=True,
                )
            )

    def record_route(self, decision) -> None:
        """Remember that this conversation was routed, for /igw/identity.

        The point of the endpoint is to distinguish "affinity is working" from
        "every request looks like a new conversation and silently pays a full
        re-prefill". The second is invisible: nothing errors, nothing warns, the
        fleet just runs slow. It cost a re-homed session on 2026-08-24 and the
        only way to see it was mailing a log parser to whoever could reach the
        box.
        """
        key = decision.identity.key
        if key is None:
            return
        k = (key, decision.class_name or decision.requested_class)
        now = time.time()
        row = self._seen.get(k)
        if row is None:
            if len(self._seen) >= 5000:
                self._seen.popitem(last=False)
            self._seen[k] = [now, now, 1, {decision.backend.name} if decision.backend else set(),
                             decision.identity.source]
            return
        row[1] = now
        row[2] += 1
        if decision.backend is not None:
            row[3].add(decision.backend.name)
        self._seen.move_to_end(k)

    def identity_stats(self, *, minutes: int = 240) -> dict[str, Any]:
        cutoff = time.time() - minutes * 60
        rows = [(k, v) for k, v in self._seen.items() if v[1] >= cutoff]
        by_class: dict[str, dict[str, Any]] = {}
        for (_key, cls), (_first, _last, count, backends, source) in rows:
            c = by_class.setdefault(
                str(cls),
                {"class": str(cls), "requests": 0, "conversations": 0,
                 "one_shot_conversations": 0, "identity_sources": {},
                 "conversations_that_moved": 0},
            )
            c["requests"] += count
            c["conversations"] += 1
            if count == 1:
                c["one_shot_conversations"] += 1
            if len(backends) > 1:
                c["conversations_that_moved"] += 1
            c["identity_sources"][source] = c["identity_sources"].get(source, 0) + 1
        for c in by_class.values():
            c["requests_per_conversation"] = round(
                c["requests"] / max(c["conversations"], 1), 2
            )
            c["verdict"] = (
                "affinity is not engaging - nearly every request is a new "
                "conversation, so each one pays a full re-prefill"
                if c["requests_per_conversation"] < 1.5
                else "conversations are being recognised across requests"
            )
        # Per backend: who is actually on each box. Answers "was that someone
        # else hitting my box?" without correlating llama.cpp's uptime-relative
        # timestamps against journalctl by hand - which is what this cost the
        # first time it was asked, and the log is not even in the journal on
        # every box.
        by_backend: dict[str, dict[str, Any]] = {}
        for (key, cls), (first, last, count, backends, source) in rows:
            for b in backends:
                e = by_backend.setdefault(
                    b, {"backend": b, "conversations": [], "requests": 0}
                )
                e["requests"] += count
                e["conversations"].append(
                    {
                        "key": key,
                        "class": str(cls),
                        "requests": count,
                        "identity": source,
                        "last_seen_s_ago": round(time.time() - last),
                        "shared_with_other_backends": sorted(backends - {b}) or None,
                    }
                )
        # Bypass detection: what the box HOLDS against what we PLACED there.
        # A box holding more conversations than the gateway sent it is being
        # used directly by somebody - a live concern while the team is still
        # being cut over, and one that also distorts routing, because that
        # traffic's KV makes the box look occupied to everyone else.
        snap = self.snapshot_provider()
        held_by_box = {
            b.name: b.slots_occupied
            for b in (snap.backends if snap else [])
        }
        for e in by_backend.values():
            e["conversations"].sort(key=lambda c: c["last_seen_s_ago"])
            e["conversation_count"] = len(e["conversations"])
            held = held_by_box.get(e["backend"])
            e["conversations_held_by_box"] = held
            if held is None:
                e["bypass"] = "unknown - the box does not report slot occupancy"
            elif held > e["conversation_count"]:
                e["bypass"] = (
                    f"{held - e['conversation_count']} conversation(s) on this "
                    "box did NOT come through the gateway"
                )
            elif held < e["conversation_count"]:
                e["bypass"] = (
                    "no; the box holds fewer than we placed (slots evicted, or "
                    "conversations ended)"
                )
            else:
                e["bypass"] = "no"

        return {
            "window_minutes": minutes,
            "backends": sorted(
                by_backend.values(), key=lambda e: -e["conversation_count"]
            ),
            "note": (
                "requests_per_conversation near 1.0 on an interactive class means "
                "affinity never engages. Expected for npu-summarise, where each "
                "compaction chunk genuinely IS a fresh prompt."
            ),
            "classes": sorted(by_class.values(), key=lambda c: -c["requests"]),
        }

    def record_failure(self, backend: str, outcome: Outcome, model: str | None) -> None:
        self.beliefs.record(backend, outcome, model=model)
        if outcome is Outcome.BACKEND_UNAVAILABLE:
            # The box (or at least its server) went away; its KV went with it.
            dropped = self.affinity.invalidate_backend(backend)
            if dropped:
                logger.info(
                    json.dumps(
                        {
                            "event": "affinity-invalidated",
                            "backend": backend,
                            "entries_dropped": dropped,
                        },
                        sort_keys=True,
                    )
                )

    def record_success(self, decision: Decision) -> None:
        assert decision.backend is not None and decision.model is not None
        self.beliefs.record(
            decision.backend.name, Outcome.OK, model=decision.model
        )
        # Affinity is a Pool-A concept; NPU chunks have no prefix worth chasing.
        backend = decision.backend
        if backend.pool is Pool.GPU and decision.class_name is not None:
            identity = decision.identity
            for key in (identity.key, identity.prefix_key):
                if key is not None:
                    self.affinity.record(
                        key, backend.name, decision.class_name, identity.source
                    )


def _error_response(
    status_code: int,
    message: str,
    error_type: str,
    *,
    decision: Decision | None = None,
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    body: dict[str, Any] = {
        "error": {"message": message, "type": error_type, "code": error_type}
    }
    if decision is not None:
        body["igw"] = decision.log_record()
    return JSONResponse(body, status_code=status_code, headers=dict(headers or {}))


def _decision_headers(decision: Decision, attempt: int) -> dict[str, str]:
    identity = decision.identity
    headers = {
        "x-igw-class": decision.class_name or decision.requested_class,
        "x-igw-stage": decision.stage or "none",
        "x-igw-conversation-source": identity.source,
        "x-igw-attempt": str(attempt),
    }
    # Every stage the decision actually passed through, in order. x-igw-stage
    # names only the stage that FINISHED the decision, so a narrowing that
    # mattered on the way - the occupancy escape, say - is invisible to the
    # caller and provable only by grepping the gateway's log. AGENT-RULES asks
    # that a decision be reconstructable from its log line; this extends the
    # same courtesy to whoever made the request.
    if decision.trace:
        headers["x-igw-stages"] = ",".join(t.stage for t in decision.trace)
    if decision.backend is not None:
        headers["x-igw-backend"] = decision.backend.name
    if identity.key is not None:
        headers["x-igw-conversation-key"] = identity.key
    return headers


async def _drain_detached(
    response: httpx.Response, backend_name: str, deadline_s: float = 30.0
) -> None:
    """Read an abandoned upstream response to completion, then close it cleanly.

    Called when the CLIENT disconnected but the upstream must not see an abort.
    FastFlowLM leaks a connection slot on every aborted request and never
    reclaims it; at the cap it rejects everything while still reporting
    ``active (running)``, which systemd cannot see.

    The deadline is not optional. Without it a hung upstream trades a leaked
    socket for a leaked task - the same bug one layer up.
    """
    try:
        async with asyncio.timeout(deadline_s):
            async for _ in response.aiter_raw():
                pass
    except (TimeoutError, httpx.HTTPError) as exc:
        # NOTE: CancelledError is deliberately NOT caught. Swallowing it makes
        # this task ignore shutdown, and it silently defeated the test that was
        # supposed to prove the deadline exists.
        logger.warning(
            json.dumps(
                {
                    "event": "drain-incomplete",
                    "backend": backend_name,
                    "error": f"{type(exc).__name__}: {exc}",
                },
                sort_keys=True,
            )
        )
    finally:
        with contextlib.suppress(Exception):
            await response.aclose()


async def _forward_once(
    gateway: Gateway,
    decision: Decision,
    body: dict[str, Any],
    want_stream: bool,
    igw_headers: dict[str, str],
    *,
    user: str,
    started: float,
) -> Response | tuple[Outcome, str]:
    """One forwarding attempt. Returns a Response to send to the client, or
    (outcome, detail) telling the caller to record a failure and re-decide.

    ``user``/``started`` feed the usage record emitted at response
    completion (event "usage", the console's UsageRecord shape). Only
    COMPLETED successful responses emit one: a stream that dies mid-flight
    has partial, unknowable totals (the stream-aborted line records the
    failure instead), and an error passed through served no tokens.
    """
    assert gateway.client is not None
    assert decision.backend is not None and decision.model is not None
    backend = decision.backend
    # Per-class: should a client disconnect be hidden from the upstream?
    _spec = next(
        (c for c in gateway.config.classes if c.name == decision.class_name), None
    )
    drain_on_disconnect = bool(_spec and _spec.drain_on_disconnect)
    upstream_body = dict(body)
    upstream_body["model"] = decision.model
    url = backend.url.rstrip("/") + "/v1/chat/completions"

    queue_wait_ms = 0.0
    gate = gateway.gates.get(backend.name)
    if gate is not None:
        # The only queueing the gateway itself imposes (NPU priority gate).
        # Backend-internal queueing is invisible here and rides wall_ms.
        gate_wait_from = time.monotonic()
        await gate.acquire(decision.priority)
        queue_wait_ms = (time.monotonic() - gate_wait_from) * 1000.0
    released = False

    def emit_usage(
        prompt_tokens: int | None, completion_tokens: int | None
    ) -> None:
        logger.info(
            usage_line(
                user=user,
                class_name=decision.class_name,
                model=decision.model,
                backend=backend.name,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                wall_ms=(time.monotonic() - started) * 1000.0,
                queue_wait_ms=queue_wait_ms,
            )
        )

    def release_once() -> None:
        nonlocal released
        if gate is not None and not released:
            released = True
            gate.release()

    try:
        upstream = gateway.client.build_request("POST", url, json=upstream_body)
        try:
            response = await gateway.client.send(upstream, stream=True)
        except httpx.HTTPError as exc:
            release_once()
            return (
                Outcome.BACKEND_UNAVAILABLE,
                f"{type(exc).__name__}: {exc}",
            )

        retry_as = _RETRYABLE_STATUS.get(response.status_code)
        if retry_as is not None:
            await response.aread()
            await response.aclose()
            release_once()
            return retry_as, f"HTTP {response.status_code} from {backend.name}"

        if response.status_code < 400:
            gateway.record_success(decision)

        content_type = response.headers.get("content-type", "application/json")
        if want_stream:
            # Tee, don't buffer: the scanner sees each chunk in the same
            # iteration that hands it to the client. feed() is synchronous
            # CPU work on bytes already in hand — nothing here awaits, waits
            # for more data, or withholds a chunk, so the passthrough cannot
            # be delayed by usage capture. Only a completed stream emits.
            scanner = (
                SseUsageScanner() if response.status_code < 400 else None
            )

            async def relay() -> AsyncIterator[bytes]:
                completed = False
                detached = False
                try:
                    async for chunk in response.aiter_raw():
                        if scanner is not None:
                            scanner.feed(chunk)
                        yield chunk
                    completed = True
                except httpx.HTTPError as exc:
                    # Mid-stream death: too late to fail over (bytes are out).
                    gateway.record_failure(
                        backend.name, Outcome.BACKEND_UNAVAILABLE, decision.model
                    )
                    logger.warning(
                        json.dumps(
                            {
                                "event": "stream-aborted",
                                "backend": backend.name,
                                "error": f"{type(exc).__name__}: {exc}",
                            },
                            sort_keys=True,
                        )
                    )
                except asyncio.CancelledError:
                    # The CLIENT went away. Closing here would abort the request
                    # at the upstream; for FLM that leaks a connection slot for
                    # the life of the process. Hand it to a drain task instead.
                    if drain_on_disconnect:
                        detached = True
                        asyncio.create_task(
                            _drain_detached(response, backend.name)
                        )
                    raise
                finally:
                    if not detached:
                        await response.aclose()
                    release_once()
                    if completed and scanner is not None:
                        # Tokens may be absent (many servers omit usage on
                        # streams); the request/wall/queue facts still count.
                        emit_usage(
                            scanner.prompt_tokens, scanner.completion_tokens
                        )

            return StreamingResponse(
                relay(),
                status_code=response.status_code,
                media_type=content_type,
                headers=igw_headers,
            )

        detached = False
        try:
            payload = await response.aread()
        except httpx.HTTPError as exc:
            release_once()
            return (
                Outcome.BACKEND_UNAVAILABLE,
                f"body read failed: {type(exc).__name__}: {exc}",
            )
        except asyncio.CancelledError:
            if drain_on_disconnect:
                detached = True
                asyncio.create_task(_drain_detached(response, backend.name))
            raise
        finally:
            if not detached:
                await response.aclose()
        release_once()
        if response.status_code < 400:
            prompt_tokens, completion_tokens = usage_from_payload(payload)
            emit_usage(prompt_tokens, completion_tokens)
        return Response(
            content=payload,
            status_code=response.status_code,
            media_type=content_type,
            headers=igw_headers,
        )
    except BaseException:
        release_once()
        raise


def create_app(
    config: RouterConfig,
    snapshot_provider: SnapshotProvider | None = None,
    *,
    poll_specs: list[BackendSpec] | None = None,
    poll_interval_s: float = 5.0,
    poll_timeout_s: float = 15.0,  # see DEFAULT_TIMEOUT in igw/poller/poll.py
    config_paths: dict[str, str] | None = None,
    state_file: str | Path | None = None,
) -> FastAPI:
    """Build the front door.

    Tests MUST pass ``snapshot_provider`` (and never ``poll_specs``): the
    polling path contacts the URLs in ``poll_specs``, which in production are
    real backends. With neither, the gateway routes on config alone
    (health-unknown), which still works but never narrows on residency/load.
    """
    if snapshot_provider is not None and poll_specs is not None:
        raise ValueError("pass snapshot_provider or poll_specs, not both")

    latest: dict[str, FleetSnapshot | None] = {"snap": None}
    if snapshot_provider is None:
        provider: SnapshotProvider = lambda: latest["snap"]
    else:
        provider = snapshot_provider

    gateway = Gateway(config, provider)
    gateway.state_file = Path(state_file) if state_file else None

    @contextlib.asynccontextmanager
    async def lifespan(app: FastAPI):
        # The fleet's shared key, presented to every backend. Read from the
        # ENVIRONMENT, never from the config file: a router config is committed
        # and rendered in the console, and a secret in it would leak both ways.
        #
        # Absent var = no header. That is deliberate: §31's cutover is per box,
        # so during it some backends sit behind Caddy and some do not. Sending
        # the header to a bare llama-server is harmless (it ignores unknown
        # auth), which is why a single client-wide default works for a
        # half-migrated fleet.
        auth_headers: dict[str, str] = {}
        _key = os.environ.get(config.backend_key_env)
        if _key:
            auth_headers["Authorization"] = f"Bearer {_key}"
            logger.info(
                "presenting %s to backends (value not logged)",
                config.backend_key_env,
            )
        else:
            # Warning, not info: this state is correct only during the
            # per-box Caddy cutover window. Once every box is behind Caddy,
            # this line at startup is the only advance notice that the fleet
            # is about to 401 the gateway, and by then it must be impossible
            # to have missed.
            logger.warning(
                "no %s in the environment — backends will be called "
                "unauthenticated; correct only while they are not behind Caddy",
                config.backend_key_env,
            )
        # Restore pins from the last run. A restored pin is a BELIEF: if the
        # backend restarted too, its KV is gone and honouring the pin sends
        # somebody to a cold box while claiming it is warm. Stale pins are
        # pruned against the first snapshot below, once we can see which boxes
        # are holding anything.
        if gateway.state_file is not None:
            try:
                text = gateway.state_file.read_text()
            except OSError:
                text = ""
            if text:
                res = gateway.affinity.load_json(text)
                logger.info(
                    json.dumps({"event": "affinity-restored", **res}, sort_keys=True)
                )

        gateway.client = httpx.AsyncClient(
            headers=auth_headers,
            timeout=httpx.Timeout(
                connect=config.connect_timeout_s,
                read=config.read_timeout_s,
                write=30.0,
                pool=None,
            )
        )
        poll_task: asyncio.Task | None = None
        save_task: asyncio.Task | None = None
        if poll_specs is not None:
            from igw.poller import FlavourCache, poll_fleet

            # One cache for the life of the app: backends are flavour-probed
            # on first contact and then only re-probed on TTL expiry or when
            # collection sees contradicting evidence — not every 5 s tick.
            flavour_cache = FlavourCache()

            async def poll_loop() -> None:
                while True:
                    with contextlib.suppress(Exception):
                        latest["snap"] = await poll_fleet(
                            poll_specs, timeout=poll_timeout_s, cache=flavour_cache
                        )
                    await asyncio.sleep(poll_interval_s)

            poll_task = asyncio.create_task(poll_loop())

        if gateway.state_file is not None:
            async def save_loop() -> None:
                # Periodic, not only on shutdown: a gateway that is killed
                # rather than stopped still keeps most of its pins, and the
                # cost of a slightly stale file is at worst one re-prefill.
                while True:
                    await asyncio.sleep(60.0)
                    with contextlib.suppress(Exception):
                        gateway.save_affinity()

            save_task = asyncio.create_task(save_loop())
        try:
            yield
        finally:
            for task in (poll_task, save_task):
                if task is not None:
                    task.cancel()
                    with contextlib.suppress(asyncio.CancelledError):
                        await task
            gateway.save_affinity()
            await gateway.client.aclose()
            gateway.client = None

    app = FastAPI(title="inference-gateway", lifespan=lifespan)
    # Paths the gateway actually loaded, so /igw/version can fingerprint them
    # and config drift between the repo and the box is visible on sight. That
    # drift has bitten twice: the poll interval, and affinity_ttl_s missing
    # from the tracked config and silently defaulting to 30 minutes.
    app.state.igw_config_paths = config_paths or {}
    app.state.gateway = gateway

    @app.get("/v1/models")
    async def list_models() -> dict[str, Any]:
        return {
            "object": "list",
            "data": [
                {
                    "id": cls.name,
                    "object": "model",
                    "owned_by": "inference-gateway",
                }
                for cls in config.classes
            ],
        }

    @app.get("/igw/status")
    async def status() -> dict[str, Any]:
        snap = provider()
        age_s: float | None = None
        if snap is not None:
            polled = snap.polled_at
            if polled.tzinfo is not None:
                age_s = max(
                    0.0, (datetime.now(timezone.utc) - polled).total_seconds()
                )
        snap_now = provider()
        return {
            "affinity": gateway.affinity.stats(),
            # The exact number _load_rank ranks candidates on, plus the two
            # fields that can override it. Nothing exposed any of them.
            #
            # /igw/identity has a per-backend view, but it counts DECISION LOG
            # rows over a time window - a different number from a different
            # source. On 2026-08-25 it read a5410=13 while the affinity table
            # held 7 entries in total. Close enough to look like the same thing,
            # far enough to mislead: three conversations routed to a box holding
            # 13 while an empty peer took none, and there was no way to see what
            # the router had seen.
            #
            # slots_free is here because rank beats occupancy: an unknown
            # slots_free scores rank 1, which sorts BELOW a fully loaded box at
            # rank 0. A box that stops reporting slots quietly stops receiving
            # traffic, and that looks identical to a load-balancing failure.
            "affinity_by_backend": gateway.affinity.live_per_backend(config.load_window_s),
            "load_inputs": {
                b.name: {
                    "live_conversations": gateway.affinity.live_per_backend(config.load_window_s).get(b.name, 0),
                    "slots_free": b.slots_free,
                    "queue_depth": b.queue_depth,
                }
                for b in (snap_now.backends if snap_now else [])
            },
            "beliefs": gateway.beliefs.stats(),
            "snapshot_age_s": age_s,
            "snapshot_polled_at": None if snap is None else snap.polled_at.isoformat(),
            "npu_gates": {
                name: {"inflight": g.inflight, "waiting": g.waiting}
                for name, g in gateway.gates.items()
            },
        }

    async def _serve_upstream(
        request: Request,
        leaf: str,
        backend_name: str | None,
        class_name: str | None = None,
    ) -> Response:
        """Proxy llama.cpp's GET /props or /slots from the backend serving YOU.

        A client behind the gateway cannot otherwise see the server it is
        actually talking to. Two things need it:

        - pi-lcm probes /props to check that a configured contextWindow does not
          exceed the server's real n_ctx. With no route here that check has been
          silently skipped on every session since the gateway was stood up, and
          silent truncation is exactly the failure it exists to prevent.
        - waiting for a cancelled pre-load's slot to be released needs live slot
          state, and the poller's snapshot is seconds stale by design.

        Resolution is explicit or it refuses. Guessing a backend would answer a
        question about a machine the caller is not on, which is worse than an
        error because it looks like data.
        """
        chosen = backend_name
        via = "explicit ?backend="

        # A pin, when the caller has one. Preferred: it names the machine whose
        # slots and context actually apply to this conversation.
        if chosen is None:
            ident = identify(request.headers, {})
            if ident.key is not None:
                entry = gateway.affinity.lookup(ident.key)
                if entry is not None:
                    chosen = entry.backend
                    via = f"affinity pin ({ident.source})"

        # No pin. That is the NORMAL case for /props: pi-lcm probes it during
        # handshake, before the session has sent anything, to check a configured
        # contextWindow against the server's real n_ctx. Refusing there is why the
        # check stayed off - the first version of this endpoint required identity
        # and 400d the one caller it was built for.
        if chosen is None and class_name:
            spec = next((c for c in config.classes if c.name == class_name), None)
            if spec is not None:
                snap0 = provider()
                healthy = {
                    b.name for b in (snap0.backends if snap0 else []) if b.healthy
                }
                for b in config.backends:
                    if spec.backend_model in b.models and (
                        not healthy or b.name in healthy
                    ):
                        chosen = b.name
                        via = f"any backend serving class {class_name!r}"
                        break
        if chosen is None:
            snap0 = provider()
            for b in (snap0.backends if snap0 else []):
                if b.healthy:
                    chosen = b.name
                    via = "any healthy backend (no class, no pin)"
                    break
        if chosen is None:
            return JSONResponse(
                status_code=503,
                content={
                    "error": "no backend could be resolved",
                    "why": (
                        "no ?backend=, no affinity pin, no class in the path, and "
                        "no healthy backend in the latest snapshot"
                    ),
                    "known_backends": [b.name for b in config.backends],
                },
            )

        target = next((b for b in config.backends if b.name == chosen), None)
        if target is None:
            return JSONResponse(
                status_code=404,
                content={
                    "error": f"no backend named {chosen!r}",
                    "known_backends": [b.name for b in config.backends],
                },
            )
        if gateway.client is None:
            return JSONResponse(
                status_code=503,
                content={"error": "gateway has no HTTP client (not started?)"},
            )

        # llama-swap serves these ONLY under /upstream/<model>/; a bare
        # llama-server serves them at the root. Try the form the snapshot says
        # is right, then the other - a 404 here is a shape mismatch, not an
        # outage, and reporting it as an outage has cost a day before.
        # Use models_loaded, NOT model. llama-swap's /upstream/<x>/ wants the
        # ALIAS from its config.yaml; BackendStatus.model is deliberately the GGUF
        # file basename instead ("file basename beats alias when known",
        # poller/poll.py) because residency is a fact about the file. Building the
        # URL from it produced
        #     /upstream/Qwen3.8-27B-Q4_K_M.gguf/props -> 400
        # on a live fleet - the two fields look interchangeable and are not.
        snap = provider()
        aliases: list[str] = []
        if snap is not None:
            row = next((b for b in snap.backends if b.name == chosen), None)
            if row is not None and row.models_loaded:
                aliases = [a for a in row.models_loaded if a]

        base = target.url.rstrip("/")
        candidates = [
            f"{base}/upstream/{quote(a, safe='')}/{leaf}" for a in aliases[:4]
        ]
        candidates.append(f"{base}/{leaf}")

        attempts: list[dict[str, Any]] = []
        for url in candidates:
            try:
                r = await gateway.client.get(url, timeout=15.0)
            except httpx.HTTPError as exc:
                attempts.append({"url": url, "error": f"{type(exc).__name__}: {exc}"})
                continue
            if r.status_code != 200:
                attempts.append({"url": url, "status": r.status_code})
                continue
            try:
                payload = r.json()
            except ValueError:
                attempts.append({"url": url, "status": 200, "error": "not JSON"})
                continue
            return JSONResponse(
                content=payload,
                headers={"x-igw-backend": chosen, "x-igw-upstream": url},
            )

        return JSONResponse(
            status_code=502,
            content={
                "error": f"could not read {leaf} from {chosen}",
                "resolved_via": via,
                "attempts": attempts,
                "hint": (
                    "llama-swap serves /props and /slots only at "
                    "/upstream/<model>/; a bare llama-server serves them at the "
                    "root. Both were tried."
                ),
            },
        )

    @app.get("/props")
    async def upstream_props(
        request: Request, backend: str | None = None
    ) -> Response:
        """llama.cpp /props for the backend serving this conversation."""
        return await _serve_upstream(request, "props", backend)

    @app.get("/slots")
    async def upstream_slots(
        request: Request, backend: str | None = None
    ) -> Response:
        """llama.cpp /slots for the backend serving this conversation."""
        return await _serve_upstream(request, "slots", backend)

    # The forms pi-lcm probes second, and the shape llama-swap itself uses. The
    # path carries the class, which resolves a backend when there is no pin yet.
    @app.get("/upstream/{model}/props")
    async def upstream_props_by_model(
        model: str, request: Request, backend: str | None = None
    ) -> Response:
        return await _serve_upstream(request, "props", backend, class_name=model)

    @app.get("/upstream/{model}/slots")
    async def upstream_slots_by_model(
        model: str, request: Request, backend: str | None = None
    ) -> Response:
        return await _serve_upstream(request, "slots", backend, class_name=model)

    @app.post("/igw/admin/forget")
    async def admin_forget(
        conversation: str | None = None,
        prefix: str | None = None,
        backend: str | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        """Drop pins, so routing can be re-tested without waiting out the TTL.

        The gap this closes: /igw/admin/pin could create a pin and erase-slot
        could free KV, but nothing could UN-pin. With a four-hour TTL an admin
        mid-test had two options - wait, or restart the gateway and make every
        user re-prefill. Both are absurd while actively testing routing.

        It also matters for correctness of testing, not just convenience. A
        spread test that leaves pins behind makes every eligible box read as
        occupied, which disables the LOAD stage - so the next run cannot
        separate anyone and reports a routing bug that is really its own
        residue. That happened on 2026-08-25: five runs, 21 pins, and an
        untestable fleet.

        Exactly one selector, and anything plural needs confirm=true. Dropping
        a live user's pin costs them one re-prefill on their next turn - real,
        recoverable, and not something to do by accident.
        """
        given = [x for x in (conversation, prefix, backend) if x]
        if len(given) != 1:
            return {
                "error": "give exactly one of conversation=, prefix=, backend=",
                "why": (
                    "each selects a different scope and combining them would "
                    "hide which one matched"
                ),
            }

        if conversation:
            dropped = [conversation] if gateway.affinity.forget(conversation) else []
            scope = f"conversation {conversation!r}"
        elif prefix:
            if not confirm:
                preview = gateway.affinity.keys_with_prefix(prefix)
                out: dict[str, Any] = {
                    "dropped": 0,
                    "would_drop": len(preview),
                    "sample": preview[:10],
                    "hint": "re-send with confirm=true",
                }
                if not preview:
                    # Zero matches usually means the wrong prefix, not a clean
                    # table: stored keys are NAMESPACED by how identity was
                    # derived, so the value a client sent as x-session-affinity
                    # is stored as "conv:hdr:<value>". Somebody typing what they
                    # sent gets 0 and reads it as "nothing to clean".
                    # Show real keys rather than making them read identity.py.
                    existing = gateway.affinity.keys_with_prefix("")
                    out["why_zero"] = (
                        "no pin starts with that. Keys are namespaced: "
                        "'conv:hdr:<session-affinity value>' when a session "
                        "header supplied the identity, 'conv:hash:<digest>' "
                        "when it was derived from the prompt."
                    )
                    out["existing_keys"] = existing[:10]
                    out["total_pins"] = len(existing)
                return out
            dropped = gateway.affinity.forget_prefix(prefix)
            scope = f"prefix {prefix!r}"
        else:
            if not confirm:
                live = gateway.affinity.live_per_backend(config.load_window_s).get(backend or "", 0)
                return {
                    "dropped": 0,
                    "would_drop": live,
                    "hint": "re-send with confirm=true",
                }
            dropped = [f"<{gateway.affinity.invalidate_backend(backend or '')} on {backend}>"]
            scope = f"backend {backend!r}"

        gateway.save_affinity()
        logger.info(
            json.dumps(
                {"event": "affinity-forgotten", "scope": scope,
                 "dropped": len(dropped)},
                sort_keys=True,
            )
        )
        return {
            "dropped": len(dropped),
            "scope": scope,
            "keys": dropped[:20],
            "remaining": gateway.affinity.stats(),
            "note": (
                "each dropped conversation re-prefills once on its next turn, "
                "then is warm again"
            ),
        }

    @app.post("/igw/admin/erase-slot")
    async def admin_erase_slot(
        backend: str, slot: int, confirm: bool = False
    ) -> dict[str, Any]:
        """Free a slot whose conversation nobody is coming back for.

        The gateway has always modified backend state - every proxied
        completion allocates a slot, fills KV and can evict somebody else's
        cache. What makes an erase different is not that it writes, but that it
        destroys context its owner does not know is gone, and they learn by
        paying for it.

        So: it refuses a slot that is actively processing, and it reports what
        it is about to destroy before doing it. Call with confirm=false first
        to see that; confirm=true to go through with it.
        """
        target = next((b for b in config.backends if b.name == backend), None)
        if target is None:
            return {
                "error": f"no backend named {backend!r}",
                "known_backends": [b.name for b in config.backends],
            }
        if gateway.client is None:
            return {"error": "gateway has no HTTP client (not started?)"}

        try:
            r = await gateway.client.get(f"{target.url}/slots", timeout=10.0)
            slots = r.json()
        except Exception as exc:
            return {"error": f"could not read {backend}/slots: {exc}"}
        if not isinstance(slots, list):
            return {
                "error": f"{backend}/slots did not return a list",
                "hint": "llama-swap serves it at /upstream/<model>/slots",
            }

        row = next((s for s in slots if isinstance(s, dict) and s.get("id") == slot), None)
        if row is None:
            return {
                "error": f"no slot {slot} on {backend}",
                "slots_present": [s.get("id") for s in slots if isinstance(s, dict)],
            }
        holds = row.get("n_prompt_tokens") or 0
        processing = bool(row.get("is_processing"))

        preview = {
            "backend": backend,
            "slot": slot,
            "holds_tokens": holds,
            "is_processing": processing,
            "erased": False,
        }
        if processing:
            preview["refused"] = (
                "this slot is generating right now; erasing it would cut off a "
                "live turn. Wait for it to finish."
            )
            return preview
        if not confirm:
            preview["would_destroy"] = (
                f"{holds} tokens of context. Whoever owns this conversation "
                "will pay a full re-prefill and will not be told. "
                "Re-send with confirm=true."
            )
            return preview

        try:
            resp = await gateway.client.post(
                f"{target.url}/slots/{slot}", params={"action": "erase"}, timeout=30.0
            )
            ok = resp.status_code < 400
        except Exception as exc:
            return {**preview, "error": f"erase failed: {exc}"}

        preview["erased"] = ok
        preview["backend_status"] = resp.status_code
        logger.info(json.dumps({"event": "admin-erase-slot", **preview}, sort_keys=True))
        return preview

    @app.post("/igw/selftest/spread")
    async def selftest_spread(
        class_name: str = "deep-coder", users: int = 3, turns: int = 2
    ) -> dict[str, Any]:
        """Route several conversations for real, recording each, then forget them.

        /igw/selftest simulates and records nothing, so its second probe cannot
        see where the first landed - it cannot test the behaviour that actually
        matters when several people start work at once.

        This runs the real decision path, decide() plus record_route(), so each
        conversation sees the previous one's pin. It sends NO inference: the
        proxy that follows a decision cannot change where a conversation goes.
        No tokens, no slot, safe against a live fleet.

        POST rather than GET because it writes - it creates pins and then drops
        them. A read-only verb would be a lie about that.
        """
        from igw.router.selftest import run_spread_trial

        result = run_spread_trial(
            config,
            provider(),
            affinity=gateway.affinity,
            beliefs=gateway.beliefs,
            class_name=class_name,
            users=max(2, min(users, 8)),
            turns=max(1, min(turns, 5)),
        )
        gateway.save_affinity()
        return result

    @app.post("/igw/admin/pin")
    async def admin_pin(
        conversation: str, backend: str, class_name: str = "deep-coder"
    ) -> dict[str, Any]:
        """Send a named conversation to a named box, from now on.

        The lever that did not exist: an admin watching routing go wrong could
        only restart the gateway, which drops EVERY pin and makes everybody
        re-prefill - a cure worse than most of the diseases.

        Does not move any KV. The conversation re-prefills once on arrival and
        is warm thereafter. Conversation keys come from /igw/identity.
        """
        if not any(b.name == backend for b in config.backends):
            return {
                "error": f"no backend named {backend!r}",
                "known_backends": [b.name for b in config.backends],
            }
        previous = gateway.affinity.lookup(conversation)
        gateway.affinity.record(conversation, backend, class_name, "admin")
        gateway.save_affinity()
        result: dict[str, Any] = {
            "conversation": conversation,
            "pinned_to": backend,
            "previously": previous.backend if previous else None,
            "note": (
                "no KV is moved; this conversation re-prefills once on arrival, "
                "then stays warm there"
            ),
        }

        # Moving somebody LEAVES their cache on the old box. Nothing reclaims
        # it: under ttl:0 it sits there until another conversation evicts it,
        # meanwhile counting as occupancy against a box nobody is using.
        #
        # The gateway cannot erase it automatically - it knows which BOX a
        # conversation was on, never which SLOT, because slot ids are internal
        # to llama.cpp and appear in nothing the gateway sees. So it does the
        # legwork and leaves the destructive call to a person: here are the
        # idle slots on the old box, and the exact call to free one.
        old = previous.backend if previous else None
        if old and old != backend:
            old_be = next((b for b in config.backends if b.name == old), None)
            if old_be is not None and gateway.client is not None:
                try:
                    rr = await gateway.client.get(f"{old_be.url}/slots", timeout=10.0)
                    rows = rr.json()
                except Exception as exc:
                    result["old_box_slots"] = {"error": str(exc)}
                    rows = None
                if isinstance(rows, list):
                    idle = [
                        {
                            "slot": r.get("id"),
                            "holds_tokens": r.get("n_prompt_tokens") or 0,
                            "free_it_with": (
                                f"POST /igw/admin/erase-slot?backend={old}"
                                f"&slot={r.get('id')}&confirm=true"
                            ),
                        }
                        for r in rows
                        if isinstance(r, dict)
                        and not r.get("is_processing")
                        and (r.get("n_prompt_tokens") or 0) > 0
                    ]
                    result["left_behind_on"] = old
                    result["old_box_idle_slots"] = idle
                    result["warning"] = (
                        f"this conversation's cache is still on {old} and nothing "
                        "will reclaim it. One of the slots above is probably it - "
                        "the gateway cannot tell which, so check the token counts."
                    ) if idle else (
                        f"{old} reports no idle slots holding a conversation"
                    )
        logger.info(json.dumps({"event": "admin-pin", **result}, sort_keys=True))
        return result

    @app.delete("/igw/admin/pin/{conversation}")
    async def admin_unpin(conversation: str) -> dict[str, Any]:
        """Forget a pin, letting the conversation route normally again."""
        had = gateway.affinity.lookup(conversation)
        gateway.affinity.forget(conversation)
        gateway.save_affinity()
        return {"conversation": conversation, "was_pinned_to": had.backend if had else None}

    @app.get("/igw/version")
    async def version() -> dict[str, Any]:
        """What is actually running here, and since when.

        Written because an afternoon of deploys could only be told apart by
        noticing which fields were MISSING from other endpoints' JSON.
        """
        from igw.version import version_report

        return version_report(
            config_paths=app.state.igw_config_paths,
            state_file=gateway.state_file,
        )

    @app.get("/igw/identity")
    async def identity_audit(minutes: int = 240) -> dict[str, Any]:
        """Who is getting affinity, and who pays a re-prefill every turn.

        Exists as an endpoint rather than a script because the alternative was
        mailing a parser to whoever can reach the fleet and having them paste
        the output back. The gateway already has this data.
        """
        return gateway.identity_stats(minutes=minutes)

    @app.get("/igw/selftest")
    async def selftest() -> dict[str, Any]:
        """Would the router do the right thing right now, and how do we know?

        Runs the decision engine against the live snapshot with hypothetical
        requests. Touches no backend, spends no tokens, queues behind nothing.
        """
        from igw.router.selftest import run_selftest

        return run_selftest(
            config,
            provider(),
            affinity=gateway.affinity,
            beliefs=gateway.beliefs,
            inflight={n: g.inflight for n, g in gateway.gates.items()},
        )

    @app.post("/v1/chat/completions")
    async def chat_completions(request: Request) -> Response:
        started = time.monotonic()
        # Attribution, not auth: an UNTRUSTED self-declared label (the
        # fleet has no auth). Sanitised for the log's sake; absent -> the
        # explicit "(unattributed)". Nothing routes or gates on it.
        user = sanitise_user(request.headers.get(USER_HEADER))
        try:
            body = await request.json()
        except Exception:
            return _error_response(
                400, "request body is not valid JSON", "invalid_request_error"
            )
        if not isinstance(body, dict):
            return _error_response(
                400, "request body must be a JSON object", "invalid_request_error"
            )
        class_name = body.get("model")
        if not isinstance(class_name, str) or not class_name:
            return _error_response(
                400,
                "missing 'model': pick a model class from /v1/models",
                "invalid_request_error",
            )

        identity = identify(
            request.headers, body, prefix_chars=config.prefix_chars
        )
        origin_box = request.headers.get(ORIGIN_BOX_HEADER)
        want_stream = bool(body.get("stream"))

        exclude: set[str] = set()
        client_excluded = {
            n.strip()
            for n in (request.headers.get(EXCLUDE_HEADER) or "").split(",")
            if n.strip()
        }
        exclude |= client_excluded
        attempts = 0
        max_attempts = len(config.backends) + 1
        last_failure: str | None = None

        while attempts < max_attempts:
            snapshot = provider()
            decision = decide(
                RouteRequest(
                    class_name=class_name,
                    identity=identity,
                    origin_box=origin_box,
                    exclude=frozenset(exclude),
                ),
                config,
                snapshot,
                beliefs=gateway.beliefs,
                affinity=gateway.affinity,
                # The only load signal an NPU has: FLM reports no queue and no
                # slots, so without this every NPU ties and spill falls through
                # to alphabetical order.
                inflight={n: g.inflight for n, g in gateway.gates.items()},
                # Conversations the gateway believes live on each box. Counted
                # over the affinity TTL, so it agrees with the stage that
                # decides whether a returning conversation goes back there.
                # NOT kv_tokens_held: an abandoned conversation leaves its KV
                # resident under ttl:0 forever, so held-KV only ever grows and
                # eventually marks every box occupied.
                active=gateway.affinity.live_per_backend(config.load_window_s),
            )
            # The decision log line, with the user label carried alongside
            # the engine's record (the engine itself never sees users).
            route_record = decision.log_record()
            route_record["user"] = user
            logger.info(json.dumps(route_record, sort_keys=True, default=str))
            gateway.record_route(decision)
            gateway.prune_restored_pins_once()

            if not decision.routed:
                if decision.reason.startswith("unknown-class"):
                    return _error_response(
                        404, decision.reason, "model_not_found", decision=decision
                    )
                if last_failure is not None:
                    return _error_response(
                        502,
                        f"all eligible backends failed (last: {last_failure}); "
                        f"{decision.reason}",
                        "all_backends_failed",
                        decision=decision,
                    )
                return _error_response(
                    503, decision.reason, "no_eligible_backend", decision=decision
                )

            attempts += 1
            assert decision.backend is not None
            result = await _forward_once(
                gateway,
                decision,
                body,
                want_stream,
                _decision_headers(decision, attempts),
                user=user,
                started=started,
            )
            if isinstance(result, Response):
                return result

            outcome, detail = result
            last_failure = f"{decision.backend.name}: {outcome.value} ({detail})"
            gateway.record_failure(decision.backend.name, outcome, decision.model)
            exclude.add(decision.backend.name)
            logger.warning(
                json.dumps(
                    {
                        "event": "outcome",
                        "backend": decision.backend.name,
                        "outcome": outcome.value,
                        "detail": detail,
                        "attempt": attempts,
                    },
                    sort_keys=True,
                )
            )

        return _error_response(
            502,
            f"gave up after {attempts} attempts (last: {last_failure})",
            "all_backends_failed",
        )

    return app
