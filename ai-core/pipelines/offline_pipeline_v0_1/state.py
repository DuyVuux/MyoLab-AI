from typing import List, Set, Dict
from .exceptions import TransitionError

class PipelineStateMachine:
    TERMINAL: Set[str] = {"REPORTED", "FAILED", "ABSTAINED"}
    ALLOWED: Dict[str, Set[str]] = {
        "RECEIVED": {"PREFLIGHT_PASSED", "FAILED"},
        "PREFLIGHT_PASSED": {"IMPORTED", "FAILED"},
        "IMPORTED": {"QC_PASSED", "QC_WARNING", "QC_FAILED", "FAILED"},
        "QC_PASSED": {"FEATURES_READY", "FAILED"},
        "QC_WARNING": {"FEATURES_READY", "FAILED"},
        "QC_FAILED": {"ABSTAINED"},
        "FEATURES_READY": {"INFERENCE_READY", "FAILED"},
        "INFERENCE_READY": {"ANALYZED", "ABSTAINED", "FAILED"},
        "ANALYZED": {"REPORTED", "FAILED"},
    }

    def __init__(self, initial_state: str = "RECEIVED"):
        self.current_state = initial_state
        self.history: List[str] = [initial_state]

    def transition(self, next_state: str) -> str:
        """Transitions to the next state if allowed."""
        if self.current_state in self.TERMINAL:
            raise TransitionError(f"Cannot transition from terminal state: {self.current_state}")
            
        allowed_next = self.ALLOWED.get(self.current_state, set())
        if next_state not in allowed_next:
            raise TransitionError(f"INVALID_TRANSITION: {self.current_state} -> {next_state}")
            
        self.current_state = next_state
        self.history.append(next_state)
        return next_state

    def force_fail(self):
        """Forces the state machine to FAILED, bypassing normal checks (fail-closed)."""
        # If we are already in a terminal state, just record the intent or do nothing
        if self.current_state not in self.TERMINAL:
            self.current_state = "FAILED"
            self.history.append("FAILED")
