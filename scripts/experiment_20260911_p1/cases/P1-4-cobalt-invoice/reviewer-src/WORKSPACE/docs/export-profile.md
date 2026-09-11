# cobalt-invoice — export profile

Current export profile (2026-09 platform sign-off):

| setting | value | notes |
|---|---|---|
| `format` | pdf-a3 | PDF/A-3 with embedded ledger XML; finance audit requirement |
| `retention_days` | 90 | archive window before cold storage |
| `rounding` | bankers | line-item sums must use banker's rounding per the audit standard |

These values passed the September finance review and are the deployment
defaults. Changes require a fresh finance sign-off.

## Related

- Invoice templates are versioned under `templates/` (not part of this
  config).
- The archive uploader retries with backoff; no config needed here.
