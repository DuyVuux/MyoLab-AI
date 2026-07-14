# Product Boundaries - v0.1 Draft

## Safety baseline
The product requires human review and uses abstention when data quality, metadata, protocol context, or MFCV/CV eligibility is insufficient.

## In scope for MVP-0
- Offline import of synthetic and generic CSV/TXT sEMG files.
- Noraxon-style export compatibility once a real export format is audited.
- Session metadata and protocol validation.
- Signal quality gate with pass, warning, fail, and reason-code outputs.
- Preprocessing, windowing, and feature extraction for fatigue evidence.
- RMS, MAV, MDF, MNF, slope, and trend summaries.
- Optional MFCV/CV eligibility output; calculation remains disabled unless eligibility is proven.
- Rule-based fatigue evidence aggregation.
- Human-readable report prototype with conservative wording.

## Out of scope for MVP-0
- Direct EMG device control.
- Replacement of Noraxon/myoRESEARCH.
- Autonomous diagnosis or treatment decisions.
- Automatic return-to-play clearance.
- Validated realtime clinical alerting.
- Deep learning or multi-site model training.
- Real patient raw signal committed to the repository.

## Allowed claims
| Claim | Allowed wording |
|---|---|
| Product category | Clinical Intelligence layer compatible with sEMG/Motion Lab/Noraxon-style data exports. |
| Signal quality | The system checks whether data is sufficient for fatigue evidence extraction. |
| Fatigue evidence | The system extracts fatigue-related evidence such as RMS/MAV/MDF/MNF trends and optional MFCV/CV when eligible. |
| Clinical interpretation | The system supports clinician/KTV review by summarizing evidence in use-case-specific language. |
| Longitudinal tracking | The system can compare sessions only when protocol, muscle, side, and normalization are compatible. |

## Prohibited claims
| Claim | Why prohibited | Safer wording |
|---|---|---|
| “Diagnoses muscle disease” | Overclaim; not the product scope. | “Supports functional fatigue assessment.” |
| “Replaces Noraxon/myoRESEARCH” | Wrong competitive positioning. | “Works on top of Motion Lab/Noraxon-compatible data.” |
| “Automatically decides return-to-play” | Clinical safety risk. | “Provides supporting evidence for return-to-play review.” |
| “Realtime clinical alert is validated” | Not validated at MVP-0. | “Near-real-time demo; offline-first MVP.” |
| “Always computes MFCV” | Needs electrode array, geometry, orientation, and sampling eligibility. | “Computes MFCV only when eligible.” |
| “No fatigue detected” after quality fail | Conflates missing evidence with negative evidence. | “Data quality is insufficient; analysis abstained.” |
