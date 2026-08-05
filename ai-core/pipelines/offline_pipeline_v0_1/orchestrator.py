import logging
from typing import Dict, Any
from .state import PipelineStateMachine
from .guards import verify_model_bundle
from .exceptions import PipelineError, GovernanceError, TransitionError

logger = logging.getLogger(__name__)

class OfflinePipeline:
    def __init__(self, config: Dict[str, Any], model_bundle: Dict[str, Any]):
        self.config = config
        self.model_bundle = model_bundle
        
        logger.info("Initializing OfflinePipeline v0.1")
        verify_model_bundle(model_bundle)

    def run_synthetic(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a synthetic pipeline run.
        Employs a fail-closed try-except wrapper to guarantee safe transitions.
        """
        sm = PipelineStateMachine("RECEIVED")
        
        try:
            logger.info(f"Starting pipeline for session: {session.get('session_id', 'unknown')}")
            sm.transition("PREFLIGHT_PASSED")
            sm.transition("IMPORTED")
            
            quality = session.get("quality_status", "pass")
            if quality == "fail":
                logger.warning("Quality check failed. Transitioning to ABSTAINED.")
                sm.transition("QC_FAILED")
                sm.transition("ABSTAINED")
                return self._report(session, sm, "abstain_quality_fail")
                
            sm.transition("QC_WARNING" if quality == "warning" else "QC_PASSED")
            sm.transition("FEATURES_READY")
            sm.transition("INFERENCE_READY")
            
            # Simulated inference confidence check
            confidence = session.get("confidence", 1.0)
            threshold = session.get("threshold", 0.5)
            if confidence < threshold:
                logger.warning(f"Low confidence ({confidence} < {threshold}). Transitioning to ABSTAINED.")
                sm.transition("ABSTAINED")
                return self._report(session, sm, "abstain_low_confidence")
                
            sm.transition("ANALYZED")
            sm.transition("REPORTED")
            logger.info("Pipeline completed successfully.")
            return self._report(session, sm, "accept")
            
        except TransitionError as te:
            logger.error(f"State transition error: {te}")
            sm.force_fail()
            return self._report(session, sm, "error_transition")
        except Exception as e:
            logger.error(f"Unexpected pipeline error: {e}", exc_info=True)
            sm.force_fail()
            return self._report(session, sm, "error_unexpected")

    def run_normalized(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Placeholder for normalized mode."""
        raise NotImplementedError("Normalized mode not yet implemented in v0.1")

    def run_raw_index(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Placeholder for raw-index mode."""
        raise NotImplementedError("Raw-index mode not yet implemented in v0.1")

    def _report(self, session: Dict[str, Any], sm: PipelineStateMachine, decision: str) -> Dict[str, Any]:
        return {
            "session_id": session.get("session_id", "unknown"),
            "status": sm.current_state,
            "history": sm.history,
            "quality": {"status": session.get("quality_status", "pass")},
            "inference": {"decision": decision, "training_executed": False},
            "taskc": {"supportability": "SUPPORTED" if sm.current_state == "REPORTED" else "NOT_RUN"},
            "context": {"hard_fatigue_diagnosis_allowed": False},
            "provenance": {
                "pipeline_version": "v0.1",
                "model_bundle_sha256": self.model_bundle.get("bundle_sha256", "unknown")
            },
            "safety": {
                "clinical_use_allowed": False,
                "treatment_recommendation_allowed": False
            },
            "sealed_test_opened": False,
        }
