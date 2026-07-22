# Kế hoạch kiểm thử Golden Regression Day 16

## Test matrix

| ID | Fixture | Kỳ vọng chính |
|---|---|---|
| D16-G01 | Golden | completed / supported_pattern |
| D16-W01 | Clipping | completed_with_warnings / CLIPPING_SUSPECTED |
| D16-W02 | Motion | completed_with_warnings / MOTION_ARTIFACT_HIGH |
| D16-W03 | Powerline | completed_with_warnings / POWERLINE_NOISE_HIGH |
| D16-F01 | Flatline | abstained / FLATLINE_EXCESSIVE |
| D16-F02 | Nonfinite | abstained / NONFINITE_RATIO_EXCESSIVE |
| D16-F03 | Short duration | abstained / ACTIVE_DURATION_TOO_SHORT |
| D16-R01 | Golden rerun | cùng fingerprint và stage payload hashes |

## Exit criteria

- 100% test matrix pass.
- Không forbidden key trong package.
- Numerical anchors golden trong profile ranges.
- Analytical validation report ghi rõ `not_validated`.
