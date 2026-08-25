import { AutomationProblemError, contractProblem } from "./problem";
import type {
  ProcessingManifestEvidence,
  SessionEvidenceDetail,
  SignalDescriptor,
  SignalIndex,
} from "./evidence-detail";
import type { ReviewActionReceipt, ReviewCaseDetail } from "./review-actions";
import type { SignalWindow } from "./signal";
import { parseMetricEvidence, parseQualityAssessment, parseSignalWindow } from "./validators";

type R = Record<string, unknown>;
function fail(message: string): never { throw new AutomationProblemError(contractProblem(message)); }
function rec(v: unknown, label: string): R {
  if (!v || typeof v !== "object" || Array.isArray(v)) fail(`${label} must be object`);
  return v as R;
}
function str(o: R, k: string, req=true): string|undefined {
  const v=o[k]; if(v==null){ if(req) fail(`${k} is required`); return undefined; }
  if(typeof v!=="string") fail(`${k} must be string`); return v;
}
function num(o:R,k:string,req=true):number|undefined{
  const v=o[k]; if(v==null){ if(req) fail(`${k} is required`); return undefined; }
  if(typeof v!=="number"||!Number.isFinite(v)) fail(`${k} must be finite number`); return v;
}
function bool(o:R,k:string):boolean{ const v=o[k]; if(typeof v!=="boolean") fail(`${k} must be boolean`); return v; }
function strings(o:R,k:string):string[]{ const v=o[k]; if(v==null)return[]; if(!Array.isArray(v)||!v.every(x=>typeof x==="string")) fail(`${k} must be string[]`); return v as string[]; }

export function parseSignalDescriptor(value:unknown):SignalDescriptor{
  const o=rec(value,"signal descriptor"); const fs=num(o,"sampling_rate_hz")!; if(fs<=0) fail("sampling_rate_hz must be > 0");
  return {channel_id:str(o,"channel_id")!,label:str(o,"label",false),unit:str(o,"unit")!,sampling_rate_hz:fs,
    sample_count:num(o,"sample_count",false),duration_s:num(o,"duration_s",false),raw_available:bool(o,"raw_available"),
    processed_available:bool(o,"processed_available"),processing_manifest_id:str(o,"processing_manifest_id",false)};
}

export function parseSignalIndex(value:unknown):SignalIndex{
  const o=rec(value,"signal index"); if(!Array.isArray(o.signals)) fail("signals must be array");
  return {session_id:str(o,"session_id")!,signals:o.signals.map(parseSignalDescriptor),source_hash:str(o,"source_hash",false),evidence_ref:str(o,"evidence_ref",false)};
}

export function parseProcessingManifestEvidence(value:unknown):ProcessingManifestEvidence{
  const o=rec(value,"processing manifest"); if(!Array.isArray(o.steps)) fail("steps must be array");
  return {processing_manifest_id:str(o,"processing_manifest_id")!,session_id:str(o,"session_id")!,source_hash:str(o,"source_hash")!,
    profile_id:str(o,"profile_id",false),profile_version:str(o,"profile_version",false),code_version:str(o,"code_version",false),
    config_hash:str(o,"config_hash",false),created_at:str(o,"created_at",false),
    steps:o.steps.map(x=>{const s=rec(x,"step");return{step_name:str(s,"step_name")!,status:str(s,"status")! as any,config_version:str(s,"config_version",false),reason_code:str(s,"reason_code",false)}})};
}

export function parseSessionEvidenceDetail(value:unknown):SessionEvidenceDetail{
  const o=rec(value,"session evidence"); if(!Array.isArray(o.metrics)) fail("metrics must be array");
  return {session_id:str(o,"session_id")!,source_hash:str(o,"source_hash",false),
    quality:o.quality==null?undefined:parseQualityAssessment(o.quality),
    metrics:o.metrics.map(parseMetricEvidence),
    signal_index:o.signal_index==null?undefined:parseSignalIndex(o.signal_index),
    processing_manifests:Array.isArray(o.processing_manifests)?o.processing_manifests.map(parseProcessingManifestEvidence):undefined,
    review_case_ids:strings(o,"review_case_ids"),limitations:strings(o,"limitations"),evidence_refs:strings(o,"evidence_refs")};
}

export function parseReviewCaseDetail(value:unknown):ReviewCaseDetail{
  const o=rec(value,"review case"); const revision=num(o,"revision")!; if(!Number.isInteger(revision)||revision<0) fail("revision must be non-negative integer");
  return {case_id:str(o,"case_id")!,session_id:str(o,"session_id")!,state:str(o,"state")! as any,reason_codes:strings(o,"reason_codes"),
    revision,created_at:str(o,"created_at",false),updated_at:str(o,"updated_at",false),evidence_ref:str(o,"evidence_ref",false)};
}

export function parseReviewActionReceipt(value:unknown):ReviewActionReceipt{
  const o=rec(value,"review action receipt"); if(!bool(o,"accepted")) fail("review action receipt must be accepted");
  return {case_id:str(o,"case_id")!,session_id:str(o,"session_id")!,action:str(o,"action")! as any,state:str(o,"state")! as any,
    revision:num(o,"revision")!,audit_event_id:str(o,"audit_event_id")!,idempotency_key:str(o,"idempotency_key")!,accepted:true,evidence_ref:str(o,"evidence_ref",false)};
}

export function parseScientificSignalWindow(value:unknown):SignalWindow{
  const p=parseSignalWindow(value);
  if(!p.provenance?.source_hash&&!p.provenance?.source_id) fail("signal window requires source identity");
  if(p.representation==="PROCESSED"&&!p.provenance.processing_manifest_id) fail("processed signal requires processing manifest");
  return p;
}
