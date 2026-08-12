from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
APPLICATION = ROOT / "services/quality-gate-service/src/application"
sys.path.insert(0, str(APPLICATION))

from normalization_eligibility import (  # noqa: E402
    NormalizationMethod,
    NormalizationReference,
    NormalizationRequest,
    ReferenceType,
    evaluate_normalization_eligibility,
)


REFERENCE_HASH = "b" * 64


def request(**overrides):
    values = {
        "source_window_id": "w",
        "method": NormalizationMethod.MVC_PERCENT,
        "protocol_id": "p1",
        "domain_id": "d1",
        "partition": "benchmark-development",
        "units": "uV",
        "distribution_support_status": "SUPPORTED",
    }
    values.update(overrides)
    return NormalizationRequest(**values)


def main():
    reference = NormalizationReference(
        "mvc-01",
        ReferenceType.MVC,
        REFERENCE_HASH,
        "1.0.0",
        "p1",
        "d1",
        "reference-development",
        "uV",
    )
    cases = {
        "eligible": evaluate_normalization_eligibility(
            request(),
            [reference],
        ).to_dict(),
        "missing": evaluate_normalization_eligibility(
            request(),
            [],
        ).to_dict(),
        "domain_mismatch": evaluate_normalization_eligibility(
            request(domain_id="d2"),
            [reference],
        ).to_dict(),
        "locked": evaluate_normalization_eligibility(
            request(partition="benchmark-locked"),
            [reference],
        ).to_dict(),
    }
    passed = (
        cases["eligible"]["status"] == "ELIGIBLE"
        and cases["missing"]["metric_value"] is None
        and cases["locked"]["status"] == "BLOCKED"
    )
    output = {
        "cases": cases,
        "status": "PASS" if passed else "FAIL",
    }
    evidence_path = (
        ROOT
        / "qa-validation/evidence/day44-normalization-eligibility-evidence.json"
    )
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text(json.dumps(output, indent=2) + "\n")
    summary = {
        "status": output["status"],
        "case_statuses": {
            key: value["status"]
            for key, value in cases.items()
        },
    }
    print(json.dumps(summary, sort_keys=True))
    if not passed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
