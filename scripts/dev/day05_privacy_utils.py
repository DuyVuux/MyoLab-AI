from __future__ import annotations
from pathlib import Path
from typing import Any
import json
import yaml

HIPAA_DIRECT_KEYS = {
    # 1. Names
    "first_name", "last_name", "name", "full_name", "patient_name", "subject_name",
    # 2. Geographic info
    "address", "street", "city", "county", "zip", "zipcode", "postal_code", 
    # 3. Dates (except year)
    "dob", "date_of_birth", "birth_date", "admission_date", "discharge_date",
    # 4-6. Contact info
    "phone", "telephone", "mobile", "fax", "email",
    # 7-11. Numbers/IDs
    "ssn", "social_security", "mrn", "medical_record_number", "health_plan_id", "account_number", "license_number",
    # 12-15. Electronic/Device
    "vehicle_id", "license_plate", "device_id", "device_serial", "url", "ip_address",
    # 16-17. Biometrics
    "biometric", "fingerprint", "face_photo"
}

def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file_obj:
        data = yaml.safe_load(file_obj)
    if not isinstance(data, dict):
        raise TypeError(f"Expected mapping in {path}")
    return data

def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file_obj:
        data = json.load(file_obj)
    if not isinstance(data, dict):
        raise TypeError(f"Expected object in {path}")
    return data

def classify_structured_fields(fields: dict[str, Any]) -> str:
    lowered = {str(key).lower() for key in fields}
    if lowered & HIPAA_DIRECT_KEYS:
        return "DIRECT_IDENTIFIER_DETECTED"
    if fields.get("governance_status") == "UNKNOWN":
        return "GOVERNANCE_STATUS_UNKNOWN"
    record_name = str(fields.get("record_name", "")).lower()
    if "patient" in record_name or "name" in record_name:
        return "FREE_TEXT_REVIEW_REQUIRED"
    return "PASS_STRUCTURED_ID_CHECK"

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
