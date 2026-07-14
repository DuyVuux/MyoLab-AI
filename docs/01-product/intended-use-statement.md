# Intended Use Statement - v0.1 Draft

## Intended use
The sEMG/MFCV Fatigue Clinical Intelligence Layer is intended to support clinicians, rehabilitation staff, Motion Lab technicians, and research teams by analyzing quality-checked sEMG-derived fatigue evidence from standardized sessions. The system summarizes signal quality, fatigue-related features, fatigue resistance trends, MFCV/CV eligibility, use-case routing, and clinician-review-ready interpretation.

## Intended users
- Rehabilitation physician.
- Sports medicine or orthopedic clinician.
- Motion Lab technician.
- Rehabilitation technician.
- Biomedical signal reviewer.
- Research or clinical AI team during validation.

## Intended data sources
- Synthetic sEMG demo files.
- Generic CSV/TXT sEMG exports.
- Noraxon/myoRESEARCH-compatible exports when available.
- Optional Motion Lab synchronized data when export and sync assumptions are confirmed.
- MFCV/CV-related inputs only when electrode geometry and sampling eligibility are confirmed.

## Non-intended use
- Not for automated disease diagnosis.
- Not for autonomous treatment prescription.
- Not for automatic return-to-play clearance.
- Not for replacing clinical judgement, Motion Lab technicians, Noraxon/myoRESEARCH, or existing acquisition workflow.
- Not for reporting MFCV/CV when electrode geometry, channel ordering, muscle-fiber orientation, and sampling eligibility are not confirmed.
- Not for clinical-grade realtime alerting in MVP-0.

## Human-in-the-loop rule
A final clinical-facing report requires review and sign-off by qualified clinical or technical staff. AI/rule output is supporting evidence, not a final medical decision.

## Quality and abstention rule
If signal quality, metadata, protocol consistency, or MFCV eligibility is insufficient, the system must return an abstention result such as “data not sufficient for analysis” with reason codes rather than forcing a fatigue conclusion.
