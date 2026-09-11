# atlas-backfill

Nightly + ad-hoc backfill runner for the atlas event pipeline.

## Usage

```
./backfill run --shard <shard-id>          # backfill a single shard
./backfill run --shard <a> --shard <b>     # several shards, sequential
./backfill status                          # per-shard sync state
```

A shard is a month partition (`YYYY-MM`). Shards are listed in `shards.list`;
`state.json` is the runner's local view of what is current.

Bulk runs write through the standard bulk writer path. Utilities that don't
ship with this repo live in the team scripts repo.
