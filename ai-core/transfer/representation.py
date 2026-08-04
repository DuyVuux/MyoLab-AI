import numpy as np
import numpy.typing as npt

def channel_summary_representation(x: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
    """
    Transforms multi-channel temporal features into a channel-summary representation.
    Extracts mean, std, min, max, and median across channels (axis=1).
    Input shape must be: (samples, channels, features)
    Returns: (samples, features * 5)
    """
    x = np.asarray(x, dtype=np.float64)
    
    if x.ndim != 3:
        raise ValueError(f"EXPECTED_ROWS_CHANNELS_FEATURES (3D). Got {x.ndim}D array.")
        
    if not np.isfinite(x).all():
        raise ValueError("NONFINITE_FEATURES: Input array contains NaN or Inf.")
        
    return np.concatenate([
        np.mean(x, axis=1),
        np.std(x, axis=1, ddof=1),
        np.min(x, axis=1),
        np.max(x, axis=1),
        np.median(x, axis=1)
    ], axis=1)
