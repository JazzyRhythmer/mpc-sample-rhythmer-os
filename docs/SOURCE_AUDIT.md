# Source audit

The runtime and port sources are pinned in SOURCE_LOCK.json. Prebuilt artifact identity, download size and checksum are recorded in config/releases.lock.json. Port-specific changes are documented in ports/*/VENDORED.md.

The runtime supports sixteen tracks. The sampler's original per-track pool has 32 live and eight spare/fade slots. No new global 32-voice policy is introduced. Plugin voice counts remain engine-specific.

Existing sample-base startup/recovery, bounded command paths and plugin lifecycle boundaries are retained. The third-party Open MPC wrapper uses its original mutex; hard real-time compliance is not asserted.

Rhythmer musical source snapshots, GPL notice and hashes are in third_party/jiant-gen. Native adaptation coverage is described in GEN8_BREAK.md. No proprietary ROM or bundled break audio is supplied.

Offline validation results are in VERIFICATION.md. Full asset/dependency redistribution review and real-device validation remain separate gates.
