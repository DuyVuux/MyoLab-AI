# DAY38 QC Regression Freeze — Reproducibility & Safety Verification

## Status
`QC_REPRODUCIBILITY_FROZEN`

## Objective
DAY38 freezes the research QC core by verifying safety invariants with property/metamorphic tests and by content-addressing the contracts/configs that define QC semantics. It does not certify clinical performance.

## Verification results
- DAY38 focused property/metamorphic tests: 7/7 PASS.
- Cumulative QC/property regression: 640+ PASS, 1 historical DAY21 anti-future-scope guard deselected.
- Freeze manifest: 15/15 hashes matched.
- Locked evaluation consumed: 0.
- Site thresholds remain NOT_VERIFIED.

## Frozen boundary
The allowlist includes QC taxonomy/LF registry where present, six detector modules, DAY29 data integrity, DAY30 aggregation, DAY31 metric handoff, DAY35 research thresholds, and benchmark/challenge manifests. The boundary is intentionally content-focused rather than whole-repository hashing.

## Property evidence
1. Raw arrays are unchanged by challenge evaluation.
2. Same input/config/seed produces same result across randomized replay.
3. QC FAIL always produces BLOCKED metric handoff.
4. Unknown/insufficient QC produces ABSTAINED with reasons, not a metric value.
5. Low-amplitude physiology stress cannot become poor-contact or quality-block solely because amplitude is low.
6. Descriptive distribution SHIFTED does not imply QC failure.
7. No OOD score exists.
8. Unit conversion is copy-on-write with explicit conversion provenance.
9. Missing/NaN artifact survives scalar unit conversion.
10. All frozen file hashes match.

## DAY37 remediation review
- Hard-integrity false-allow: none observed in reference sentinels.
- DAY33 truth-window misalignment: repaired via versioned DAY35 aligned fixtures; historical evidence preserved.
- Poor contact: remains open limitation because no multi-channel positive known truth. This does not permit poor-contact threshold/site claim.
- Public/expert/clinical evidence: not available and not required for research-core freeze claim.

## Stop-condition review
No unresolved hard-integrity false-allow and no reproducibility break were found. DAY39 Gate C-R may proceed.
