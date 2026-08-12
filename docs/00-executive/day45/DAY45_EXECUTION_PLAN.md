# DAY45 EXECUTION PLAN — Raw-to-Processed Provenance Chain & Processing Events

> **Program:** MyoLab-AI / sEMG Quality Intelligence  
> **Phase:** Phase 3R — Versioned Processing, Metric & Evidence Engine  
> **Day:** DAY45  
> **Status at close:** PASS  
> **Highest allowed claim:** `PROCESSING_PROVENANCE_READY`  
> **Clinical status:** NOT CLINICALLY VALIDATED / NOT FOR CLINICAL USE  
> **Roadmap authority:** DAY32–DAY90 Independent Research & Portfolio Roadmap v2.0  
> **Convergence inputs:** DAY11 + DAY19 + DAY40 + DAY41 + DAY42 + DAY43 + DAY44

---

## 0. Document Control

DAY45 is a convergence day. It does not introduce a new signal-processing algorithm. Its purpose is to make every downstream processed artifact auditable and replayable by recording the exact raw source identity, WindowIdentity, processing recipe, code/config versions, input/output hashes, mask lineage, eligibility references and processing lifecycle events.

The day closes a safety gap that exists whenever DSP code can produce an array but the system cannot prove exactly how that array was produced. A processed waveform without an unbroken lineage is invalid for the MyoLab-AI research pipeline even if the numerical waveform looks plausible.

### Authoritative outputs

1. `data-platform/contracts/processing-manifest.v0.1.yaml`
2. `data-platform/events/processing-event-emission-contract.v0.1.yaml`
3. `packages/semg-core/semg_core/provenance/processing_manifest.py`

Additional formalization:

- `packages/common-schemas/json/processing-manifest.schema.json`
- `configs/processing/day45-convergence-recipe.v0.1.yaml`
- `qa-validation/automated-tests/processing/test_processing_lineage.py`
- `qa-validation/evidence/day45-processing-lineage-evidence.json`
- `qa-validation/traceability/day45-requirement-impact.yaml`

---

## 1. Executive Intent

The DAY41–44 batch deliberately produced four sibling capabilities on top of the frozen DAY40 contract rather than one hidden monolithic pipeline. DAY45 is the first day allowed to converge those siblings into a unified provenance model.

The critical objective is therefore not “run all filters.” The critical objective is:

```text
exact immutable source bytes
        ↓
exact WindowIdentity
        ↓
exact processing request identity
        ↓
exact ordered processing step records
        ↓
exact processed artifact hash
        ↓
lineage graph + lifecycle events
```

A DAY45 result is only valid when an engineer can start at one processed artifact and trace backward to:

- the DAY11 `source_id` and source SHA-256;
- the exact DAY22-style window/session/channel sample bounds;
- the processing recipe/version/fingerprint;
- every relevant code component and its content hash;
- every transformation method and explicit parameter set;
- every step input/output hash;
- every mask input/output hash;
- QC/normalization eligibility references;
- the final output hash, mask hash, sample count and unit.

---

## 2. Why DAY45 Exists

DAY41 analytically verified a band-pass implementation. DAY42 verified explicit notch behavior and preserved pre-notch spectral evidence. DAY43 implemented rectification, smoothing and mask-not-delete semantics. DAY44 implemented normalization eligibility without numeric normalization. Those capabilities are independently useful, but without DAY45 they are still disconnected implementation islands.

The system needs to answer questions such as:

- Which exact raw source produced this waveform?
- Which window and channel did it come from?
- Was a 20–400 Hz research band-pass used, and with which code version?
- Was 50 Hz notch explicitly enabled because the synthetic fixture declared 50 Hz, or was it silently guessed?
- Did the mask change between steps?
- Was a normalization reference used, and if so which one?
- Did any step fit parameters on a locked partition?
- Can an exact retry be recognized as the same processing request?
- If processing failed, can the system accidentally expose a final-looking processed artifact?
- Can the event stream be reconstructed without storing waveform samples in the event store?

DAY45 makes those questions machine-answerable.

---

## 3. Source of Truth and Conflict Resolution

Priority used for implementation:

1. Current independent roadmap DAY45 definition.
2. Frozen DAY40 processing profile contract and DAY41–44 accepted branch outputs.
3. DAY11 immutable SourceRecord identity.
4. DAY19 event privacy/idempotency style.
5. DAY31 eligibility/fail-closed semantics.
6. Original 90-day roadmap details where they add traceability without overriding current scope.
7. Legacy notebooks/scripts only as historical reference.

### Resolved conflict

The older roadmap names `services/preprocessing-service/src/provenance/processing_manifest.py` as a target. The current authoritative roadmap names `packages/semg-core/semg_core/provenance/processing_manifest.py`. DAY45 follows the current roadmap. No duplicate source-of-truth implementation is created in a service folder.

---

## 4. Preconditions

### Input A — DAY11 SourceRecord ledger

Required fact:

```text
source_id = src_sha256_<exact source byte hash>
```

DAY45 does not invent a new raw identity. `RawSourceRef` requires both `source_id` and SHA-256 and validates that they correspond exactly. `immutable_raw` must be true.

### Input B — DAY19 event contract

DAY19 established useful event-system patterns:

- deterministic event identity;
- explicit correlation ID;
- source refs are IDs/hashes, not local paths;
- no raw payload/PHI in event;
- terminal success/failure are distinct;
- persistent event store is not fabricated before its implementation day.

DAY45 adapts those patterns for processing lifecycle events.

### Input C — DAY40 frozen processing profile contract

DAY45 must not rewrite the active DAY40 profile. The DAY45 convergence recipe is additive and marked `RESEARCH_INTEGRATION_TEST_ONLY`.

### Input D — DAY41–44 sibling processors

Consumed code:

- `semg_core.processing.bandpass`
- `semg_core.processing.notch`
- `semg_core.processing.masking`
- `semg_core.processing.envelope`
- DAY44 normalization eligibility evaluator

### Input E — DAY31 eligibility boundary

DAY45 records eligibility references. It does not override a blocked/abstained decision or create a new mechanism to rehabilitate QC-failed data.

---

## 5. Objectives

1. Define a versioned `ProcessingManifest` contract.
2. Make processing run identity content-addressed and deterministic.
3. Record source/window/profile/code/config/input/output/mask lineage.
4. Validate contiguous step-hash and mask-hash chains.
5. Distinguish completed and failed manifest shapes.
6. Prevent failed processing from producing final-looking artifacts.
7. Define processing lifecycle events:
   - `PROCESSING_STARTED`
   - `PROCESSING_COMPLETED`
   - `PROCESSING_FAILED`
   - `REPROCESS_TRIGGERED`
8. Ensure events contain references/reasons only, no waveform or file paths.
9. Provide a machine-readable lineage graph.
10. Preserve `RESEARCH_ONLY` / no-site-binding claim boundary.

---

## 6. Non-Goals

DAY45 does **not**:

- implement a persistent Clinical/Research Event Store;
- create an audit database;
- train or fit a model;
- fit normalization parameters;
- implement numeric MVC normalization;
- promote DAY41 20–400 Hz or DAY42 50 Hz to a site default;
- create a production/realtime streaming profile;
- infer a clinical condition from processing behavior;
- modify raw signal bytes;
- change QC status after preprocessing;
- execute or inspect benchmark-locked outcomes for tuning;
- implement DAY46 metrics.

---

## 7. Core Domain Model

### 7.1 `RawSourceRef`

Fields:

```text
source_id
sha256
immutable_raw
```

Invariant:

```text
source_id == "src_sha256_" + sha256
```

This directly preserves DAY11 content-addressed source identity.

### 7.2 `WindowRef`

Fields:

```text
window_id
session_id
channel_id
start_sample
end_sample_exclusive
```

The manifest does not accept a context-free arbitrary crop.

### 7.3 `ProcessingProfileRef`

Fields:

```text
profile_id
version
config_fingerprint
claim_scope
site_binding
```

For DAY45:

```text
claim_scope = RESEARCH_ONLY
site_binding = null
```

### 7.4 `CodeComponentRef`

Every implementation component is represented by:

```text
component_id
version
artifact_sha256
```

This makes the processing result traceable not just to “DAY41 code” but to exact code bytes.

### 7.5 `ProcessingStepRecord`

Each completed step records:

```text
sequence
step_id
processor
processor_version
method
parameters
config_sha256
input_sha256
output_sha256
input_mask_sha256
output_mask_sha256
status
effect
reference_ids
```

The `config_sha256` must equal the canonical SHA-256 of the explicit `parameters` mapping.

### 7.6 `ProcessedArtifactRef`

A final artifact is content-addressed from:

- processing run ID;
- final output hash;
- final mask hash;
- sample count;
- output unit.

---

## 8. Content-Addressed Processing Run Identity

`processing_run_id` is deterministic over execution facts known before output creation:

```text
source identity
+ WindowIdentity
+ profile identity/fingerprint
+ code component hashes
+ input array hash
+ input mask hash
+ native Fs
+ input unit
+ partition
+ QC eligibility ref
+ normalization eligibility ref
+ optional reprocess parent
```

The identifier has the form:

```text
prun_sha256_<64 hex>
```

The reference convergence run produced:

```text
prun_sha256_203ffa82c3769d184e1b7f92374e6483eae453a8d7d580704eae2df3860f3547
```

Exact retry with exactly the same execution facts yields the same run ID. Changing the processing recipe fingerprint changes the run ID.

---

## 9. Manifest Identity

A completed or failed manifest is itself content-addressed from its semantic payload. `manifest_id` is:

```text
pman_sha256_<64 hex>
```

Reference manifest:

```text
pman_sha256_a5ff54249952f465a2df0d5a45bf2379f708bce4cc266cb2bc54732ca5e0b71c
```

The manifest ID excludes no safety-relevant semantic field; it is independent of mutable storage paths and event timestamps.

---

## 10. Processed Artifact Identity

Reference processed artifact:

```text
part_sha256_590f2f1296ba85d3254dfa22eca526c73fff486a95897e5c2eb39621467444b7
```

An artifact cannot exist in a valid FAILED manifest.

This separates:

```text
processing request identity  → processing_run_id
processing record identity   → manifest_id
processed result identity    → artifact_id
```

Those identifiers answer different provenance questions and should not be conflated.

---

## 11. Step Hash Lineage

For ordered steps `S0...Sn`, validation requires:

```text
manifest.input_hash == S0.input_hash
S0.output_hash == S1.input_hash
S1.output_hash == S2.input_hash
...
Sn.output_hash == final_artifact.output_hash
```

A single mismatch invalidates the manifest.

The same rule applies to mask hashes:

```text
manifest.input_mask_hash == S0.input_mask_hash
S0.output_mask_hash == S1.input_mask_hash
...
Sn.output_mask_hash == final_artifact.mask_hash
```

This is more informative than recording only a final output hash because it localizes where lineage broke.

---

## 12. Mask Lineage

DAY43 froze `MASK_NOT_DELETE`. DAY45 carries it forward by hashing the mask at every processing boundary.

The integrated convergence case explicitly changes the mask only at the metadata-mask step. It does not delete samples. Output length remains equal to raw input length, and masked samples remain unavailable (`NaN`) after envelope construction.

This gives downstream DAY46 a defensible answer to:

> “Was this metric derived from a window containing masked samples?”

without needing to infer masking from waveform values.

---

## 13. Grid and Unit Provenance

The manifest explicitly records:

```text
native_fs_hz
processed_fs_hz
is_resampled
input_units
output_units
```

DAY45 reference convergence does not resample:

```text
native_fs_hz = processed_fs_hz = 2000 Hz
is_resampled = false
```

Therefore a mismatch between native and processed Fs while `is_resampled=false` is a lineage failure.

No unit conversion or normalization is performed in the reference convergence recipe. Input and output remain `uV`.

---

## 14. Normalization Convergence Semantics

DAY44 is an eligibility evaluator, not a numeric normalizer. DAY45 preserves that boundary.

The convergence evidence invokes `NormalizationMethod.NONE`, producing an eligibility result with:

```text
status = ELIGIBLE
metric_value = null
```

A content-addressed reference to that eligibility result is stored in the manifest. DAY45 does not compute a ratio, MVC percentage or learned reference.

---

## 15. DAY45 Convergence Recipe

File:

`configs/processing/day45-convergence-recipe.v0.1.yaml`

Fingerprint:

```text
precipe_sha256_07dfd4b38537be69dd6d6435c92a1923f1b928a095f5de385cbb83bc1b9d7401
```

Status:

```text
RESEARCH_INTEGRATION_TEST_ONLY
```

The recipe is additive. It does not mutate `preprocessing-profiles.v0.1.yaml` and does not become a site default.

The reference recipe uses:

1. DAY41 20–400 Hz research band-pass on synthetic research input.
2. DAY42 explicit 50 Hz notch only because the synthetic context is explicitly declared 50 Hz.
3. DAY43 metadata mask with mask-not-delete.
4. DAY43 full-wave rectification + 50 ms moving average example.
5. DAY44 normalization eligibility with method `NONE` and no numeric normalization.

These values are integration-test evidence, not clinical/site recommendations.

---

## 16. Processing Event Contract

DAY45 defines four event types:

```text
PROCESSING_STARTED
PROCESSING_COMPLETED
PROCESSING_FAILED
REPROCESS_TRIGGERED
```

Every event includes:

- deterministic event ID;
- processing run ID;
- manifest contract version;
- correlation ID;
- session ID;
- source refs using DAY11-style source IDs;
- profile ID/fingerprint;
- UTC emission timestamp;
- sequence;
- terminal outcome/reason where applicable.

### Privacy boundary

Events forbid:

- waveform samples;
- raw payload;
- local source path;
- patient name;
- MRN;
- clinical free-text note.

### Event store boundary

```text
persistent_event_store_implemented = false
persistent_event_store_target_day = 53
```

DAY45 closes the emission contract only. It does not pretend the persistent store exists.

---

## 17. Failed Processing Semantics

A FAILED manifest must satisfy:

```text
final_artifact = null
processed_fs_hz = null
output_units = null
steps = []
reason_codes != []
```

This intentionally sacrifices partial-step persistence in v0.1 to keep the fail-closed contract unambiguous. If future requirements need partial processing traces, they require a versioned contract extension rather than overloading a completed-step list.

A failed processing attempt can emit `PROCESSING_FAILED`, but that event cannot create a processed-looking result.

---

## 18. Reprocess Semantics

A reprocess request is represented by a new content-addressed processing request including `reprocess_of_run_id`.

This creates a new run identity while preserving the parent relationship.

`REPROCESS_TRIGGERED` is non-terminal. It does not mean processing succeeded and it does not mutate the old manifest.

---

## 19. Lineage Graph

`build_lineage_graph()` returns explicit nodes/edges:

```text
RAW_SOURCE
  → WINDOW
    → PROCESSING_RUN
      → STEP 0
        → STEP 1
          → ...
            → PROCESSED_ARTIFACT
```

The graph is a read model over an already validated manifest. It does not replace the manifest as source of truth.

---

## 20. Detailed Execution Procedure

### STEP 1 — Validate convergence authorization

**Input**
- DAY41–44 handoffs and verification results.
- DAY40 frozen profile contract.

**Action**
- Confirm all sibling branches are PASS.
- Confirm no branch changed frozen DAY40 baseline.

**Output**
- DAY45 execution authorized.

**Verification**
- DAY41–44 focused regression later re-run from merged overlay.

**Failure condition**
- Any branch missing or FAIL → DAY45 BLOCKED.

### STEP 2 — Load immutable source identity semantics

**Input**
- DAY11 `SourceRecord` / `source_ledger.py`.

**Action**
- Reuse `src_sha256_<digest>` convention.
- Do not copy local storage paths into processing events.

**Output**
- `RawSourceRef` contract.

**Verification**
- Source ID/hash mismatch negative test.

**Failure condition**
- Source identity not content-addressable → lineage invalid.

### STEP 3 — Define processing run identity

**Input**
- source/window/profile/code/input/mask/eligibility facts.

**Action**
- Canonical JSON serialization.
- SHA-256 content address.

**Output**
- `prun_sha256_*`.

**Verification**
- Exact retry deterministic test.
- Changed profile changes ID test.

**Failure condition**
- Run ID depends on local path/current timestamp/random UUID → FAIL.

### STEP 4 — Define ProcessingManifest schema

**Input**
- Current roadmap mandatory contract.
- Original roadmap traceability requirements.

**Action**
- Define YAML contract + Draft 2020-12 JSON Schema.

**Output**
- `processing-manifest.v0.1.yaml`.
- `processing-manifest.schema.json`.

**Verification**
- Schema check and valid manifest test.
- Failed-shape negative validation.

**Failure condition**
- Schema permits failed manifest with a final artifact → BLOCK.

### STEP 5 — Define step hash chain

**Input**
- DAY41–43 processor metadata.

**Action**
- Convert each executed step to `ProcessingStepRecord`.
- Hash canonical parameter dictionaries.

**Output**
- ordered step records.

**Verification**
- Input/output mismatch rejected.
- Parameter/config hash mismatch rejected.

**Failure condition**
- Any broken edge → entire manifest invalid.

### STEP 6 — Define mask lineage

**Input**
- DAY43 mask semantics.

**Action**
- Record mask hash before/after every step.
- Preserve final mask with final artifact.

**Output**
- mask lineage chain.

**Verification**
- Integrated masked interval remains unavailable and sample count remains 1:1.

**Failure condition**
- Deleted/cropped masked samples without declared grid transformation → BLOCK.

### STEP 7 — Converge normalization eligibility without numeric normalization

**Input**
- DAY44 evaluator.

**Action**
- Evaluate `NONE` method for convergence evidence.
- Hash result into eligibility reference.

**Output**
- `normalization_eligibility_ref`.

**Verification**
- `metric_value is None`.

**Failure condition**
- Numeric normalization produced in DAY45 → scope violation.

### STEP 8 — Define lifecycle event contract

**Input**
- DAY19 event style.

**Action**
- Define four event types and privacy rules.

**Output**
- `processing-event-emission-contract.v0.1.yaml`.

**Verification**
- deterministic event ID tests.
- no-waveform/path tests.

**Failure condition**
- signal values or raw paths embedded in event → BLOCK.

### STEP 9 — Generate integrated research evidence

**Input**
- deterministic 2-second synthetic uV waveform.
- explicit research recipe.

**Action**
- band-pass → explicit notch → metadata mask → envelope.
- preserve raw copy.
- generate manifest and lineage graph.

**Output**
- `day45-processing-lineage-evidence.json`.

**Verification**
- raw hash/bytes unchanged.
- manifest validates.
- output mask preserves 1:1 length.

**Failure condition**
- any manifest/hash/mask validation error → BLOCK.

### STEP 10 — Validate failed/reprocess states

**Input**
- deterministic failure example.

**Action**
- build FAILED manifest.
- create FAILED event.
- create new content-addressed reprocess run and trigger event.

**Output**
- failure/reprocess evidence.

**Verification**
- failed manifest has no artifact.
- reprocess event links parent run.

**Failure condition**
- failure can appear completed → BLOCK.

### STEP 11 — Run focused tests

**Command**

```bash
python3 -m pytest -q   qa-validation/automated-tests/processing/test_processing_lineage.py
```

**Actual result**

```text
25 passed
```

### STEP 12 — Run processing convergence regression

**Command**

```bash
python3 -m pytest -q   qa-validation/automated-tests/processing/test_day40_processing_profile_contract.py   qa-validation/automated-tests/processing/test_bandpass.py   qa-validation/automated-tests/processing/test_notch.py   qa-validation/automated-tests/processing/test_envelope_masking.py   qa-validation/automated-tests/processing/test_normalization_eligibility.py
```

**Actual result**

```text
78 passed
```

### STEP 13 — Run provenance/event upstream regression

DAY11 + DAY19 regression was also run after loading DAY18 Vicon adapter dependencies required by historical DAY19 tests.

**Actual result**

```text
82 passed
```

### STEP 14 — Package and integrity freeze

- Build day-owned artifact manifest.
- Run Python/YAML/JSON syntax checks.
- Scan package for cache/PHI/secrets/local absolute paths.
- Build `SHA256SUMS` after final content freeze.
- Test archive extraction and execute package verifier from extracted directory.

---

## 21. Test Matrix

| Test type | Purpose | Result |
|---|---|---|
| Unit/contract | Processing IDs, manifests, events, failure semantics | 25/25 PASS |
| Integrated DSP lineage | DAY41→43 + DAY44 eligibility convergence | PASS |
| Schema | Draft 2020-12 manifest | PASS |
| Negative | broken hash/config/source/event/privacy/failure shapes | PASS |
| Processing regression | DAY40–44 | 78/78 PASS |
| Source/event regression | DAY11 + DAY19 | 82/82 PASS |
| Determinism | run/manifest/event identity | PASS |
| Raw immutability | integrated synthetic replay | PASS |

Total relevant executed tests before packaging:

```text
25 + 78 + 82 = 185 PASS
```

---

## 22. Acceptance Criteria

DAY45 is PASS only if all are true:

- mandatory roadmap outputs exist;
- source ID matches exact source hash;
- processing run ID is content-addressed and deterministic;
- manifest ID is content-addressed;
- every completed step records exact method/params/version;
- step input/output hashes form one continuous chain;
- mask hashes form one continuous chain;
- final artifact equals the last step output/mask hashes;
- raw is immutable;
- failed manifest has no final artifact;
- event IDs are deterministic;
- events contain no raw waveform or source path;
- persistent event store is not falsely claimed;
- no locked-set fitting occurs;
- DAY40–44 regression passes;
- DAY11/DAY19 provenance/event behavior remains compatible.

---

## 23. Stop / Block Conditions

Immediate block conditions:

1. Source hash and source ID mismatch.
2. Window identity missing or invalid.
3. Profile fingerprint malformed or site-bound.
4. Any step input hash differs from previous output hash.
5. Any mask hash chain breaks.
6. Step config hash does not match canonical explicit parameters.
7. Failed result contains a processed artifact.
8. Undeclared Fs change while `is_resampled=false`.
9. Any fitting performed in DAY45.
10. Any fitting on `benchmark-locked`.
11. Event embeds waveform/source path/direct identifiers.
12. Processing event is presented as persisted even though DAY53 store is not implemented.

---

## 24. Requirement Traceability

DAY45 supports/revalidates:

- **FR-051** processing method/parameters/version/input/output references.
- **FR-053** raw must never be overwritten.
- **FR-057** future raw-vs-processed viewing requires reliable linkage.
- **NFR-001** reproducibility.
- **NFR-002** traceability.
- **NFR-003** data integrity/raw immutability.
- **NFR-011** versioning.
- **ICR-005** reproducible experiment/evidence chain.
- **ICR-006** unsupported/failure states fail closed.

DAY45 does not claim clinical compliance or certification.

---

## 25. Evidence Boundaries

### What DAY45 proves

- The processing provenance contract is implementable and testable.
- Exact processing request identity is deterministic.
- A synthetic research processing chain can be traced end-to-end.
- Broken hash lineage fails closed.
- Failed processing cannot masquerade as completed output.
- Processing lifecycle event semantics can be emitted without raw signal data.

### What DAY45 does not prove

- clinical correctness of the processing recipe;
- site-specific preprocessing validity;
- correct mains frequency at any real site;
- efficacy of 20–400 Hz for any patient/task;
- clinician usability;
- production event-store durability;
- realtime processing behavior;
- metric validity.

---

## 26. Known Limitations

1. `ZERO_PHASE` DAY41/42 research filters remain acausal and batch-only.
2. DAY45 convergence recipe is integration-test-only, not a promoted DAY40 active profile.
3. Numeric normalization remains out of scope.
4. Persistent event storage remains deferred to DAY53.
5. Partial failed-step trace persistence is intentionally not represented in v0.1 FAILED manifests.
6. No public raw dataset processing was performed.
7. No clinical/site/expert validation was performed.

---

## 27. Rollback

DAY45 is additive. Rollback consists of removing only DAY45-owned files:

```text
configs/processing/day45-convergence-recipe.v0.1.yaml
data-platform/contracts/processing-manifest.v0.1.yaml
data-platform/events/processing-event-emission-contract.v0.1.yaml
packages/common-schemas/json/processing-manifest.schema.json
packages/semg-core/semg_core/provenance/
qa-validation/automated-tests/processing/test_processing_lineage.py
qa-validation/evidence/day45-*
qa-validation/requirements/day45-acceptance-criteria.md
qa-validation/traceability/day45-requirement-impact.yaml
scripts/dev/day45_*
scripts/dev/run_day45_checks.sh
docs/00-executive/day45/
```

DAY40–44 files are not modified or overwritten by the rollback.

---

## 28. Handoff to DAY46

DAY46 — RMS/MAV Metric Registry may begin only after live-repo merge verification passes.

DAY46 should consume:

- `ProcessingManifest` / final processed artifact identity;
- DAY31 metric eligibility;
- final mask lineage;
- output units;
- source WindowIdentity;
- processing profile/recipe fingerprint;
- code/config version refs.

DAY46 must **not** compute RMS/MAV when DAY31 blocks the metric or when DAY43 mask policy excludes the window.

---

## 29. Final Status

```text
ENGINEERING_VALIDATION       = PASS
PROCESSING_PROVENANCE        = READY
PROCESSING_RUN_ID             = CONTENT_ADDRESSED_DETERMINISTIC
PROCESSING_MANIFEST_ID        = CONTENT_ADDRESSED_DETERMINISTIC
STEP_HASH_LINEAGE             = ENFORCED
MASK_HASH_LINEAGE             = ENFORCED
RAW_IMMUTABILITY              = REVALIDATED
FAILED_FALSE_SUCCESS_GUARD    = ENFORCED
PROCESSING_EVENTS             = CONTRACT_AND_REFERENCE_EMISSION_READY
PERSISTENT_EVENT_STORE        = NOT_IMPLEMENTED
NORMALIZATION_FITTING         = NOT_PERFORMED
LOCKED_SET_FITTING            = FORBIDDEN
SITE_VALIDATION               = NOT_PERFORMED
CLINICAL_VALIDATION           = NOT_PERFORMED
HIGHEST_ALLOWED_CLAIM         = PROCESSING_PROVENANCE_READY
DAY46_READINESS               = YES_AFTER_LIVE_MERGE_VERIFICATION
```


---

## 30. Architecture Decision Records Embedded in DAY45

### ADR-45-01 — One canonical provenance implementation

**Decision:** `packages/semg-core/semg_core/provenance/processing_manifest.py` is the canonical implementation.

**Problem solved:** the legacy roadmap named a service-local module while the current roadmap moved provenance into the reusable `semg_core` package. Duplicating the logic would allow the service and package contracts to drift.

**Risk reduced:** divergent manifest IDs, different hash canonicalization rules, and inconsistent failure semantics.

**Cost:** service adapters that need this capability must import the package rather than own a second implementation.

**Test:** all focused tests import the package implementation; there is no second DAY45 business-logic copy.

### ADR-45-02 — Event contract without persistent store

**Decision:** define deterministic processing events now, but do not implement storage until DAY53.

**Problem solved:** downstream work needs stable event semantics and correlation IDs before a storage engine exists.

**Risk reduced:** avoids coupling provenance semantics to an immature persistence technology and avoids making a false production capability claim.

**Cost:** DAY45 evidence uses an in-memory collecting sink only for tests/reference emission.

**Test:** contract asserts `persistent_event_store_implemented: false` and the reference sink rejects duplicate event IDs.

### ADR-45-03 — Fail-closed FAILED manifest shape

**Decision:** v0.1 FAILED manifests contain no final artifact, processed Fs, output unit or completed-step list.

**Problem solved:** partial outputs can easily look consumable even when the operation failed.

**Risk reduced:** downstream consumers have one unambiguous rule: a FAILED manifest has no processed artifact.

**Cost:** partial step observability is deferred. If needed later, a new attempt-trace structure must be versioned explicitly.

**Test:** both Python semantic validation and JSON Schema reject failed manifests containing processed-looking fields.

### ADR-45-04 — Convergence recipe stays additive

**Decision:** DAY45 adds `day45-convergence-recipe.v0.1.yaml` without editing DAY40's active profile catalog.

**Problem solved:** DAY41–44 were intentionally sibling workstreams. A convergence test needs one deterministic recipe but must not silently promote branch research parameters to a global/site default.

**Risk reduced:** prevents 20–400 Hz and explicit 50 Hz synthetic assumptions from becoming operational defaults.

**Cost:** DAY46 and later consumers must distinguish the integration-test recipe from any future approved processing profile.

**Test:** recipe status is `RESEARCH_INTEGRATION_TEST_ONLY`, claim scope is `RESEARCH_ONLY`, and `site_binding` is null.

---

## 31. Failure Injection Matrix

| Failure injection | Expected behavior | Evidence/test |
|---|---|---|
| Source ID does not match source SHA | reject run identity | `test_source_id_must_match_source_hash` |
| Step input hash not equal previous output | reject manifest | `test_broken_step_hash_chain_is_rejected` |
| Step parameter hash forged | reject manifest | `test_broken_step_config_hash_is_rejected` |
| FAILED manifest retains final artifact | reject manifest | `test_failed_manifest_cannot_claim_artifact` |
| Fitting marked true on locked partition | reject manifest | `test_no_locked_set_fitting` |
| FAILED event lacks reason | reject event | `test_processing_failed_event_requires_reason` |
| Reprocess event lacks parent run | reject event | `test_reprocess_event_requires_parent_run` |
| Event source ref is local file path | reject event | `test_event_rejects_non_source_id_reference` |
| Same event emitted twice to reference sink | reject duplicate | `test_event_sink_rejects_duplicate_event_id` |
| Same exact request replayed | same processing run ID | `test_processing_run_id_is_deterministic` |
| Profile fingerprint changed | new processing run ID | `test_run_id_changes_when_profile_changes` |

The negative tests are not ancillary. They define the edges of the contract. A provenance system that only proves its happy path is especially dangerous because malformed records often remain syntactically plausible.

---

## 32. Manual Review Checklist

A senior engineer reviewing a DAY45 manifest should be able to answer these questions without opening a notebook:

1. Does `source_id` match the source SHA-256 exactly?
2. Is the window identity complete and sample-bounded?
3. Is the profile/recipe claim scope research-only and site binding null?
4. Are code-component hashes present for every processing implementation used?
5. Does every step state method, parameters and processor version explicitly?
6. Does every step config hash equal the canonical parameters hash?
7. Is the signal hash chain continuous from manifest input to final artifact?
8. Is the mask hash chain continuous?
9. Did any processing step silently change sampling rate?
10. Did any fitting occur?
11. Is a normalization eligibility/reference recorded when relevant?
12. If outcome is FAILED, is the final artifact absent?
13. Do event payloads contain only IDs/hashes/reasons rather than raw data?
14. Is the persistent event-store claim still false?
15. Can the final artifact be linked to DAY46 metric provenance without guessing?

Any “no” on items 1–13 invalidates the manifest or blocks downstream use. Items 14–15 determine maturity/downstream readiness rather than waveform correctness.

---

## 33. Reproducibility Definition for DAY45

DAY45 uses a stricter definition than “the script runs twice.” Reproducibility has four layers:

### Layer A — Identity reproducibility
Same execution facts must yield the same `processing_run_id`.

### Layer B — Record reproducibility
Same completed outcome, step records and output hashes must yield the same `manifest_id`.

### Layer C — DSP replay reproducibility
The same synthetic input and step configuration must regenerate the same step/final hashes within the current deterministic implementation.

### Layer D — Package reproducibility
The downloadable DAY45 ZIP must extract cleanly and its verifier must reconstruct a temporary overlay of frozen upstream evidence plus DAY45 changes and re-run the relevant tests.

A failure in any layer is reported separately. For example, a changing event timestamp does not invalidate run identity because event time is workflow metadata, not an execution-identity fact.

---

## 34. Security and Privacy Review

DAY45 does not implement authentication or RBAC because there is no public API or persistent store in scope. Nevertheless it reduces privacy/security risk in two concrete ways.

First, events use only content-addressed source references. Local storage paths, subject names, MRNs and free-text notes are excluded from the event contract. This reduces accidental identifier propagation into future analytics/process-mining systems.

Second, manifest identity is based on hashes and typed technical metadata rather than user-entered names. This makes replay portable across machines and discourages filename-based identity conventions that can leak patient information.

Cryptographic signing, access control, key management and tamper-evident persistent storage are not claimed by SHA-256 content addressing alone. SHA-256 here provides content identity/integrity checks, not authorization or non-repudiation.

---

## 35. Performance Considerations

DAY45 hashing is linear in the bytes of arrays/configs being identified. For current offline research windows this is acceptable and materially improves traceability. The manifest stores hashes/metadata, not duplicate waveform arrays, so event and provenance payloads remain small.

No optimization such as hash sampling or skipping intermediate hashes is introduced because that would weaken the lineage guarantee before performance is shown to be a real bottleneck. If later profiling demonstrates cost at scale, optimization must preserve the same semantic contract or introduce a versioned hash policy.

---

## 36. Final Adversarial Review

### Junior engineer challenge
Could a new engineer reproduce the reference run from files and explicit parameters without asking which filter defaults were “usually used”? **Yes.** Parameters and component hashes are explicit.

### Senior DSP challenge
Could provenance make an analytically verified offline filter appear clinically validated? **No.** Claim scope and recipe status remain research-only; provenance records what happened, not whether it is clinically appropriate.

### Clinical-safety challenge
Could a failed processing attempt leave a processed-looking output that DAY46 consumes? **The v0.1 manifest forbids it.**

### QA challenge
Could one broken intermediate hash be ignored while the final output hash still matches? **No.** Every edge is checked.

### Data-governance challenge
Could source paths or patient identifiers leak into processing events by design? **No allowed field exists for them, and tests reject non-source-ID refs.**

### Program-management challenge
Does DAY45 pretend DAY53 persistent event infrastructure exists? **No.** It explicitly marks it not implemented and hands off only the event emission contract.
