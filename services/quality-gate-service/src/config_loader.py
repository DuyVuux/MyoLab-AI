"""Configuration/protocol loading helpers for the MVP-0 quality gate."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("PyYAML is required: pip install pyyaml") from exc


def _load_yaml_mapping(path: Path) -> dict[str, Any]:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, Mapping):
        raise ValueError(f"YAML root must be an object: {path}")
    return dict(raw)


def load_qc_config(path: Path) -> dict[str, Any]:
    config = _load_yaml_mapping(path)
    if config.get("schema_version") != "qc-config.v0.1":
        raise ValueError(
            f"Unsupported QC config schema: {config.get('schema_version')!r}"
        )
    if config.get("clinical_validation_status") == "validated":
        # This guard is intentionally conservative: v0.1 starter code must not
        # silently masquerade as a clinically validated threshold set.
        raise ValueError("qc_v0.1 starter implementation cannot be marked validated")
    return config


def load_protocol(path: Path) -> dict[str, Any]:
    protocol = _load_yaml_mapping(path)
    required = {"protocol_id", "version", "task", "acquisition", "analysis"}
    missing = sorted(required - set(protocol))
    if missing:
        raise ValueError(f"Protocol missing fields: {', '.join(missing)}")
    return protocol
