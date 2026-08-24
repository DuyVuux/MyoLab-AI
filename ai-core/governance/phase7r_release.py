from __future__ import annotations

from dataclasses import dataclass, asdict
from hashlib import sha256
from pathlib import Path
import json
import re
from typing import Iterable

ALLOWED_FINAL = {"PORTFOLIO_RESEARCH_READY", "READY_WITH_LIMITATIONS", "BLOCKED_WITH_EVIDENCE"}
FORBIDDEN_IDENTITY = re.compile(r"day[\-_ ]?\d+|^d[0-9]+[\-_.]", re.IGNORECASE)
SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{12,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]
UNSUPPORTED_CLAIMS = [
    re.compile(r"\bclinically validated\b", re.I),
    re.compile(r"\bvalidated at vinmec\b", re.I),
    re.compile(r"\bdeployed at vinmec\b", re.I),
    re.compile(r"\bhospital[- ]ready\b", re.I),
    re.compile(r"\bclinical predictor\b", re.I),
    re.compile(r"\bpathology detector\b", re.I),
]
NEGATION_MARKERS = ("not ", "not_", "no ", "never ", "do not ", "không ", "cấm ", "forbidden")


@dataclass(frozen=True)
class Check:
    name: str
    status: str
    detail: str


@dataclass(frozen=True)
class Phase7Entry:
    allowed: bool
    checks: tuple[Check, ...]

    def to_dict(self) -> dict:
        return {"allowed": self.allowed, "checks": [asdict(c) for c in self.checks]}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def _json(path: Path) -> dict:
    try:
        return json.loads(_read(path))
    except Exception:
        return {}


def sha256_file(path: Path) -> str:
    h = sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def evaluate_phase7_entry(repo: Path) -> Phase7Entry:
    milestone = repo / "docs/00-executive/milestones/m6-r-research-ml.md"
    gate = repo / "docs/00-executive/gates/gate-f-r-research-ml-decision.md"
    leak = repo / "qa-validation/evidence/phase6r-leakage-audit.json"
    claims = repo / "qa-validation/evidence/phase6r-claim-audit-contextual.json"
    branch = repo / "qa-validation/evidence/phase6r-branch-decision.json"
    handoff = repo / "ai-core/research/phase6r/governance/phase6r-to-locked-validation-handoff.yaml"

    milestone_text = _read(milestone)
    gate_text = _read(gate)
    leak_obj = _json(leak)
    claim_obj = _json(claims)
    branch_obj = _json(branch)
    handoff_text = _read(handoff)

    checks = []
    checks.append(Check("m6_r", "PASS" if "RESEARCH_ML_NOT_JUSTIFIED" in milestone_text else "FAIL", str(milestone)))
    checks.append(Check("gate_f_r", "PASS" if "RESEARCH_ML_NOT_JUSTIFIED" in gate_text else "FAIL", str(gate)))

    leak_status = str(leak_obj.get("status") or leak_obj.get("overall_status") or "").upper()
    checks.append(Check("phase6r_leakage", "PASS" if leak_status == "PASS" else "FAIL", leak_status or "missing"))

    unsupported_count = claim_obj.get("blocking_violations")
    if unsupported_count is None:
        unsupported_count = len(claim_obj.get("violations", [])) if isinstance(claim_obj.get("violations"), list) else 0
    claim_status = str(claim_obj.get("status") or claim_obj.get("overall_status") or "").upper()
    claim_ok = claim_status == "PASS" or unsupported_count == 0
    checks.append(Check("phase6r_claims", "PASS" if claim_ok else "FAIL", f"status={claim_status or 'unknown'} blocking={unsupported_count}"))

    branch_status = str(branch_obj.get("m6_r") or branch_obj.get("milestone") or branch_obj.get("final_status") or "")
    if not branch_status and "RESEARCH_ML_NOT_JUSTIFIED" in json.dumps(branch_obj):
        branch_status = "RESEARCH_ML_NOT_JUSTIFIED"
    checks.append(Check("phase6r_branch", "PASS" if branch_status == "RESEARCH_ML_NOT_JUSTIFIED" else "FAIL", branch_status or "missing"))

    upper_handoff = handoff_text.upper()
    ml_off = any(token in upper_handoff for token in [
        "ML_DEFAULT: OFF",
        "CORE_ML_DEFAULT: OFF",
        "CORE ML DEFAULT: OFF",
        "ML_ENABLED: FALSE",
        "DEFAULT_ML_OFF_STATUS: PASS",
        "DEFAULT_ML_OFF_STATUS: OFF",
        "MODEL_INCLUSION_STATUS: EXCLUDED",
        "MODEL_INCLUSION_STATUS: NO",
    ])
    checks.append(Check("ml_default_off", "PASS" if ml_off else "FAIL", str(handoff)))

    required_exist = all(p.exists() for p in (milestone, gate, leak, claims, branch, handoff))
    checks.append(Check("required_phase6r_artifacts", "PASS" if required_exist else "FAIL", "all required paths exist" if required_exist else "one or more required paths missing"))

    return Phase7Entry(all(c.status == "PASS" for c in checks), tuple(checks))


def freeze_manifest(repo: Path, paths: Iterable[Path]) -> dict:
    rows = []
    for path in sorted({p.resolve() for p in paths}):
        try:
            rel = path.relative_to(repo.resolve())
        except ValueError:
            raise ValueError(f"freeze path outside repo: {path}")
        if not path.is_file():
            raise ValueError(f"freeze path is not a file: {rel}")
        rel_s = rel.as_posix()
        if any(x in rel_s for x in ("/.git/", "/.venv/", "__pycache__", "node_modules/")):
            raise ValueError(f"forbidden freeze path: {rel_s}")
        rows.append({"path": rel_s, "sha256": sha256_file(path), "bytes": path.stat().st_size})
    if not rows:
        raise ValueError("locked evaluation freeze set cannot be empty")
    payload = {"contract": "LockedEvaluationFreeze v1.0", "items": rows}
    payload["lock_sha256"] = sha256(json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return payload


def verify_manifest(repo: Path, payload: dict) -> list[Check]:
    checks = []
    for row in payload.get("items", []):
        path = repo / row["path"]
        if not path.is_file():
            checks.append(Check(row["path"], "FAIL", "missing"))
        else:
            actual = sha256_file(path)
            checks.append(Check(row["path"], "PASS" if actual == row["sha256"] else "FAIL", actual))
    return checks


def identity_audit(paths: Iterable[Path]) -> list[str]:
    bad = []
    for p in paths:
        for part in p.parts:
            if FORBIDDEN_IDENTITY.search(part):
                bad.append(str(p))
                break
    return sorted(set(bad))


def claim_audit(paths: Iterable[Path]) -> list[dict]:
    findings = []
    for p in paths:
        if p.suffix.lower() not in {".md", ".txt", ".py", ".yaml", ".yml", ".json", ".sh"}:
            continue
        text = _read(p)
        lines = text.splitlines()
        for line_no, line in enumerate(lines, 1):
            lower = line.lower()
            for pat in UNSUPPORTED_CLAIMS:
                if not pat.search(line):
                    continue
                window = " ".join(lines[max(0, line_no-3): min(len(lines), line_no+2)]).lower()
                negated = any(marker in lower or marker in window for marker in NEGATION_MARKERS)
                policy_context = any(token in window for token in ("claim boundary", "forbidden", "unsupported", "do not claim", "không được", "audit", "pattern"))
                if not (negated or policy_context):
                    findings.append({"path": str(p), "line": line_no, "text": line.strip(), "pattern": pat.pattern})
    return findings


def secret_audit(paths: Iterable[Path]) -> list[dict]:
    findings = []
    for p in paths:
        if p.suffix.lower() not in {".md", ".txt", ".py", ".yaml", ".yml", ".json", ".sh", ".env"}:
            continue
        text = _read(p)
        for i, line in enumerate(text.splitlines(), 1):
            for pat in SECRET_PATTERNS:
                if pat.search(line):
                    findings.append({"path": str(p), "line": i, "pattern": pat.pattern})
    return findings


def decide_final_status(critical_pass: bool, noncritical_limitations: list[str]) -> str:
    if not critical_pass:
        return "BLOCKED_WITH_EVIDENCE"
    if noncritical_limitations:
        return "READY_WITH_LIMITATIONS"
    return "PORTFOLIO_RESEARCH_READY"
