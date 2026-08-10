"""Shared provenance and source linkage primitives.

The module provides stable source tracking and run identity hashing 
across multiple ingestion adapters.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SourceLinkage:
    source_path: str
    source_name: str
    size_bytes: int
    sha256: str
    source_id: str


@dataclass(frozen=True)
class ParserProvenance:
    parser_id: str
    parser_version: str
    contract_id: str
    contract_version: str
    source_id: str
    run_id: str


def sha256_file(path: Path) -> str:
    with path.open("rb") as file_obj:
        return hashlib.file_digest(file_obj, "sha256").hexdigest()


def source_linkage(path: Path) -> SourceLinkage:
    resolved = path.resolve()
    digest = sha256_file(resolved)
    return SourceLinkage(
        source_path=str(resolved),
        source_name=path.name,
        size_bytes=resolved.stat().st_size,
        sha256=digest,
        source_id=f"src_sha256_{digest}",
    )


def stable_run_id(*, source_id: str, parser_version: str, contract_version: str) -> str:
    payload = {
        "source_id": source_id,
        "parser_version": parser_version,
        "contract_version": contract_version,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return "parse_sha256_" + hashlib.sha256(encoded).hexdigest()
