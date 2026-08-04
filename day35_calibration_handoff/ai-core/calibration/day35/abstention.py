def decide(quality_status,confidence,threshold,warning_delta=0.05):
    if quality_status=="fail":return "abstain_quality_fail"
    required=threshold+warning_delta if quality_status=="warning" else threshold
    if confidence<required:
        return "abstain_low_quality_confidence" if quality_status=="warning" else "abstain_low_confidence"
    return "accept_with_warning" if quality_status=="warning" else "accept"
