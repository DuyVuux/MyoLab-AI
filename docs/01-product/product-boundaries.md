# Product Boundaries — v0.1 Draft

## Safety baseline
The product requires human review and uses abstention when data quality, metadata, or MFCV eligibility is insufficient.

## Allowed claims
| Claim                   | Allowed wording                                                                                                 |
| -------------------------| -----------------------------------------------------------------------------------------------------------------|
| Product category        | Clinical Intelligence layer compatible with sEMG/Motion Lab/Noraxon-style data exports.                         |
| Signal quality          | The system checks whether data is sufficient for fatigue evidence extraction.                                   |
| Fatigue evidence        | The system extracts fatigue-related evidence such as RMS/MAV/MDF/MNF trends and optional MFCV/CV when eligible. |
| Clinical interpretation | The system supports clinician/KTV review by summarizing evidence in use-case-specific language.                 |
| Longitudinal tracking   | The system can compare sessions only when protocol, muscle, side, and normalization are compatible.             |

## Prohibited claims
| Claim                                  | Why prohibited                           | Safer wording                                             |
| ----------------------------------------| ------------------------------------------| -----------------------------------------------------------|
| “Diagnoses muscle disease”             | Overclaim; not the product scope.        | “Supports functional fatigue assessment.”                 |
| “Replaces Noraxon/myoRESEARCH”         | Wrong competitive positioning.           | “Works on top of Motion Lab/Noraxon-compatible data.”     |
| “Automatically decides return-to-play” | Clinical safety risk.                    | “Provides supporting evidence for return-to-play review.” |
| “Realtime clinical alert is validated” | Not validated at MVP-0.                  | “Near-real-time demo; offline-first MVP.”                 |
| “Always computes MFCV”                 | Needs electrode array/geometry/sampling. | “Computes MFCV only when eligible.”                       |
