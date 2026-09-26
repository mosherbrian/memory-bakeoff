# Vault source availability — bounded cycle84 correction

Tern ·26 September2026 · read-only archive inspection, no extraction/build/run.

The path already recorded in `systems/perseus.md` exists:
`/var/home/bmosher/bakeoff-archive/perseus-vault/source/perseus-9c82920.tar.gz`.
Archive SHA256: `e5f3f6120030499b19917ef059b0474a4ac39f6d6ba42ed5dbd17ef24ecbf26f`.
Its `Cargo.toml` identifies `perseus-vault` version2.23.2. This is source availability, not a newly verified match to the running binary.

Direct reads were limited to Cargo metadata, `src/trust_admission.rs`, `docs/specs/memory-poisoning-admission-v1.md` and `docs/integration/ephemeral-admission-fixture.md`. Native admission documents approval transitioning pending evidence into admitted durable state, and validates approval reasons. These files do not establish that a Pi-facing agent-confirm tier disables draft expiration. Native approval is not evidence of the wrapper's lifetime configuration.

Thus Cairn's absent-artifact result is true for the inspected wheel directory, not the workspace/archive inventory. The no-expiry guarantee remains **unestablished**, with the unresolved target now correctly named: the configured Pi-wrapper confirmation/expiry path, or an explicitly identified native equivalent. No substitute identity, no product verdict from a missing search hit, no source modification.
