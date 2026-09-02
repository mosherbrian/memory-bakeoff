"""Strict JSONL controller for Pi 0.81 RPC-mode integration.

This deliberately speaks only Pi's public headless protocol.  It never opens a
second Pi process to inspect an active session; all state and ledger reads are
RPC commands sent to the one child it started.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
import queue
import subprocess
import threading
import time
from typing import Any


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class RpcProtocolError(RuntimeError):
    pass


@dataclass
class RpcTrace:
    pid: int | None = None
    started_at: str = field(default_factory=utcnow)
    stopped_at: str | None = None
    stdin: list[dict[str, Any]] = field(default_factory=list)
    stdout: list[dict[str, Any]] = field(default_factory=list)
    stderr: list[dict[str, str]] = field(default_factory=list)
    lifecycle: list[dict[str, Any]] = field(default_factory=list)

    def event(self, kind: str, **data: Any) -> None:
        self.lifecycle.append({"at": utcnow(), "kind": kind, **data})

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.__dict__, indent=2, sort_keys=True) + "\n")


class PiRpc:
    """One persistent Pi RPC child and its auditable command/event stream."""

    def __init__(self, argv: list[str], *, cwd: Path, env: dict[str, str], trace: RpcTrace | None = None):
        self.argv, self.cwd, self.env = argv, cwd, env
        self.trace = trace or RpcTrace()
        self.proc: subprocess.Popen[str] | None = None
        self._lines: queue.Queue[tuple[str, str]] = queue.Queue()
        self._next_id = 0
        self.session_ids: list[str] = []

    def start(self) -> None:
        self.proc = subprocess.Popen(self.argv, cwd=self.cwd, env=self.env, text=True, bufsize=1,
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.trace.pid = self.proc.pid
        self.trace.event("process_started", argv=self.argv, pid=self.proc.pid)
        assert self.proc.stdout and self.proc.stderr
        for stream, label in ((self.proc.stdout, "stdout"), (self.proc.stderr, "stderr")):
            threading.Thread(target=self._read_stream, args=(stream, label), daemon=True).start()
        # Pi RpcClient itself permits a 100 ms initialization window.  This only
        # establishes that the child did not fail to exec; it is not quiescence.
        time.sleep(0.15)
        if self.proc.poll() is not None:
            raise RpcProtocolError(f"Pi RPC exited during startup: {self.diagnostics()}")

    def _read_stream(self, stream: Any, label: str) -> None:
        for line in iter(stream.readline, ""):
            self._lines.put((label, line.rstrip("\n")))

    def _record_stdout(self, line: str) -> dict[str, Any]:
        try:
            data = json.loads(line)
        except json.JSONDecodeError as exc:
            raise RpcProtocolError(f"Pi RPC stdout is not JSONL: {line!r}") from exc
        entry = {"at": utcnow(), "data": data}
        self.trace.stdout.append(entry)
        return data

    def _drain_stderr(self) -> None:
        while True:
            try:
                label, line = self._lines.get_nowait()
            except queue.Empty:
                return
            if label == "stderr":
                self.trace.stderr.append({"at": utcnow(), "text": line})
            else:
                # Retain events even when they happen while another operation is
                # being inspected; callers do not discard protocol evidence.
                self._record_stdout(line)

    def command(self, payload: dict[str, Any], *, timeout: float = 30) -> dict[str, Any]:
        if not self.proc or self.proc.poll() is not None or not self.proc.stdin:
            raise RpcProtocolError(f"Pi RPC is not live: {self.diagnostics()}")
        self._next_id += 1
        command = {**payload, "id": f"gen25_{self._next_id}"}
        self.trace.stdin.append({"at": utcnow(), "data": command})
        self.proc.stdin.write(json.dumps(command, separators=(",", ":")) + "\n")
        self.proc.stdin.flush()
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                label, line = self._lines.get(timeout=max(0.01, deadline - time.monotonic()))
            except queue.Empty:
                break
            if label == "stderr":
                self.trace.stderr.append({"at": utcnow(), "text": line})
                continue
            data = self._record_stdout(line)
            if data.get("type") == "response" and data.get("id") == command["id"]:
                if not data.get("success"):
                    raise RpcProtocolError(f"Pi RPC {payload['type']} failed: {data.get('error')}")
                return data.get("data", {})
        raise RpcProtocolError(f"Timed out awaiting {payload['type']}: {self.diagnostics()}")

    def prompt_until_settled(self, message: str, *, timeout: float = 180) -> None:
        self.command({"type": "prompt", "message": message})
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                label, line = self._lines.get(timeout=max(0.01, deadline - time.monotonic()))
            except queue.Empty:
                break
            if label == "stderr":
                self.trace.stderr.append({"at": utcnow(), "text": line})
                continue
            data = self._record_stdout(line)
            if data.get("type") == "agent_settled":
                self.trace.event("agent_settled")
                return
        raise RpcProtocolError(f"Timed out awaiting agent_settled: {self.diagnostics()}")

    def state(self) -> dict[str, Any]:
        data = self.command({"type": "get_state"})
        session_id = data.get("sessionId")
        if not isinstance(session_id, str):
            raise RpcProtocolError("get_state did not return sessionId")
        self.session_ids.append(session_id)
        self.trace.event("state", state=data)
        return data

    def entries(self, since: str | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {"type": "get_entries"}
        if since is not None:
            payload["since"] = since
        data = self.command(payload)
        if "leafId" not in data:
            raise RpcProtocolError("get_entries did not return leafId")
        self.trace.event("entries", leaf_id=data["leafId"], count=len(data.get("entries", [])))
        return data

    def diagnostics(self) -> dict[str, Any]:
        return {"returncode": self.proc.poll() if self.proc else None, "stderr": self.trace.stderr[-20:]}

    def stop(self) -> None:
        if not self.proc:
            return
        if self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait(timeout=5)
        self._drain_stderr()
        self.trace.event("process_stopped", returncode=self.proc.returncode)
        self.trace.stopped_at = utcnow()


def require_quiescence(rpc: PiRpc, *, debug_events: list[dict[str, Any]], stability_seconds: float = 1.0) -> dict[str, Any]:
    """Frozen Gen25 completion boundary, after a real terminal OM debug event.

    The stability window only guards a race after terminal evidence; it cannot
    substitute for it.  A controller caller supplies parsed native debug events
    from the same session's OM debug log.
    """
    state = rpc.state()
    if state.get("isStreaming") or state.get("isCompacting"):
        raise RpcProtocolError("Pi has not settled (streaming or compacting)")
    if len(set(rpc.session_ids)) != 1:
        raise RpcProtocolError(f"session changed during normal interaction: {rpc.session_ids}")
    errors = [e for e in debug_events if e.get("event") == "observer.error" or "error" in e.get("event", "")]
    terminal = [e for e in debug_events if e.get("event") in {"observer.records", "reflector.records", "dropper.records", "observer.skipped", "reflector.skipped", "dropper.skipped"}]
    if errors:
        raise RpcProtocolError(f"OM debug error: {errors[-1]}")
    if not terminal:
        raise RpcProtocolError("OM has no auditable terminal debug stage")
    first = rpc.entries()
    time.sleep(stability_seconds)
    second = rpc.entries(since=first["leafId"])
    if first["leafId"] != second["leafId"] or second.get("entries"):
        raise RpcProtocolError("Pi ledger changed during post-terminal stability window")
    return {"session_id": state["sessionId"], "leaf_id": first["leafId"], "terminal_event": terminal[-1]["event"]}


PIPELINE_TERMINALS = {"dropper.waiting_for_reflection", "dropper.not_ready", "dropper.append"}
PIPELINE_STARTS = {"observer.start", "reflector.agent_start", "dropper.stage_start"}


def run_terminal(events: list[dict[str, Any]], run_id: str) -> dict[str, Any] | None:
    """Return the exact terminal event for one OM run, never a prior run."""
    scoped = [event for event in events if event.get("runId") == run_id]
    names = {event.get("event") for event in scoped}
    errors = [event for event in scoped if "error" in str(event.get("event"))]
    if errors:
        return errors[-1]
    # A reflector that was due must reach its result and the following dropper
    # decision.  The observer itself is not terminal in that case.
    if "reflector.agent_start" in names:
        if "reflector.result" not in names:
            return None
        return next((event for event in reversed(scoped) if event.get("event") in PIPELINE_TERMINALS), None)
    if "dropper.stage_start" in names:
        return next((event for event in reversed(scoped) if event.get("event") == "dropper.append"), None)
    return next((event for event in reversed(scoped) if event.get("event") in {"observer.records", "observer.empty"}), None)


def observation_barrier(
    rpc: PiRpc,
    *,
    read_debug: callable,
    baseline_debug_count: int,
    launch_guard_seconds: float = 2.0,
    terminal_timeout_seconds: float = 180.0,
    stability_seconds: float = 1.0,
    clock: callable = time.monotonic,
    sleeper: callable = time.sleep,
) -> dict[str, Any]:
    """Gen26 per-observation barrier for the just-completed live Pi turn.

    `baseline_debug_count` is captured immediately before that turn.  Therefore
    a terminal event from any earlier run cannot satisfy this barrier.
    """
    initial_state = rpc.state()
    if initial_state.get("isStreaming") or initial_state.get("isCompacting"):
        raise RpcProtocolError("Pi has not settled after observation turn")
    initial_leaf = rpc.entries()["leafId"]
    session_id = initial_state["sessionId"]
    guard_deadline = clock() + launch_guard_seconds
    launched: dict[str, Any] | None = None
    while clock() < guard_deadline:
        recent = read_debug()[baseline_debug_count:]
        starts = [event for event in recent if event.get("event") in PIPELINE_STARTS]
        if starts:
            launched = starts[0]
            break
        sleeper(0.05)
    if launched is None:
        sleeper(stability_seconds)
        later_state = rpc.state()
        later = rpc.entries(since=initial_leaf)
        if later_state["sessionId"] != session_id:
            raise RpcProtocolError("session changed during no-stage-due barrier")
        if later_state.get("isStreaming") or later_state.get("isCompacting") or later["leafId"] != initial_leaf or later.get("entries"):
            raise RpcProtocolError("ledger changed during no-stage-due barrier")
        return {"outcome": "no_consolidation_due", "session_id": session_id, "leaf_id": initial_leaf}

    run_id = launched.get("runId")
    if not isinstance(run_id, str):
        raise RpcProtocolError("native stage-start event lacks runId")
    terminal_deadline = clock() + terminal_timeout_seconds
    terminal: dict[str, Any] | None = None
    while clock() < terminal_deadline:
        terminal = run_terminal(read_debug()[baseline_debug_count:], run_id)
        if terminal is not None:
            break
        sleeper(0.05)
    if terminal is None:
        raise RpcProtocolError(f"timed out awaiting native terminal for run {run_id}")
    if "error" in str(terminal.get("event")):
        raise RpcProtocolError(f"OM terminal error for run {run_id}: {terminal}")
    # The newly completed run may legitimately have appended ledger entries.
    # Freeze the leaf *after* its terminal evidence, then guard only against a
    # subsequent race; comparing with the pre-run leaf would reject success.
    terminal_leaf = rpc.entries()["leafId"]
    sleeper(stability_seconds)
    later_state = rpc.state()
    later = rpc.entries(since=terminal_leaf)
    if later_state["sessionId"] != session_id:
        raise RpcProtocolError("session changed during post-terminal barrier")
    if later_state.get("isStreaming") or later_state.get("isCompacting"):
        raise RpcProtocolError("Pi active after native terminal")
    if later["leafId"] != terminal_leaf or later.get("entries"):
        raise RpcProtocolError("ledger changed during post-terminal stability guard")
    return {"outcome": "consolidation_terminal", "run_id": run_id, "terminal_event": terminal["event"], "session_id": session_id, "leaf_id": terminal_leaf}
