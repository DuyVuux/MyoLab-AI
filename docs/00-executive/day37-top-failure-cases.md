# DAY37 Top-20 Replayable Error / Risk Cases

These are ranked engineering error/risk cases. Sentinel/control cases are not mislabeled as observed production failures.

| Rank | Source | Category | Case | Score | Replay |
|---:|---|---|---|---:|---|
| 1 | DAY34 | CORPUS_TRUTH_GAP | `rbw_sha256_149323075a106bb92b0fb05546c046ba6a92dd293d5ac1144579f8053fc7f034` | 166 | `python3 scripts/dev/day34_analysis_runner.py` |
| 2 | DAY34 | CORPUS_TRUTH_GAP | `rbw_sha256_af2e62669302d7f10a04082bf95f367f458bbf7af55fcce5261a176d6f19c952` | 166 | `python3 scripts/dev/day34_analysis_runner.py` |
| 3 | DAY34 | CORPUS_TRUTH_GAP | `rbw_sha256_bc1f293f3cac5f5d6a3243a01c2cd32cb4ff9ee0129972b7988a042ffdf19036` | 166 | `python3 scripts/dev/day34_analysis_runner.py` |
| 4 | DAY34 | CORPUS_TRUTH_GAP | `rbw_sha256_eb2d3c3aedca993e0175ff913a8410f8f3e92b80d8fa7a3b0f39118734ca4b21` | 166 | `python3 scripts/dev/day34_analysis_runner.py` |
| 5 | DAY34 | HARD_INTEGRITY_CONTROL | `rbw_sha256_356219d09c031de34a5c8ce7568bcad74e31d97f838f314352720943cc47baf0` | 126 | `python3 scripts/dev/day34_analysis_runner.py` |
| 6 | DAY34 | HARD_INTEGRITY_CONTROL | `rbw_sha256_86076e1e773151f6e16b5199441cafd7b92a3a2ca26fa1e80414c76643c8a8fb` | 126 | `python3 scripts/dev/day34_analysis_runner.py` |
| 7 | DAY34 | UNRESOLVED_KNOWN_TRUTH | `rbw_sha256_396c54907282fbb4dab620de8ae7e02f900b25586b2f3fbc48f8438a6a72e6bd` | 121 | `python3 scripts/dev/day34_analysis_runner.py` |
| 8 | DAY34 | PHYSIOLOGY_SENTINEL | `rbw_sha256_4a7f23b1168a3001f8885afe28fd8c43c1adbbae9a4d977a5990d52bbc77c647` | 111 | `python3 scripts/dev/day34_analysis_runner.py` |
| 9 | DAY34 | DETECTOR_DISAGREEMENT | `rbw_sha256_0d670244b7e3913b80b398af7541050fecd0e9dfceb3a037a0227174ff528caf` | 81 | `python3 scripts/dev/day34_analysis_runner.py` |
| 10 | DAY34 | DETECTOR_DISAGREEMENT | `rbw_sha256_f04fdf53fe57dcb9f53eaf9ccafce3ccd25058dd4aea58b7b62c90dee200b1a6` | 81 | `python3 scripts/dev/day34_analysis_runner.py` |
| 11 | DAY34 | DETECTOR_DISAGREEMENT | `rbw_sha256_fd96f5f236d14104824b52a9be69cb6cb66a9391a7a23a947e06fff4379f9986` | 81 | `python3 scripts/dev/day34_analysis_runner.py` |
| 12 | DAY36 | PHYSIOLOGY_SENTINEL | `D36-AMP-LOW-010` | 80 | `python3 scripts/dev/day36_challenge_runner.py` |
| 13 | DAY36 | PHYSIOLOGY_SENTINEL | `D36-AMP-LOW-025` | 80 | `python3 scripts/dev/day36_challenge_runner.py` |
| 14 | DAY36 | EXPECTED_HARD_BLOCK_CONTROL | `D36-DROPOUT-HARD-CONTROL` | 75 | `python3 scripts/dev/day36_challenge_runner.py` |
| 15 | DAY36 | EXPECTED_HARD_BLOCK_CONTROL | `D36-REQUIRED-MODALITY-MISSING` | 75 | `python3 scripts/dev/day36_challenge_runner.py` |
| 16 | DAY36 | DOMAIN_SUPPORT_UNKNOWN | `D36-OPTIONAL-MODALITY-UNKNOWN` | 70 | `python3 scripts/dev/day36_challenge_runner.py` |
| 17 | DAY36 | DOMAIN_SHIFT_SENTINEL | `D36-FS-1000` | 55 | `python3 scripts/dev/day36_challenge_runner.py` |
| 18 | DAY36 | DOMAIN_SHIFT_SENTINEL | `D36-FS-4000` | 55 | `python3 scripts/dev/day36_challenge_runner.py` |
| 19 | DAY36 | DOMAIN_SHIFT_SENTINEL | `D36-LAYOUT-B` | 55 | `python3 scripts/dev/day36_challenge_runner.py` |
| 20 | DAY36 | DOMAIN_SHIFT_SENTINEL | `D36-MORPH-HARMONIC` | 55 | `python3 scripts/dev/day36_challenge_runner.py` |

## Remediation priorities
- Preserve DAY35 aligned-fixture repair for dropout/clipping.
- Add multi-channel positive known truth before poor-contact threshold/effectiveness claims.
- Keep unresolved/UNKNOWN explicit.
- DAY38 must property-test hard-integrity precedence, immutability, deterministic replay and artifact persistence.
