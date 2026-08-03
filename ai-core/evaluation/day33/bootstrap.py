from collections import defaultdict

import numpy as np
from sklearn.metrics import f1_score


def _metric(rows,order):
    b=defaultdict(list)
    for r in rows:b[r["subject_id"]].append(r)
    vals=[]
    for rs in b.values():
        vals.append(f1_score([x["y_true"] for x in rs],[x["y_pred"] for x in rs],
                             labels=order,average="macro",zero_division=0))
    return float(np.mean(vals))

def subject_cluster_bootstrap(rows,iterations=2000,seed=3301,confidence=0.95):
    order=rows[0]["class_order"]; b=defaultdict(list)
    for r in rows:b[r["subject_id"]].append(r)
    subjects=sorted(b)
    if len(subjects)<2: raise ValueError("need_two_subjects")
    rng=np.random.default_rng(seed); values=[]
    for _ in range(iterations):
        sampled=rng.choice(subjects,size=len(subjects),replace=True)
        rs=[]
        for i,s in enumerate(sampled):
            for r in b[s]:
                c=dict(r); c["subject_id"]=f"draw{i}:{s}"; rs.append(c)
        values.append(_metric(rs,order))
    alpha=(1-confidence)/2
    return {"schema_version":"day33-subject-cluster-bootstrap.v1","cluster_unit":"subject_id",
            "iterations":iterations,"seed":seed,"point_estimate":_metric(rows,order),
            "ci_low":float(np.quantile(values,alpha)),
            "ci_high":float(np.quantile(values,1-alpha)),
            "window_bootstrap_used":False}
