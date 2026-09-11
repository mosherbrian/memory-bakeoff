# Contributing to wrenfmt

## Releases

When bumping the version for a release, update it in exactly three places:

1. `pyproject.toml` — `project.version`
2. `src/wrenfmt/_version.py` — `__version__`
3. `docs/conf.py` — `release`

Nothing else in the repo carries the version string. The README badge and
the changelog derive from a release tag at publish time and are never
edited by hand.

## Style

Python follows `ruff check` + `ruff format` defaults (see CI config).
