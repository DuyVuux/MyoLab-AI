# DAY07 Acceptance Criteria

## Automated engineering acceptance

- [ ] Three mandatory roadmap outputs exist.
- [ ] `legacy-asset-inventory.v1.0.yaml` validates against JSON Schema.
- [ ] Exactly five allowed dispositions are used: REUSE_AS_IS, ADAPT, REVALIDATE, PARK, DEPRECATE.
- [ ] Legacy family IDs are unique.
- [ ] Regression scope validates and every suite has `clinical_claim_allowed: false`.
- [ ] MFCV is not marked site-ready or default-enabled.
- [ ] Binary-fatigue product center is deprecated.
- [ ] Public healthy datasets are research/regression-only.
- [ ] Old post-PRE-DAY41 lower-limb schedule is deprecated as schedule.
- [ ] PRD Product Principles, NFR-001 and NFR-011 traceability exists.
- [ ] No raw patient data/model-training artifact is introduced by DAY07 patch.
- [ ] Python files compile under Python 3.11+ syntax.
- [ ] Package/repo patch contains no cache artifacts.

## Evidence / human acceptance

- [ ] Current post-DAY06 repository scan executed.
- [ ] All critical/high-risk unclassified legacy candidates reviewed.
- [ ] Family-level disposition bound to actual current paths.
- [ ] Human semantic review completed.
- [ ] No unresolved source conflict silently reconciled.

## Final status

- `GO_FOR_DAY_08`: automated + current-repo confirmation + human review pass.
- `READY_WITH_LIMITATIONS`: engineering pass but repo confirmation or non-critical human review remains.
- `BLOCKED_WITH_EVIDENCE`: critical source/evidence/governance ambiguity prevents safe disposition.
