"use client";
import {useMemo,useState} from "react";
import type {ReviewActionReceipt,ReviewCaseDetail,TechnicalReviewAction} from "../../contracts/automation";
const ACTIONS:TechnicalReviewAction[]=["ACCEPTED_TECHNICAL","REPROCESS_REQUESTED","REMEASURE_SUGGESTED","INCONCLUSIVE"];

export function ReviewActionPanel(props:{reviewCase:ReviewCaseDetail;onSubmit:(x:any)=>Promise<ReviewActionReceipt>}){
 const[action,setAction]=useState<TechnicalReviewAction>("INCONCLUSIVE"),[reason,setReason]=useState(""),[busy,setBusy]=useState(false),[receipt,setReceipt]=useState<ReviewActionReceipt|null>(null);
 const key=useMemo(()=>`ui-i3:${props.reviewCase.case_id}:${props.reviewCase.revision}:${action}`,[props.reviewCase.case_id,props.reviewCase.revision,action]);
 return <section><h3>Technical review</h3><p>State: <strong>{props.reviewCase.state}</strong> · revision {props.reviewCase.revision}</p>
  <label>Action<select value={action} onChange={e=>setAction(e.target.value as TechnicalReviewAction)}>{ACTIONS.map(x=><option key={x}>{x}</option>)}</select></label>
  <label>Reason code<input value={reason} onChange={e=>setReason(e.target.value)} /></label>
  <button disabled={busy||!reason.trim()} onClick={async()=>{setBusy(true);try{setReceipt(await props.onSubmit({action,reason_code:reason.trim(),expected_revision:props.reviewCase.revision,idempotency_key:key}))}finally{setBusy(false)}}}>Submit technical review action</button>
  {receipt?<p role="status">Recorded. Audit event: <code>{receipt.audit_event_id}</code></p>:null}
 </section>
}
