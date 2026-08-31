"""Minimal progress shim for vendored MemBukkit raw retrieval."""
from __future__ import annotations


def emit(callback, phase, current, total, detail=""):
    if callback is not None:
        try:
            callback({"phase": phase, "current": current, "total": total, "detail": detail})
        except TypeError:
            callback(phase, current, total, detail)


def encode_with_progress(encoder, texts, on_progress=None):
    try:
        return encoder.encode(texts, normalize=True, show_progress=False)
    except TypeError:
        try:
            return encoder.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        except TypeError:
            return encoder.encode(texts)
