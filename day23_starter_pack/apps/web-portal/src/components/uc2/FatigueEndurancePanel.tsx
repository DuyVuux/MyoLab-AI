import type{QuantitativeMetric}from'../../schemas/uc2-assessment.schema';
export interface FatigueEndurancePanelProps{readonly metric:QuantitativeMetric|undefined;}
export function FatigueEndurancePanel({metric}:FatigueEndurancePanelProps):JSX.Element{return <section><h2>Fatigue/Endurance</h2><p>{metric?.value===null||metric===undefined?'Không khả dụng':`${metric.value.toFixed(1)} ${metric.unit??''}`}</p><p>Kết quả hỗ trợ review, không phải khuyến nghị tăng/giảm tải tự động.</p></section>;}
