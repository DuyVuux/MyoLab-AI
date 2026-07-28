from __future__ import annotations
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core"))

import zipfile
from data.day27.safe_archive import inventory_archive


def test_safe_zip(tmp_path):
    path = tmp_path / "safe.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("subject01/file.csv", "x")
    report = inventory_archive(path)
    assert report["safeToExtract"] is True


def test_path_traversal_detected(tmp_path):
    path = tmp_path / "unsafe.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("../escape.txt", "x")
    report = inventory_archive(path)
    assert report["safeToExtract"] is False
    assert report["unsafePaths"]
