# Assumptions and Open Questions — Day 1

## Assumptions
| ID | Assumption | Why it matters | Risk if false | Owner mode | Validation plan |
|---|---|---|---|---|---|
| A-001 | MVP starts offline-first using synthetic/CSV/Noraxon export files. | Reduces premature realtime clinical claims. | Demo may feel limited. | Duy | Confirm in demo script. |
| A-002 | MFCV/CV is optional until linear electrode array, inter-electrode distance, orientation, and sampling are confirmed. | Prevents overclaim. | Cannot advertise MFCV in MVP. | Duy | Motion Lab/Noraxon audit. |
| A-003 | Human review is required before final clinical report. | Clinical safety and workflow fit. | Product may look like autonomous diagnosis. | Quân | Report wording review. |
| A-004 | No real patient raw data will be committed to repo. | Privacy/security baseline. | Data governance incident. | Quân | Gitignore + data policy. |

## Open questions for Day 2+
1. Which first protocol should be used: quadriceps isometric 60s, biceps isometric, or repeated squat?
2. Which data format is most likely available from Motion Lab/Noraxon: CSV, TXT, MAT, C3D, or processed report?
3. Is the first pitch aimed at Motion Lab director, rehabilitation clinician, KTV, or executive sponsor?
4. Is return-to-play included in MVP-1 or only in roadmap/demo narrative?
5. What exact wording is acceptable for “fatigue detected,” “review suggested,” and “not enough data”?
