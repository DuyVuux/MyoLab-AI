# DAY40 Open Questions and Decisions

## Frozen implementation decisions

1. DAY40 active research profile is preserve-only; no DSP transform is enabled.
2. Fingerprint algorithm is `sha256-canonical-json-v1`.
3. Runtime Fs and unit are mandatory.
4. Base deterministic profile does not require validated distribution support.
5. Locked evaluation may receive a pre-registered fixed profile, but profile fitting/tuning on locked data is forbidden.

## Open for downstream days

- DAY41: Which band-pass design and phase mode pass analytical verification?
- DAY42: Which notch design/width policy is analytically acceptable when mains is explicit?
- DAY43: How should filter edge contamination expand processed masks?
- DAY44: Which normalization reference types are eligible for which protocols?
- DAY45: Exact persistent ProcessingManifest schema/storage/event contract.

None of these open questions block the DAY40 contract.
