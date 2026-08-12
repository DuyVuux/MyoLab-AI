import { assertNoFalseFinalState } from './model.mjs';

function esc(value) {
  return String(value)
    .replaceAll('&', '&amp;').replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#39;');
}

export function renderExceptionDashboard(summary) {
  const cards = summary.items.map((item) => {
    assertNoFalseFinalState(item);
    const reasons = item.reason_codes.length
      ? `<ul aria-label="Reason codes">${item.reason_codes.map((r) => `<li><code>${esc(r)}</code></li>`).join('')}</ul>`
      : '<p data-reasons="none">No additional reason code supplied.</p>';
    return `<article class="qc-card" data-attention="${esc(item.attention)}" aria-label="${esc(item.label)} for ${esc(item.case_id)}">
      <h2>${esc(item.label)}</h2>
      <p><strong>Case:</strong> ${esc(item.case_id)}</p>
      <p><strong>Supportability:</strong> ${esc(item.supportability)}</p>
      <p><strong>Evaluation:</strong> ${esc(item.evaluation_status)}</p>
      ${reasons}
      <a href="#case-${esc(item.case_id)}-evidence">Open evidence</a>
    </article>`;
  }).join('\n');

  return `<main aria-labelledby="qc-dashboard-title">
    <aside role="note" aria-label="Research-only notice"><strong>RESEARCH ONLY</strong> — technical evidence review, not diagnosis.</aside>
    <h1 id="qc-dashboard-title">Exception-first QC queue</h1>
    <p>Order: FAIL/BLOCKED → WARNING/NEEDS_REVIEW → UNKNOWN/NOT_EVALUATED → PASS.</p>
    <section role="list" aria-label="QC cases">${cards}</section>
  </main>`;
}
