# Vinmec MotionLab Data Request Pack v0.1

**Purpose:** request the minimum governed evidence needed to move P0/P1/Knee discovery forward. No raw patient files are embedded in this repository artifact. 

**Regulatory Principle:** This request adheres to **GDPR Data Minimization (Article 5(1)(c))** — we only request data strictly necessary for the specified purpose. Evidence collected must also meet **FDA Real-World Data (RWD)** standards for *Relevance* (fits the clinical question) and *Reliability* (data provenance and quality assurance).
## A. P0 — sEMG Data Processing & Quality Intelligence
Request, subject to approved governance/de-identification:
1. One representative MR4 **single CSV** export with metadata header and mixed signals if normally produced.
2. Matching/representative **separated export**: `info.csv` + individual EMG/signal files.
3. At least one technically good and one known-problematic session/window, with clinician/operator explanation of why it is problematic.
4. Current protocol context: muscle, side, task, load/speed when applicable, normalization reference, filters/windowing/preprocessing currently used.
5. Device/software/version/export settings available for the recording.
6. Remeasurement example/reason where available.

**Do not include direct identifiers in the analysis package.** If exact timestamps or other quasi-identifiers are required, retain only under the approved policy.

## B. P1 — Plantar pressure left/right
1. Pressure/contact/COP export with exact field names and units.
2. Clinician-confirmed L/R reference.
3. Include abnormal/pathological gait examples, not only easy healthy gait.
4. Definition of `LT Force` / `RT Force` and device semantics remains a site/vendor question until confirmed.

## C. Knee/ACL discovery — DR-K01
Request one real governed failure case containing, as allowed:
- raw/underlying recording reference;
- movement/task;
- current graph/output judged wrong;
- Vicon/video context if approved and necessary;
- clinician statement identifying the failure;
- exact software/version/model/coordinate context when known.
No Knee correction algorithm may be started merely because another public knee dataset exists.

## D. Transfer package metadata
Each delivered source should have a source ID, governance status, de-identification status, data owner/contact role, acquisition date handling policy, device/software version if available, protocol/task, file inventory and checksum ledger generated in the approved environment.

## E. Explicitly not requested at DAY06
- unrestricted patient identifiers;
- a large dataset “just in case”;
- model-training authorization;
- clinical diagnosis labels unrelated to approved use;
- MFCV claims without geometry eligibility evidence.
