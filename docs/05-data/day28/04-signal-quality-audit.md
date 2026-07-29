# Signal Quality Audit — Descriptive Only

## Required statistics

- sample count and duration;
- non-finite ratio;
- mean, median, STD, MAD;
- RMS, MAV;
- p01/p99 and robust range;
- flatline candidate ratio;
- clipping candidate ratio;
- DC offset ratio;
- powerline/low-frequency ratios only when Fs is verified.

## Provisional rules

Rules in `day28_quality_rules.provisional.yaml` are engineering review triggers, not clinical acceptance thresholds. A warning never means “bad patient signal”; it means “inspect source file/channel and document disposition.”
