# DAY33 EXECUTION PLAN — Research Benchmark Corpus v1: Public + Synthetic Evidence Pack

## 0. Document Control

- **Program:** MyoLab-AI / sEMG Quality Intelligence
- **Day:** DAY33
- **Continuation mode:** Independent Research / Portfolio
- **Upstream:** DAY32 Annotation Readiness Protocol & Evidence-Tier Design
- **Clinical status:** NOT CLINICALLY VALIDATED
- **Training authorization:** FALSE
- **Primary outcome:** a research benchmark corpus with verified public-source governance and deterministic synthetic known-truth payloads.

## 1. Executive Intent

DAY33 replaces the former assumption that clinicians will annotate real MotionLab windows. The
project no longer has guaranteed access to site data or clinicians, so the correct research move
is to construct a corpus whose evidence authority is explicit. DAY33 therefore combines two
assets without conflating them: (a) **verified public dataset sources** with primary-source
license/provenance and (b) **synthetic known-truth challenge windows** generated locally from a
deterministic engineering signal. Public raw data remains outside Git; synthetic fixtures may be
committed because they contain no patient data and are reproducible by seed.

The central safety decision is that public-source verification does not create a clinical evidence
tier. Public datasets are external research sources. The DAY32 four-tier ladder continues to govern
annotation authority. Since DAY33 does not yet run the QC labeling functions over acquired public
windows, the actual corpus `items` are synthetic and therefore use exactly
`SYNTHETIC_KNOWN_TRUTH`. Public sources are registered separately and become window-level items
only after local acquisition, canonical adaptation and DAY22 windowing in a later step.

## 2. Why DAY33 Exists

DAY32 made annotation possible without inventing expert truth. DAY33 makes **evaluation data
engineering** possible without inventing clinical access. The project needs real external source
metadata, valid licensing and a reproducible challenge corpus before DAY34 can compare labeling
functions or DAY35 can study threshold sensitivity. Without this day, later analyses could quietly
mix unlicensed datasets, synthetic pathology, arbitrary random crops, or tuned/locked data.

## 3. Critical Path

```text
DAY32 evidence authority
        ↓
public source/license verification
        +
deterministic synthetic fixture generation
        ↓
DAY22 WindowIdentity + context
        ↓
research corpus manifest
        ↓
development / locked split
        ↓
DAY34 weak-label disagreement evaluation
```

## 4. Preconditions

Input contracts required from the live repository:

1. DAY22 `semg_core.qc_windowing.WindowIdentity` and `QC_WINDOW_WITH_CONTEXT` semantics.
2. DAY32 `qc-annotation-research.v0.2` evidence authority.
3. DAY32 rule that automatic evidence promotion is forbidden.
4. The independent roadmap claim boundary: research only; no clinical/site validation.

The DAY32 handoff reports PASS, so DAY33 may begin. No clinician and no hospital data is a
precondition for this day.

## 5. Objectives

1. Verify a conservative shortlist of public sEMG sources at the primary repository/license level.
2. Produce machine-readable dataset cards/catalog entries.
3. Define an external-storage acquisition policy that never commits bulk raw public data.
4. Generate deterministic synthetic known-truth challenge signals.
5. Bind every synthetic corpus window to DAY22 WindowIdentity with context.
6. Create `benchmark-development` and `benchmark-locked` partitions.
7. Keep locked truth absent from the DAY33 manifest while storing a cryptographic commitment.
8. Make DAY33 entirely training-free.

## 6. Explicit Non-Goals

DAY33 does **not** train a model, tune a QC threshold, report detector accuracy, claim public data
represent Vinmec, create synthetic stroke, build a public dataset adapter, or reveal locked truth.
It also does not import multi-gigabyte datasets into the handoff ZIP.

## 7. Public Source Decision

Four sources are admitted to the catalog because their license and core metadata were verified from
primary repository pages on 2026-08-11:

- GRABMyo v1.1.0 — CC BY 4.0.
- Hyser v2.0.0 — Open Data Commons Attribution License v1.0.
- Mendeley 4-channel Hand Gesture v2 — CC BY 4.0.
- Cerqueira sEMG + Self-Perceived Fatigue v2 — CC BY 4.0.

Three categories are deliberately deferred/excluded from the default DAY33 corpus: Ninapro because
reuse licensing was not promoted to VERIFIED in the project audit; putEMG because CC BY-NC is not
the default public-portfolio reuse posture; PhysioMio because its custom DUA/restrictions are
incompatible with a frictionless public portfolio corpus.

## 8. Evidence Authority Model

The following rule is frozen:

```text
public dataset source metadata != annotation evidence tier
```

A dataset being open and well documented says where a signal came from. It does not turn a dataset
label into expert QC truth. DAY33 corpus payloads therefore remain synthetic known-truth. When a
public dataset is later acquired, its original labels remain source metadata with their original
meaning. QC weak labels are generated only by the project labeling functions, and expert tiers are
created only by qualified human review.

## 9. Data Partition Governance

`benchmark-development` is visible to engineers and can be used by DAY34/35 research analysis.
`benchmark-locked` is a process guard against opportunistic threshold tuning. Locked signal files are
present, but the manifest contains `synthetic_truth: null`. A SHA-256 commitment covers each hidden
truth tuple. This is not a cryptographic secret—the generator exists in source control—but it is a
clear governance barrier: DAY33/35 tooling must not consume locked labels.

Development and locked partitions use disjoint seed ranges. Any overlap is a hard failure.

## 10. Repository Placement

```text
data-platform/datasets/
├── public-sEMG-catalog.v0.1.yaml
├── day33-public-acquisition-plan.v0.1.yaml

packages/common-schemas/json/
└── research-benchmark-corpus.v0.1.schema.json

docs/05-data/dataset-cards/
├── GRABMyo-v1.1.0.md
├── Hyser-v2.0.0.md
├── Mendeley-4ch-hand-gesture-v2.md
└── Cerqueira-fatigue-v2.md

qa-validation/test-data/research/day33/
├── README.md
└── corpus/
    └── signals/*.npz                 # synthetic only

qa-validation/evidence/
├── research-benchmark-corpus-v0.1.manifest.yaml
├── day33-public-source-verification.v0.1.yaml
├── day33-data-readiness.reference.yaml
└── day33-locked-truth-commitments.v0.1.json

scripts/data/
├── build_research_benchmark_corpus.py
└── register_public_dataset_files.py
```

## 11. Data & Evidence Safety Invariants

- Raw patient/site data must never appear in DAY33 artifacts.
- Public raw payload must remain external to Git and ZIP.
- Synthetic fixtures must carry `clinical_evidence=false`.
- Low-amplitude synthetic stress cannot contain pathology labels.
- Every corpus item must use `QC_WINDOW_WITH_CONTEXT`.
- Every corpus item must have a content hash and deterministic seed.
- Public source `license_status != VERIFIED` means not corpus-eligible.
- Locked truth cannot be visible in the research manifest.
- No model fitting or threshold tuning occurs in DAY33.

## 12. Environment

Required runtime:

```text
Python >= 3.11
numpy
PyYAML
jsonschema
pytest
DAY22 semg_core.qc_windowing
```

No network dependency is allowed in the corpus builder. Source verification is an engineering
documentation action; reproducible corpus generation must work offline.

## 13. STEP 1 — Load DAY32 Contracts

**Goal:** Confirm the evidence ladder and WindowIdentity requirement before touching data.

**Input:** DAY32 schema/policy and DAY22 windowing module.

**Why:** A data engineer must not reinterpret public labels or create contextless windows.

**Action:** Verify exact four evidence tiers and `QC_WINDOW_WITH_CONTEXT`.

**Expected output:** No contract drift.

**Negative check:** Reject attempts to add `PUBLIC_EXTERNAL_EVIDENCE` as an annotation authority tier.
Public external is a source class, not a DAY32 annotation tier.

**Evidence:** DAY33 traceability impact file.

**Stop condition:** DAY32 contract missing/incompatible.

**Pass:** Contracts available and unchanged.

## 14. STEP 2 — Verify Public Dataset Governance

**Goal:** Choose only sources with verified rights and provenance.

**Input:** pre-DAY25 dataset research plus current primary repository records.

**Action:** Record dataset ID, version, DOI, repository, license, access class, subject/session count,
Fs where verified, channel/task summary, limitations and acquisition status.

**Output:** `public-sEMG-catalog.v0.1.yaml`.

**Negative checks:** An accessible dataset with ambiguous license remains excluded. A non-commercial
license is not silently treated as portfolio-safe. Restricted DUA data is not bundled.

**Pass:** At least one source is `corpus_eligible=true` and `license_status=VERIFIED`.

## 15. STEP 3 — Produce Dataset Cards

Each dataset card must answer five questions: What is it? What license applies? What acquisition facts
are verified? Why is it useful? What can it **not** prove? Cards are not marketing pages; their
purpose is to prevent later team members from converting source convenience into false clinical
claims.

**Output:** four cards under `docs/05-data/dataset-cards/`.

**Negative check:** Card language must not say `clinically validated` or site-equivalent.

## 16. STEP 4 — Freeze External Raw Storage Policy

The repository stores only metadata, adapters, hashes and synthetic fixtures. When public data is
acquired later, the operator sets `MYOLAB_PUBLIC_DATA_ROOT`, downloads according to the official
source terms, then runs `register_public_dataset_files.py`. The ledger contains relative file names,
SHA-256 and size but redacts the workstation root.

This preserves reproducibility without making the Git repository a data warehouse.

## 17. STEP 5 — Build Deterministic Synthetic Base Signal

The synthetic base is intentionally simple: 80 Hz + 120 Hz components plus seeded Gaussian noise.
It is not a physiological generator and is not called healthy muscle. Its purpose is to provide a
stable carrier on which known engineering corruptions can be injected.

**Negative check:** Do not call base waveform a patient/control sample.

## 18. STEP 6 — Inject Known-Truth Challenges

Development scenarios include clean, missing, zero dropout, flatline, clipping, elevated baseline
noise, 50 Hz power-line, low-frequency drift, motion transient, low-amplitude stress, duplicate
timestamp and non-monotonic timestamp.

The transform chain is recorded per item. Timestamp corruptions are stored in the raw synthetic time
sidecar while WindowIdentity is based on canonical sample indices, preserving the architecture that
integrity failures are checked before downstream processing.

## 19. STEP 7 — Bind DAY22 WindowIdentity

Each synthetic source receives a content-derived `source_id`. A versioned 250 ms/250 ms-step window
profile with 250 ms context is then used to create canonical windows. The selected central window
preserves `start_sample`, `end_sample_exclusive`, context bounds, source/session/channel identity and
window-profile fingerprint.

**Negative check:** No item is created from a free-form timestamp crop.

## 20. STEP 8 — Create Development / Locked Partitions

Development seeds are `33000+`; locked seeds are `33900+`. Seed overlap is prohibited. Development
items expose `scenario` and `truth_class`; locked items expose neither and use opaque item IDs and
file names. Only a SHA-256 truth commitment is committed.

## 21. STEP 9 — Generate Manifest and Schema Validation

The manifest is validated against Draft 2020-12 JSON Schema and semantic guards. Schema checks shape;
semantic validation checks things JSON Schema cannot conveniently prove, including file hashes,
seed separation, commitment coverage and pathology-token exclusion.

## 22. STEP 10 — Reproducibility Test

The builder is executed twice into separate temporary roots with the same catalog and environment.
Manifest text and `.npz` SHA-256 values must match exactly. This establishes known deterministic
engineering behavior before DAY34 reads any weak-label outcome.

## 23. STEP 11 — Confidentiality / Path Hygiene

Artifact scans must reject home-directory paths, direct identifiers, patient data, caches and public
raw payload. Source URLs/DOIs are allowed; local workstation roots are not.

## 24. STEP 12 — Automated Verification

Focused DAY33 tests cover mandatory artifacts, catalog licenses, evidence authority, WindowIdentity,
partition locking, synthetic pathologies, source hashing, offline builder behavior, metadata
completeness and deterministic replay.

The master script additionally runs DAY32 focused regression when the live repository contains it.

## 25. STEP 13 — Closeout / DAY34 Handoff

DAY34 receives:

- a verified public-source catalog;
- a development synthetic known-truth partition;
- a locked research partition with truth commitments;
- a WindowIdentity-linked manifest;
- no trained model and no threshold changes.

DAY34 is allowed to run the six labeling functions over development items and analyze disagreement.
It must not reinterpret public-source metadata as expert QC truth and must not unlock the locked
partition for tuning.

## 26. Automated Validation Matrix

| Area | Positive evidence | Negative evidence |
|---|---|---|
| License | 4 primary-source verified sources | ambiguous/restricted default sources excluded |
| Provenance | DOI/version/source URL | local workstation path absent |
| Evidence tier | synthetic items exact DAY32 tier | expert/weak auto-promotion rejected |
| Windowing | canonical WindowIdentity + context | random crop forbidden |
| Synthetic truth | explicit development truth | pathology fabrication forbidden |
| Locked split | truth absent + commitment | label leakage rejected |
| Hashing | signal SHA verified | mutation/hash mismatch rejected |
| Training | none | `.fit(`/optimizer/backward absent |

## 27. Manual Review Checklist

A reviewer must inspect each dataset card and confirm that the source role is narrower than its
scientific ambition. In particular, the Cerqueira self-perceived fatigue label is not a clinical
diagnosis, and Hyser/GRABMyo healthy participants are not MotionLab clinical validation cohorts.
The reviewer should also confirm that all selected source licenses are appropriate for the intended
research/portfolio workflow and that attribution requirements are preserved in future publications.

## 28. Failure Injection

Test failures intentionally include: unverified public license, raw payload marked committed,
direct identifier present, contextless window, visible locked truth, seed overlap, missing signal
file, modified signal hash and synthetic pathology token. Each must fail closed.

## 29. Traceability

DAY33 implements ICR-003, ICR-004, ICR-005, ICR-008 and ICR-009 directly. ICR-011 is enforced by
partition separation and the explicit absence of training. The day inherits DAY22 window identity
and DAY32 evidence authority.

## 30. Definition of Done

DAY33 is complete when the catalog, cards, corpus schema, manifest, builder, synthetic payload,
locked truth commitments, tests and evidence reports all exist and validate; the public raw payload
is absent; and `DAY33_DATA_READINESS=RESEARCH_READY` is defensible solely from verified public source
metadata plus reproducible synthetic fixtures.

## 31. Stop / Block Conditions

- Selected public source has unverified/ambiguous license.
- Any patient/company raw export appears in the package.
- Synthetic low amplitude is relabeled as pathology.
- Locked labels leak into the public manifest.
- Development/locked seeds overlap.
- Random crops replace DAY22 WindowIdentity.
- Builder requires internet or model fitting.
- Rebuild changes manifest/hashes unexpectedly.

## 32. Known Limitations

The public datasets are not yet downloaded into a local external data root and therefore no public
window is part of the DAY33 payload. This is deliberate. Dataset adapters and public windowization
belong to later public-benchmark work. DAY33 proves source governance and corpus mechanics, not
cross-dataset algorithm performance.

The synthetic base is an engineering carrier, not a biophysical muscle simulator. Known corruption
truth proves whether a detector can respond to constructed faults; it cannot establish clinical
sensitivity/specificity. No expert annotations exist.

## 33. Integration Procedure

From repository root, copy the DAY33 `repo_patch` preserving paths. Do not overwrite DAY22 or DAY32
contracts. Then run:

```bash
export PYTHONPATH="$PWD/packages/semg-core${PYTHONPATH:+:$PYTHONPATH}"
bash scripts/dev/run_day33_checks.sh
```

If live `semg_core.qc_windowing` differs from the frozen DAY22 API, stop and reconcile the upstream
contract rather than adding a silent compatibility shim to production.

## 34. Final Status Semantics

Allowed closeout:

```text
ENGINEERING_VALIDATION = PASS
RESEARCH_CORPUS = READY
PUBLIC_SOURCE_GOVERNANCE = VERIFIED
PUBLIC_RAW_PAYLOAD = NOT_ACQUIRED_IN_REPO
SYNTHETIC_KNOWN_TRUTH = READY
EXPERT_ANNOTATION = NOT_PERFORMED
CLINICAL_VALIDATION = NOT_PERFORMED
TRAINING = NOT_AUTHORIZED
DAY34 = GO_AFTER_LIVE_REGRESSION
```


## 35. Public Dataset Selection Rationale

DAY33 deliberately chooses a **small, auditable shortlist** rather than collecting every famous sEMG dataset. The selection objective is not leaderboard coverage. It is to establish a portfolio corpus with defensible legal provenance and complementary technical domains.

### 35.1 GRABMyo

GRABMyo is admitted because it provides a multi-day external domain with a clear open license and a manageable conceptual structure. Its three-session design is particularly valuable later for testing whether source/day variation changes QC supportability. It is not selected because gesture recognition is the product goal; gesture labels are incidental to DAY33. The signal and session structure are the useful assets.

### 35.2 Hyser

Hyser is selected because it deliberately challenges sparse-channel assumptions. A 256-channel HD-sEMG source creates a very different domain fingerprint from the original MotionLab sparse/bipolar setting. This mismatch is a feature for future distribution-support research, provided the project never calls Hyser a site surrogate. Its size also demonstrates why the external-data-root policy is necessary.

### 35.3 Mendeley 4-channel hand gesture

The Mendeley source is useful at the opposite extreme: a compact four-channel acquisition. It creates a future test for whether canonical adapters and QC contracts remain meaningful across channel density. DAY33 preserves fields only when verified from the source page. Sampling rate is therefore left `null` in the catalog rather than inferred from memory or secondary reports.

### 35.4 Cerqueira fatigue dataset

This source introduces long/upper-body fatigue context and a non-2048-Hz sampling rate. It is useful because the project must already support heterogeneous sampling rates. The self-perceived fatigue label is explicitly preserved as source-context evidence; it is not converted into an expert QC label or a clinical fatigue diagnosis.

## 36. Why Some Famous Datasets Are Deferred

A high-quality project should be able to say **no** to a dataset. Ninapro is historically important, but the current project audit did not promote its reuse license to the same verified state as the four selected sources. The correct action is to preserve it in the research inventory while excluding it from the default DAY33 corpus.

putEMG is technically useful, but its CC BY-NC condition makes it inappropriate as the default source for a portfolio artifact whose future reuse context may not always be strictly non-commercial. It can still be used later under an explicitly compatible research scenario.

PhysioMio has high scientific value for stroke rehabilitation but is governed by a custom/restricted usage agreement and no-redistribution constraints. DAY33 therefore keeps it out of the frictionless corpus. This is exactly the kind of governance discipline that prevents a portfolio repository from accidentally publishing restricted data.

## 37. Corpus Item Contract

Each DAY33 payload item has five identities that must not be confused:

1. **Source identity** — `source_id`, derived from exact synthetic bytes.
2. **Window identity** — `window_id`, derived from source/session/channel/sample coordinates and a versioned window profile.
3. **Corpus identity** — `item_id`, derived from partition, seed, source and window.
4. **Evidence authority** — `SYNTHETIC_KNOWN_TRUTH`.
5. **Partition authority** — development or locked.

Changing one layer does not authorize silently changing another. For example, moving an item to a different partition should create a different corpus item identity. Changing the window profile changes WindowIdentity. Changing source bytes changes source ID. These dependencies are intentional because they make accidental result reuse visible.

## 38. Synthetic Fixture Design Constraints

Synthetic fixtures are designed around **minimal causal intervention**. The base signal is deterministic and then one primary corruption is added per scenario. This makes debugging easier than creating a complex simulator containing many simultaneous abnormalities.

The initial scenario set intentionally spans both waveform quality and data-integrity faults:

| Scenario | Layer stressed | Known construction fact |
|---|---|---|
| `MISSING` | raw signal/data availability | NaNs inserted in known interval |
| `ZERO_DROPOUT` | acquisition/data integrity | zero segment inserted |
| `FLATLINE` | channel integrity | constant plateau inserted |
| `CLIPPING` | amplitude/acquisition | rail-like clipping inserted |
| `BASELINE_NOISE` | noise floor | broadband noise added |
| `POWERLINE_50HZ` | spectral contamination | 50-Hz sinusoid added |
| `MOTION_DRIFT` | low-frequency contamination | 2-Hz drift added |
| `MOTION_TRANSIENT` | transient artifact | high-amplitude transient added |
| `SYNTHETIC_LOW_AMPLITUDE_STRESS` | preserve-physiology guardrail | amplitude scaled only |
| `TIMESTAMP_DUPLICATE` | temporal integrity | one timestamp duplicated |
| `TIMESTAMP_NON_MONOTONIC` | temporal integrity | one time step reversed |

The construction fact is narrower than any downstream detector decision. `POWERLINE_50HZ` means a component was injected, not that the final QC policy must fail. Likewise low-amplitude stress is not poor contact unless corroborating evidence exists.

## 39. Locked-Partition Governance in Detail

The locked partition is intentionally introduced early because leakage is easier to prevent than to repair. DAY35 will perform threshold-sensitivity analysis. Without a locked partition, a researcher could repeatedly change thresholds until every synthetic challenge looks correct, then later report the same examples as validation evidence.

DAY33 therefore establishes three controls:

- distinct seed ranges;
- no truth fields in locked manifest items;
- a truth commitment digest for each locked item.

The handoff does not claim this is equivalent to a blinded clinical study. It is an engineering rehearsal for disciplined evaluation. The correct downstream behavior is: use development truth for rule analysis; leave locked cases untouched until a later explicitly authorized validation gate.

## 40. Public Acquisition Procedure for Future Use

When the team decides to acquire a selected public dataset, the exact flow is:

```text
verify source version + license still match catalog
        ↓
download into $MYOLAB_PUBLIC_DATA_ROOT/<dataset_id>/
        ↓
run register_public_dataset_files.py
        ↓
store external payload ledger in repo
        ↓
implement/verify dataset adapter
        ↓
canonicalize with source hashes preserved
        ↓
DAY22 WindowIdentity
        ↓
only then enter benchmark windows
```

No script in DAY33 automatically downloads data because network access, source authentication and legal terms are environmental concerns. A reproducible engineering artifact should not silently fetch hundreds of gigabytes during tests.

## 41. No-Training Governance

The builder and runner are scanned to ensure they do not fit a model. DAY33 does not create feature matrices for learning, optimize hyperparameters, or calculate performance metrics. Even deterministic threshold selection is deferred. The allowed computations are generation, hashing, schema validation, provenance registration and partition construction.

This matters for the project narrative: DAY33 is a **data engineering and research-governance milestone**, not an AI-results milestone. Strong ML systems often fail because this layer is skipped.

## 42. Failure-Safety Matrix

| Failure | Required response |
|---|---|
| Public license missing | Exclude/default ineligible; do not guess |
| Public source removed/version changed | Re-verify catalog before acquisition |
| Local raw public path accidentally committed | Validation failure; remove payload and rotate evidence ledger if needed |
| Synthetic hash mismatch | Reject corpus item |
| WindowIdentity unavailable | Stop; reconcile DAY22 dependency |
| Contextless crop | Reject item |
| Development/locked seed overlap | Reject corpus build |
| Locked truth appears in manifest | Reject build as leakage |
| Direct identifier field appears | Reject item/package |
| Synthetic pathology language appears | Reject item/document |
| Public source called clinical validation | Claim audit failure |

## 43. Security and Privacy Posture

DAY33 is intentionally low-risk because committed payload is synthetic. Nevertheless, the package tests the same habits required for sensitive data later: no absolute workstation paths, no direct identifiers, no hidden raw copies, content hashes, minimal metadata, and explicit source governance.

Public data can still contain demographic or participant identifiers that are legal to publish under the source license but unnecessary for this project. Future adapters should minimize fields to what is required for protocol/session grouping and research reproducibility. The fact that a public dataset contains a field does not mean MyoLab-AI needs to propagate it.

## 44. Reproducibility Definition

DAY33 reproducibility means more than “the script runs twice.” The following must remain stable for identical code/config:

- scenario list;
- seed allocation;
- synthetic sample arrays;
- synthetic time arrays;
- source IDs;
- window profile fingerprint;
- WindowIdentity;
- corpus item IDs;
- `.npz` content hashes;
- manifest serialization;
- locked truth commitment hashes.

If any one changes intentionally, the builder/version or relevant configuration must change so the evidence chain makes the change visible.

## 45. Research Claim Matrix

| Statement | DAY33 status |
|---|---|
| “We have verified open public sEMG sources.” | Supported for the selected catalog entries |
| “We have downloaded all selected public datasets.” | **Not supported** |
| “We have a deterministic synthetic QC challenge corpus.” | Supported |
| “The QC detectors are clinically accurate.” | **Not supported** |
| “The public datasets represent Vinmec patients.” | **Not supported** |
| “We can reproduce the corpus from seeds/config.” | Supported by tests |
| “We have expert annotations.” | **Not performed** |
| “We have a clinical gold standard.” | **Not performed** |

## 46. Adversarial Review Roles

Before integration, reviewers should attack DAY33 from five viewpoints:

- **Data Engineer:** Can source/version/hash be reconstructed without hidden local knowledge?
- **DSP Engineer:** Does the fixture preserve native sampling and avoid preprocessing before evidence capture?
- **ML Researcher:** Are development/locked boundaries sufficient to prevent obvious leakage?
- **Safety/QA:** Can synthetic/public evidence accidentally become a clinical claim?
- **Portfolio Reviewer:** Can a recruiter understand what is real, synthetic, public, not downloaded, and not validated?

A PASS requires all high-severity concerns to be fixed or explicitly recorded as limitations.

## 47. Integration and Rollback

DAY33 is additive. It must not overwrite DAY32 evidence contracts, DAY22 windowing logic, QC thresholds or metric policies. If integration causes upstream tests to fail, remove DAY33 files and restore the repository to the previous commit. Public acquisition ledgers, when added later, should be regenerated rather than manually edited after a rollback.

Recommended Git procedure:

```bash
git status --short
git switch -c day33-research-corpus
# copy repo_patch preserving paths
bash scripts/dev/run_day33_checks.sh
git diff --check
git status --short
```

Only after peer review should the branch be merged/tagged. The handoff status `PASS` refers to the reference staging environment; live repository promotion remains conditional on full live regression.

## 48. DAY34 Handoff Contract

DAY34 receives a **development set whose truth is known by construction** and a set of public sources whose legal/source metadata is verified. Its primary job is to run the six labeling functions over the development synthetic windows, measure rule coverage/disagreement and classify failure modes.

DAY34 must not:

- use the locked truth for tuning;
- claim reviewer agreement;
- call machine-rule correlation inter-rater reliability;
- calculate clinical sensitivity/specificity;
- promote public source labels into expert QC truth;
- train a label model unless a later roadmap decision explicitly authorizes it.

The appropriate DAY34 evidence statement is analytical: “On constructed challenge X, rule Y emitted candidate Z under config/version V.”

## 49. Exit Checklist

- [ ] Catalog has only verified active licenses.
- [ ] Dataset cards match catalog versions/DOIs.
- [ ] Public raw payload absent.
- [ ] Synthetic payload contains no patient data.
- [ ] Every item has stable DAY22 WindowIdentity.
- [ ] Every development item exposes construction truth.
- [ ] Every locked item hides truth and has commitment.
- [ ] Development and locked seeds are disjoint.
- [ ] No pathology fabrication.
- [ ] No model training/tuning.
- [ ] Focused tests PASS.
- [ ] DAY32 regression PASS.
- [ ] Artifact integrity PASS.
- [ ] Peer review status honestly recorded.

## 50. Final Engineering Interpretation

DAY33 converts the project from “we know some public datasets exist” into a governed research-data substrate. The important artifact is not the number of gigabytes downloaded. It is the ability to state, for every usable source or synthetic window: **where it came from, what rights apply, what bytes define it, what transformation created it, what authority supports its label, what partition it belongs to, and what conclusions are forbidden**.
