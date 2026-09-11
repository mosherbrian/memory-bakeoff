# cobalt-invoice

Invoice generation service for the cobalt billing stack: renders
invoices from ledger events and manages the export archive.

## Layout

- `docs/export-profile.md` — current export profile (authoritative)
- `config/export.json` — runtime export configuration (created at
  deploy)

## Configuration

Export runtime settings live in `config/export.json`. The current
export profile — format, retention, rounding — is recorded in
`docs/export-profile.md`; treat that document as the source of truth.
