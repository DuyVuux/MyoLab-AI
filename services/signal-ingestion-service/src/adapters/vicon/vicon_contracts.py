from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from adapters.vicon.vicon_models import ViconParseError


@dataclass(frozen=True)
class SectionLayout:
    header_rows: int
    column_header_index: int
    units_index: int | None


@dataclass(frozen=True)
class ViconStackedContract:
    contract_id: str
    version: str
    supported_sections: tuple[str, ...]
    evidence_only_sections: tuple[str, ...]
    layouts: dict[str, SectionLayout]


DEFAULT_CONTRACT_PATH = (
    Path(__file__).resolve().parents[5]
    / "data-platform/contracts/vicon/stacked-sections.v0.1.yaml"
)


def load_vicon_contract(
    path: Path = DEFAULT_CONTRACT_PATH,
) -> ViconStackedContract:
    path = Path(path)
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    try:
        supported = tuple(payload["scope"]["parse_supported_sections"])
        evidence_only = tuple(
            payload["scope"]["preserve_evidence_only_sections"]
        )
        layouts = {
            name: SectionLayout(
                header_rows=int(spec["header_rows"]),
                column_header_index=int(spec["column_header_index"]),
                units_index=(
                    None
                    if spec.get("units_index") is None
                    else int(spec["units_index"])
                ),
            )
            for name, spec in payload["section_layouts"].items()
        }
    except (KeyError, TypeError, ValueError) as exc:
        raise ViconParseError(
            "VICON_CONTRACT_INVALID",
            "Vicon contract is malformed",
            source_path=path,
        ) from exc

    if set(supported) != set(layouts):
        raise ViconParseError(
            "VICON_CONTRACT_INVALID",
            "supported sections and layouts differ",
            source_path=path,
        )
    if (
        payload["invariants"].get("x_y_z_to_anatomical_plane")
        != "NOT_VERIFIED"
    ):
        raise ViconParseError(
            "VICON_CONTRACT_INVALID",
            "v0.1 must not authorize anatomical plane mapping",
            source_path=path,
        )

    return ViconStackedContract(
        contract_id=payload["contract_id"],
        version=str(payload["version"]),
        supported_sections=supported,
        evidence_only_sections=evidence_only,
        layouts=layouts,
    )
