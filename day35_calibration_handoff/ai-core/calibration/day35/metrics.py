import numpy as np

def multiclass_brier(y_index,proba):
    p=np.asarray(proba,float);y=np.asarray(y_index,int)
    one=np.zeros_like(p);one[np.arange(len(y)),y]=1
    return float(np.mean(np.sum((p-one)**2,axis=1)))

def expected_calibration_error(y_index,proba,n_bins=15):
    p=np.asarray(proba,float);y=np.asarray(y_index,int)
    conf=p.max(axis=1);pred=p.argmax(axis=1);edges=np.linspace(0,1,n_bins+1)
    ece=0.;bins=[]
    for i in range(n_bins):
        mask=(conf>=edges[i]) & (conf < edges[i+1] if i<n_bins-1 else conf<=edges[i+1])
        n=int(mask.sum())
        if not n: bins.append({"bin":i,"count":0});continue
        acc=float(np.mean(pred[mask]==y[mask]));c=float(np.mean(conf[mask]))
        ece+=n/len(y)*abs(acc-c);bins.append({"bin":i,"count":n,"accuracy":acc,"confidence":c})
    return float(ece),bins

def coverage_risk(y_index,proba,thresholds):
    p=np.asarray(proba,float);y=np.asarray(y_index,int)
    conf=p.max(axis=1);pred=p.argmax(axis=1);rows=[]
    for t in thresholds:
        accept=conf>=t;coverage=float(np.mean(accept))
        acc=float(np.mean(pred[accept]==y[accept])) if accept.any() else float("nan")
        rows.append({"threshold":float(t),"coverage":coverage,
                     "selective_accuracy":acc,
                     "selective_risk":1-acc if accept.any() else float("nan")})
    return rows
