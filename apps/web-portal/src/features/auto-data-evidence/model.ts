import type { MetricEvidence, SignalWindow } from "../../contracts/automation";
export function metricDisplayState(metric:MetricEvidence){
  if(metric.eligibility!=="AVAILABLE") return {valueText:"NOT AVAILABLE",reason:metric.reason_code??"UNSUPPORTED_WITHOUT_REASON"};
  return {valueText:metric.value==null?"INVALID AVAILABLE VALUE":`${metric.value}${metric.unit?` ${metric.unit}`:""}`};
}
export function assertComparableWindows(raw:SignalWindow,processed:SignalWindow):void{
  if(raw.session_id!==processed.session_id) throw new Error("RAW_PROCESSED_SESSION_MISMATCH");
  if(raw.channel_id!==processed.channel_id) throw new Error("RAW_PROCESSED_CHANNEL_MISMATCH");
  if(raw.start_s!==processed.start_s||raw.end_s!==processed.end_s) throw new Error("RAW_PROCESSED_TIMEBASE_MISMATCH");
  if(raw.representation!=="RAW") throw new Error("RAW_WINDOW_IDENTITY_INVALID");
  if(processed.representation!=="PROCESSED") throw new Error("PROCESSED_WINDOW_IDENTITY_INVALID");
  if(!processed.provenance.processing_manifest_id) throw new Error("PROCESSED_WINDOW_MANIFEST_REQUIRED");
}
