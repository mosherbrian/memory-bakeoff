#!/usr/bin/env python3
"""Trivial mark-superseded-on-newer-write layer — the S7-3 probe.

A state layer must earn its existence, so this is the smallest thing that
could possibly work, measured before any of it is built (roadmap Phase-G
ban). A record carries a key: (scope, fact_type). When a newer write carries
the same key as a live original, the original is marked superseded and the
newer write answers for the key from then on. Any other newer write — a
near-neighbor distractor in a different scope — leaves the original alone.
No scoring, no merging, no similarity thresholds, no TTLs.
"""


class ThinLayer:
    def __init__(self):
        self.live = {}        # key -> newest record id answering for it
        self.superseded = {}  # original record id -> id of the write that displaced it

    @staticmethod
    def key_of(record):
        return (record["scope"], record["fact_type"])

    def on_write(self, record):
        """Apply a write. Returns True if it superseded a live original."""
        key = self.key_of(record)
        prev = self.live.get(key)
        if prev is None:
            self.live[key] = record["id"]
            return False
        self.superseded[prev] = record["id"]
        self.live[key] = record["id"]
        return True

    def decide(self, original, newer):
        """Would `newer` supersede `original` under this layer's rule?"""
        return self.key_of(original) == self.key_of(newer)
