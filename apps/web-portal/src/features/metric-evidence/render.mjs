import { explainMetric } from './model.mjs';
function esc(v){return String(v).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');}
export function renderMetricEvidence(view){
  const value=view.value==null ? '<span data-value="unavailable">Unavailable</span>' : `<span data-value="available">${esc(view.value)} ${esc(view.units ?? '')}</span>`;
  const reasons=view.reason_codes.length ? `<ul aria-label="Metric reason codes">${view.reason_codes.map(r=>`<li><code>${esc(r)}</code></li>`).join('')}</ul>` : '<p>No blocking reason code.</p>';
  const ds=view.distribution_support;
  const u=view.uncertainty ?? {};
  const uncertaintyText=u.uncertainty_type==='RULE_CONFIDENCE'
    ? `RULE_CONFIDENCE = ${esc(u.rule_confidence_level ?? 'UNKNOWN')} — not probability.`
    : `${esc(u.uncertainty_type ?? 'NOT_APPLICABLE')} / calibration ${esc(u.calibration_status ?? 'NOT_APPLICABLE')}`;
  const ood=ds.score==null ? 'OOD score: NOT AVAILABLE' : `OOD score: ${esc(ds.score)}`;
  return `<article class="metric-evidence" data-status="${esc(view.metric_status)}" aria-label="Metric evidence for ${esc(view.metric_name)}">
    <aside role="note"><strong>RESEARCH ONLY</strong></aside>
    <h2>${esc(view.metric_name)}</h2><p><strong>${esc(view.status_label)}</strong></p>
    <p>Value: ${value}</p>${reasons}
    <section aria-label="Distribution support"><h3>Distribution support</h3><p>Status: ${esc(ds.status)}</p><p>Method: ${esc(ds.method_status)}</p><p>${ood}</p></section>
    <section aria-label="Uncertainty semantics"><h3>Uncertainty</h3><p>${uncertaintyText}</p><p><strong>RULE_CONFIDENCE ≠ PROBABILITY</strong></p></section>
    <p class="explanation">${esc(explainMetric(view))}</p>
  </article>`;
}
