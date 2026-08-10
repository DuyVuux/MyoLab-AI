from __future__ import annotations
from pathlib import Path
from typing import Any
import json
import yaml

def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file_obj:
        data = yaml.safe_load(file_obj)
    if not isinstance(data, dict): raise TypeError(f"Expected mapping in {path}")
    return data

def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file_obj:
        data = json.load(file_obj)
    if not isinstance(data, dict): raise TypeError(f"Expected object in {path}")
    return data

def promotable_tier(item: dict[str, Any]) -> str:
    human = item.get("source_class") in {"DEIDENTIFIED_HISTORICAL", "PROSPECTIVE", "PILOT"}
    if human and (item.get("governance_status") == "UNKNOWN" or item.get("deidentification_status") == "UNKNOWN"):
        return "BLOCKED"
    if item.get("source_class") == "SYNTHETIC": return "E0"
    if item.get("source_class") == "VENDOR_SAMPLE": return "E1"
    return "REVIEW_REQUIRED"

def scan_project_files(root_dir: Path) -> list[Path]:
    """Scans the project directory, skipping specified directories and honoring specific whitelists."""
    skip_dirs = {"__pycache__", ".pytest_cache", ".venv", "env", ".git", "node_modules", "raw", "datasets", "experiments", "fixtures"}
    found_files = []
    
    for path in root_dir.rglob("*"):
        if not path.is_file():
            continue
        
        # Check if file is in a skipped directory
        is_skipped = False
        for parent in path.parents:
            if parent.name in skip_dirs:
                is_skipped = True
                break
        
        if is_skipped:
            continue
            
        found_files.append(path)
        
    return found_files
