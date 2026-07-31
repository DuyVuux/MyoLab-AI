from __future__ import annotations
from collections import defaultdict, Counter
import numpy as np

def deterministic_majority_vote(labels, class_order):
    counts = Counter(labels)
    return max(class_order, key=lambda c: (counts.get(c, 0), -class_order.index(c)))

def aggregate_window_labels(
    predictions,
    repetition_ids,
    subject_ids,
    true_labels,
    class_order,
) -> list[dict]:
    buckets = defaultdict(list)
    truth = {}
    subject = {}
    for pred, rep, subj, true in zip(predictions, repetition_ids, subject_ids, true_labels):
        key = (subj, rep)
        buckets[key].append(pred)
        truth[key] = true
        subject[key] = subj
    rows = []
    for key, values in buckets.items():
        rows.append({
            "subject_id": subject[key],
            "repetition_id": key[1],
            "y_true": truth[key],
            "y_pred": deterministic_majority_vote(values, class_order),
            "window_count": len(values),
        })
    return rows
