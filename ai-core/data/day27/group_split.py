from __future__ import annotations

import hashlib
import json
import random
from collections.abc import Iterable, Mapping


class GroupSplitError(ValueError):
    pass


def _hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def assert_no_overlap(groups: dict[str, list[str]]) -> None:
    train, validation, test = map(set, (groups["train"], groups["validation"], groups["test"]))
    if train & validation:
        raise GroupSplitError("TRAIN_VALIDATION_OVERLAP")
    if train & test:
        raise GroupSplitError("TRAIN_TEST_OVERLAP")
    if validation & test:
        raise GroupSplitError("VALIDATION_TEST_OVERLAP")


def build_subject_split(
    records: Iterable[Mapping[str, object]],
    *,
    dataset_id: str,
    seed: int = 2701,
    ratios: tuple[float, float, float] = (0.67, 0.17, 0.16),
) -> dict[str, object]:
    rows = [dict(row) for row in records]
    if not rows:
        raise GroupSplitError("NO_RECORDS")
    if abs(sum(ratios) - 1.0) > 1e-9:
        raise GroupSplitError("RATIOS_MUST_SUM_TO_ONE")
    missing = [index for index, row in enumerate(rows) if not row.get("subject_id")]
    if missing:
        raise GroupSplitError(f"MISSING_SUBJECT_ID:{missing[:5]}")
    subjects = sorted({str(row["subject_id"]) for row in rows})
    if len(subjects) < 6:
        raise GroupSplitError("AT_LEAST_SIX_SUBJECTS_REQUIRED")

    shuffled = subjects[:]
    random.Random(seed).shuffle(shuffled)
    n = len(shuffled)
    n_train = max(1, round(n * ratios[0]))
    n_val = max(1, round(n * ratios[1]))
    if n_train + n_val >= n:
        n_train, n_val = n - 2, 1
    groups = {
        "train": sorted(shuffled[:n_train]),
        "validation": sorted(shuffled[n_train:n_train+n_val]),
        "test": sorted(shuffled[n_train+n_val:]),
    }
    assert_no_overlap(groups)
    payload: dict[str, object] = {
        "schemaVersion": "subject-group-split.v1",
        "datasetId": dataset_id,
        "groupUnit": "subject",
        "seed": seed,
        "ratios": {"train": ratios[0], "validation": ratios[1], "test": ratios[2]},
        "groups": groups,
        "counts": {"subjects": n, "records": len(rows)},
        "metadataIndexSha256": _hash(rows),
        "testSetSealed": True,
        "testOpened": False,
    }
    payload["splitSha256"] = _hash(payload)
    return payload
