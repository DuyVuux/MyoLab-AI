# Processing Profile Contract v0.1 — DAY40

## 1. Purpose

DAY40 establishes the **contract boundary** between the frozen QC research core (`qc-core-research-v0.1`) and later signal-processing implementations. It does not implement filters. It answers a more fundamental question: **under exactly which declared configuration, input context, eligibility state, and provenance may a processing operation run?**

The contract exists to prevent four classes of failure that are especially dangerous in sEMG research systems:

1. a legacy processing choice silently becoming a universal default;
2. preprocessing hiding acquisition failures or changing the meaning of QC evidence;
3. processing different datasets on incompatible grids/units without traceability;
4. tuning/adapting processing parameters on locked evaluation data.

The DAY40 highest defensible claim is `PROCESSING_PROFILE_CONTRACT_READY`. No filter is analytically verified by this day.

## 2. Upstream authority

DAY40 consumes, but does not modify, the following upstream boundaries:

- GATE C-R: `QC_RESEARCH_CORE_READY`;
- DAY31 `QualityEligibility` and `processing_permission` semantics;
- DAY33 public/synthetic research corpus metadata and split governance;
- DAY35 research-only QC threshold authority;
- DAY36 distinction between signal quality and distribution support;
- DAY38 frozen QC behavior hashes.

A DAY40 profile is therefore downstream configuration. It cannot reinterpret a QC FAIL as usable, convert an abstention into PASS, or override the quality gate.

## 3. Core architectural rule

```text
Raw/native signal
   │
   ├── immutable
   ├── explicit Fs
   ├── explicit unit
   ├── WindowIdentity / source provenance
   └── incoming mask
        │
        ▼
DAY31 QualityEligibility
        │
        ├── BLOCK_UNSUPPORTED_METRIC ──> no automatic processing
        ├── HOLD_FOR_REVIEW ──────────> no automatic processing
        ├── ABSTAIN ──────────────────> no automatic processing
        └── ALLOW_PROFILED_PROCESSING
                    │
                    ▼
          DAY40 Processing Profile
                    │
                    ├── explicit version
                    ├── deterministic fingerprint
                    ├── explicit runtime Fs/unit
                    ├── explicit transform enable/disable
                    ├── mask-not-delete
                    └── no locked-set fitting
```

The contract deliberately separates **permission to process** from **how to process**.

## 4. Profile identity

Every profile has:

- `profile_id` — stable logical identifier;
- `version` — semantic version;
- `config_fingerprint` — SHA-256 over canonical JSON excluding the fingerprint field itself;
- `claim_scope = RESEARCH_ONLY`;
- `site_binding = null` at DAY40;
- provenance references to the QC core, quality-gate contract and supporting evidence.

The fingerprint algorithm is frozen as `sha256-canonical-json-v1`:

1. remove `config_fingerprint`;
2. recursively sort object keys;
3. encode compact UTF-8 JSON;
4. SHA-256 the exact bytes;
5. prefix with `pprof_sha256_`.

This allows configuration equality to be checked without relying on YAML formatting, comments or key order.

## 5. Why the DAY40 active profile is preserve-only

The active entry profile is `research-native-grid-preserve-v0.1`. All transforms are explicitly declared but disabled:

- resampling: disabled;
- band-pass: disabled;
- notch: disabled;
- rectification: disabled;
- smoothing: disabled;
- normalization: disabled.

This is intentional. `research default` means **safe phase-entry behavior**, not `historically common DSP settings`.

The following are therefore not defaults:

- 20–450 Hz band-pass;
- 50 Hz notch;
- any fixed notch Q;
- 2 kHz resampling;
- MVC normalization;
- arbitrary envelope smoothing.

DAY41 and later days must produce analytical evidence before creating an executable profile that enables those operations.

## 6. Runtime protocol binding

The active profile uses `protocol_binding.mode = RUNTIME_EXPLICIT`.

At minimum, execution requires:

- `sampling_rate_hz`;
- `units`;
- `source_window_id`;
- `source_id`.

This prevents a profile from hiding assumptions such as `Fs=2000 Hz` or `unit=uV`. Optional protocol/domain references can be carried when available. Future protocol-specific profiles can tighten the required runtime fields without breaking this base contract.

## 7. Native grid versus processed grid

Raw and native data remain on the acquisition grid unless resampling is explicitly enabled. The required output metadata includes:

- `native_fs_hz`;
- `processed_fs_hz`;
- `is_resampled`.

If resampling is disabled:

```text
processed_fs_hz = native_fs_hz
is_resampled = false
```

If a later profile enables decimation, the profile must explicitly specify a method and anti-aliasing policy. DAY40 does not authorize a runtime function to invent a low-pass filter automatically based on convenience.

## 8. Band-pass contract

A band-pass step has explicit fields:

- method;
- `low_cut_hz`;
- `high_cut_hz`;
- filter order;
- phase mode;
- parameter origin;
- effect metadata.

Schema validation ensures an enabled step cannot omit these fields. Runtime semantic validation additionally checks:

```text
0 < low_cut_hz < high_cut_hz < native_fs_hz / 2
```

The last inequality is runtime-dependent and therefore cannot be fully expressed by static JSON Schema.

DAY40 does not say that a particular passband is physiologically or analytically correct. DAY41 owns that verification.

## 9. Notch contract

A notch step can only be enabled when `mains_frequency_hz` is explicit. There is no implicit 50 Hz or 60 Hz fallback.

An enabled notch must additionally declare exactly one width representation:

- `q_factor`, or
- `bandwidth_hz`.

The runtime contract checks that the notch frequency is below Nyquist.

This design protects two separate concepts:

- a country/site may commonly use 50 or 60 Hz power;
- the profile still needs explicit evidence/configuration before modifying a signal.

The first does not automatically authorize the second.

## 10. Rectification and smoothing

Rectification is represented by:

- `NONE`;
- `FULL_WAVE`;
- `HALF_WAVE`.

Smoothing is represented by:

- `NONE`;
- `MOVING_AVERAGE` with `window_ms`;
- `BUTTERWORTH_LOWPASS` with cutoff/order.

The schema ensures enabled methods carry the method-specific parameters. Timing and amplitude effects must be represented in step effect metadata. DAY43 will own implementation and boundary/mask behavior verification.

## 11. Normalization

Normalization is explicitly present in the profile contract even though DAY44 owns eligibility. This is necessary because an absent normalization block could otherwise be interpreted as an implementation default.

DAY40 rules:

- `fitting_allowed = false`;
- disabled normalization has `reference_id = null`;
- no MVC/reference is inferred;
- locked evaluation data cannot be used to learn or select a reference;
- unnormalized output remains in physical units.

Later enabling normalization must be coupled to DAY44 eligibility, not just a processing toggle.

## 12. Mask handling

DAY40 freezes:

```text
MASK_NOT_DELETE
RAW_IS_IMMUTABLE
```

A processing profile must preserve incoming mask alignment and cannot delete raw or masked samples. Later filter implementations may need to update an output mask because filtering near a masked boundary can contaminate neighboring output samples. If that occurs, the update must be provenance-backed; it cannot erase the original mask.

The active preserve profile uses `PRESERVE_MASK_NO_DELETION`.

## 13. Quality eligibility mapping

Automatic profile binding is allowed only when DAY31 says:

```text
processing_permission = ALLOW_PROFILED_PROCESSING
```

The runtime contract rejects:

- `BLOCK_UNSUPPORTED_METRIC`;
- `HOLD_FOR_REVIEW`;
- `ABSTAIN`.

This is intentionally stricter than allowing a DSP routine to run and then discarding the result. The forbidden computation itself can create misleading cached artifacts or accidental downstream reuse.

Manual review workflows may later authorize explicit reprocessing, but that is a workflow action and not a DAY40 automatic-profile behavior.

## 14. Distribution support

DAY39 froze distribution support at `INFORMATIONAL_RESEARCH_ONLY`. Therefore the base deterministic DSP profile sets:

```text
distribution_support_required = false
```

A `SHIFTED` status does not automatically block native-grid deterministic processing. This preserves the DAY36 invariant:

```text
DOMAIN SHIFT != SIGNAL QUALITY FAILURE
```

The contract nonetheless supports future capability-specific profiles with `distribution_support_required = true`. In that mode:

- `SUPPORTED` may proceed;
- `SHIFTED` holds for review;
- `UNKNOWN/NOT_EVALUATED` abstains.

No OOD score is created by DAY40.

## 15. Distribution-effect metadata

Every profile records expected effects on:

- sampling grid;
- spectral content;
- amplitude scale;
- timing;
- support reassessment requirement.

This metadata is not a substitute for analytical measurement. It is a declared contract useful for downstream evidence and for deciding whether a transformed representation still belongs to the same distribution context.

For the preserve-only profile every effect is `UNCHANGED`.

## 16. Required output metadata

DAY40 does not implement the full DAY45 `ProcessingManifest`, but it freezes the minimum information every later processing output must be able to supply:

- source window ID;
- profile ID/version;
- profile fingerprint;
- native and processed Fs;
- resampling flag;
- input/output unit;
- input/output hashes;
- mask reference;
- effect summary.

DAY45 can extend this into the full raw-to-processed provenance chain without redefining DAY40 identity semantics.

## 17. Public and synthetic protocols

DAY33 has verified public dataset sources and synthetic research corpora, but public raw payloads have not yet been acquired/executed. Consequently DAY40 does not create source-specific “validated” profiles for GRABMyo, Hyser, Mendeley or Cerqueira.

Their metadata instead informs the contract requirements:

- Fs can differ;
- units can differ;
- channel layouts can differ;
- profiles must be runtime-bound and versioned.

A future dataset-specific profile must reference actual acquired/canonicalized source metadata, not a table copied from research notes.

## 18. Failure semantics

DAY40 fail-closed conditions include:

- non-positive/missing Fs;
- missing/unsupported unit;
- upstream processing permission not `ALLOW_PROFILED_PROCESSING`;
- enabled step missing required parameters;
- notch enabled without explicit mains frequency;
- invalid band-pass ordering;
- Nyquist violation;
- decimation without explicit anti-aliasing policy;
- invalid config fingerprint;
- site-bound DAY40 profile;
- duplicate profile ID/version;
- any attempt to allow locked-set fitting or adaptive processing.

The expected behavior is a typed contract/runtime error, not a guessed fallback.

## 19. Security and data-integrity posture

DAY40 adds no network/API/database surface. Security-relevant rules are therefore primarily integrity controls:

- configuration is versioned and hashable;
- raw signal is immutable;
- no PHI or source path is required in profile configuration;
- only source/window identifiers are required for future lineage;
- site names are not embedded in processing profiles;
- locked evaluation fitting is forbidden.

This keeps profile files portable and safe to publish in the research portfolio.

## 20. Compatibility with later days

### DAY41
Can create a new profile version that enables band-pass only after analytical verification.

### DAY42
Can enable notch with explicit mains frequency and width/Q provenance.

### DAY43
Can implement rectification/smoothing/mask propagation while preserving the step contract.

### DAY44
Can enable normalization only after eligibility/reference validation.

### DAY45
Can build `ProcessingManifest` using the output metadata keys frozen here.

No later day should need to change the meaning of `profile_id`, `version`, `config_fingerprint`, native/processed grid separation, or QC permission binding.

## 21. Claim boundary

Passing DAY40 supports only:

> `PROCESSING_PROFILE_CONTRACT_READY`

It does **not** support:

- `BANDPASS_VERIFIED`;
- `NOTCH_VERIFIED`;
- `PREPROCESSING_CLINICALLY_VALIDATED`;
- `SITE_PROFILE_VALIDATED`;
- `PUBLIC_DATASET_PROCESSING_VALIDATED`;
- `MOTIONLAB_PROFILE_READY`.

Those claims require downstream implementation/evidence that does not exist on DAY40.
