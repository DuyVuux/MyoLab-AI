# Reproducible Training Policy — sEMG Clinical Intelligence

**Artifact:** `docs/09-mlops-devops/reproducible-training-policy.md`  
**schema_version:** `1.0`  
**status:** `PROVISIONAL_LOCKED_FOR_DAY26_BLUEPRINT`  
**trainingAllowed:** `false`  
**Policy effect:** Defines future gates; does not authorize training on Day 26.

---

## 1. Purpose

Prevent irreproducible, leakage-prone or ungoverned training before Day 29 and later phases.
This policy locks:

- exact environment contract;
- dependency-lock requirements;
- data/split/test seals;
- fold-contained fitting;
- random seed streams;
- thread/BLAS controls;
- runtime fingerprinting;
- rerun tolerances;
- serialized pipeline contents;
- license/security preflight;
- release evidence and rollback readiness.

---

## 2. Non-negotiable rules

1. Day 26: `trainingAllowed=false`.
2. No fitting command may run unless an approved future authorization flips this flag in a
   new, reviewed execution config.
3. No random-window split as primary benchmark.
4. Split raw hierarchy before segment/window generation.
5. Scaler, learned normalization, feature selector, calibrator and threshold are fit only in
   training/inner-validation data.
6. Outer/sealed test is evaluated once under frozen decisions.
7. Task A, B and C use separate targets, manifests and result interpretations.
8. Public healthy data are engineering baseline only.
9. MFCV-dependent logic is disabled unless eligibility is verified.
10. No raw score is called probability before the probability semantic gate.
11. Human review and abstention remain mandatory.
12. No online/incremental learning from unreviewed feedback.
13. Dataset/license gate must pass before any data enter a training corpus.
14. CPU-first reference execution is mandatory; GPU is not presumed.

---

## 3. Training authorization gate

A future training job may start only when all conditions are true:

```yaml
training_authorization:
  training_allowed: true
  authorization_record_present: true
  experiment_manifest_valid: true
  dataset_manifest_hash_verified: true
  split_manifest_hash_verified: true
  test_seal_present_and_unopened: true
  environment_contract_lock_verified: true
  resolved_dependency_lock_present: true
  resolved_dependency_lock_hash_verified: true
  license_gate_passed: true
  leakage_preflight_passed: true
  task_target_and_metric_contract_locked: true
  code_commit_clean_or_diff_archived: true
  human_reviewer_required_for_result_promotion: true
```

Any false/unknown field blocks execution.

---

## 4. Reference environment lock

### 4.1. Exact core versions

```yaml
python: "3.13.14"
numpy: "2.5.1"
scipy: "1.18.0"
scikit_learn: "1.9.0"
mlflow: "3.14.0"
uv: "0.11.32"
```

Status: `PROVISIONAL_ENGINEERING_LOCK`.

The lock is exact because sklearn persistence and numerical behavior are not guaranteed across
versions. This is not a clinical approval.

### 4.2. Lock files

Required before Day 29:

```text
configs/environment-lock.research.yaml        # authoritative version contract
environment/pyproject.toml                    # exact direct requirements
environment/requirements-core.lock.txt        # human-readable exact core pins
environment/uv.lock                           # fully resolved transitive lock, generated pre-Day29
```

The Day 26 package intentionally does not fabricate a resolver-generated `uv.lock`. The
preflight script must block training until a real resolved lock is generated in the approved
environment and its hash is recorded.

### 4.3. Allowed lock update

A lock update requires:

- decision-ledger entry;
- reason and security/compatibility review;
- separate experiment series;
- golden-fixture comparison;
- persistence compatibility review;
- no silent combination with model/feature search changes.

---

## 5. Environment capture

Every run stores a JSON fingerprint containing:

```text
Python executable and version
package versions and locations
OS / kernel / architecture / libc
CPU model / flags / core counts
RAM
NumPy build configuration
BLAS / LAPACK / OpenMP runtime
threadpoolctl output
thread environment variables
joblib backend and n_jobs
locale and timezone
Git remote / branch / commit / dirty state
container image digest, if any
lock file path and SHA-256
hostname pseudonymous identifier
```

Command:

```bash
python scripts/capture_environment.py \
  --output /data/experiments/runs/<experiment_id>/environment.json
```

No PHI is collected.

---

## 6. Data and split immutability

### 6.1. Required data hierarchy

```text
subject_id
└── day_id
    └── session_id
        └── trial_id
            └── repetition_id
                └── segment_id
                    └── window_id
```

### 6.2. Split order

```text
raw registry
→ duplicate/near-duplicate audit
→ group-aware split
→ segment within each partition
→ window within each partition
→ fit transforms only on train/inner train
```

### 6.3. Required manifests

- dataset manifest;
- raw-file registry and hashes;
- class ontology;
- channel mapping;
- split manifest with group keys;
- sealed-test record;
- license records;
- preprocessing/feature/model/calibration/threshold/abstention configs.

### 6.4. Duplicate controls

- SHA-256 exact duplicate check;
- source/session/repetition identity audit;
- near-duplicate review where repeated exports or trims are possible;
- augmented children inherit parent partition;
- no filename/path/ID fields in predictors.

---

## 7. Nested group-validation policy

### 7.1. Outer loop

Purpose: estimate generalization only.

Permitted primary regimes:

- cross-subject grouped outer CV;
- cross-session/cross-day grouped evaluation;
- personalized new-subject with predeclared target calibration subset and locked target test;
- electrode remove-and-replace;
- fatigue-stratified audit retaining the primary group split;
- unsupported/unknown/abstention evaluation retaining group separation.

Within-session is sanity/debug only.

### 7.2. Inner loop

The inner loop alone may choose:

```text
normalization/scaler
feature family/selector
model family and hyperparameters
class weights/priors
calibration method
classification threshold
reject/abstention threshold
context-to-action mapping
personalization strategy parameters
```

### 7.3. Outer test prohibition

Outer test must never influence:

- search-space revision;
- selected feature count;
- calibrator choice;
- threshold/coverage target;
- class ontology;
- failure handling;
- report narrative.

A violation is `LEAKAGE_CRITICAL` and invalidates the result.

---

## 8. Random seed policy

### 8.1. Root and named streams

```yaml
root_seed: 260826
named_seeds:
  split: <spawned>
  inner_cv: <spawned>
  estimator: <spawned>
  feature_selection: <spawned>
  calibration: <spawned>
  threshold: <spawned>
  bootstrap: <spawned>
  synthetic_fixture: <spawned>
```

The values are stored in the experiment manifest. They must be spawned deterministically from
one root seed rather than manually improvised.

### 8.2. Estimator requirements

- `random_state=None` is prohibited for stochastic decision-grade components.
- Every CV splitter with shuffle receives explicit seed.
- Bootstrap seed is independent from estimator seed.
- Calibration/threshold selection seed is separate from base estimator seed.
- Parallel child work receives deterministic spawned streams, not shared mutable RNG.

### 8.3. Multiple-seed sensitivity

If the selected algorithm is materially stochastic, run a predeclared seed set inside the
same development protocol. Do not select the best seed. Report distribution or lock a fixed
seed before the outer test.

---

## 9. Threading and numerical-runtime policy

### 9.1. Reference reproducibility profile

```bash
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export BLIS_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
```

```yaml
n_jobs: 1
compute_device: cpu
runtime_profile: reference_reproducibility_cpu_single_thread
```

### 9.2. Performance profile

A separate profile may use more threads, but requires:

- explicit thread values;
- its own environment fingerprint;
- result-equivalence check;
- p50/p95 timing under declared load;
- no claim that timing is deterministic.

### 9.3. GPU profile

Not permitted by default. See Section 16.

---

## 10. Preprocessing and feature reproducibility

Every preprocessing/feature configuration must specify:

```text
input units
sampling-rate assumptions
bandpass/notch/filter design and implementation
zero-phase/causal mode
filter order and coefficients or design parameters
resampling method
window length and increment/overlap
transition handling
artifact mask policy
normalization method and fitting scope
feature definitions and units
feature order
channel aggregation/order
missing/nonfinite policy
software implementation version
```

Feature order is a compatibility field. Silent reorder is prohibited.

Any threshold learned from noise floor, rest, MVC, session statistics or population statistics
must declare the data scope and live inside the proper fold/calibration subset.

---

## 11. Serialized pipeline requirements

A future model bundle must include or reference:

```text
input schema
channel/class mappings
preprocessing
scaler
feature selector
model or metric engine
calibrator
thresholds
abstention policy
reason-code registry
version metadata
environment lock
model card
license record
hash ledger
```

### 11.1. Canonical format

Preferred for simple classical pipelines:

```text
JSON/YAML metadata
+ NumPy arrays with allow_pickle=False
+ strict schemas
```

### 11.2. ONNX

Allowed only after:

- supported operator audit;
- fixed opset/converter/runtime versions;
- golden input equivalence;
- class-order and score parity;
- calibrator/threshold/abstention parity;
- latency/memory profile;
- sandboxed runtime.

### 11.3. Pickle/joblib

- trusted research snapshot only;
- hash verified;
- exact environment required;
- never load external/untrusted artifact;
- not pilot default;
- loader runs with least privilege;
- cross-version load is blocked unless migrated and revalidated.

---

## 12. Rerun protocol

### Step 0 — Preflight

**Input**

- Valid manifest and authorization record.

**Output**

```yaml
preflight: pass|fail
failures: []
```

### Step 1 — Clean environment reconstruction

**Input**

- exact Python/toolchain and resolved lock.

**Action**

```bash
uv sync --frozen
uv lock --check
```

**Output**

- environment fingerprint and lock hash.

### Step 2 — Verify immutable inputs

**Input**

- dataset/split/config files.

**Action**

- verify every SHA-256;
- verify test seal unopened;
- verify class/channel/protocol versions.

**Output**

- hash verification report.

### Step 3 — Execute reference run

**Input**

- same code commit, seeds and reference runtime profile.

**Output**

- result ledger, metrics, logs and artifact hashes.

### Step 4 — Compare

**Input**

- original and rerun outputs.

**Output**

- exact/tolerance comparison report.

### Step 5 — Review

**Input**

- rerun report and differences.

**Output**

- `PASS`, `PASS_WITH_EXPLAINED_DIFFERENCE` or `FAIL`.

Unexplained differences block candidate promotion.

---

## 13. Rerun tolerance contract

### 13.1. Exact equality

- split/group assignments;
- class/channel order;
- selected feature names/order;
- integer predictions;
- abstention reasons;
- manifest/config hashes;
- model component versions.

### 13.2. Floating values

Reference same-runtime provisional tolerance:

```text
array rtol = 1e-7
array atol = 1e-9
scalar metric absolute delta <= 1e-8
```

A tolerance pass does not excuse a changed dependency/CPU profile; environment difference must
still be disclosed.

### 13.3. Operational values

Latency and memory are reported statistically. They are not expected to reproduce exactly.
Compare:

- workload identity;
- warm/cold mode;
- sample count;
- median/p95;
- system load and runtime profile.

---

## 14. Experiment result completeness

A future training run is incomplete unless it emits:

```text
schema-checked experiment manifest
outer OOF prediction ledger
metric summary
per-class/subject/session reports
calibration report where applicable
coverage/risk/abstention report where applicable
failure cases
operational profile
environment fingerprint
hash ledger
model card draft
license summary
review status
```

No single accuracy/F1 number can close an experiment.

---

## 15. License preflight

Before data are admitted to training:

1. Resolve canonical source and license/DUA.
2. Record version and review date.
3. Separate data access from reuse rights.
4. Determine research, commercial, redistribution and trained-artifact rights.
5. Record attribution/share-alike/DUA/IRB obligations.
6. Fail closed on ambiguity.
7. Propagate obligations into model card and release manifest.

Data with `CC BY-NC`, research-only or custom DUA may be acceptable for a specifically
approved research experiment but cannot silently flow to pilot-commercial release.

---

## 16. Deployment-compute policy

### 16.1. CPU-first

Reference baseline and reproducibility run uses CPU. This is appropriate for the current
classical ladder and avoids unjustified GPU complexity.

### 16.2. GPU gate

GPU research requires all:

```text
site-confirmed budget not met on CPU
profiling proves compute bottleneck
end-to-end p95 benefit including transfer/startup
memory/driver/security/maintenance acceptable
exact GPU environment lock
CPU fallback
license clearance
new release/runtime profile
```

GPU is not allowed merely because it is available.

### 16.3. Latency budget

No clinical threshold is defined. Measure according to:

```text
t_window_start
t_window_close
t_decision_ready
t_user_visible
```

Budget fields remain `NOT_VERIFIED` until site/human-factor evidence.

---

## 17. Failure handling

| Failure | Required action |
|---|---|
| Hash mismatch | Stop; preserve evidence; investigate tampering/corruption |
| Missing resolved lock | Stop training |
| Test seal opened | Stop; log incident; invalidate protocol as applicable |
| License unknown | Remove source or obtain review; no training |
| Group overlap | Rebuild split; invalidate result |
| Fit outside fold | `LEAKAGE_CRITICAL`; invalidate result |
| Rerun outside tolerance | Block promotion; root-cause analysis |
| Unsupported device/config | Block/abstain; no silent adaptation |
| Pickle/joblib trust unknown | Refuse load |
| Resource exhaustion | Stop; reject/defer candidate; preserve logs |
| Human-review gate missing | No release/pilot promotion |

---

## 18. Negative tests

| Test ID | Invalid behavior | Expected rejection |
|---|---|---|
| `REP-NEG-001` | Day 26 `trainingAllowed=true` | Config invalid |
| `REP-NEG-002` | Missing `uv.lock` after training authorization | Preflight fail |
| `REP-NEG-003` | Lock hash differs from manifest | Preflight fail |
| `REP-NEG-004` | Scaler fit on all data | Leakage critical |
| `REP-NEG-005` | Feature selection before grouped CV | Leakage critical |
| `REP-NEG-006` | Threshold tuned on outer test | Leakage critical |
| `REP-NEG-007` | Seed omitted for stochastic estimator | Preflight fail |
| `REP-NEG-008` | Window split before subject/session split | Protocol invalid |
| `REP-NEG-009` | Rerun under different sklearn version | Compatibility fail |
| `REP-NEG-010` | Untrusted joblib/pickle load | Security fail |
| `REP-NEG-011` | GPU path without CPU profiling evidence | Policy fail |
| `REP-NEG-012` | License ambiguity ignored | License gate fail |
| `REP-NEG-013` | Task B score called probability without gate | Semantic fail |
| `REP-NEG-014` | MFCV fields emitted when eligibility false/unknown | Compatibility/safety fail |

---

## 19. Definition of Done

- [ ] Exact core environment contract exists.
- [ ] Real resolved `uv.lock` is a pre-Day29 hard gate.
- [ ] Runtime fingerprint contract exists.
- [ ] Root/named seed policy exists.
- [ ] CPU single-thread reference profile exists.
- [ ] BLAS/thread variables are recorded.
- [ ] Split-first/window-later and nested grouped CV are locked.
- [ ] Test-seal policy is locked.
- [ ] Rerun tolerance is defined.
- [ ] Serialized pipeline contents are defined.
- [ ] Pickle/joblib security warning is explicit.
- [ ] ONNX equivalence gate is explicit.
- [ ] License preflight is mandatory.
- [ ] CPU-first/GPU gate is explicit.
- [ ] No clinical latency threshold is fabricated.
- [ ] No Day 26 training/model artifact.

---

## 20. Handoff

### Provisional decisions

- Exact reference core versions selected.
- `uv.lock` resolver output required before Day29.
- CPU single-thread is reference mode.
- Named seed streams and strict manifests are mandatory.
- Typed canonical serialization is preferred.

### Rejected alternatives

- Unlocked/`latest` dependencies.
- Global preprocessing/feature selection.
- Test-set threshold tuning.
- Cross-version pickle/joblib load.
- GPU-by-default.

### NOT_VERIFIED

- Final site runtime profile.
- Actual transitive dependency lock until generated.
- Clinical latency/memory budgets.
- ONNX support for every future composite pipeline.

### Go status

**`GO_WITH_CONDITIONS`**; resolved dependency lock and approved training authorization remain
hard pre-Day29 dependencies.
