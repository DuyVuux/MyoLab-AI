# sEMG/MFCV Fatigue Clinical Intelligence Layer

## Positioning
This repository contains an offline-first Clinical Intelligence layer for sEMG/MFCV fatigue evidence. It works on top of Motion Lab/Noraxon-style exports, synthetic data, and later validated clinical workflows. It is not an EMG acquisition device and not a replacement for Noraxon/myoRESEARCH.

## MVP principles
- Signal quality before AI or fatigue inference.
- Explainable rules before black-box models.
- Human review before any clinical-facing report.
- Abstention before unsafe or unsupported conclusions.
- MFCV/CV only when electrode geometry, channel ordering, sampling rate, and protocol eligibility are confirmed.

## What the product does
- Imports synthetic or exported sEMG session files.
- Validates metadata, protocol context, and signal quality.
- Extracts fatigue-related features such as RMS, MAV, MDF, MNF, slopes, and optional MFCV/CV when eligible.
- Produces structured evidence for technical and clinical review.
- Generates conservative report wording with limitations and reason codes.

## What the product does not do
- Not direct device control.
- Not autonomous diagnosis.
- Not automated treatment prescription.
- Not automatic return-to-play clearance.
- Not clinical-grade realtime alerting in MVP-0.
- Not storage of real patient raw signal in this repository.

## Day 1 status
Day 1 establishes the product boundary, intended use, safety language, quality gate, abstention behavior, and human-in-the-loop rule for MVP-0.
