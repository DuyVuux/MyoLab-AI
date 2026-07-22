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

## Day 2 status
Day 2 establishes the data import contract (Generic CSV + JSON sidecar manifest) and the first versioned clinical protocol (`quad-isometric-60s`). It implements a multi-layer signal validation pipeline and quality gate (L0-L4) to explicitly block invalid data and separate basic sEMG eligibility from advanced MFCV analysis.

## Day 3 status
Day 3 implements the generic CSV ingestion pipeline and the canonical normalized signal contract (`NormalizedSignal`). It enforces read-only arrays after construction, strips raw data from the output JSON summary, and verifies file formats, metadata, and deterministic source hashing before moving to downstream processing.

## Day 4 status
Day 4 implements the Signal Quality Gate (QC) module to evaluate signals against invalidation criteria like Flatline, Clipping, Powerline Noise, and Motion Artifacts. It finalizes the data integration layer and implements a fail-fast abstention policy for unsafe data.

## Day 5 status
Day 5 builds the core signal preprocessing pipeline and service orchestration. It implements a multi-stage preprocessing flow including band-pass and dynamic notch filtering, integrating directly with the QC Gate to dynamically apply noise removal only when specific noise flags are present.

## Day 6 status
Day 6 focuses on the empirical verification of the multi-frequency signal preprocessing pipeline. It validates filter implementations using a deterministic sample array against theoretical expectations for spectral leakage and frequency response, finalizing the preprocessing verification work.

## Day 7 status
Day 7 implements protocol-aligned segmentation and windowing logic. It enforces strict alignment between clinical protocols and feature extraction configurations, explicitly rejecting execution on configuration mismatches.

## Day 8 status
Day 8 delivers the time-domain feature extraction module. It implements deterministic RMS and MAV feature extraction logic, associated schema definitions, and validation reports to ensure mathematical correctness.

## Day 9 status
Day 9 implements the spectral estimation pipeline using Welch's method. It establishes the robust calculation of Power Spectral Density (PSD) and handles frequency resolution bounds according to clinical protocols.

## Day 10 status
Day 10 introduces the frequency-domain feature extraction. It computes Median Frequency (MDF) and Mean Frequency (MNF) from the PSD, implementing standardized mathematical formulas and strict validation schemas.

## Day 11 status
Day 11 implements the Trend Feature extraction module. It calculates the linear regression slopes for RMS, MAV, MDF, and MNF over time windows. It strictly enforces a descriptive-only approach, stripping inferential statistics (like p-values or confidence intervals) to prevent premature clinical conclusions.
