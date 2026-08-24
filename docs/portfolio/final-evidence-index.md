# Final Evidence Index

| Major Claim Area | Evidence Tier | Artifact | Verification Command | Limitation |
| --- | --- | --- | --- | --- |
| Ingestion & Parser | Synthetic / Public | `final-parser-integrity-results-v1.0.json` | `finish_phase7r_critical_path.sh` | Public research shapes only |
| Quality Control | Two-Tier (Synth/Public) | `final-qc-metrics-v1.0.json` | `finish_phase7r_critical_path.sh` | No clinical ground truth |
| DSP Metrics | Synthetic Known-Answer | `final-processing-metric-results-v1.0.json` | `finish_phase7r_critical_path.sh` | MFCV/Timing unsupported |
| Workflow Safety | Fault Injection | `final-workflow-safety-results-v1.0.json` | `pytest qa-validation/automated-tests/` | Fail-closed research rules |
| Human Review | Deterministic Simulation | `nonclinical-workflow-study-status-v1.0.json` | `finish_phase7r_critical_path.sh` | Simulated workflow only |
| ML Decision | Governance Freeze | `m6-r-research-ml.md` | `finish_phase7r_critical_path.sh` | ML default OFF |
