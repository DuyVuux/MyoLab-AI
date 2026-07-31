#!/usr/bin/env python3
"""Day 32 — Generate synthetic feature matrix for tooling validation.

Creates a 12-subject, 4-class, 24-feature synthetic dataset that mimics
the structure of the Mendeley F-TD8 arm. This matrix is used exclusively
for verifying that the modeling pipeline works end-to-end.

No real clinical data is generated or used.
"""
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]

rng = np.random.default_rng(3201)
classes = np.array(["rest", "hand_close", "wrist_flexion", "wrist_extension"])
subjects = [f"S{i:02d}" for i in range(1, 13)]

rows = []
ys = []
groups = []
repetitions = []
dataset_ids = []

for s_idx, subject in enumerate(subjects):
    for c_idx, label in enumerate(classes):
        center = np.zeros(24)
        center[c_idx * 4:(c_idx + 1) * 4] = 1.5
        subject_shift = rng.normal(0, 0.15, size=24)
        for rep in range(3):
            for window in range(4):
                rows.append(
                    center + subject_shift + rng.normal(0, 0.5, size=24)
                )
                ys.append(label)
                groups.append(subject)
                repetitions.append(f"{subject}-{label}-R{rep}")
                dataset_ids.append("synthetic-day32-mendeley-like")

out = ROOT / "qa-validation" / "fixtures" / "day32-synthetic-matrix.npz"
out.parent.mkdir(parents=True, exist_ok=True)
np.savez_compressed(
    out,
    X=np.asarray(rows, dtype=float),
    y=np.asarray(ys),
    groups=np.asarray(groups),
    repetition_ids=np.asarray(repetitions),
    dataset_ids=np.asarray(dataset_ids),
)
print(f"Synthetic matrix written: {out}")
print(f"  Rows: {len(rows)}, Features: 24, Subjects: {len(subjects)}, Classes: {len(classes)}")
