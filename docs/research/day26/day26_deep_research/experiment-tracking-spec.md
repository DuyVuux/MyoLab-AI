# Experiment Tracking Specification — sEMG Clinical Intelligence

**Artifact:** `docs/09-mlops-devops/experiment-tracking-spec.md`  
**schema_version:** `1.0`  
**status:** `PROVISIONAL_LOCKED_FOR_DAY26_BLUEPRINT`  
**trainingAllowed:** `false`  
**Owner:** Single Operator / ML Engineering  
**Mandatory review:** DSP/ML reviewer before `candidate`; clinical/site review before `pilot-candidate`.

---

## 1. Purpose

Define how every research experiment is identified, reproduced, audited, reviewed and linked
to datasets, splits, code, configurations, evidence, licenses and future release artifacts.

This specification applies independently to:

- **Task A:** Gesture Recognition.
- **Task B:** Fatigue Context / Confidence Adjustment / Abstention.
- **Task C:** Quantitative Assessment.

It does not authorize training during Day 26.

---

## 2. Decision: hybrid tracking

### 2.1. Governance source of truth

Authoritative record:

```text
content-addressed experiment manifest
+ immutable referenced files
+ Git-reviewed specifications
+ SHA-256 ledger
```

### 2.2. Convenience layer

MLflow local server provides:

- run search/filtering;
- UI comparison;
- parameter/metric visualization;
- artifact browsing;
- model lineage convenience.

MLflow tags/aliases do not replace registry state records or human approval.

### 2.3. Reconciliation rule

An experiment is valid only when:

```text
manifest.experiment_id == mlflow.tags.experiment_id
manifest SHA-256 == mlflow.tags.manifest_sha256
code commit matches
all referenced hashes verify
```

A mismatch yields `TRACKING_DIVERGENCE` and blocks review/promotion.

---

## 3. Storage layout

```text
/data/projects/semg-fatigue/                    # Git worktree/specifications
/data/datasets/                                 # Controlled raw/processed/external data
/data/experiments/
├── runs/<experiment_id>/
│   ├── experiment-manifest.yaml
│   ├── environment.json
│   ├── hash-ledger.json
│   ├── logs/
│   ├── metrics/
│   ├── predictions/
│   └── artifacts/
├── registry/experiments/
├── registry/models/<model_id>/<version>/
└── mlflow/
    ├── mlflow.db
    └── artifacts/
/data/models/exported/<model_id>/<version>/
/data/backups/mlflow/
```

Raw clinical signal is never committed to Git or copied into MLflow by default. Tracking stores
controlled references and checksums.

---

## 4. Experiment identity

### 4.1. ID pattern

```text
EXP-YYYYMMDD-TASKA-<purpose>-NNN
EXP-YYYYMMDD-TASKB-<purpose>-NNN
EXP-YYYYMMDD-TASKC-<purpose>-NNN
```

Example blueprint ID:

```text
EXP-20260727-TASKA-CLASSICAL-BASELINE-001
```

### 4.2. Immutable identity fields

After execution starts, these fields cannot be changed in place:

- experiment ID;
- task ID;
- hypothesis version;
- dataset manifest hash;
- split manifest hash;
- test seal hash;
- code commit;
- environment lock hash;
- config hashes;
- root seed;
- metric contract ID.

A change creates a new experiment ID and links `supersedes`.

---

## 5. Manifest contract

Canonical schema:

```text
schemas/experiment-manifest.schema.json
```

Minimum fields:

| Group | Required fields |
|---|---|
| Governance | `schema_version`, `status`, `rationale`, `evidence_ids`, `open_questions`, `training_allowed` |
| Identity | `experiment_id`, `task_id`, `title`, `hypothesis`, `created_at`, `created_by` |
| Code | repository, commit, branch, dirty state, code archive/hash if required |
| Data | dataset ID/version/hash, source/license record, raw registry hash |
| Split | regime, group keys, split manifest hash, test seal hash/open state |
| Configs | preprocessing, feature, model, calibration, threshold, abstention refs/hashes |
| Seeds | root seed and named child seeds |
| Environment | lock path/hash, Python/library versions, OS/CPU/BLAS/thread profile |
| Metrics | metric contract ID, `NOT_RUN` or result references |
| Artifacts | path/URI, media type, size, SHA-256, role, trust class |
| License | training/research/commercial/redistribution/trained-artifact decisions |
| Review | reviewer, decision, timestamp, reason, evidence references |

---

## 6. Hash policy

### 6.1. File hash

```text
SHA-256(raw bytes)
```

### 6.2. Canonical structured-object hash

Before hashing JSON/YAML:

1. Parse into data object.
2. Reject duplicate keys.
3. Normalize to canonical JSON:
   - UTF-8;
   - sorted object keys;
   - no insignificant whitespace;
   - deterministic number/string representation;
   - LF line endings.
4. SHA-256 the canonical bytes.

### 6.3. Directory hash

Create a sorted ledger:

```text
<relative_path>\t<size_bytes>\t<sha256>\n
```

Then hash the ledger itself.

### 6.4. Required hashes

```text
dataset_manifest_sha256
raw_registry_sha256
split_manifest_sha256
test_seal_sha256
preprocessing_config_sha256
feature_config_sha256
model_config_sha256
calibration_config_sha256
threshold_policy_sha256
abstention_policy_sha256
environment_lock_sha256
code_archive_sha256_or_git_commit
model_card_sha256
release_manifest_sha256
```

---

## 7. Test seal

### 7.1. Purpose

Prevent the outer/sealed test from becoming an extended validation set.

### 7.2. Seal contents

```text
raw registry hash
split manifest hash
outer test IDs or encrypted/controlled reference
class ontology version
label provenance version
schema version
seal timestamp
seal owner
opened flag
open reason and approver
```

### 7.3. Rules

- `opened=false` during development.
- Any access is logged.
- Outer test can be evaluated only under a frozen manifest.
- Method/config/threshold changes after test access create `TEST_CONTAMINATION_INCIDENT`.
- Test re-use for a revised candidate requires a new independent test or explicit downgrade of evidence status.

---

## 8. MLflow mapping

| Manifest field | MLflow mapping |
|---|---|
| `experiment_id` | tag `experiment_id` + run name |
| `task_id` | tag `task_id` |
| `manifest_sha256` | tag `manifest_sha256` |
| `code.commit` | tag `git_commit` |
| config values | parameters; full files remain artifacts/references |
| metrics | metrics only after run; no fake values |
| dataset/split IDs | tags |
| dataset/split hashes | tags |
| environment lock hash | tag |
| registry state | tag mirror only; authoritative state is file registry |
| reviewer decision | tag mirror + authoritative review record |

No PHI, MRN, patient name or free-text clinical note may be stored in MLflow tags.

---

## 9. Local MLflow operation

### Step 0 — Verify blueprint mode

**Input**

- Day 26 config.
- Git status.

**Action**

```bash
rg 'trainingAllowed: false|training_allowed: false' configs examples docs
```

**Output**

```yaml
blueprint_mode: true
training_allowed: false
```

**Failure**

- Any Day 26 execution config permits fitting.

### Step 1 — Initialize directories

**Input**

- Approved `/data` layout.

**Action**

```bash
mkdir -p \
  /data/experiments/mlflow/artifacts \
  /data/experiments/runs \
  /data/experiments/registry/experiments \
  /data/experiments/registry/models \
  /data/backups/mlflow
```

**Output**

- Controlled local directories.

### Step 2 — Start local server

**Input**

- MLflow exact environment.

**Action**

```bash
scripts/start_mlflow_local.sh
```

**Output**

- Server on `127.0.0.1:5000`.

**Failure**

- Server binds `0.0.0.0` without approved authentication/network controls.

### Step 3 — Create manifest before run

**Input**

- Hypothesis.
- Dataset and split manifests.
- Configs.
- Environment lock.

**Action**

- Validate schema.
- Compute all hashes.
- Store in `/data/experiments/runs/<experiment_id>/`.

**Output**

- `experiment-manifest.yaml` with `status=planned`.

### Step 4 — Mirror to MLflow

**Input**

- Schema-checked manifest.

**Action**

- Create run.
- Set identity/hash tags.
- Log only approved artifact references.

**Output**

- `mlflow_run_id` added to a new manifest revision or run-link record.

### Step 5 — Close and review

**Input**

- Run outputs.
- Hash ledger.
- Review checklist.

**Action**

- Verify hashes.
- Mark `completed` then `reviewed`/`rejected`.
- Never overwrite run evidence.

**Output**

- Reviewer decision and immutable closeout record.

---

## 10. Backup and restore

### 10.1. Coordinated backup

Backup together:

```text
mlflow.db
mlflow/artifacts/
registry manifests
release bundles
```

Record:

- backup ID;
- timestamp;
- source paths;
- file counts and sizes;
- SHA-256 ledger;
- encryption/access state;
- restore-test status.

### 10.2. Restore drill

At least before pilot:

1. Restore to isolated directory/server.
2. Verify DB opens.
3. Compare run/model counts.
4. Verify sample artifact hashes.
5. Reconstruct one release from manifests.
6. Document duration and failure points.

A backup never tested for restore is not accepted as a rollback control.

---

## 11. Concurrency and future migration

### Single operator

- SQLite accepted.
- One MLflow writer process preferred.
- File manifests reviewed through Git.
- No remote unauthenticated access.

### Multi-user trigger

Migration to PostgreSQL/object storage is required when concurrent writers, pilot users,
RBAC, network access or stronger availability become necessary.

Migration package must include:

```text
migration plan
pre-migration backup
schema/version compatibility
artifact-copy verification
row and hash reconciliation
RBAC/TLS design
rollback plan
post-migration smoke tests
```

---

## 12. Retention and immutability

| Object | Default treatment |
|---|---|
| Raw clinical data | Controlled data store; policy determined by site, not Git/MLflow default |
| Experiment manifest | Permanent project audit record |
| Split/test seal | Permanent audit record |
| Run logs/metrics | Retain with experiment evidence |
| Rejected model artifact | Retain or quarantine per storage policy; registry record remains permanent |
| Release bundle | Immutable, retained with rollback chain |
| Temporary caches | Deletable after hash-verified outputs exist |

Deletion requires a reasoned record and must not break release reconstruction.

---

## 13. Negative tests

| Test ID | Invalid behavior | Expected result |
|---|---|---|
| `TRK-NEG-001` | Dataset hash missing | Manifest invalid |
| `TRK-NEG-002` | Split hash missing | Manifest invalid |
| `TRK-NEG-003` | `test_opened=true` while status planned/research | Preflight fail |
| `TRK-NEG-004` | MLflow manifest hash differs from file manifest | `TRACKING_DIVERGENCE` |
| `TRK-NEG-005` | PHI-like field in run tags | Metadata validation fail |
| `TRK-NEG-006` | Dirty code allowed without diff/archive reference | Review fail |
| `TRK-NEG-007` | Seed `None` or absent for stochastic estimator | Preflight fail |
| `TRK-NEG-008` | Existing experiment ID overwritten | Hard fail |
| `TRK-NEG-009` | Raw clinical file copied into Git package | Security/data-governance fail |
| `TRK-NEG-010` | Run deleted before release evidence export | Incident/escalation |

---

## 14. Definition of Done

- [ ] Hybrid decision recorded.
- [ ] File manifest is authoritative.
- [ ] MLflow local topology uses SQLite + local artifact store.
- [ ] Loopback-only startup script exists.
- [ ] Experiment manifest schema validates.
- [ ] Dataset, split, test seal and all config hashes are required.
- [ ] Environment lock/hash and runtime fingerprint are required.
- [ ] Named seeds are required.
- [ ] License gate is required.
- [ ] Review decision is required.
- [ ] Backup/restore policy exists.
- [ ] Future PostgreSQL/object-store migration path exists.
- [ ] No Day 26 training or fake metrics.

---

## 15. Handoff

### Provisional decisions

- Hybrid tracking selected.
- File manifests are SSOT.
- Local MLflow is allowed as a convenience layer.
- SQLite is accepted for single operator only.

### Rejected alternatives

- MLflow-only governance.
- File-only forever without indexing.
- Raw data/model binaries committed to Git.

### NOT_VERIFIED

- Final site storage paths/access policy.
- Future pilot auth/RBAC topology.
- Backup retention schedule.

### Dependencies

- Data versioning spec.
- Test-seal manifest.
- Environment lock.
- Model registry spec.
- Release and rollback schemas.

### Go status

**`GO_WITH_CONDITIONS`**.
