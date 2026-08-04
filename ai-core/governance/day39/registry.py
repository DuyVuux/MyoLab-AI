import json
from pathlib import Path
from .models import RegistryStateEnum, RunManifest

PROHIBITED_CLINICAL_STATES = {
    "CLINICALLY_VALIDATED",
    "APPROVED_FOR_PATIENT_USE",
    "PRODUCTION_CLINICAL"
}

def validate_registry_state(state: str) -> bool:
    """
    Validates that a given state string is not a prohibited clinical state,
    and is a known registry state.
    """
    # Hard block for clinical states
    if state in PROHIBITED_CLINICAL_STATES:
        raise PermissionError(f"CRITICAL: Prohibited clinical state requested: {state}. "
                              "This system is for research only. Patient-facing use is strictly blocked.")
    
    # Must be one of the known registry states
    try:
        RegistryStateEnum(state)
    except ValueError:
        raise ValueError(f"Unknown registry state: {state}")
    
    return True

def load_and_validate_manifest(path: str | Path) -> RunManifest:
    """
    Loads a manifest JSON file and validates it strictly using Pydantic.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Manifest file not found: {path}")
    
    data = json.loads(path.read_text(encoding="utf-8"))
    
    # Validate clinical states first before Pydantic parsing
    # This ensures we catch raw string violations even if the parser would reject it as invalid enum
    raw_state = data.get("registry_state")
    if raw_state:
        validate_registry_state(raw_state)
    
    # Pydantic validation
    manifest = RunManifest.model_validate(data)
    return manifest
