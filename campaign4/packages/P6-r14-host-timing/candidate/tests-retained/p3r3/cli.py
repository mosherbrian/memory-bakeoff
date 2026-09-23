"""ADAPTED P6-r13 cli shim: the new core surface ships no CLI module.

Only helper used by the adapted P3 tests is ``ledger_packages`` (a trivial
projection over ``store.ledger_view()``, byte-identical logic to P3-r3
``src/cli.py``). CLI-driven subprocess tests are excluded from the adapted
set and recorded as a residual.
"""


def ledger_packages(store):
    out = {}
    for q, revs in store.ledger_view().items():
        for rev, rec in revs.items():
            out["%s-r%d" % (q, rev)] = rec
    return out
