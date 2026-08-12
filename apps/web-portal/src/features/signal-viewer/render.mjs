function esc(v){return String(v).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');}
function polyline(points,width=800,height=180){
  const valid=points.filter(p=>p.y!=null);
  if(!valid.length) return '';
  const xs=valid.map(p=>p.x), ys=valid.map(p=>p.y);
  const xmin=Math.min(...xs), xmax=Math.max(...xs), ymin=Math.min(...ys), ymax=Math.max(...ys);
  const xr=xmax-xmin||1, yr=ymax-ymin||1;
  return valid.map(p=>`${((p.x-xmin)/xr*width).toFixed(2)},${(height-(p.y-ymin)/yr*height).toFixed(2)}`).join(' ');
}
export function renderSignalViewer(model){
  const figures=model.panels.map(panel=>{
    const mask=panel.mask_intervals.map(m=>`<li>${m.start_s.toFixed(6)}–${m.end_s.toFixed(6)} s</li>`).join('') || '<li>None</li>';
    return `<figure data-series-kind="${panel.kind}" aria-label="${panel.kind} waveform">
      <figcaption>${panel.kind} waveform — unit: ${esc(panel.units)}</figcaption>
      <svg viewBox="0 0 800 180" role="img" aria-label="${panel.kind} signal plot"><polyline fill="none" stroke="currentColor" points="${polyline(panel.points)}"/></svg>
      <p>Source ref: <a href="#evidence-${esc(panel.source_ref)}">${esc(panel.source_ref)}</a></p>
      ${panel.kind==='PROCESSED'?`<p>Processing manifest: <a href="#manifest-${esc(panel.manifest_id)}">${esc(panel.manifest_id)}</a></p><p>Profile: ${esc(panel.profile_id ?? 'UNKNOWN_PROFILE')}</p>`:''}
      <details><summary>Masked intervals</summary><ul>${mask}</ul></details>
    </figure>`;
  }).join('\n');
  const w=model.window_identity;
  return `<main aria-labelledby="signal-viewer-title"><aside role="note"><strong>RESEARCH ONLY</strong></aside><h1 id="signal-viewer-title">Raw vs processed signal evidence</h1>
    <section aria-label="Window identity"><code>${esc(w.window_id)}</code> · channel ${esc(w.channel_id)} · samples ${w.start_sample}:${w.end_sample_exclusive}</section>${figures}</main>`;
}
