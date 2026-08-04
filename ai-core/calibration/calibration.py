import numpy as np
from scipy.optimize import minimize_scalar
from scipy.special import softmax
from sklearn.linear_model import LogisticRegression
from sklearn.isotonic import IsotonicRegression
from typing import Union, List

class TemperatureScaler:
    """
    Temperature Scaling for model calibration.
    Learns a single scalar parameter (temperature) to scale logits before softmax.
    """
    def __init__(self):
        self.temperature_ = 1.0

    def fit(self, logits: np.ndarray, y_index: np.ndarray) -> "TemperatureScaler":
        logits = np.asarray(logits, dtype=float)
        y = np.asarray(y_index, dtype=int)
        
        def objective(log_t):
            t = np.exp(log_t)
            p = softmax(logits / t, axis=1)
            # Add eps to avoid log(0)
            eps = 1e-12
            p = np.clip(p, eps, 1.0 - eps)
            # Calculate Negative Log Likelihood (NLL)
            log_probs = np.log(p[np.arange(len(y)), y])
            return -np.mean(log_probs)

        # Optimize log(T) to ensure T is strictly positive
        result = minimize_scalar(objective, bounds=(-4, 4), method="bounded")
        self.temperature_ = float(np.exp(result.x))
        return self

    def predict_proba(self, logits: np.ndarray) -> np.ndarray:
        logits = np.asarray(logits, dtype=float)
        return softmax(logits / self.temperature_, axis=1)


class PlattOVR:
    """
    Platt Scaling with One-Vs-Rest approach for multiclass calibration.
    Fits a logistic regression per class on the raw scores.
    """
    def __init__(self):
        self.models_: List[LogisticRegression] = []
        self.n_classes_: int = 0

    def fit(self, scores: np.ndarray, y_index: np.ndarray) -> "PlattOVR":
        scores = np.asarray(scores, dtype=float)
        y = np.asarray(y_index, dtype=int)
        
        self.n_classes_ = len(np.unique(y))
        # Fallback if y doesn't contain all classes, derive from scores shape
        if self.n_classes_ < scores.shape[1]:
            self.n_classes_ = scores.shape[1]
            
        self.models_ = []
        
        for c in range(self.n_classes_):
            # Binary target for class c
            y_binary = (y == c).astype(int)
            # Use raw scores for class c
            score_c = scores[:, c].reshape(-1, 1)
            
            lr = LogisticRegression(solver='lbfgs')
            lr.fit(score_c, y_binary)
            self.models_.append(lr)
            
        return self

    def predict_proba(self, scores: np.ndarray) -> np.ndarray:
        scores = np.asarray(scores, dtype=float)
        calibrated_probs = np.zeros((scores.shape[0], self.n_classes_))
        
        for c in range(self.n_classes_):
            score_c = scores[:, c].reshape(-1, 1)
            # predict_proba returns [P(y=0), P(y=1)], we want P(y=1)
            calibrated_probs[:, c] = self.models_[c].predict_proba(score_c)[:, 1]
            
        # Normalize to ensure probabilities sum to 1
        sums = calibrated_probs.sum(axis=1, keepdims=True)
        # Avoid division by zero
        sums[sums == 0] = 1e-12 
        return calibrated_probs / sums


class IsotonicOVR:
    """
    Isotonic Regression with One-Vs-Rest approach for multiclass calibration.
    Fits an isotonic regression per class on the raw scores/probabilities.
    """
    def __init__(self):
        self.models_: List[IsotonicRegression] = []
        self.n_classes_: int = 0

    def fit(self, scores: np.ndarray, y_index: np.ndarray) -> "IsotonicOVR":
        scores = np.asarray(scores, dtype=float)
        y = np.asarray(y_index, dtype=int)
        
        self.n_classes_ = len(np.unique(y))
        if self.n_classes_ < scores.shape[1]:
            self.n_classes_ = scores.shape[1]
            
        self.models_ = []
        
        for c in range(self.n_classes_):
            y_binary = (y == c).astype(int)
            score_c = scores[:, c]
            
            ir = IsotonicRegression(out_of_bounds='clip')
            ir.fit(score_c, y_binary)
            self.models_.append(ir)
            
        return self

    def predict_proba(self, scores: np.ndarray) -> np.ndarray:
        scores = np.asarray(scores, dtype=float)
        calibrated_probs = np.zeros((scores.shape[0], self.n_classes_))
        
        for c in range(self.n_classes_):
            score_c = scores[:, c]
            calibrated_probs[:, c] = self.models_[c].predict(score_c)
            
        # Normalize
        sums = calibrated_probs.sum(axis=1, keepdims=True)
        sums[sums == 0] = 1e-12
        return calibrated_probs / sums
