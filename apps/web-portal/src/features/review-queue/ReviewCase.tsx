"use client";
import React,{useMemo,useState} from 'react';
const reasonRequired=new Set(['OVERRIDE_WITH_REASON','REQUEST_REPROCESS','SUGGEST_REMEASURE','MARK_INCONCLUSIVE']);
export function ReviewCase({record}:{record:any}){
 const [state,setState]=useState(record.review_state??'REVIEWING'); const [reason,setReason]=useState(''); const [audit,setAudit]=useState<any[]>([]);
 const fail=['FAIL','BLOCKED'].includes(record.attention); const actions=useMemo(()=>[
  ['ACCEPT_TECHNICAL','ACCEPTED_TECHNICAL',fail],['OVERRIDE_WITH_REASON','ACCEPTED_TECHNICAL',fail],['REQUEST_REPROCESS','REPROCESS_REQUESTED',false],['SUGGEST_REMEASURE','REMEASURE_SUGGESTED',false],['MARK_INCONCLUSIVE','INCONCLUSIVE',false]
 ],[fail]);
 function act(action:string,target:string){if(reasonRequired.has(action)&&!reason)return; const e={action,state_before:state,state_after:target,reason:reason||null}; setState(target);setAudit(v=>[...v,e]);}
 return <main><aside role="note"><strong>RESEARCH ONLY</strong> — not for clinical use.</aside><h1>Case {record.case_id}</h1><p data-testid="review-state">State: {state}</p><p>Attention: {record.attention}</p><nav><a href={`/review-queue/${record.case_id}/qc`}>QC evidence</a> · <a href={`/review-queue/${record.case_id}/signal`}>Signal</a> · <a href={`/review-queue/${record.case_id}/metrics`}>Metrics</a></nav><label>Reason <input aria-label="Review reason" value={reason} onChange={e=>setReason(e.target.value)}/></label><section aria-label="Review actions">{actions.map(([a,t,blocked]:any)=><button key={a} disabled={blocked||(reasonRequired.has(a)&&!reason)} onClick={()=>act(a,t)}>{a}</button>)}</section><h2>Audit history</h2><ul data-testid="audit-history">{audit.map((e,i)=><li key={i}>{e.action}: {e.state_before} → {e.state_after}{e.reason?` (${e.reason})`:''}</li>)}</ul></main>
}
