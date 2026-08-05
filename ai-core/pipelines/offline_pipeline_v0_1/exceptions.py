class PipelineError(Exception):
    """Base exception for pipeline errors."""
    pass

class TransitionError(PipelineError):
    """Raised when an invalid state transition is attempted."""
    pass

class GovernanceError(PipelineError):
    """Raised when governance rules are violated."""
    pass

class QualityError(PipelineError):
    """Raised when data quality fails fatal checks."""
    pass
