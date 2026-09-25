# T answer — P-INDEX-7 (ex-R24-T-w1)

## What I did
Ran the authorized next action via the local CLI only (from /var/home/bmosher/r24-arms/T):
```
python3 pindex_cli.py --action diagnose-index --owner tern --question Q-WORK-BENEFIT --arm T --execution ex-R24-T-w1 --docs fixtures/docs --out out
```
Exit 0. Produced `out/diagnosis.json`, `out/evidence.json`, `out/receipt.json`.

## Why
Step 2/4 `build_index` failed (exit 1): missing optional dependency `idx-extra==2.1`, no network to install. Per the T rule packet: diagnose before re-dispatching, do not blindly re-dispatch the known-broken step, and move to a concrete authorized next action with an owner actually started through the CLI. So I ran `diagnose-index` (owner: tern) rather than retrying `build_index`.

## Result
- `diagnosis.json`: cause = missing optional `idx-extra==2.1`, no network; bound = single local run, no network/install; failed step 2/4; next = `rebuild-noextra` over local docs without idx-extra.
- No network, installs, production changes, or R20 stamps. Scope: local files only. No permission denial or sponsor stop was indicated, so no escalation was recorded.
