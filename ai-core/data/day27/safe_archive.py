from __future__ import annotations

import tarfile
import zipfile
from pathlib import Path, PurePosixPath


class UnsafeArchiveError(ValueError):
    pass


def is_safe_member(name: str) -> bool:
    normalized = name.replace("\\", "/")
    path = PurePosixPath(normalized)
    return not path.is_absolute() and ".." not in path.parts


def inventory_archive(path: Path) -> dict[str, object]:
    entries: list[dict[str, object]] = []
    unsafe: list[str] = []
    archive_type = "unknown"

    if zipfile.is_zipfile(path):
        archive_type = "zip"
        with zipfile.ZipFile(path) as archive:
            for info in archive.infolist():
                if not is_safe_member(info.filename):
                    unsafe.append(info.filename)
                entries.append({
                    "path": info.filename,
                    "sizeBytes": info.file_size,
                    "compressedSizeBytes": info.compress_size,
                    "isDirectory": info.is_dir(),
                    "extension": Path(info.filename).suffix.lower(),
                })
    elif tarfile.is_tarfile(path):
        archive_type = "tar"
        with tarfile.open(path, "r:*") as archive:
            for member in archive.getmembers():
                if not is_safe_member(member.name):
                    unsafe.append(member.name)
                entries.append({
                    "path": member.name,
                    "sizeBytes": member.size,
                    "compressedSizeBytes": None,
                    "isDirectory": member.isdir(),
                    "extension": Path(member.name).suffix.lower(),
                })
    else:
        raise UnsafeArchiveError("UNSUPPORTED_OR_INVALID_ARCHIVE")

    extension_counts: dict[str, int] = {}
    for entry in entries:
        ext = str(entry["extension"] or "<none>")
        extension_counts[ext] = extension_counts.get(ext, 0) + 1

    return {
        "schemaVersion": "public-dataset-archive-inventory.v1",
        "archiveType": archive_type,
        "entryCount": len(entries),
        "unsafePaths": unsafe,
        "safeToExtract": not unsafe,
        "extensionCounts": extension_counts,
        "entries": entries,
    }


def safe_extract(path: Path, destination: Path) -> None:
    inventory = inventory_archive(path)
    if not inventory["safeToExtract"]:
        raise UnsafeArchiveError("ARCHIVE_PATH_TRAVERSAL_DETECTED")
    destination.mkdir(parents=True, exist_ok=True)
    if inventory["archiveType"] == "zip":
        with zipfile.ZipFile(path) as archive:
            archive.extractall(destination)
    elif inventory["archiveType"] == "tar":
        with tarfile.open(path, "r:*") as archive:
            archive.extractall(destination, filter="data")
