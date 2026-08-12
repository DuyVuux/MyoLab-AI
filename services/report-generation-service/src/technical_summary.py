from dataclasses import dataclass
BANNED=('diagnosis','diagnose','treatment recommendation','disease confirmed','pathology confirmed')

@dataclass(frozen=True)
class SummaryRequest: 
    evidence: dict
    review_state: str
    reviewer_approval: bool=False

def can_finalize(r): 
    return r.review_state == 'FINALIZED_DEMO' and r.reviewer_approval and r.evidence.get('qc', {}).get('signal_quality') != 'FAIL'

def render(r):
    e = r.evidence
    lines = [
        'RESEARCH PROTOTYPE — NOT FOR CLINICAL USE',
        '# Technical Analysis Demo',
        f"Evidence bundle: {e.get('bundle_id','UNKNOWN')}",
        f"QC status: {e.get('qc',{}).get('signal_quality','NOT_EVALUATED')}",
        '## Findings'
    ]
    for m in e.get('metrics', []): 
        lines.append(f"- {m.get('metric_name')}: " + (
            f"unavailable ({', '.join(m.get('reason_codes',[]) or ['NO_REASON_PROVIDED'])})." 
            if m.get('value') is None 
            else f"{m['value']} {m.get('units','')}. Research measurement only."
        ))
    lines += [
        '## Limitations'
    ] + [
        f"- {x}" for x in e.get('limitations',[]) or ['No additional limitation supplied.']
    ] + [
        f"Finalization status: {'ELIGIBLE' if can_finalize(r) else 'DRAFT_ONLY'}"
    ]
    t = '\n'.join(lines)
    if any(x in t.lower() for x in BANNED): 
        raise ValueError('DIAGNOSTIC_LANGUAGE_FORBIDDEN')
    return t
