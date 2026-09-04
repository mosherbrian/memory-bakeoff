"""Gen40 MemBukkit intended-model reproduction contract.

Evidence class: ``product_identity_reproduction_no_score``.

This module establishes *identity*, not accuracy. It carries the fixed
synthetic fixture (written before any model output was observed), the
fallback-detection instrumentation, the content-identity helpers used to pin
Hugging Face revisions, and the leaf digest. Nothing here reads a benchmark
corpus, and no function in this module produces a comparable score.
"""
from __future__ import annotations

import hashlib
import json
import socket
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

# --- upstream identity, from research/MEMBUKKIT_INTENDED_MODEL_GEN7.md -------

MEMBUKKIT_PINNED_COMMIT = "f28a2e58cdc0e77758c0f6d9a1e050f80dcad807"

INTENDED_ENCODER_REPO = "MemseekAI/membukkit-biencoder-v1"
INTENDED_RERANKER_REPO = "MemseekAI/membukkit-reranker-v2"
INTENDED_REPOS = (INTENDED_ENCODER_REPO, INTENDED_RERANKER_REPO)

# The substitutes the pinned resolver falls back to when the intended repos are
# unreachable. Loading either during an intended-path claim is FAIL, not pass.
FALLBACK_ENCODER = "sentence-transformers/all-mpnet-base-v2"
FALLBACK_RERANKER = "cross-encoder/ms-marco-MiniLM-L-6-v2"
FALLBACK_IDS = frozenset({FALLBACK_ENCODER, FALLBACK_RERANKER})


class FallbackDetected(RuntimeError):
    """A substitute model was requested or loaded during an intended-path claim."""


class BlockedNetwork(RuntimeError):
    """An outbound connection was attempted while the offline claim was active."""


# --- content identity --------------------------------------------------------


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_blob_sha1(path: Path) -> str:
    """Git blob object id, so non-LFS files can be pinned to a repo revision.

    Hugging Face reports ``lfs.sha256`` for large files but only the git blob
    ``oid`` for small ones. Recomputing that oid locally pins every file in a
    snapshot to an exact revision without downloading it twice.
    """
    data = path.read_bytes()
    h = hashlib.sha1()
    h.update(b"blob %d\0" % len(data))
    h.update(data)
    return h.hexdigest()


def snapshot_identity(root: Path) -> Dict[str, Dict[str, Any]]:
    """Per-file size, sha256 and git blob oid for every file in a snapshot."""
    out: Dict[str, Dict[str, Any]] = {}
    for p in sorted(root.rglob("*")):
        if not p.is_file() or ".cache" in p.parts or ".git" in p.parts:
            continue
        out[p.relative_to(root).as_posix()] = {
            "size": p.stat().st_size,
            "sha256": sha256_file(p),
            "git_oid": git_blob_sha1(p),
        }
    return out


def reconcile_snapshot(
    local: Dict[str, Dict[str, Any]], remote: Dict[str, Dict[str, Any]]
) -> Dict[str, Any]:
    """Match a downloaded snapshot against a revision's published file identity.

    ``remote`` maps filename -> {"lfs_sha256": str|None, "oid": str|None}. A
    file matches when its LFS sha256 matches, or, for non-LFS files, when its
    git blob oid matches. Files present locally but absent from the revision
    listing are reported, never silently ignored.
    """
    matched, mismatched, unlisted = [], [], []
    for name, got in sorted(local.items()):
        want = remote.get(name)
        if want is None:
            unlisted.append(name)
            continue
        if want.get("lfs_sha256"):
            ok = want["lfs_sha256"] == got["sha256"]
        elif want.get("oid"):
            ok = want["oid"] == got["git_oid"]
        else:
            ok = False
        (matched if ok else mismatched).append(name)
    return {
        "matched": matched,
        "mismatched": mismatched,
        "local_only": unlisted,
        "remote_only": sorted(set(remote) - set(local)),
        "all_match": not mismatched and not unlisted,
    }


# --- fallback detection ------------------------------------------------------


@dataclass
class LoadTrace:
    """Everything the run asked for and everything it actually loaded."""

    resolver_calls: List[Dict[str, str]]
    downloads: List[str]
    loads: List[Dict[str, str]]

    def fallback_events(self) -> List[Dict[str, str]]:
        hits: List[Dict[str, str]] = []
        for call in self.resolver_calls:
            if call["returned"] in FALLBACK_IDS:
                hits.append({"stage": "resolver", "value": call["returned"]})
        for repo in self.downloads:
            if repo in FALLBACK_IDS:
                hits.append({"stage": "download", "value": repo})
        for load in self.loads:
            if load["target"] in FALLBACK_IDS:
                hits.append({"stage": load["kind"], "value": load["target"]})
        return hits

    def assert_intended_only(self, allowed_roots: List[str]) -> None:
        events = self.fallback_events()
        if events:
            raise FallbackDetected(f"substitute models used: {events}")
        for load in self.loads:
            target = load["target"]
            if not any(target.startswith(root) for root in allowed_roots):
                raise FallbackDetected(
                    f"{load['kind']} loaded {target!r}, which is not a pinned snapshot"
                )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "resolver_calls": self.resolver_calls,
            "downloads": self.downloads,
            "loads": self.loads,
            "fallback_events": self.fallback_events(),
        }


@contextmanager
def trace_loads() -> Iterator[LoadTrace]:
    """Observe the resolver, the hub and both model constructors.

    Observation only: every wrapper forwards to the original and records what
    passed through it, so embeddings and ranking cannot be affected.
    """
    import huggingface_hub
    import sentence_transformers
    from membukkit.models import registry

    trace = LoadTrace(resolver_calls=[], downloads=[], loads=[])

    orig_enc = registry.resolve_encoder_path
    orig_rer = registry.resolve_reranker_path
    orig_dl = huggingface_hub.snapshot_download
    orig_st = sentence_transformers.SentenceTransformer.__init__
    orig_ce = sentence_transformers.CrossEncoder.__init__

    def wrap_resolver(fn, role, intended):
        def inner(config):
            got = fn(config)
            trace.resolver_calls.append(
                {"role": role, "intended_repo": intended, "returned": str(got)}
            )
            return got

        return inner

    def wrap_dl(*a, **kw):
        repo = kw.get("repo_id") or (a[0] if a else "")
        trace.downloads.append(str(repo))
        return orig_dl(*a, **kw)

    def wrap_st(self, model_name_or_path=None, *a, **kw):
        trace.loads.append({"kind": "biencoder", "target": str(model_name_or_path)})
        return orig_st(self, model_name_or_path, *a, **kw)

    def wrap_ce(self, model_name=None, *a, **kw):
        trace.loads.append({"kind": "reranker", "target": str(model_name)})
        return orig_ce(self, model_name, *a, **kw)

    registry.resolve_encoder_path = wrap_resolver(
        orig_enc, "encoder", INTENDED_ENCODER_REPO
    )
    registry.resolve_reranker_path = wrap_resolver(
        orig_rer, "reranker", INTENDED_RERANKER_REPO
    )
    huggingface_hub.snapshot_download = wrap_dl
    registry.snapshot_download = wrap_dl  # if the module imported it directly
    sentence_transformers.SentenceTransformer.__init__ = wrap_st
    sentence_transformers.CrossEncoder.__init__ = wrap_ce
    try:
        yield trace
    finally:
        registry.resolve_encoder_path = orig_enc
        registry.resolve_reranker_path = orig_rer
        huggingface_hub.snapshot_download = orig_dl
        if hasattr(registry, "snapshot_download"):
            del registry.snapshot_download
        sentence_transformers.SentenceTransformer.__init__ = orig_st
        sentence_transformers.CrossEncoder.__init__ = orig_ce


def block_network() -> None:
    """Fail closed on any non-local outbound connection, permanently.

    Used by the offline repeat so that "it ran from the frozen snapshot" is
    proved rather than asserted: a silent re-download would raise here.
    """
    orig = socket.socket.connect
    orig_ex = socket.socket.connect_ex

    def guard(sock, address, *a, **kw):
        host = address[0] if isinstance(address, tuple) else str(address)
        if host not in ("127.0.0.1", "::1", "localhost"):
            raise BlockedNetwork(f"outbound connection to {host!r} while offline")
        return orig(sock, address, *a, **kw)

    def guard_ex(sock, address, *a, **kw):
        host = address[0] if isinstance(address, tuple) else str(address)
        if host not in ("127.0.0.1", "::1", "localhost"):
            raise BlockedNetwork(f"outbound connection to {host!r} while offline")
        return orig_ex(sock, address, *a, **kw)

    socket.socket.connect = guard
    socket.socket.connect_ex = guard_ex


# --- fixed synthetic fixture -------------------------------------------------
#
# Invented content about a fictional society, chosen before any model output
# was observed, and unrelated to every benchmark corpus in this repo. Its only
# job is to make the intended models run end to end and to give each returned
# item an exact receipt to map back to.

SUBJECT = "ashfell-synthetic"

SYNTHETIC_FACTS: Tuple[Dict[str, str], ...] = tuple(
    {"fact_id": f"SYN-{i:04d}", "text": text, "timestamp": ts}
    for i, (text, ts) in enumerate(
        [
            ("The Ashfell Lighthouse Preservation Society meets on the first Tuesday of each month.", "2031-01-07"),
            ("Marek Olsztyn keeps the society's lamp-oil ledger.", "2031-01-07"),
            ("The society's founding charter was signed in the harbourmaster's office.", "2031-01-14"),
            ("The Ashfell lamp room holds a fourth-order Fresnel lens.", "2031-01-21"),
            ("The lens was re-bedded in cork gaskets during the winter overhaul.", "2031-01-28"),
            ("Brass fittings in the lamp room are polished with rottenstone paste.", "2031-02-04"),
            ("The society stores rottenstone in the tool crib behind the boat shed.", "2031-02-04"),
            ("Ida Vensdal drafted the lamp-room ventilation survey.", "2031-02-11"),
            ("The ventilation survey found the flue draught weakest in still weather.", "2031-02-11"),
            ("A copper cowl was fitted to the flue to correct the draught.", "2031-02-18"),
            ("The keeper's cottage roof is slate laid in diminishing courses.", "2031-02-25"),
            ("Slate for repairs comes from the Braedon quarry.", "2031-02-25"),
            ("The Braedon quarry supplies the society at a preservation discount.", "2031-03-04"),
            ("The society's boat is a fourteen-foot clinker-built dinghy called Wren.", "2031-03-11"),
            ("Wren is hauled out for scraping every March.", "2031-03-11"),
            ("Tobias Grell repairs Wren's oarlocks.", "2031-03-18"),
            ("The dinghy's hull is painted with red lead primer below the waterline.", "2031-03-18"),
            ("The society's archive is kept in acid-free boxes in the cottage attic.", "2031-03-25"),
            ("The archive contains keeper's logs from 1874 onward.", "2031-03-25"),
            ("The 1874 logs record a three-week fog in November.", "2031-04-01"),
            ("Fog signal duty was rotated in six-hour watches.", "2031-04-01"),
            ("The original fog bell was recast after a hairline crack.", "2031-04-08"),
            ("The recast bell carries the foundry mark of Hollis and Sons.", "2031-04-08"),
            ("Hollis and Sons closed its foundry in 1936.", "2031-04-15"),
            ("The society funds itself through an annual open day.", "2031-04-22"),
            ("The open day includes tours of the lamp room in groups of eight.", "2031-04-22"),
            ("Ticket proceeds are split between the lamp fund and the archive fund.", "2031-04-29"),
            ("The lamp fund pays for wick trimming supplies and lens cleaning.", "2031-05-06"),
            ("The archive fund pays for document conservation.", "2031-05-06"),
            ("Conservation work is done by a bindery in the cathedral quarter.", "2031-05-13"),
            ("The bindery repairs the logs with Japanese tissue and wheat starch paste.", "2031-05-13"),
            ("Wheat starch paste is mixed fresh and discarded after two days.", "2031-05-20"),
            ("The society bans adhesive tape anywhere near the archive.", "2031-05-20"),
            ("Nell Ardwick coordinates volunteer rotas.", "2031-05-27"),
            ("Volunteer rotas are published four weeks ahead.", "2031-05-27"),
            ("New volunteers complete a ladder-safety briefing before lamp-room work.", "2031-06-03"),
            ("The lamp-room ladder has forty-one rungs.", "2031-06-03"),
            ("The rungs were replaced in oak after the iron ones pitted.", "2031-06-10"),
            ("Salt spray is the main cause of corrosion on the tower ironwork.", "2031-06-10"),
            ("Ironwork is repainted every third summer.", "2031-06-17"),
            ("The tower is painted with two coats of oil-based enamel.", "2031-06-17"),
            ("Enamel is applied only when humidity stays below seventy percent.", "2031-06-24"),
            ("The society records humidity with a hair hygrometer in the lamp room.", "2031-06-24"),
            ("The hygrometer is calibrated against a sling psychrometer each spring.", "2031-07-01"),
            ("Calibration records live in the same attic archive.", "2031-07-01"),
            ("The society's constitution requires a quorum of seven for votes.", "2031-07-08"),
            ("Votes on capital spending require a two-thirds majority.", "2031-07-08"),
            ("A capital vote approved the cowl and the ladder in one motion.", "2031-07-15"),
            ("Minutes are typed and countersigned by the chair.", "2031-07-15"),
            ("Petra Lindqvist chairs the society.", "2031-07-22"),
            ("The chair serves a two-year term.", "2031-07-22"),
            ("The society keeps a spare lens prism in a padded case.", "2031-07-29"),
            ("The spare prism was donated by a retired keeper.", "2031-07-29"),
            ("Donated items are accessioned with a numbered label.", "2031-08-05"),
            ("Accession labels are written in pencil, never ink.", "2031-08-05"),
            ("The society's insurance covers the archive at replacement value.", "2031-08-12"),
            ("Insurance renewal falls due in September.", "2031-08-12"),
            ("The renewal survey inspects the cottage electrics.", "2031-08-19"),
            ("Cottage electrics were rewired in armoured cable.", "2031-08-19"),
            ("The rewiring included a dedicated circuit for the lamp room.", "2031-08-26"),
        ]
    )
)

SYNTHETIC_QUERIES: Tuple[Dict[str, str], ...] = (
    {"qid": "Q1", "text": "Who keeps the lamp-oil ledger?", "kind": "on_topic"},
    {"qid": "Q2", "text": "How is the archive paper repaired?", "kind": "on_topic"},
    {"qid": "Q3", "text": "What fixed the weak flue draught?", "kind": "on_topic"},
    {"qid": "Q4", "text": "Where does the slate for roof repairs come from?", "kind": "on_topic"},
    {"qid": "Q5", "text": "What are the rules for a capital spending vote?", "kind": "on_topic"},
    {"qid": "Q6", "text": "How is the tower ironwork protected from corrosion?", "kind": "on_topic"},
    {"qid": "Q7", "text": "What is the boiling point of gallium in kelvin?", "kind": "unrelated"},
    {"qid": "Q8", "text": "Which compiler flag enables link-time optimisation?", "kind": "unrelated"},
)

PROBE_TEXTS: Tuple[str, ...] = (
    "The lamp room ladder was rebuilt in oak.",
    "Wheat starch paste must be mixed fresh.",
    "The fog bell was recast by Hollis and Sons.",
    "Humidity is measured with a hair hygrometer.",
)
PROBE_QUERY = "How is the bell marked?"


# --- leaf digest -------------------------------------------------------------

_VOLATILE_KEYS = frozenset(
    {
        "wall_clock_seconds",
        "started_at",
        "finished_at",
        "download_seconds",
        "elapsed",
        "timings",
        "generated_at",
    }
)


def _strip_volatile(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _strip_volatile(v) for k, v in sorted(obj.items()) if k not in _VOLATILE_KEYS}
    if isinstance(obj, list):
        return [_strip_volatile(v) for v in obj]
    return obj


def leaf_digest(payload: Dict[str, Any]) -> str:
    """Deterministic digest of a result leaf, with wall-clock excluded.

    The payload is normalised through JSON first, so a digest taken in memory
    and one taken after reading the artifact back agree — int dict keys and
    tuples would otherwise diverge across the round trip.
    """
    stripped = _strip_volatile(json.loads(json.dumps(payload, sort_keys=True)))
    return hashlib.sha256(
        json.dumps(stripped, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def load_json(path: Path) -> Dict[str, Any]:
    """Read a result file, raising rather than returning an empty default."""
    if not path.exists():
        raise FileNotFoundError(f"required Gen40 artifact missing: {path}")
    return json.loads(path.read_text())


def contract_sha256() -> str:
    """Identity of this contract module."""
    return sha256_file(Path(__file__))
