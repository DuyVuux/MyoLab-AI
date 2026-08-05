import logging
from typing import Dict, Any
from .exceptions import GovernanceError

logger = logging.getLogger(__name__)

def verify_model_bundle(bundle: Dict[str, Any]) -> bool:
    """Verifies that the provided model bundle adheres to Day 39 governance rules."""
    required = ["model_id", "registry_state", "rerun_status", "model_card_present", "bundle_sha256"]
    missing = [k for k in required if k not in bundle]
    if missing:
        logger.error(f"Model bundle missing fields: {missing}")
        raise GovernanceError(f"MODEL_BUNDLE_MISSING: {missing}")
        
    if bundle.get("registry_state") not in {"RESEARCH_BASELINE", "RESEARCH_CANDIDATE"}:
        logger.error(f"Model state not eligible: {bundle.get('registry_state')}")
        raise GovernanceError("MODEL_STATE_NOT_ELIGIBLE")
        
    if bundle.get("rerun_status") not in {"EXACT_MATCH", "MATCH_WITHIN_TOLERANCE"}:
        logger.error(f"Rerun not verified: {bundle.get('rerun_status')}")
        raise GovernanceError("RERUN_NOT_VERIFIED")
        
    if bundle.get("model_card_present") is not True:
        logger.error("Model card is missing")
        raise GovernanceError("MODEL_CARD_MISSING")
        
    return True
