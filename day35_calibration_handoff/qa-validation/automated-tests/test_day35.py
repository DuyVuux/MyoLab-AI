import sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"ai-core/calibration"))
from day35.calibration import TemperatureScaler
from day35.metrics import multiclass_brier,expected_calibration_error,coverage_risk
from day35.abstention import decide

def test_temperature():
    x=np.array([[3,0],[0,3],[2,0],[0,2]],float);y=np.array([0,1,0,1])
    c=TemperatureScaler().fit(x,y);p=c.predict_proba(x)
    assert p.shape==(4,2) and np.allclose(p.sum(1),1)

def test_metrics():
    p=np.array([[.8,.2],[.1,.9]]);y=np.array([0,1])
    assert multiclass_brier(y,p)>=0 and expected_calibration_error(y,p,5)[0]>=0
    assert len(coverage_risk(y,p,[.5,.9]))==2

def test_quality_fail():assert decide("fail",.99,.5)=="abstain_quality_fail"
