"""A client disconnect must not abort the upstream for drain_on_disconnect classes.

FastFlowLM leaks a connection slot permanently on every aborted request; at its
cap it rejects everything while still reporting ``active (running)``. Measured
2026-08-26: two pi sessions wedged it within minutes. The gateway is the only
place that sees every summariser call, so it is where the abort gets absorbed.

These tests assert the DIFFERENCE the flag makes, so they fail if the detach
silently stops happening - a test that passes either way would be worthless.
"""

from __future__ import annotations

import asyncio

import httpx
import pytest

from igw.router.app import _drain_detached
from igw.router.config import ClassSpec


class FakeResponse:
    """Records whether it was closed, and how much was read before that."""

    def __init__(self, chunks: int = 3, hang: bool = False) -> None:
        self._chunks = chunks
        self._hang = hang
        self.closed = False
        self.read_chunks = 0

    async def aiter_raw(self):
        for _ in range(self._chunks):
            if self._hang:
                await asyncio.sleep(3600)
            self.read_chunks += 1
            yield b"data: {}\n\n"

    async def aclose(self) -> None:
        self.closed = True


def test_class_flag_defaults_off() -> None:
    """GPU classes must not inherit this: a discarded long generation would
    hold a GPU slot for minutes."""
    spec = ClassSpec(name="deep-coder", backend_model="qwen3.8-27b", footprint_gib=91)
    assert spec.drain_on_disconnect is False


def test_class_flag_can_be_set() -> None:
    spec = ClassSpec(
        name="npu-summarise",
        backend_model="qwen3-it:4b",
        footprint_gib=4,
        drain_on_disconnect=True,
    )
    assert spec.drain_on_disconnect is True


@pytest.mark.asyncio
async def test_drain_reads_to_completion_then_closes() -> None:
    """The whole point: the upstream sees a normal completion, not an abort."""
    r = FakeResponse(chunks=4)
    await _drain_detached(r.aiter_raw(), r, "npu-box")
    assert r.read_chunks == 4, "drain must consume the whole response"
    assert r.closed is True, "drain must still close the connection"


@pytest.mark.asyncio
async def test_drain_is_bounded_by_its_deadline() -> None:
    """Without a deadline this trades a leaked socket for a leaked task - the
    same bug one layer up.

    The drain must return BY ITSELF, on its own deadline. An earlier version of
    this test wrapped the call in asyncio.wait_for(), which supplied the bound
    externally - so it passed with the deadline deleted and proved nothing.
    The outer timeout here is generous and exists only to stop a hang; if the
    internal deadline is missing this raises TimeoutError and FAILS.
    """
    r = FakeResponse(hang=True)
    started = asyncio.get_running_loop().time()
    await asyncio.wait_for(
        _drain_detached(r.aiter_raw(), r, "npu-box", deadline_s=0.05), timeout=3
    )
    elapsed = asyncio.get_running_loop().time() - started
    assert elapsed < 1.0, f"drain ignored its own deadline (took {elapsed:.2f}s)"
    assert r.closed is True, "a timed-out drain must still close"


@pytest.mark.asyncio
async def test_drain_closes_even_when_upstream_errors() -> None:
    class Broken(FakeResponse):
        async def aiter_raw(self):
            raise httpx.ReadError("upstream died")
            yield b""  # pragma: no cover

    r = Broken()
    await _drain_detached(r.aiter_raw(), r, "npu-box")
    assert r.closed is True, "an errored drain must not leak the connection"
