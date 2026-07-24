import {metricDisplay,type QuantitativeMetric} from '../../schemas/uc2-assessment.schema';
export interface QuantitativeKpiRowProps{readonly metrics:readonly QuantitativeMetric[];}
export function QuantitativeKpiRow({metrics}:QuantitativeKpiRowProps):JSX.Element{return <section aria-labelledby="uc2-kpis"><h2 id="uc2-kpis">Chỉ số định lượng</h2><div>{metrics.slice(0,4).map(m=><article key={m.metricId}><h3>{m.labelVi}</h3><strong>{metricDisplay(m)}</strong><p>Trạng thái: {m.status}</p><small>{m.formulaVersion} · {m.validationStatus}</small></article>)}</div></section>;}
