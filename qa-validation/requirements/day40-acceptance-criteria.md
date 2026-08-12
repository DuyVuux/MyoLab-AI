# DAY40 Acceptance Criteria

DAY40 is PASS only if all conditions below hold.

- [ ] `configs/processing/preprocessing-profiles.v0.1.yaml` exists.
- [ ] `packages/common-schemas/json/processing-profile.schema.json` is Draft 2020-12 and valid.
- [ ] `docs/03-architecture/processing-profile-contract.md` exists.
- [ ] At least one `ACTIVE_RESEARCH` profile exists.
- [ ] Active DAY40 profile has `site_binding: null`.
- [ ] Active DAY40 profile enables zero unverified transforms.
- [ ] Fs and unit are runtime-required; no fallback values exist.
- [ ] Notch cannot be enabled without explicit mains frequency.
- [ ] Resampling cannot be enabled without explicit target/method/anti-alias policy.
- [ ] Runtime Nyquist checks are enforced.
- [ ] QC permissions other than `ALLOW_PROFILED_PROCESSING` reject automatic binding.
- [ ] Locked-partition fitting and adaptive processing are false.
- [ ] Incoming mask is preserved; raw deletion is false.
- [ ] Fingerprint recomputation matches embedded fingerprint.
- [ ] DAY38 frozen QC hashes remain unchanged.
- [ ] Focused tests PASS.
- [ ] Applicable upstream regression PASS.
- [ ] Claim boundary remains `RESEARCH_ONLY` / `PROCESSING_PROFILE_CONTRACT_READY`.
