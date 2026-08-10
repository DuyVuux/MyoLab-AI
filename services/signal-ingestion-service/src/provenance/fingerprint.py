"""Fingerprinting utilities for source immutability tracking."""
import hashlib
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class SourceFingerprint:
    source_ids: tuple[str, ...]
    combined_digest: str
    file_count: int

def fingerprint_or_empty(path: Path) -> SourceFingerprint:
    """Creates a fingerprint of a file or directory tree."""
    if not path.exists():
        return SourceFingerprint((), digest_text("MISSING:" + str(path.resolve())), 0)
    if path.is_file():
        digest = sha256_file(path)
        return SourceFingerprint(("src_sha256_" + digest,), digest, 1)
    if path.is_dir():
        files = sorted(item for item in path.rglob("*") if item.is_file())
        source_ids = tuple("src_sha256_" + sha256_file(item) for item in files)
        combined = digest_text("\n".join(source_ids))
        return SourceFingerprint(source_ids, combined, len(files))
    return SourceFingerprint((), digest_text("UNSUPPORTED:" + str(path.resolve())), 0)

def sha256_file(path: Path) -> str:
    """Computes SHA-256 for a single file."""
    with path.open("rb") as file_obj:
        return hashlib.file_digest(file_obj, "sha256").hexdigest()

def digest_text(value: str) -> str:
    """Computes SHA-256 for a text string."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
