# Parallel Intended Use v0.1

## Platform

MyoLab-AI is a research Clinical Intelligence layer for governed sEMG analysis. It supports signal-quality assessment, functional-state recognition, fatigue-related context, quantitative metrics, provenance and human review.

It does not replace Noraxon/myoRESEARCH, diagnose injury, prescribe treatment or autonomously clear return-to-sport.

## Parallel portfolio

### A1 — Hand-gesture recognition

Active program for hand/wrist gesture recognition, personalization, calibration, abstention and future site transfer. The branch remains active independently of the lower-limb expansion.

### A2 — Lower-limb functional-state recognition

Active program for recognizing supported exercise, gait or movement-phase states. It is not an ACL diagnosis classifier.

### B1/B2 — Fatigue context and supportability

Rule-first evidence aggregation that may preserve or reduce Task A confidence. It cannot increase recognition confidence and cannot convert elapsed time, force level or one sEMG feature into a hard fatigue diagnosis.

### C1/C2 — Quantitative assessment

Metric pipelines for repetition, similarity, co-activation, bilateral or longitudinal evidence when eligibility contracts pass. C2 supports knee/ACL rehabilitation review but does not decide return-to-sport.

## Intended users

- rehabilitation clinicians;
- sports-medicine clinicians;
- physiotherapists;
- Motion Lab operators;
- researchers.

## Human review

All clinical-facing interpretations remain pending until reviewed by an authorized clinician or operator according to site workflow.

## Site boundary

Public datasets are engineering and research evidence. Deployment claims require site-verified Noraxon exports, protocols, muscle/channel mapping, metadata, local validation and governance approval.
