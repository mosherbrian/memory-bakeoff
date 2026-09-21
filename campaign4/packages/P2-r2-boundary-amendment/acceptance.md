# P2 r2.1 acceptance and freeze — Tern, 2026-09-21

**COMPLETE; specification accepted and frozen.** The authoritative director
boundary decision is `acceptance.json`, published with terminal state and
`successor_opened` together after P3's bounded admission wake was acknowledged.
This is a manual campaign record, not a claim that the future controller or
its live state projection has already been implemented.

Frozen source commit: `5bfbb071e6efdb6f15de1c582295363a94cd08c7`.

| Artifact | SHA256 |
|---|---|
| contract.md | 874354050fc81e3b366bcfe91904f1248c7248fd4927df025b28bc112840ef53 |
| transitions.md | 3afedd357aefa40e3d402d8038337a57e8dc87beabffe8f0ad0bcc58c4f211e2 |
| ownership.md | cd198c0b6343bc7b06a133b851178482f6b3374c836081c38d9aae7bb9006dcf |
| walkthrough.md | 12348310cd92208e10685bacb44fb2ce8b84f6bbcc89bdc078e97adba772ba69 |
| changes.md | c081291c67c7626f8cd93b830096b9ba81c2e13d41b00a7af06e0fc87c19ba22 |
| boundary-schema.md | ec6daf093b59ea6b970a694960305e64e05862e93b812536967d8a56a16bfaa8 |
| verification.md | 93263e9ab53c22db43b810e72bda169fc2b77c1e6b63281bd25fa30dc96297cc |

Tern read the resulting lifecycle, interface, ownership, contract, walkthrough,
change record and independent verification, then recomputed these hashes and
the true pre-repair changes artifact (`a4aa894b…`). The former gaps now have
explicit exhaustion and phase-preserving verification-resume rules. Terminal
closure requires an attributed disposition; successor chains and legitimate
rest are distinguished. The atomic boundary section governs the table's
terminal rows. INVALID is a validation fault, not a lifecycle terminal.

The documents define the accepted behavioral baseline and textual interface.
P3 must demonstrate its executable serialization and validator with adversarial
cases; these documents and illustrative examples are not themselves a running
validator, authenticated launcher, or proof of operational enforcement.

## Process deviation retained, not retroactively authorized

Cairn's archive correction was necessary and independently checked, and changed
no worker output. But its additional 20-minute re-verification allocation was
not authorized by Tern. The recovery rule allowed at most 10 minutes per pass,
inside remaining package allocations. A cumulative campaign ceiling did not
permit overriding that bound. From recorded correction 17:06:33Z to PASS
17:18:24Z is 11m51s, also beyond 10 minutes if measured on that basis.

I accept the artifact evidence after checking it; I do not certify this as a
budget-compliant recovery demonstration or rewrite its timestamps. P3 includes
explicit phase/incident allocation enforcement and rejects that inference.
Future extensions require a prospective, recorded Tern decision.

## Successor opened at this boundary

`P3-core-validator` is warranted and explicitly allocated: implement the
deterministic lifecycle core, durable events, fake executor and boundary
validator with standard-library tests. Corvid's independent admission is in
flight with an acknowledged receipt and absolute deadline; see its
`admission-receipt.json`. Cairn may dispatch only on accepted admission of the
exact contract and this freeze, under `P3-core-validator/admission-dispatch.md`.

No live watcher, state.json, agent adapter, service change or research run is
authorized by this freeze. The provisional contract template is superseded by
the frozen contract linked above; preserve it as historical source.
