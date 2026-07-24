import type{QuantitativeMetric}from'../../schemas/uc2-assessment.schema';
export interface RepeatabilityPanelProps{readonly metric:QuantitativeMetric|undefined;}
export function RepeatabilityPanel({metric}:RepeatabilityPanelProps):JSX.Element{return <section><h2>Repeatability</h2><p>{metric?.value??'Chưa có dữ liệu'} {metric?.unit??''}</p><p>CoV thấp hơn thường biểu thị ổn định hơn, nhưng không phải clinical score.</p></section>;}
