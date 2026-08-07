#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, re, sys
from collections import Counter
from pathlib import Path
from typing import Any
import yaml
from jsonschema import Draft202012Validator

EVIDENCE_STATES = {
    "VERIFIED_DOCUMENTED","OBSERVED_SAMPLE_DATA","SITE_VERIFIED","INFERRED","ASSUMPTION",
    "UNKNOWN","TBD","NOT_VERIFIED","DISCOVERY_REQUIRED","CONFLICTING"
}
IMPLEMENTATION_STATES = {
    "IDENTIFIED","DESIGNED","IMPLEMENTED","VALIDATED","FROZEN","DEFERRED","BLOCKED","OUT_OF_SCOPE"
}
EXPECTED_FR = {
    *[f"FR-{i:03d}" for i in range(1,11)],
    *[f"FR-{i:03d}" for i in range(20,26)],
    *[f"FR-{i:03d}" for i in range(30,42)],
    *[f"FR-{i:03d}" for i in range(50,58)],
    *[f"FR-{i:03d}" for i in range(60,67)],
    *[f"FR-{i:03d}" for i in range(70,78)],
    *[f"FR-{i:03d}" for i in range(80,86)],
}
EXPECTED_DRK = {f"DR-K{i:02d}" for i in range(1,9)}
EXPECTED_NFR = {f"NFR-{i:03d}" for i in range(1,13)}
EXPECTED_AC = {f"AC-{i:02d}" for i in range(1,11)}
EXPECTED_TBD = {f"TBD-{i:02d}" for i in range(1,9)}
EXPECTED_SRS = EXPECTED_FR | EXPECTED_DRK | EXPECTED_NFR | EXPECTED_AC | EXPECTED_TBD

def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        obj = yaml.safe_load(f)
    if not isinstance(obj, dict):
        raise ValueError(f"{path}: expected YAML object")
    return obj

def load_json(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(obj, dict):
        raise ValueError(f"{path}: expected JSON object")
    return obj

def validate_schema(instance: dict[str, Any], schema: dict[str, Any], label: str) -> list[str]:
    errors = sorted(Draft202012Validator(schema).iter_errors(instance), key=lambda e: list(e.path))
    return [f"{label}: {'/'.join(str(x) for x in e.path)}: {e.message}" for e in errors]

def valid_day(day: str) -> bool:
    m = re.fullmatch(r"DAY_(\d{2})", day or "")
    return bool(m and 1 <= int(m.group(1)) <= 90)

def scan_raw_patient_files(root: Path) -> list[str]:
    suspicious=[]
    binary_signal_ext={".mat",".c3d",".edf",".bdf",".h5",".hdf5",".parquet",".npy",".npz"}
    skip_dirs={".venv","env",".git","node_modules","raw","datasets","experiments","fixtures"}
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if p.name == "day5-preprocess-golden.npz":
            continue
        if any(d in p.relative_to(root).parts for d in skip_dirs):
            continue
        rel=p.relative_to(root).as_posix().lower()
        if p.suffix.lower() in binary_signal_ext:
            suspicious.append(rel)
        if any(tok in rel for tok in ("raw_patient","patient_signal","subject_signal","mr4_treadmill_running")):
            suspicious.append(rel)
    return sorted(set(suspicious))

def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    ap.add_argument("--tests-passed", action="store_true")
    args=ap.parse_args()
    root=args.repo_root.resolve()
    reg_path=root/"data-platform/contracts/requirement-registry.v0.1.yaml"
    dec_path=root/"docs/00-executive/decisions/motionlab-rebaseline-decision-ledger.v0.1.yaml"
    oq_path=root/"docs/01-product/motionlab-rebaseline/open-questions-register.v0.1.yaml"
    hierarchy_path=root/"docs/03-architecture/traceability/source-of-truth-hierarchy.v0.1.yaml"
    schemas=root/"packages/common-schemas/json"
    report_path=root/"qa-validation/evidence/day01-validation-report.json"
    failures: list[str]=[]

    try:
        reg=load_yaml(reg_path); dec=load_yaml(dec_path); oq=load_yaml(oq_path); hierarchy=load_yaml(hierarchy_path)
        req_schema=load_json(schemas/"requirement-registry.schema.json")
        dec_schema=load_json(schemas/"decision-record.schema.json")
        oq_schema=load_json(schemas/"open-question.schema.json")
        for schema,name in [(req_schema,"requirement schema"),(dec_schema,"decision schema"),(oq_schema,"open-question schema")]:
            try: Draft202012Validator.check_schema(schema)
            except Exception as exc: failures.append(f"{name} invalid: {exc}")
        failures += validate_schema(reg,req_schema,"requirement registry")
        failures += validate_schema(dec,dec_schema,"decision ledger")
        failures += validate_schema(oq,oq_schema,"open-question register")
    except Exception as exc:
        print(f"[FATAL] parse/schema setup failed: {exc}", file=sys.stderr)
        return 2

    reqs=reg.get("requirements",[])
    ids=[r.get("requirement_id") for r in reqs]
    counts=Counter(ids)
    duplicates=sorted(k for k,v in counts.items() if v>1)
    if duplicates: failures.append(f"duplicate requirement IDs: {duplicates}")

    srs_ids={r["requirement_id"] for r in reqs if r.get("source",{}).get("document")=="SRS_MotionLab_Data_Intelligence_v0.1"}
    missing=sorted(EXPECTED_SRS-srs_ids)
    unexpected=sorted(srs_ids-EXPECTED_SRS)
    if missing: failures.append(f"missing required SRS IDs: {missing}")
    if unexpected: failures.append(f"unexpected SRS IDs: {unexpected}")

    invalid_ev=[]; invalid_impl=[]; missing_source=[]; missing_day=[]; invalid_day=[]; missing_verification=[]
    silent_assumptions=[]; silent_thresholds=[]
    for r in reqs:
        rid=r.get("requirement_id","?")
        ev=r.get("evidence",{}).get("status")
        impl=r.get("implementation",{}).get("state")
        if ev not in EVIDENCE_STATES: invalid_ev.append((rid,ev))
        if impl not in IMPLEMENTATION_STATES: invalid_impl.append((rid,impl))
        src=r.get("source",{})
        if not src.get("document") or not src.get("section"): missing_source.append(rid)
        days=r.get("roadmap",{}).get("planned_days") or []
        if not days and impl not in {"DEFERRED","OUT_OF_SCOPE"}: missing_day.append(rid)
        for d in days:
            if not valid_day(d): invalid_day.append((rid,d))
        if not (r.get("verification",{}).get("methods") or []): missing_verification.append(rid)
        if ev=="ASSUMPTION" and not (r.get("notes") or []): silent_assumptions.append(rid)
        if r.get("requirement_type")=="KPI_FRAMEWORK" and r.get("clinical_threshold_status")=="NOT_APPLICABLE":
            silent_thresholds.append(rid)
        if rid=="FR-064" and r.get("clinical_threshold_status")!="NOT_VERIFIED":
            silent_thresholds.append(rid)
    for label,items in [
        ("invalid evidence states",invalid_ev),("invalid implementation states",invalid_impl),
        ("missing source",missing_source),("missing planned day",missing_day),
        ("invalid roadmap day",invalid_day),("missing verification method",missing_verification),
        ("silent assumptions",silent_assumptions),("silent clinical thresholds",silent_thresholds)]:
        if items: failures.append(f"{label}: {items}")

    # Decisions
    dids=[d.get("decision_id") for d in dec.get("decisions",[])]
    ddups=sorted(k for k,v in Counter(dids).items() if v>1)
    if ddups: failures.append(f"duplicate decision IDs: {ddups}")
    source_ids={s.get("source_id") for s in hierarchy.get("sources",[])}
    invalid_dec_sources=[]
    for d in dec.get("decisions",[]):
        for s in d.get("source",[]):
            if s not in source_ids: invalid_dec_sources.append((d.get("decision_id"),s))
    if invalid_dec_sources: failures.append(f"decision sources not in source hierarchy: {invalid_dec_sources}")

    # Open questions
    qids=[q.get("question_id") for q in oq.get("questions",[])]
    qdups=sorted(k for k,v in Counter(qids).items() if v>1)
    if qdups: failures.append(f"duplicate open-question IDs: {qdups}")
    bad_q_days=[(q.get("question_id"),q.get("target_day")) for q in oq.get("questions",[]) if not valid_day(q.get("target_day",""))]
    if bad_q_days: failures.append(f"open questions invalid target day: {bad_q_days}")

    # Safety gates derived from source-backed registry/decisions
    req_by_id={r["requirement_id"]:r for r in reqs}
    mfcv=req_by_id.get("TBD-08",{}).get("evidence",{}).get("status")
    fr064=req_by_id.get("FR-064",{})
    if mfcv!="NOT_VERIFIED": failures.append(f"MFCV site status must remain NOT_VERIFIED, got {mfcv}")
    if "optional" not in fr064.get("requirement_text","").lower():
        failures.append("FR-064 no longer states MFCV optional capability")
    drk_states=[req_by_id.get(x,{}).get("evidence",{}).get("status") for x in sorted(EXPECTED_DRK)]
    knee_authorized=not all(x=="DISCOVERY_REQUIRED" for x in drk_states)
    if knee_authorized: failures.append("Knee/ACL discovery gate is not intact")
    d06=next((d for d in dec.get("decisions",[]) if d.get("decision_id")=="D06"),None)
    if not d06 or "Never auto-diagnose" not in d06.get("decision",""):
        failures.append("autonomous diagnosis/treatment/finalization prohibition missing")

    raw_files=scan_raw_patient_files(root)
    if raw_files: failures.append(f"raw patient/signal artifacts found: {raw_files}")

    # Traceability duplicate row key
    trace=root/"docs/03-architecture/traceability/requirements-traceability-baseline.v0.1.csv"
    row_keys=[]
    with trace.open("r",encoding="utf-8",newline="") as f:
        for row in csv.DictReader(f): row_keys.append(row["row_key"])
    trace_dups=sorted(k for k,v in Counter(row_keys).items() if v>1)
    if trace_dups: failures.append(f"traceability duplicate row keys: {trace_dups}")

    tests_passed=bool(args.tests_passed) and not failures
    status="GO_FOR_DAY_02" if tests_passed else ("READY_WITH_LIMITATIONS" if not failures else "BLOCKED_WITH_EVIDENCE")
    report={
      "day":"DAY01","task":"Requirements Re-baseline & Decision Ledger",
      "requirement_registry_valid":not any("requirement registry" in x or "requirement schema" in x for x in failures),
      "registry_item_count":len(reqs),
      "srs_coverage":{
        "FR":{"expected":len(EXPECTED_FR),"found":len(EXPECTED_FR & srs_ids),"missing":sorted(EXPECTED_FR-srs_ids)},
        "DR-K":{"expected":len(EXPECTED_DRK),"found":len(EXPECTED_DRK & srs_ids),"missing":sorted(EXPECTED_DRK-srs_ids)},
        "NFR":{"expected":len(EXPECTED_NFR),"found":len(EXPECTED_NFR & srs_ids),"missing":sorted(EXPECTED_NFR-srs_ids)},
        "AC":{"expected":len(EXPECTED_AC),"found":len(EXPECTED_AC & srs_ids),"missing":sorted(EXPECTED_AC-srs_ids)},
        "TBD":{"expected":len(EXPECTED_TBD),"found":len(EXPECTED_TBD & srs_ids),"missing":sorted(EXPECTED_TBD-srs_ids)}
      },
      "duplicate_requirement_ids":len(duplicates),"missing_required_requirements":missing,
      "unexpected_srs_requirements":unexpected,
      "invalid_evidence_states":[{"requirement_id":a,"value":b} for a,b in invalid_ev],
      "invalid_implementation_states":[{"requirement_id":a,"value":b} for a,b in invalid_impl],
      "silent_assumption_count":len(silent_assumptions),
      "silent_clinical_threshold_count":len(set(silent_thresholds)),
      "decision_count":len(dids),"open_question_count":len(qids),
      "mfcv_status":mfcv,"knee_algorithm_authorized":knee_authorized,
      "training_executed":False,"real_patient_data_read":False,
      "raw_patient_files_in_pack":len(raw_files),
      "tests_passed":tests_passed,"validation_failures":failures,
      "day_status":status
    }
    report_path.parent.mkdir(parents=True,exist_ok=True)
    report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    if failures:
        for item in failures: print(f"[FAIL] {item}",file=sys.stderr)
        return 1
    print(f"[PASS] registry={len(reqs)}; SRS={len(srs_ids)}/{len(EXPECTED_SRS)}; decisions={len(dids)}; open_questions={len(qids)}")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
