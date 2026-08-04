import sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"ai-core/personalization"))
from day34.fewshot import make_fewshot_split,class_centroids,nearest_centroid_predict
from day34.gate import decide_gate

def test_split():
    s=np.array(["S"]*16);y=np.array(["a"]*8+["b"]*8)
    r=np.array([f"a{i//2}" for i in range(8)]+[f"b{i//2}" for i in range(8)])
    c,e=make_fewshot_split(s,y,r,"S",2,1);assert set(c).isdisjoint(set(e))

def test_centroid():
    X=np.array([[0,0],[0,1],[10,10],[10,11]],float);y=np.array(["a","a","b","b"])
    assert nearest_centroid_predict(np.array([[0,.2],[10,10.2]]),class_centroids(X,y)).tolist()==["a","b"]

def test_gate(): assert decide_gate(.05,.01,-.01,.01,-1)=="PASS"
