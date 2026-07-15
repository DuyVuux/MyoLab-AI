# Intended Use Statement — v0.1 Draft

## Intended use
The sEMG/MFCV Fatigue Clinical Intelligence Layer is intended to support clinicians and rehabilitation/motion-lab technicians by analyzing quality-checked sEMG-derived fatigue evidence from standardized sessions. The system summarizes signal quality, fatigue-related features, fatigue resistance trends, use-case routing, and clinician-review-ready interpretations for rehabilitation, sports medicine, Motion Lab assessment, longitudinal rehab tracking, and return-to-play support.

## Intended users
- Rehabilitation physician.
- Sports medicine / orthopedic clinician.
- Motion Lab technician.
- Rehabilitation technician.
- Research/clinical AI team during validation.

## Intended data sources
- Synthetic sEMG demo files.
- CSV/TXT sEMG export files.
- Noraxon/myoRESEARCH-compatible exports when available.
- Optional Motion Lab synchronized data when export/sync are confirmed.
- MFCV/CV-related inputs only when electrode geometry and sampling eligibility are confirmed.

## Non-intended use
- Not for automated disease diagnosis.
- Not for autonomous treatment prescription.
- Not for automatic return-to-play clearance.
- Not for replacing clinical judgement, Motion Lab technicians, Noraxon/myoRESEARCH, or existing acquisition workflow.
- Not for reporting MFCV/CV when electrode geometry and sampling eligibility are not confirmed.

## Human-in-the-loop rule
A final clinical-facing report requires review/sign-off by qualified clinical or technical staff. AI/rule output is supporting evidence, not final medical decision.

## Abstention rule
If signal quality, metadata, protocol consistency, or MFCV eligibility is insufficient, the system must return “data not sufficient for analysis” with reason codes rather than forcing a fatigue conclusion.
