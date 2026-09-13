"""Portfolio P2 arm composition (charter Patch 3, G0-approved).

One place declares the locked baseline arms and the entry path each uses,
so the P2 run matrix composes arms by name and nothing enters through a
bespoke side door:

- ``longcontext_null``  — engine ``search(question)`` shape: the row-4
  instrument, run by the memconflict-side scorer directly. It is not a
  memory system and never enters the provider registry.
- ``pi_lcm_store_reader`` — provider interface (``PROVIDERS`` registry,
  controlled core: corpus materialized into the exact pi-lcm schema).
- ``pi_lcm_history_null`` — provider interface (the SAME materialization
  presented as raw history via ``LongContextNull`` itself).

The memconflict benchmark dataset is materialized and triple-pin-verified
(commit `ec51d5d…`, blob `6dcbf9e5…`, sha256 `8ef9ec…`; receipt
`docs/PORTFOLIO-P1-discovery/MEMCONFLICT-MATERIALIZATION.md`, 2026-09-13).
This module composes the arms; executing the run matrix is the P2 turn.
"""
from __future__ import annotations

from memory_bakeoff.longcontext_null import ARM_VERSION as LONGCONTEXT_NULL_VERSION

PROVIDER_ARMS: dict[str, str] = {
    "pi_lcm_store_reader": "controlled_core",
    "pi_lcm_history_null": "baseline",
}

ENGINE_ARMS: dict[str, str] = {
    "longcontext_null": LONGCONTEXT_NULL_VERSION,
}

LOCKED_BASELINE_ARMS: tuple[str, ...] = (
    "longcontext_null",
    "pi_lcm_store_reader",
    "pi_lcm_history_null",
)


def validate_composition() -> dict:
    """Check the declaration against the live registry and classes.

    Raises RuntimeError on any drift (renamed arm, changed experiment
    class, engine version change) so a P2 run cannot silently compose a
    different portfolio than the charter locked.
    """
    from memory_bakeoff.longcontext_null import LongContextNull
    from memory_bakeoff.providers import PROVIDERS

    problems: list[str] = []
    for name, expected_class in PROVIDER_ARMS.items():
        if name not in PROVIDERS:
            problems.append(f"{name}: missing from the PROVIDERS registry")
            continue
        provider = PROVIDERS[name]()
        actual = provider.experiment_class("raw")
        if actual != expected_class:
            problems.append(f"{name}: experiment_class {actual!r} != declared {expected_class!r}")
    if LONGCONTEXT_NULL_VERSION != ENGINE_ARMS.get("longcontext_null"):
        problems.append(f"longcontext_null: ARM_VERSION {LONGCONTEXT_NULL_VERSION!r} drifted from declaration")
    if LongContextNull.search.__doc__ is None:  # pragma: no cover - structural sanity
        problems.append("longcontext_null: search shape unavailable")
    for arm in LOCKED_BASELINE_ARMS:
        if arm not in PROVIDER_ARMS and arm not in ENGINE_ARMS:
            problems.append(f"{arm}: locked baseline has no declared entry path")
    if problems:
        raise RuntimeError("portfolio composition drift: " + "; ".join(problems))
    return {
        "provider_arms": dict(PROVIDER_ARMS),
        "engine_arms": dict(ENGINE_ARMS),
        "locked_baseline_arms": list(LOCKED_BASELINE_ARMS),
    }
