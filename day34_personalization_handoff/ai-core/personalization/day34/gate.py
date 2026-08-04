def decide_gate(mean_delta,ci_low,worst_delta,bottom_quartile_delta,failure_delta,leakage=0):
    if leakage:return "BLOCKED_WITH_EVIDENCE"
    if worst_delta < -0.05 or bottom_quartile_delta < 0 or failure_delta > 0:return "HARM_DETECTED"
    if mean_delta>0 and ci_low>0 and worst_delta>=-0.02:return "PASS"
    if mean_delta>0 and worst_delta>=-0.02:return "PROMISING_NOT_PROVEN"
    return "HARM_DETECTED"
