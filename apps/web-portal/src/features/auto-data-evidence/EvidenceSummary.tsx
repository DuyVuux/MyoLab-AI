"use client";
import type { SessionEvidenceDetail } from "../../contracts/automation";
import { metricDisplayState } from "./model";

export function EvidenceSummary({evidence}:{evidence:SessionEvidenceDetail}){
 return <section aria-labelledby="evidence-summary-title">
  <p>TECHNICAL EVIDENCE</p>
  <h2 id="evidence-summary-title">Session evidence</h2>
  <p>Research only · Not clinically validated · Not for clinical use</p>
  <dl>
   <div><dt>Session</dt><dd>{evidence.session_id}</dd></div>
   <div><dt>Source hash</dt><dd><code>{evidence.source_hash??"Unavailable"}</code></dd></div>
   <div><dt>QC</dt><dd>{evidence.quality?.overall_status??"UNKNOWN"}</dd></div>
  </dl>
  <div>
   {evidence.metrics.map(metric=>{const d=metricDisplayState(metric);return <article key={metric.metric_id}>
    <h3>{metric.metric_name}</h3><strong>{d.valueText}</strong><p>{metric.eligibility}</p>
    {d.reason?<code>{d.reason}</code>:null}
   </article>})}
  </div>
 </section>
}
