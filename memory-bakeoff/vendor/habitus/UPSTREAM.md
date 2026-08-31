# Vendored Habitus core

Source: `munch2u-a11y/Habitus-AI`

Pinned upstream commit: `f93b770e4b3c1875151dc13eb90421598c3efa5f` (2026-08-28)

The benchmark vendors only the dependency-free runtime modules required by
`HabitusAI.remember()` / `HabitusAI.recall()`.  Their Git blob hashes are checked
against upstream:

| file | upstream Git blob SHA |
|---|---|
| `embeddings.py` | `d6ab2d5920d42462b267c0b05d374704f7ad81cf` |
| `types.py` | `d3b07d403e89bbb580658d3ea369f9f426177697` |
| `context.py` | `e0baf1484e02daaa668f9435d0a9982c6d5765c0` |
| `surface.py` | `7ce52ada22090538302fad0bcecdc998dfbcf222` |
| `working_memory.py` | `84d9cff079c6de3758cbee9382f3185266def5c0` |
| `store.py` | `dde73a57fe33fd6fa9ec81c585af900f71466620` |
| `graph.py` | `9540fd5b0ad5d4078ece2ea9c86a3bd3e469c8ed` |
| `retrieval.py` | `85384c37b697fdf78db71bff51c73552eed0a399` |
| `pipeline.py` | `165e2c8b4e4e9a37913ad43fa0acee408fb3723a` |

`src/habitus_ai/__init__.py` is intentionally a benchmark-local shim that exports
only the memory pipeline.  Upstream's package initializer also imports the UI,
audio, agent, Ollama model, tools, and vector-adapter modules; none participates
in the raw memory-engine benchmark.

To verify the vendored files locally:

```bash
cd vendor/habitus/src/habitus_ai
git hash-object embeddings.py types.py context.py surface.py working_memory.py \
  store.py graph.py retrieval.py pipeline.py
```
