from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class BlueprintValidationError(ValueError):
    """Raised when a Day 26 blueprint violates a locked invariant."""


def load_yaml(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise BlueprintValidationError(f"Expected mapping in {path}")
    return data


@dataclass(frozen=True)
class BlueprintStatus:
    valid: bool
    training_allowed: bool
    execution_state: str
    errors: tuple[str, ...]


def validate_blueprint(configs: list[dict[str, Any]]) -> BlueprintStatus:
    errors: list[str] = []
    for index, cfg in enumerate(configs):
        if cfg.get("trainingAllowed") is not False:
            errors.append(f"config[{index}] must set trainingAllowed=false")
        state = cfg.get("execution_state")
        if state is not None and state != "NOT_RUN":
            errors.append(f"config[{index}] execution_state must be NOT_RUN")
    return BlueprintStatus(
        valid=not errors,
        training_allowed=False,
        execution_state="NOT_RUN",
        errors=tuple(errors),
    )
