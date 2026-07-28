# Leakage Prevention Plan

1. Split raw hierarchy before segmentation/windowing.
2. Keep all sibling windows from one repetition in one partition.
3. Outer group keys reflect the scientific question.
4. Fit scaler, normalization, selector, calibrator and threshold inside inner folds.
5. Target personalization calibration subset is separate from locked target test.
6. Outer test is opened once under a frozen manifest.
7. Any test-guided revision creates a contamination incident and evidence downgrade.
