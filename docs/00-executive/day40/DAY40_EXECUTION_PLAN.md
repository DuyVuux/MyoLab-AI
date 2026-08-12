# DAY40 EXECUTION PLAN — Protocol-Specific Preprocessing Profile Contract

## 0. Document Control

| Field | Value |
|---|---|
| Day | DAY40 |
| Phase | Phase 3R — Versioned Processing, Metric & Evidence Engine |
| Task | Protocol-Specific Preprocessing Profile Contract |
| Upstream gate | GATE C-R |
| Upstream status | `QC_RESEARCH_CORE_READY` |
| Claim scope | `RESEARCH_ONLY` |
| Highest allowed claim | `PROCESSING_PROFILE_CONTRACT_READY` |
| Clinical/site validation | `NOT_PERFORMED` |

## 1. Executive Intent

DAY40 is the entry contract for the signal-processing phase. The purpose is **not** to implement a traditional EMG filter chain. The purpose is to make it impossible for later code to silently assume a sampling frequency, power-line frequency, resampling grid, normalization reference, or legacy passband.

The day creates three mandatory outputs:

- `configs/processing/preprocessing-profiles.v0.1.yaml`;
- `packages/common-schemas/json/processing-profile.schema.json`;
- `docs/03-architecture/processing-profile-contract.md`.

Supporting implementation adds a deterministic profile fingerprint and runtime binding validator, but performs zero signal filtering.

## 2. Why DAY40 Exists

Before Phase 3R, the project has a frozen QC core with strict fail-closed behavior. Processing now becomes the next source of risk. A filter can make a waveform visually cleaner while simultaneously hiding dropout edges, attenuating physiologically meaningful low-amplitude activity, introducing phase delay, or changing the grid so provenance is lost.

Therefore the first processing day freezes **configuration semantics before DSP implementation**.

## 3. Critical Path

```text
GATE C-R
  ↓
DAY31 QualityEligibility
  ↓
DAY40 profile identity + runtime binding
  ↓
DAY41 band-pass analytical verification
  ↓
DAY42 notch verification
  ↓
DAY43 rectification/smoothing/mask handling
  ↓
DAY44 normalization eligibility
  ↓
DAY45 processing provenance
```

## 4. Inputs

### Required

1. `docs/00-executive/gates/GATE-C-R-qc-research-readiness.md`
2. `packages/common-schemas/json/quality-eligibility.schema.json`
3. `services/quality-gate-service/src/application/quality_gate.py`
4. `qa-validation/evidence/research-benchmark-corpus-v0.1.manifest.yaml`
5. `configs/qc/thresholds.research-v0.1.yaml`
6. `qa-validation/evidence/day38-qc-freeze-manifest.v0.2.json`
7. `qa-validation/test-data/ood-challenge-set-manifest.v0.2-research.yaml`

### Input authority assumptions

- GATE C-R must contain `QC_RESEARCH_CORE_READY`.
- DAY38 hashes must still match.
- Site thresholds remain `NOT_VERIFIED`.
- Distribution support remains informational only.

## 5. Non-Goals

DAY40 does not:

- implement a band-pass filter;
- verify 20–450 Hz or any alternative passband;
- enable a 50/60 Hz notch;
- rectify a waveform;
- create an envelope;
- resample raw data;
- normalize to MVC;
- fit processing parameters;
- evaluate public raw datasets;
- produce clinical/site claims;
- change DAY30/DAY31 QC decisions.

## 6. Frozen Safety Invariants

1. `RAW_IS_IMMUTABLE`.
2. `MASK_NOT_DELETE`.
3. `QC_FAIL_MUST_NOT_BE_REHABILITATED_BY_PREPROCESSING`.
4. `NO_SILENT_DEFAULT_FS`.
5. `NO_SILENT_DEFAULT_MAINS_FREQUENCY`.
6. `NO_LOCKED_SET_FITTING`.
7. `ALL_PROCESSING_MUST_BE_VERSIONED`.
8. `CONFIG_FINGERPRINT_MUST_BE_DETERMINISTIC`.
9. `SHIFTED_DOMAIN != QUALITY_FAILURE`.
10. `NULL_PLUS_REASON != ZERO`.

## 7. Design Decision — Safe Entry Profile

### Decision

The only active DAY40 research profile is `research-native-grid-preserve-v0.1`.

### Rationale

A “research default” containing 20–450 Hz, notch 50 Hz, or 2 kHz resampling would silently legitimize legacy assumptions before analytical verification. The safe phase-entry profile instead makes every transform explicit and disabled.

### Consequence

DAY41+ must release a new profile version when an operation becomes analytically verified. No in-place mutation of the DAY40 active profile is allowed.

## 8. Required Output Tree

```text
configs/processing/
└── preprocessing-profiles.v0.1.yaml

packages/common-schemas/json/
└── processing-profile.schema.json

packages/semg-core/semg_core/processing/
├── __init__.py
└── profile_contract.py

docs/03-architecture/
└── processing-profile-contract.md

qa-validation/automated-tests/processing/
└── test_day40_processing_profile_contract.py

scripts/dev/
├── day40_contract_validator.py
├── check_day40_artifacts.py
└── run_day40_checks.sh
```

## 9. STEP 1 — Verify Phase Entry

**Goal:** Prove DAY40 starts on a valid frozen QC boundary.

**Input:** GATE C-R and DAY38 freeze manifest.

**Action:**

```bash
python3 scripts/dev/day40_contract_validator.py --repo-root "$PWD"
```

The validator checks:

- gate status;
- DAY31 processing permissions;
- all DAY38 frozen hashes;
- profile schema/catalog;
- no active unverified transforms;
- no site binding.

**Expected output:** JSON status `PASS`.

**Negative check:** A modified DAY38 frozen file must stop DAY40 verification.

**Pass:** all frozen hashes match.

## 10. STEP 2 — Freeze Profile Identity

**Goal:** Define reproducible profile identity independent of YAML formatting.

**Input:** profile dictionary.

**Action:** canonicalize configuration, remove `config_fingerprint`, sort recursively, JSON-encode and hash SHA-256.

**Expected:** `pprof_sha256_<64 hex>`.

**Verification:** key order changes do not change fingerprint; semantic field changes do.

**Stop:** embedded fingerprint differs from recomputed value.

## 11. STEP 3 — Define Runtime Input Contract

**Goal:** Prevent hidden source assumptions.

**Required runtime values:**

- sampling rate;
- physical unit;
- source window ID;
- source ID;
- DAY31 processing permission;
- distribution support status.

**Why:** public/synthetic sources differ in Fs, units and layout. A static profile cannot safely infer these from dataset name.

**Expected:** runtime binding cannot be constructed with non-positive Fs or missing units.

## 12. STEP 4 — Define QC Authorization Boundary

**Goal:** Keep preprocessing downstream of DAY31.

Allowed automatic permission:

```text
ALLOW_PROFILED_PROCESSING
```

Rejected:

```text
BLOCK_UNSUPPORTED_METRIC
HOLD_FOR_REVIEW
ABSTAIN
```

**Negative check:** no “filter first, discard later” behavior.

**Safety value:** prevents creation of processed-looking artifacts from upstream blocked data.

## 13. STEP 5 — Separate Native and Processed Grid

**Goal:** Make resampling explicit and traceable.

The active profile declares:

```yaml
native_grid_policy: PRESERVE_UNLESS_EXPLICITLY_RESAMPLED
resampling:
  enabled: false
  target_fs_hz: null
```

**Output metadata contract:** native Fs, processed Fs and `is_resampled` are always available downstream.

**Negative:** no fallback target Fs.

## 14. STEP 6 — Define Band-Pass Contract

**Goal:** Ensure later band-pass implementations cannot omit design parameters.

If disabled, all method/cutoff/order/phase fields are null.

If enabled, schema requires:

- method;
- low cutoff;
- high cutoff;
- order;
- phase mode.

Runtime validator enforces `high_cut < Fs/2`.

**DAY40 result:** disabled, contract only.

## 15. STEP 7 — Define Notch Contract

**Goal:** Make power-line assumptions explicit.

If notch is enabled:

- mains frequency is mandatory;
- exactly one of Q or bandwidth is required.

**Negative:** enabling notch with `mains_frequency_hz=null` must fail schema validation.

**DAY40 result:** disabled.

## 16. STEP 8 — Define Rectification and Smoothing Contract

Rectification supports explicit method semantics only.

Smoothing supports method-specific required fields:

- moving average → window milliseconds;
- low-pass → cutoff + order.

No smoothing exists in active DAY40 profile.

## 17. STEP 9 — Freeze Normalization/Fitting Boundary

**Goal:** Ensure normalization cannot become hidden data fitting.

Rules:

- `fitting_allowed=false`;
- disabled reference is null;
- locked partition fitting false;
- adaptive processing false.

DAY44 owns eligibility and actual reference semantics.

## 18. STEP 10 — Preserve Mask and Raw Signal

**Goal:** Prevent preprocessing from deleting evidence.

Profile mask policy:

```text
PRESERVE_MASK_NO_DELETION
```

Required booleans:

- delete masked samples = false;
- preserve sample alignment = true;
- raw deleted = false.

Later filters may expand a processed mask with provenance, but never erase the incoming raw mask.

## 19. STEP 11 — Declare Distribution Effects

Profiles record whether they change:

- sampling grid;
- spectral content;
- amplitude scale;
- timing.

This is contract metadata, not measured analytical evidence.

The preserve profile declares all unchanged.

## 20. STEP 12 — Validate Distribution-Support Interaction

Base deterministic profile:

```yaml
distribution_support_required: false
```

Therefore `SHIFTED` does not automatically block processing when QC has passed.

A future distribution-sensitive profile can set the flag true. Then:

- supported → proceed;
- shifted → review;
- unknown/not evaluated → abstain.

No OOD score is created.

## 21. STEP 13 — Freeze Required Output Metadata

The profile requires downstream processing artifacts to carry enough information for DAY45 lineage:

- source window;
- profile ID/version/fingerprint;
- native/processed Fs;
- units;
- input/output hashes;
- mask reference;
- effect summary.

DAY40 does not create processed waveform outputs, so these are contract fields only.

## 22. Automated Test Matrix

| Area | Happy path | Negative / adversarial |
|---|---|---|
| Schema | catalog validates | enabled step missing fields rejected |
| Fingerprint | deterministic | mismatch rejected |
| Fs | 1/2/4 kHz runtime allowed | 0 Hz rejected |
| Units | V/uV | unsupported unit rejected |
| QC permission | ALLOW | BLOCK/HOLD/ABSTAIN rejected |
| Band-pass | disabled safe | invalid ordering/Nyquist rejected |
| Notch | disabled safe | missing mains/Nyquist rejected |
| Resampling | native grid | decimation without anti-alias rejected |
| Distribution | SHIFTED allowed for DSP-independent | SHIFTED held when required |
| Site | null | site binding rejected |
| Locking | process fixed locked profile possible | fitting locked data forbidden |

Focused suite target: all tests PASS.

## 23. Regression Strategy

Run cumulative QC/research/property regression to ensure profile work does not mutate QC semantics:

```bash
python3 -m pytest -q \
  qa-validation/automated-tests/qc \
  qa-validation/automated-tests/research \
  qa-validation/property-tests \
  -k 'not test_43_no_day22_window_implementation'
```

The deselected historical DAY21 guard only asserted that DAY22 code must not exist *during DAY21*. It is not a functional regression check for DAY40.

## 24. Artifact Integrity

DAY40 artifacts are manifest-scoped and SHA-256 checked after finalization.

`SHA256SUMS` must be generated last.

No cache, pyc, raw public data, patient data, secrets or confidential site exports may enter ZIP.

## 25. Failure Injection

Required negative cases include:

1. corrupt fingerprint;
2. explicit site binding;
3. duplicate profile ID/version;
4. invalid Fs;
5. unsupported unit;
6. QC blocked permission;
7. notch without mains;
8. high cutoff >= Nyquist;
9. downsampling without anti-alias declaration;
10. locked-set fitting enabled.

Each must fail closed before any DSP operation.

## 26. Traceability

DAY40 supports roadmap ICR-005 and ICR-006 and retains key SRS principles:

- reproducibility;
- traceability;
- raw immutability;
- versioned preprocessing;
- fail closed;
- no silent missing-to-zero behavior.

The current independent roadmap, not the discontinued clinical deployment roadmap, defines the claim boundary.

## 27. Acceptance Criteria

DAY40 passes only if:

- mandatory schema/config/architecture document exist;
- JSON Schema validates;
- semantic validator passes;
- config fingerprint deterministic;
- no site binding;
- no silent Fs/mains target;
- no active unverified DSP transform;
- every step has version, parameter authority and effect metadata;
- DAY38 frozen hashes remain intact;
- full applicable regression passes.

## 28. Stop / Block Conditions

`BLOCKED` if any of the following holds:

- GATE C-R no longer ready;
- DAY38 freeze mismatch;
- enabled operation lacks required parameters;
- fingerprint cannot be reproduced;
- config contains silent legacy defaults;
- DAY31 blocked/hold/abstain state can bind automatically;
- site-specific assumption appears in active profile;
- locked-set fitting is enabled.

## 29. Known Limitations

After DAY40:

- there is still no verified band-pass implementation;
- there is still no verified notch implementation;
- public raw benchmark processing has not run;
- site profile remains absent;
- normalization reference is absent;
- clinical/expert validation remains absent.

These are expected and do not block DAY41.

## 30. Rollback

DAY40 is additive. Rollback consists of removing DAY40-owned files. It does not modify DAY38/QC frozen files.

No migration/database/API compatibility risk is introduced.

## 31. Definition of Done

```text
MANDATORY_OUTPUTS = PRESENT
SCHEMA_VALIDATION = PASS
SEMANTIC_VALIDATION = PASS
FINGERPRINT_DETERMINISM = PASS
NO_SILENT_FS = ENFORCED
NO_SILENT_MAINS = ENFORCED
QC_PERMISSION_BOUNDARY = ENFORCED
DAY38_FREEZE = UNCHANGED
SITE_BINDING = NONE
ACTIVE_DSP_TRANSFORMS = 0
FINAL_CLAIM = PROCESSING_PROFILE_CONTRACT_READY
```

## 32. Handoff to DAY41

DAY41 may consume:

- `preprocessing-profiles.v0.1.yaml`;
- `processing-profile.schema.json`;
- `profile_contract.py`;
- DAY40 validation evidence.

DAY41 must create analytical band-pass evidence before enabling a band-pass profile version. It must preserve all DAY40 profile identity and runtime authorization rules.
