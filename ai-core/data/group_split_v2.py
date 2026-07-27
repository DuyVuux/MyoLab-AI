from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass
from typing import Iterable, Mapping


class GroupSplitError(ValueError):
    pass


@dataclass(frozen=True)
class SplitRatios:
    train: float = 0.67
    validation: float = 0.17
    test: float = 0.16

    def validate(self) -> None:
        values = (self.train, self.validation, self.test)
        if any(value <= 0 or value >= 1 for value in values):
            raise GroupSplitError("SPLIT_RATIOS_MUST_BE_IN_OPEN_INTERVAL_ZERO_ONE")
        if abs(sum(values) - 1.0) > 1e-9:
            raise GroupSplitError("SPLIT_RATIOS_MUST_SUM_TO_ONE")


def canonical_hash(payload: object) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def assert_no_group_leakage(
    train: Iterable[str],
    validation: Iterable[str],
    test: Iterable[str],
) -> None:
    train_set = set(train)
    validation_set = set(validation)
    test_set = set(test)
    if train_set & validation_set:
        raise GroupSplitError("TRAIN_VALIDATION_GROUP_LEAKAGE")
    if train_set & test_set:
        raise GroupSplitError("TRAIN_TEST_GROUP_LEAKAGE")
    if validation_set & test_set:
        raise GroupSplitError("VALIDATION_TEST_GROUP_LEAKAGE")


def build_group_split(
    records: Iterable[Mapping[str, object]],
    *,
    dataset_id: str,
    group_unit: str = "subject",
    ratios: SplitRatios = SplitRatios(),
    seed: int = 2501,
) -> dict[str, object]:
    ratios.validate()
    if group_unit not in {"subject", "session"}:
        raise GroupSplitError("GROUP_UNIT_MUST_BE_SUBJECT_OR_SESSION")

    rows = [dict(row) for row in records]
    if not rows:
        raise GroupSplitError("NO_RECORDS")

    group_key = "subject_id" if group_unit == "subject" else "session_id"
    missing = [index for index, row in enumerate(rows) if not row.get(group_key)]
    if missing:
        raise GroupSplitError(f"MISSING_GROUP_ID:{group_key}:{missing[:5]}")

    groups = sorted({str(row[group_key]) for row in rows})
    if len(groups) < 6:
        raise GroupSplitError("AT_LEAST_SIX_GROUPS_REQUIRED")

    rng = random.Random(seed)
    shuffled = groups[:]
    rng.shuffle(shuffled)

    n_groups = len(shuffled)
    n_train = max(1, int(round(n_groups * ratios.train)))
    n_validation = max(1, int(round(n_groups * ratios.validation)))
    if n_train + n_validation >= n_groups:
        n_train = n_groups - 2
        n_validation = 1

    train = sorted(shuffled[:n_train])
    validation = sorted(shuffled[n_train:n_train + n_validation])
    test = sorted(shuffled[n_train + n_validation:])
    if not test:
        raise GroupSplitError("TEST_GROUP_EMPTY")
    assert_no_group_leakage(train, validation, test)

    source_hash = canonical_hash(rows)
    payload: dict[str, object] = {
        "schemaVersion": "subject-group-split.v0.2",
        "datasetId": dataset_id,
        "groupUnit": group_unit,
        "seed": seed,
        "ratios": {
            "train": ratios.train,
            "validation": ratios.validation,
            "test": ratios.test,
        },
        "groups": {
            "train": train,
            "validation": validation,
            "test": test,
        },
        "counts": {
            "totalGroups": n_groups,
            "trainGroups": len(train),
            "validationGroups": len(validation),
            "testGroups": len(test),
            "recordCount": len(rows),
        },
        "sourceMetadataHashSha256": source_hash,
        "testSetSealed": True,
    }
    payload["splitHashSha256"] = canonical_hash(payload)
    return payload
