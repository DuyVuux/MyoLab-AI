import numpy as np
from scipy.optimize import minimize_scalar
from scipy.special import softmax

class TemperatureScaler:
    def __init__(self): self.temperature_=1.0
    def fit(self,logits,y_index):
        logits=np.asarray(logits,float);y=np.asarray(y_index,int)
        def objective(log_t):
            p=softmax(logits/np.exp(log_t),axis=1)
            return -np.mean(np.log(np.clip(p[np.arange(len(y)),y],1e-12,1)))
        result=minimize_scalar(objective,bounds=(-4,4),method="bounded")
        self.temperature_=float(np.exp(result.x));return self
    def predict_proba(self,logits):
        return softmax(np.asarray(logits,float)/self.temperature_,axis=1)
