# Day 2 Acceptance Criteria

## Scope

Protocol v0.1, Generic CSV import contract, signal validation/QC policy, and validation scaffolding.

## Acceptance criteria

- [ ] `quad-isometric-60s.v0.1.yaml` validates against `protocol-schema.json`.
- [ ] Protocol is explicitly marked technical-demo-only and `clinical_use_allowed: false`.
- [ ] Generic CSV format separates numeric signal data from sidecar metadata.
- [ ] Direct identifiers are prohibited.
- [ ] Format fixture passes format validation.
- [ ] The same one-second fixture fails protocol validation with the **expected negative test** code `ACTIVE_DURATION_TOO_SHORT`.
- [ ] QC policy states that critical failure blocks fatigue analysis and triggers abstention.
- [ ] MFCV ineligibility disables MFCV only and does not fabricate a value.
- [ ] QC thresholds are labelled provisional and not clinically validated.
- [ ] No feature extraction, FRS, ML model, or clinical recommendation is produced on Day 2.
- [ ] `scripts/dev/run_day2_checks.sh` exits with code 0.
- [ ] Open questions requiring external clinical/Motion Lab review are recorded.
