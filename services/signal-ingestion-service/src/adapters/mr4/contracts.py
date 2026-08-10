"""Data contracts and schemas for MR4 parsing."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SingleCsvContract:
    contract_id: str
    contract_version: str
    known_metadata: frozenset[str]
    text_columns: frozenset[str]
    known_column_units: dict[str, str] = field(default_factory=dict)
    
    def get_column_semantics(self, column: str) -> tuple[str, str | None, str, bool]:
        """Resolve the semantic role, unit, unit_evidence and unknown flag for a column."""
        if column in self.text_columns:
            return ("EVENT_TEXT", None, "OBSERVED_CONTRACT", False)
        if column in self.known_column_units:
            return ("NUMERIC_SIGNAL", self.known_column_units[column], "OBSERVED_CONTRACT", False)
        if "COP" in column:
            return ("NUMERIC_SIGNAL", "mm", "OBSERVED_CONTRACT", False)
        if column.startswith(("LT ", "RT ")) and not column.endswith("Force"):
            return ("SEMG_VENDOR_CHANNEL", "uV", "OBSERVED_CONTRACT_PATTERN", False)
        return ("UNKNOWN_VENDOR_FIELD", None, "UNKNOWN", True)


# The default DAY09 frozen contract extracted from the legacy implementation.
MR4_SINGLE_CSV_V0_1 = SingleCsvContract(
    contract_id="MR4_SINGLE_CSV_V0_1",
    contract_version="0.1.0",
    known_metadata=frozenset({
        "type",
        "begin_time",
        "frequency",
        "count",
        "created with version",
        "exported with version",
        "measurement_date",
        "record_name",
    }),
    text_columns=frozenset({"Activity", "Marker"}),
    known_column_units={
        "Pressure Platform-Velocity": "m/s",
        "LT Force": "N",
        "RT Force": "N",
        "LT Max Pressure": "N/cm^2",
        "RT Max Pressure": "N/cm^2",
    },
)

@dataclass(frozen=True)
class SeparatedCsvContract:
    contract_id: str
    contract_version: str
    known_info_fields: frozenset[str]
    known_units: frozenset[str]

# The default DAY10 frozen contract for separated CSVs
MR4_SEPARATED_RECORD_V0_1 = SeparatedCsvContract(
    contract_id="MR4_SEPARATED_RECORD_V0_1+MR4_SIGNAL_FILE_V0_1",
    contract_version="0.1.0",
    known_info_fields=frozenset({
        "type",
        "created_with_version",
        "exported_with_version",
        "project",
        "last_name",
        "first_name",
        "born",
        "sex",
        "measurement_date",
        "record_name",
    }),
    known_units=frozenset({"s", "V", "uV", "N", "mm", "m/s", "N/cm^2", "FS"}),
)
