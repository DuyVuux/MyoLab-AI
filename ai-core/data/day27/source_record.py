from __future__ import annotations

from urllib.parse import urlparse

from .contracts import find_placeholders, is_sha256


class SourceRecordError(ValueError):
    pass


def _https(value: object) -> bool:
    return isinstance(value, str) and urlparse(value).scheme == "https"


def validate_source_record(record: dict[str, object]) -> dict[str, object]:
    errors: list[str] = []
    if record.get("schemaVersion") != "public-source-record.v1":
        errors.append("INVALID_SCHEMA_VERSION")
    placeholders = find_placeholders(record, include_none=False)
    if placeholders:
        errors.append("PLACEHOLDERS_OR_NULLS:" + ",".join(placeholders[:20]))

    for field in ("canonicalRecordUrl",):
        if not _https(record.get(field)):
            errors.append(f"HTTPS_REQUIRED:{field}")

    download = record.get("download")
    if not isinstance(download, dict) or not _https(download.get("url")):
        errors.append("HTTPS_REQUIRED:download.url")

    license_block = record.get("license")
    if not isinstance(license_block, dict):
        errors.append("LICENSE_BLOCK_REQUIRED")
    else:
        if not _https(license_block.get("url")):
            errors.append("HTTPS_REQUIRED:license.url")
        if not is_sha256(license_block.get("snapshotSha256")):
            errors.append("INVALID_LICENSE_SNAPSHOT_SHA256")
        if license_block.get("reviewStatus") != "VERIFIED":
            errors.append("LICENSE_NOT_VERIFIED")
        if not license_block.get("researchUseAllowed"):
            errors.append("RESEARCH_USE_NOT_ALLOWED")
        if not license_block.get("internalEngineeringAllowed"):
            errors.append("INTERNAL_ENGINEERING_NOT_ALLOWED")

    access = record.get("access")
    if not isinstance(access, dict) or access.get("termsAccepted") is not True:
        errors.append("ACCESS_TERMS_NOT_ACCEPTED")

    verification = record.get("verification")
    required_flags = (
        "canonicalRecordOpened",
        "titleMatched",
        "versionCaptured",
        "licenseCaptured",
        "downloadLinkMatchedCanonicalRecord",
    )
    if not isinstance(verification, dict):
        errors.append("VERIFICATION_BLOCK_REQUIRED")
    else:
        for flag in required_flags:
            if verification.get(flag) is not True:
                errors.append(f"VERIFICATION_FALSE:{flag}")

    status = "VERIFIED" if not errors else "INVALID"
    return {"status": status, "errors": errors}
