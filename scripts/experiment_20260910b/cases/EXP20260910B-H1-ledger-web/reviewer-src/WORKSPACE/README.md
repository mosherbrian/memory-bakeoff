# ledger-web

Internal metrics dashboard (Node/TypeScript, no framework).

## Development

```
npm install
npm run dev          # starts on the port given in deploy/config.dev.json
npm run build
npm start            # expects deploy/config.<NODE_ENV>.json
```

## Configuration

The server reads its settings from `deploy/config.<NODE_ENV>.json`
(`host`, `port`, `tls`). There is no built-in default: a missing or
incomplete config file is a startup error, on purpose — per-environment
values are chosen explicitly, never assumed.

Environment configs are generated per deployment; this repo only carries
`deploy/config.dev.json` for local work.
