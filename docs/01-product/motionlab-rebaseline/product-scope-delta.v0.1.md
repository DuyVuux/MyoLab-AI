# Product Scope Delta v0.1

## Purpose

Record the deliberate product re-baseline after `PRE-DAY41_01` so legacy technical momentum does not silently redefine the new Vinmec MotionLab problem.

| Area | Legacy emphasis | DAY01 baseline | Disposition |
|---|---|---|---|
| Core product | Gesture/fatigue/MFCV clinical-intelligence framing | Data-processing toil + quality intelligence | **SUPERSEDED as product center** |
| sEMG ingestion/QC/DSP primitives | Existing technical assets | Useful engineering inputs | **REUSE / REVALIDATE** |
| Gesture classifiers | Core/major track in older work | Not P0 | **KEEP AS REGRESSION** |
| Binary fatigue classifier | Product-facing direction in older assets | Fatigue only as evidence/context when supported | **DEPRECATE AS PRODUCT CENTER** |
| MFCV | Important research capability | Optional, site-gated | **REVALIDATE ON MOTIONLAB** |
| Public healthy datasets | Training/research assets | Engineering/regression only | **NOT clinical-effectiveness evidence** |
| Plantar pressure | Secondary workflow problem | P1 | **PRESERVE** |
| Knee/ACL | Lower-limb algorithm momentum | DR-K01..08 discovery first | **DISCOVERY-GATED** |
| Clinician authority | Human-in-the-loop present in older framing | Explicit final authority | **NON-NEGOTIABLE** |
| Raw signal | Needed for analysis | Immutable source of provenance | **NON-NEGOTIABLE** |

## What is explicitly not authorized on DAY01

No parser, DSP filter, QC detector, ML model, threshold tuning, MFCV estimator, pressure classifier/corrector, Knee algorithm, frontend implementation, or clinical claim is created by this pack.
