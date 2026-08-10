# MotionLab Evidence-Tier Policy v0.1

This is an internal project evidence hierarchy, not a universal clinical evidence standard.

## Rule 0 — Governance before promotion
A human-data source with `governance_status` or `deidentification_status` equal to `UNKNOWN` cannot be promoted into a site-evidence tier or used to support downstream clinical/site claims.

## Tiers (Mapped to IMDRF / FDA SaMD Framework)
- **E0 ENGINEERING_ONLY (Pre-Analytical)** — synthetic fixtures. Supports code correctness, not site compatibility or clinical effectiveness.
- **E1 FORMAT_DISCOVERY (Pre-Analytical)** — vendor/sample/documented structure. Supports contract design, not proof that the installed MotionLab export is identical.
- **E2 SITE_HISTORICAL_GOVERNED (Analytical Validation)** — de-identified historical MotionLab data with approved governance and provenance. Supports site-specific parser/QC retrospective engineering within its cohort/protocol limits to prove the software correctly processes the input (FDA RWD Reliability).
- **E3 SITE_PROSPECTIVE_GOVERNED (Clinical Validation)** — prospectively collected/observed site evidence under an approved protocol. Supports questions explicitly covered by that collection to prove the software yields a clinically meaningful output (FDA RWD Relevance).
- **E4 CONTROLLED_PILOT (Clinical Validation)** — locked controlled-pilot evidence for predefined workflow/safety/performance endpoints. Does not imply autonomous use or broad clinical effectiveness.

## Non-substitution rules
1. Public/healthy data cannot substitute for Vinmec clinical-effectiveness evidence.
2. Vendor sample cannot substitute for site field-level export verification.
3. Synthetic artifact truth cannot substitute for expert-annotated real windows.
4. A missing Knee failure case cannot be replaced by a convenient public dataset while keeping a DR-K01 claim.
5. MFCV remains NOT_VERIFIED unless site geometry/IED/alignment/config evidence supports eligibility.

## Cohort-bias rule
Evidence only supports the population, task, protocol, hardware/software configuration and acquisition conditions actually represented. Pathology/body-habitus variation must not be silently treated as artifact or assumed covered by healthy samples.
