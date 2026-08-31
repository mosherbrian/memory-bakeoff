"""Local no-op telemetry shim for the vendored MemBukkit raw benchmark.

The upstream retrieval/storage code calls these hooks only for observability. This shim
keeps the semantic path intact without pulling OpenTelemetry extras into the isolated
benchmark container.
"""
from __future__ import annotations
from contextlib import contextmanager

class _Counter:
    def add(self, *args, **kwargs):
        return None

class _Span:
    def set_attribute(self, *args, **kwargs):
        return None
    def record_exception(self, *args, **kwargs):
        return None

class _Histogram:
    def record(self, *args, **kwargs):
        return None


def counter(*args, **kwargs):
    return _Counter()


def histogram(*args, **kwargs):
    return _Histogram()


def set_attributes(span, **kwargs):
    return None


@contextmanager
def span(*args, **kwargs):
    yield _Span()


@contextmanager
def timed(*args, **kwargs):
    yield _Span()


def capture_content():
    return False
