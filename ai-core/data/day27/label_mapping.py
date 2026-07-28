from __future__ import annotations


class LabelMappingError(ValueError):
    pass


ALLOWED_TARGETS = {
    "rest",
    "hand_open",
    "hand_close",
    "wrist_flexion",
    "wrist_extension",
}
PROTECTED_NON_TARGETS = {
    "unknown",
    "ambiguous",
    "artifact",
    "not_attempted",
    "transition",
}


def validate_label_map(config: dict[str, object]) -> dict[str, str | None]:
    if config.get("mapUnknownToRest") is not False:
        raise LabelMappingError("UNKNOWN_TO_REST_FORBIDDEN")
    mappings = config.get("mappings")
    if not isinstance(mappings, list) or not mappings:
        raise LabelMappingError("MAPPINGS_REQUIRED")

    result: dict[str, str | None] = {}
    for row in mappings:
        if not isinstance(row, dict):
            raise LabelMappingError("INVALID_MAPPING_ROW")
        source = str(row.get("sourceLabel", "")).strip()
        target = row.get("canonicalLabel")
        status = row.get("mappingStatus")
        evidence = str(row.get("evidence", "")).strip()
        if not source or source.startswith("<"):
            raise LabelMappingError("SOURCE_LABEL_REQUIRED")
        if source in result:
            raise LabelMappingError(f"DUPLICATE_SOURCE_LABEL:{source}")
        if status not in {"VERIFIED", "EXCLUDED", "UNMAPPED"}:
            raise LabelMappingError(f"INVALID_MAPPING_STATUS:{source}")
        if status == "VERIFIED":
            if target not in ALLOWED_TARGETS:
                raise LabelMappingError(f"INVALID_CANONICAL_LABEL:{source}:{target}")
            if not evidence or evidence.startswith("<"):
                raise LabelMappingError(f"MAPPING_EVIDENCE_REQUIRED:{source}")
            result[source] = str(target)
        else:
            if target is not None:
                raise LabelMappingError(f"NONVERIFIED_TARGET_MUST_BE_NULL:{source}")
            result[source] = None
    return result


def map_label(source_label: str, mapping: dict[str, str | None]) -> str:
    if source_label not in mapping:
        raise LabelMappingError(f"UNMAPPED_SOURCE_LABEL:{source_label}")
    target = mapping[source_label]
    if target is None:
        raise LabelMappingError(f"SOURCE_LABEL_EXCLUDED_OR_UNMAPPED:{source_label}")
    return target
