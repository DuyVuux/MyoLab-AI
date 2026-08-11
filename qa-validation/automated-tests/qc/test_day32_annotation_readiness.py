from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import jsonschema
import pytest
import yaml


ROOT = Path(__file__).resolve().parents[3]


def _load_module(name: str, rel: str):
    path = ROOT / rel
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


semantics = _load_module(
    "day32_annotation_semantics_test",
    "qa-validation/lib/day32_annotation_semantics.py",
)


@pytest.fixture(scope="module")
def contract():
    return yaml.safe_load(
        (ROOT / "clinical/labels/qc-annotation-schema.v0.2-research.yaml").read_text()
    )


@pytest.fixture(scope="module")
def acquisition():
    return yaml.safe_load(
        (ROOT / "clinical/labels/annotation-acquisition-policy.v0.2-research.yaml").read_text()
    )


@pytest.fixture(scope="module")
def schema():
    return json.loads(
        (ROOT / "packages/common-schemas/json/qc-annotation-item.research.v0.2.schema.json")
        .read_text()
    )


@pytest.fixture(scope="module")
def validator(schema):
    return jsonschema.Draft202012Validator(schema)


@pytest.mark.parametrize(
    "rel",
    [
        "clinical/labels/qc-annotation-protocol.v0.2-research.md",
        "clinical/labels/qc-annotation-schema.v0.2-research.yaml",
        "clinical/review-templates/qc-adjudication-policy.v0.2-research.md",
        "clinical/labels/annotation-acquisition-policy.v0.2-research.yaml",
        "clinical/labels/annotation-budget-policy.v0.2-research.md",
        "qa-validation/evidence/day32-data-readiness.template.yaml",
    ],
)
def test_mandatory_outputs_exist(rel):
    assert (ROOT / rel).is_file()


def test_json_schema_is_draft_2020_12(schema):
    assert schema["$schema"].endswith("draft/2020-12/schema")
    jsonschema.Draft202012Validator.check_schema(schema)


def test_evidence_ladder_exact(contract):
    assert [x["id"] for x in contract["evidence_tiers"]] == [
        "SYNTHETIC_KNOWN_TRUTH",
        "WEAK_LABEL_CANDIDATE",
        "EXPERT_ANNOTATION",
        "ADJUDICATED_REFERENCE",
    ]


def test_automatic_promotion_forbidden(contract):
    assert contract["automatic_promotion_forbidden"] is True


def test_random_crop_forbidden(contract, acquisition):
    assert contract["annotation_unit"]["random_crop_forbidden"] is True
    assert acquisition["random_crop_forbidden"] is True
    assert acquisition["selection_unit"] == "QC_WINDOW_WITH_CONTEXT"


def test_binary_artifact_pathology_forbidden(contract):
    assert contract["rubric"]["binary_artifact_vs_pathology_forbidden"] is True
    assert "INSUFFICIENT_EVIDENCE" in contract["rubric"]["artifact_vs_physiology"]
    assert "BOTH_POSSIBLE" in contract["rubric"]["artifact_vs_physiology"]


def test_diagnosis_labels_forbidden(contract):
    assert contract["rubric"]["diagnosis_labels_forbidden"] is True


def test_no_hard_quota(acquisition):
    assert all(x["hard_quota"] is None for x in acquisition["selection_strata"])


@pytest.mark.parametrize(
    "stratum",
    [
        "REPRESENTATIVE_RANDOM",
        "DETECTOR_DISAGREEMENT",
        "DOMAIN_NOVELTY",
        "HIGH_RISK_FALSE_ALLOW",
        "HIGH_WORKFLOW_IMPACT",
        "ARTIFACT_VS_PHYSIOLOGY_AMBIGUITY",
    ],
)
def test_acquisition_strata_present(acquisition, stratum):
    assert stratum in {x["id"] for x in acquisition["selection_strata"]}


@pytest.mark.parametrize(
    "name",
    [
        "valid-synthetic-known-truth.json",
        "valid-weak-label-candidate.json",
        "valid-expert-annotation-schema-fixture.json",
        "valid-adjudicated-reference-schema-fixture.json",
    ],
)
def test_positive_fixtures_validate(validator, name):
    item = json.loads((ROOT / "qa-validation/test-data/day32" / name).read_text())
    validator.validate(item)
    semantics.validate_item_semantics(item)


@pytest.mark.parametrize(
    "name",
    [
        "invalid-random-crop.json",
        "invalid-synthetic-auto-promoted-expert.json",
        "invalid-nonclinical-expert.json",
        "invalid-single-reviewer-adjudication.json",
        "invalid-no-context.json",
        "invalid-weak-ground-truth-claim.json",
        "invalid-probability-confidence.json",
        "invalid-direct-identifier-field.json",
        "invalid-context-bounds.json",
        "invalid-forced-pathology-label.json",
    ],
)
def test_negative_fixtures_rejected_by_schema_or_semantics(validator, name):
    item = json.loads((ROOT / "qa-validation/test-data/day32" / name).read_text())
    schema_rejected = bool(list(validator.iter_errors(item)))
    try:
        semantics.validate_item_semantics(item)
        semantic_rejected = False
    except semantics.AnnotationContractError:
        semantic_rejected = True
    assert schema_rejected or semantic_rejected


@pytest.mark.parametrize(
    "from_tier",
    ["SYNTHETIC_KNOWN_TRUTH", "WEAK_LABEL_CANDIDATE"],
)
def test_machine_or_synthetic_cannot_auto_promote_to_expert(from_tier):
    with pytest.raises(semantics.AnnotationContractError):
        semantics.validate_evidence_transition(
            from_tier,
            "EXPERT_ANNOTATION",
            semantics.TransitionContext(human_review_performed=False),
        )


@pytest.mark.parametrize(
    "from_tier",
    ["SYNTHETIC_KNOWN_TRUTH", "WEAK_LABEL_CANDIDATE"],
)
def test_new_qualified_review_can_create_expert_annotation(from_tier):
    semantics.validate_evidence_transition(
        from_tier,
        "EXPERT_ANNOTATION",
        semantics.TransitionContext(human_review_performed=True),
    )


@pytest.mark.parametrize(
    "refs,performed",
    [
        ((), False),
        (("a",), True),
        (("a", "a"), True),
        (("a", "b"), False),
    ],
)
def test_adjudication_requires_two_independent_refs_and_action(refs, performed):
    with pytest.raises(semantics.AnnotationContractError):
        semantics.validate_evidence_transition(
            "EXPERT_ANNOTATION",
            "ADJUDICATED_REFERENCE",
            semantics.TransitionContext(
                independent_expert_annotation_refs=refs,
                adjudication_performed=performed,
            ),
        )


def test_two_independent_refs_plus_action_can_create_adjudicated_reference():
    semantics.validate_evidence_transition(
        "EXPERT_ANNOTATION",
        "ADJUDICATED_REFERENCE",
        semantics.TransitionContext(
            independent_expert_annotation_refs=("expert-A", "expert-B"),
            adjudication_performed=True,
        ),
    )


@pytest.mark.parametrize(
    "status",
    [
        "RESEARCH_READY",
        "SYNTHETIC_ONLY_READY_WITH_LIMITATIONS",
        "BLOCKED_DATA_GOVERNANCE",
    ],
)
def test_day33_readiness_allowed_statuses(status):
    readiness = yaml.safe_load(
        (ROOT / "qa-validation/evidence/day32-data-readiness.template.yaml").read_text()
    )
    assert status in readiness["allowed_values"]["day33_data_readiness"]


def test_current_reference_readiness_is_synthetic_only():
    readiness = yaml.safe_load(
        (ROOT / "qa-validation/evidence/day32-data-readiness.reference.yaml").read_text()
    )
    assert readiness["day33_data_readiness"] == "SYNTHETIC_ONLY_READY_WITH_LIMITATIONS"
    assert readiness["clinical_claims_allowed"] is False


def test_nonclinical_reviewer_not_expert(contract):
    assert "NON_CLINICAL_REVIEWER" in contract["reviewer_classes"]
    assert "NON_CLINICAL_REVIEWER" not in contract["expert_annotation_allowed_reviewer_classes"]


def test_machine_evidence_hidden_by_default(acquisition):
    assert acquisition["machine_evidence_display"]["default"] == "HIDDEN_UNTIL_INITIAL_JUDGMENT"


def test_active_learning_not_running(acquisition):
    assert acquisition["maturity"] == {
        "selection_engine_running": False,
        "trained_active_learning_model": False,
        "label_model_trained": False,
    }


def test_day30_day31_cannot_be_bypassed(contract):
    boundary = contract["day30_day31_boundaries"]
    assert boundary["annotation_may_override_day30_qc_automatically"] is False
    assert boundary["annotation_may_compute_metric"] is False
    assert boundary["annotation_may_bypass_day31_eligibility"] is False
