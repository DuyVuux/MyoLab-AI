# Executive Blueprint - v0.1 Draft

## One-line definition
MyoLab-AI is a Clinical Intelligence layer that transforms quality-checked sEMG/MFCV and Motion Lab/Noraxon-compatible data into fatigue evidence, use-case-specific interpretation, longitudinal tracking, and human-reviewed reports.

## Product is
- A signal quality gate for sEMG sessions.
- A fatigue evidence extraction layer using RMS, MAV, MDF, MNF, slopes, and optional MFCV/CV when eligible.
- A use-case routing layer for rehabilitation, post-op monitoring, sports medicine, Motion Lab assessment, longitudinal tracking, and return-to-play review support.
- A human-in-the-loop report workflow for technical and clinical review.
- An abstention-first system when signal quality, metadata, protocol consistency, or MFCV eligibility is insufficient.

## Product is not
- Not an EMG hardware product.
- Not a replacement for Noraxon/myoRESEARCH.
- Not an automated disease diagnosis tool.
- Not a fully autonomous treatment or return-to-play decision system.
- Not a validated realtime clinical alerting system in MVP-0.

## Day 1 decision status
| Area | Decision | Status |
|---|---|---|
| Intended use | Decision-support evidence layer for sEMG fatigue assessment | Draft |
| Product boundary | Clinical Intelligence on top of exported/synthetic data | Draft |
| Clinical claims | Restricted; no diagnosis or treatment claim | Draft |
| Realtime wording | Demo only; offline-first MVP | Draft |
| MFCV claim | Optional and eligibility-gated | Draft |
| Review model | Human review required before clinical-facing report | Draft |
| Failure behavior | Quality fail returns abstention, not forced fatigue/no-fatigue | Draft |

## Next gate
Gate 1 passes only if a stakeholder can clearly repeat: this is a clinical intelligence and reporting layer, not a new EMG device, not a Noraxon replacement, and not an autonomous diagnosis system.
