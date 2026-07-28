from __future__ import annotations

from collections import defaultdict
from typing import Iterable, Sequence


def _f1_for_class(y_true: Sequence[str], y_pred: Sequence[str], label: str) -> float:
    tp = sum(t == label and p == label for t, p in zip(y_true, y_pred))
    fp = sum(t != label and p == label for t, p in zip(y_true, y_pred))
    fn = sum(t == label and p != label for t, p in zip(y_true, y_pred))
    denominator = 2 * tp + fp + fn
    return 0.0 if denominator == 0 else (2.0 * tp) / denominator


def macro_f1(y_true: Sequence[str], y_pred: Sequence[str], labels: Sequence[str]) -> float:
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred length mismatch")
    if not labels:
        raise ValueError("labels must be fixed and non-empty")
    return sum(_f1_for_class(y_true, y_pred, label) for label in labels) / len(labels)


def subject_macro_repetition_macro_f1(
    rows: Iterable[dict[str, str]], labels: Sequence[str]
) -> float:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["subject_id"]].append(row)
    if not grouped:
        raise ValueError("No subject rows")
    values = []
    for subject_rows in grouped.values():
        y_true = [r["true_label"] for r in subject_rows]
        y_pred = [r["predicted_label"] for r in subject_rows]
        values.append(macro_f1(y_true, y_pred, labels))
    return sum(values) / len(values)


def unsafe_prediction_rate(unsafe_events: int, mandatory_abstain_units: int) -> float:
    if mandatory_abstain_units <= 0:
        raise ValueError("mandatory_abstain_units must be positive")
    if unsafe_events < 0 or unsafe_events > mandatory_abstain_units:
        raise ValueError("unsafe_events out of range")
    return unsafe_events / mandatory_abstain_units
