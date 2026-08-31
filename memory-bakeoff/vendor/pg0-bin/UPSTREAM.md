# pg0 binary provenance

Preserved solely to make the Hindsight service/runtime experiment reproducible in this
network-isolated sandbox.

- Upstream: `vectorize-io/pg0`
- Release: `v0.15.1`
- Release commit: `e68cbf52921cb5efd595dbd12b883b9cc29980ee`
- GitHub Actions release run: `30660347265`
- Artifact: `cli-linux-x86_64-gnu` (`8804934259`)
- Binary: `pg0-linux-x86_64-gnu`
- Reported version: `pg0 0.15.1`
- SHA-256: `3b2a129c761ed371dfb0908e227bc90e652a7d60d8bcc1be037c3767f855b91f`

The Actions artifact was still live when transferred and was scheduled to expire on
2026-10-29. The checksum matches the corresponding upstream Linux x86_64 GNU release
binary digest.

Smoke validation in this sandbox (run as unprivileged user `oai`):

- pg0 unpacked PostgreSQL 18.1;
- pgvector 0.8.5 was available;
- a localhost instance accepted `SELECT version()`;
- shutdown completed cleanly.

PostgreSQL intentionally refuses `initdb` as root, so future smoke/service runs should
also launch pg0 under an unprivileged user.
