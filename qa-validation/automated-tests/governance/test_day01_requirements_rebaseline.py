from __future__ import annotations
import csv, hashlib, json
from collections import Counter
from pathlib import Path
import yaml
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[3]
REG=ROOT/"data-platform/contracts/requirement-registry.v0.1.yaml"
DEC=ROOT/"docs/00-executive/decisions/motionlab-rebaseline-decision-ledger.v0.1.yaml"
OQ=ROOT/"docs/01-product/motionlab-rebaseline/open-questions-register.v0.1.yaml"
HIER=ROOT/"docs/03-architecture/traceability/source-of-truth-hierarchy.v0.1.yaml"
TRACE=ROOT/"docs/03-architecture/traceability/requirements-traceability-baseline.v0.1.csv"
MAN=ROOT/"qa-validation/evidence/day01-artifact-manifest.json"
REPORT=ROOT/"qa-validation/evidence/day01-validation-report.json"
SCHEMAS=ROOT/"packages/common-schemas/json"

EV={"VERIFIED_DOCUMENTED","OBSERVED_SAMPLE_DATA","SITE_VERIFIED","INFERRED","ASSUMPTION","UNKNOWN","TBD","NOT_VERIFIED","DISCOVERY_REQUIRED","CONFLICTING"}
IMPL={"IDENTIFIED","DESIGNED","IMPLEMENTED","VALIDATED","FROZEN","DEFERRED","BLOCKED","OUT_OF_SCOPE"}
EXPECTED_FR={*[f"FR-{i:03d}" for i in range(1,11)],*[f"FR-{i:03d}" for i in range(20,26)],*[f"FR-{i:03d}" for i in range(30,42)],*[f"FR-{i:03d}" for i in range(50,58)],*[f"FR-{i:03d}" for i in range(60,67)],*[f"FR-{i:03d}" for i in range(70,78)],*[f"FR-{i:03d}" for i in range(80,86)]}
EXPECTED_DRK={f"DR-K{i:02d}" for i in range(1,9)}
EXPECTED_NFR={f"NFR-{i:03d}" for i in range(1,13)}
EXPECTED_AC={f"AC-{i:02d}" for i in range(1,11)}
EXPECTED_TBD={f"TBD-{i:02d}" for i in range(1,9)}
EXPECTED_SRS=EXPECTED_FR|EXPECTED_DRK|EXPECTED_NFR|EXPECTED_AC|EXPECTED_TBD

def y(path): return yaml.safe_load(path.read_text(encoding="utf-8"))
def j(path): return json.loads(path.read_text(encoding="utf-8"))
def reqs(): return y(REG)["requirements"]
def sha(path: Path) -> str:
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()

def test_required_files_exist():
    required=[
      REG,DEC,OQ,HIER,TRACE,
      SCHEMAS/"requirement-registry.schema.json",SCHEMAS/"decision-record.schema.json",SCHEMAS/"open-question.schema.json",
      ROOT/"clinical/governance/evidence-status-taxonomy.v0.1.yaml",
      ROOT/"docs/00-executive/day01/requirements-rebaseline-summary.v0.1.md",
      ROOT/"docs/01-product/motionlab-rebaseline/product-scope-delta.v0.1.md",
      ROOT/"qa-validation/requirements/day01-acceptance-criteria.md",
      ROOT/"qa-validation/traceability/day01-requirement-test-matrix.csv",
      ROOT/"qa-validation/evidence/day01-source-hash-ledger.json",
      ROOT/"scripts/dev/validate_day01_requirements.py",ROOT/"scripts/dev/check_day01_artifacts.py",ROOT/"scripts/dev/run_day01_checks.sh",MAN,REPORT
    ]
    assert all(p.is_file() for p in required), [str(p) for p in required if not p.is_file()]

def test_yaml_json_parse():
    for p in [REG,DEC,OQ,HIER,ROOT/"clinical/governance/evidence-status-taxonomy.v0.1.yaml"]: assert isinstance(y(p),dict)
    for p in [SCHEMAS/"requirement-registry.schema.json",SCHEMAS/"decision-record.schema.json",SCHEMAS/"open-question.schema.json",
              ROOT/"qa-validation/evidence/day01-source-hash-ledger.json",REPORT,MAN]: assert isinstance(j(p),dict)

def test_json_schemas_are_valid():
    cases=[(REG,"requirement-registry.schema.json"),(DEC,"decision-record.schema.json"),(OQ,"open-question.schema.json")]
    for data_path,schema_name in cases:
        schema=j(SCHEMAS/schema_name)
        Draft202012Validator.check_schema(schema)
        assert not list(Draft202012Validator(schema).iter_errors(y(data_path)))

def test_requirement_ids_unique():
    ids=[r["requirement_id"] for r in reqs()]
    assert len(ids)==len(set(ids))

def test_expected_srs_ids_represented():
    found={r["requirement_id"] for r in reqs() if r["source"]["document"]=="SRS_MotionLab_Data_Intelligence_v0.1"}
    assert found==EXPECTED_SRS, {"missing":sorted(EXPECTED_SRS-found),"unexpected":sorted(found-EXPECTED_SRS)}

def test_every_requirement_has_source():
    assert all(r["source"]["document"] and r["source"]["section"] and r["evidence"]["source_refs"] for r in reqs())

def test_every_requirement_has_evidence_status():
    assert all(r["evidence"]["status"] in EV for r in reqs())

def test_every_requirement_has_implementation_state():
    assert all(r["implementation"]["state"] in IMPL for r in reqs())

def test_roadmap_mapping_or_disposition():
    for r in reqs():
        if r["implementation"]["state"] not in {"DEFERRED","OUT_OF_SCOPE"}:
            assert r["roadmap"]["planned_days"], r["requirement_id"]
            assert r["roadmap"]["target_artifacts"], r["requirement_id"]

def test_decision_ids_unique():
    ids=[d["decision_id"] for d in y(DEC)["decisions"]]
    assert len(ids)==len(set(ids))

def test_decision_sources_exist():
    source_ids={s["source_id"] for s in y(HIER)["sources"]}
    for d in y(DEC)["decisions"]:
        assert set(d["source"])<=source_ids,(d["decision_id"],set(d["source"])-source_ids)

def test_open_questions_have_target_day():
    for q in y(OQ)["questions"]:
        assert q["target_day"].startswith("DAY_")
        n=int(q["target_day"].split("_")[1]); assert 1<=n<=90

def test_no_unknown_evidence_enum():
    assert set(y(REG)["evidence_status_enum"])==EV
    assert all(r["evidence"]["status"] in EV for r in reqs())

def test_no_silent_clinical_threshold():
    for r in reqs():
        if r["requirement_type"]=="KPI_FRAMEWORK":
            assert r["clinical_threshold_status"]=="TBD", r["requirement_id"]
        if r["requirement_id"]=="FR-064":
            assert r["clinical_threshold_status"]=="NOT_VERIFIED"
    kpi1=next(r for r in reqs() if r["requirement_id"]=="PRD-KPI-01")
    assert any("not a committed/site-validated threshold" in x for x in kpi1["evidence"]["limitations"])

def test_mfcv_remains_optional_not_verified():
    by={r["requirement_id"]:r for r in reqs()}
    assert "optional" in by["FR-064"]["requirement_text"].lower()
    assert by["TBD-08"]["evidence"]["status"]=="NOT_VERIFIED"
    oq16=next(q for q in y(OQ)["questions"] if q["question_id"]=="OQ-016")
    assert oq16["evidence_status"]=="NOT_VERIFIED"
    assert "not system failure" in oq16["fallback"].lower()

def test_knee_remains_discovery_gated():
    by={r["requirement_id"]:r for r in reqs()}
    assert all(by[rid]["evidence"]["status"]=="DISCOVERY_REQUIRED" for rid in EXPECTED_DRK)
    d04=next(d for d in y(DEC)["decisions"] if d["decision_id"]=="D04")
    assert "Do not design or implement" in d04["decision"]

def test_no_autonomous_clinical_claim():
    d06=next(d for d in y(DEC)["decisions"] if d["decision_id"]=="D06")
    assert d06["decision"].startswith("Never auto-diagnose")
    by={r["requirement_id"]:r for r in reqs()}
    assert "chưa có clinician approval" in by["FR-076"]["requirement_text"]

def test_no_raw_patient_signal_artifact():
    forbidden={".mat",".c3d",".edf",".bdf",".h5",".hdf5",".npy",".npz",".pt",".pth",".ckpt",".onnx"}
    skip_dirs={".venv","env",".git","node_modules","raw","datasets","experiments","fixtures"}
    bad=[]
    for p in ROOT.rglob("*"):
        if not p.is_file(): continue
        if p.name == "day5-preprocess-golden.npz": continue
        if any(d in p.relative_to(ROOT).parts for d in skip_dirs): continue
        rel=p.relative_to(ROOT).as_posix().lower()
        if p.suffix.lower() in forbidden or "raw_patient" in rel or "patient_signal" in rel:
            bad.append(rel)
    assert not bad,bad

def test_traceability_row_keys_unique():
    with TRACE.open("r",encoding="utf-8",newline="") as f:
        keys=[row["row_key"] for row in csv.DictReader(f)]
    assert len(keys)==len(set(keys))
    assert len(keys)==len(reqs())

def test_artifact_manifest_matches_filesystem():
    manifest=j(MAN)
    exclusions={Path("qa-validation/evidence/day01-artifact-manifest.json"),Path("qa-validation/evidence/day01-validation-report.json")}
    live=[]
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file(): continue
        rel=p.relative_to(ROOT)
        if rel in exclusions: continue
        if any(x in {"__pycache__",".pytest_cache",".venv","env",".git","node_modules","raw","datasets","experiments","fixtures"} for x in rel.parts): continue
        live.append({"path":rel.as_posix(),"size_bytes":p.stat().st_size,"sha256":sha(p)})
    assert manifest["files"]==live
