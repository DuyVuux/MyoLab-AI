from collections import defaultdict
import numpy as np

def make_fewshot_split(subject_ids,labels,repetition_ids,subject,k,seed):
    rng=np.random.default_rng(seed)
    idx=np.where(np.asarray(subject_ids)==subject)[0]
    by_class=defaultdict(list)
    for i in idx: by_class[str(labels[i])].append(i)
    cal=[];eva=[]
    for label,indices in sorted(by_class.items()):
        reps=defaultdict(list)
        for i in indices: reps[str(repetition_ids[i])].append(i)
        keys=sorted(reps)
        if len(keys)<k+1: raise ValueError(f"INELIGIBLE:{subject}:{label}")
        chosen=set(rng.choice(keys,size=k,replace=False).tolist())
        for rep,rows in reps.items(): (cal if rep in chosen else eva).extend(rows)
    if set(cal)&set(eva): raise RuntimeError("CALIBRATION_EVALUATION_OVERLAP")
    return np.asarray(sorted(cal)),np.asarray(sorted(eva))

def class_centroids(X,y):
    y=np.asarray(y)
    return {c:np.mean(X[y==c],axis=0) for c in sorted(set(y.tolist()))}

def nearest_centroid_predict(X,centroids):
    classes=list(centroids);matrix=np.vstack([centroids[c] for c in classes])
    dist=((X[:,None,:]-matrix[None,:,:])**2).sum(axis=2)
    return np.asarray([classes[i] for i in np.argmin(dist,axis=1)])
