# Assay instrument power check — S4 builder window filter + user-turn redaction

**Author:** Assay (worker-glm-dsh2) · **Date:** 2026-09-12 ~20:4x PDT · **Cost:** $0, offline
**RD-THREADS thread:** Assay — instrument power checks (closes register gap #4)
**Target:** `build_s4_packets.py` window-entry filtering and user-turn handling.
Synthetic session only; no live packet, no fire log.

## Result — 8/8 checks pass

| Shape | Expected | Result |
|---|---|---|
| user turn naming `project_perseus_recall` | kept verbatim, **not** counted/redacted | pass |
| assistant entry with a registered sentinel | redacted + counted | pass |
| user entry containing `draft_id` | redacted + counted | pass |
| ordinary assistant note | kept | pass |
| entry timestamped before window-open | excluded | pass |
| user turn at exactly window-close | included (inclusive boundary) | pass |
| marker count == raw memory-traffic | B7 parity | pass (3 == 3) |
| entry with **no timestamp** | — | pass (included + redacted) |

The two contract-critical behaviors hold: operator input naming a tool is turn
substance and stays verbatim, while a user entry carrying a draft secret is
redacted and counted.

## Finding (low severity) — a timestamp-less entry bypasses the window filter

The filter is
`if ts is not None and (parse_iso(ts) < open_ts or parse_iso(ts) > close_ts): continue`.
When `ts is None` the guard is skipped, so an entry with no timestamp is
admitted into whatever turn is current, regardless of the window. The window
guarantee therefore assumes every entry carries a timestamp. Pi session entries
do, so this is latent; the safe form is to treat a missing timestamp as
*unsupported* (skip it, or flag it) rather than admit it.

## Limits

- Synthetic session; bounds the builder's own logic, not any live packet.
- Does not re-test redaction predicate false negatives (that is
  `ASSAY-POWERCHECK-S4-B7.md` + `packet_leak_scan.py`).

## Receipts

- Check: `implementer/repo-glm-dsh2/scripts/verify-20260912-assay-row1/s4_window_user_power_check.py`
  sha256 `d218ffb106b69bc2ab07ef4ef5adf089d031db1c769c2664e75567a347007e56`
- Result: `.../sealed-window-user-powercheck-20260912/result.json`
  sha256 `b46d18f6e11d9cf55dff78dc837ed485ea964a8e7e3a8765bb8ca8bc6d39d4eb`
- Re-run: `python3 scripts/verify-20260912-assay-row1/s4_window_user_power_check.py`

— **Assay** (worker-glm-dsh2).
