from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class AnnotationContractError(ValueError):
    """Raised when an annotation object violates DAY32 semantic invariants."""


EXPERT_REVIEWER_CLASSES = {"CLINICAL_EXPERT", "BIOMEDICAL_SIGNAL_EXPERT"}


@dataclass(frozen=True)
class TransitionContext:
    human_review_performed: bool = False
    independent_expert_annotation_refs: tuple[str, ...] = ()
    adjudication_performed: bool = False


def validate_evidence_transition(
    from_tier: str,
    to_tier: str,
    context: TransitionContext,
) -> None:
    if from_tier == to_tier:
        return
    if to_tier == "EXPERT_ANNOTATION":
        if not context.human_review_performed:
            raise AnnotationContractError(
                "EXPERT_ANNOTATION requires a new qualified human review; "
                "automatic promotion forbidden"
            )
        return
    if to_tier == "ADJUDICATED_REFERENCE":
        refs = tuple(dict.fromkeys(context.independent_expert_annotation_refs))
        if len(refs) < 2 or not context.adjudication_performed:
            raise AnnotationContractError(
                "ADJUDICATED_REFERENCE requires >=2 independent expert annotations "
                "and adjudication"
            )
        return
    if from_tier in {"EXPERT_ANNOTATION", "ADJUDICATED_REFERENCE"} and to_tier in {
        "SYNTHETIC_KNOWN_TRUTH",
        "WEAK_LABEL_CANDIDATE",
    }:
        raise AnnotationContractError(
            "evidence authority cannot be silently downgraded by mutation"
        )


def validate_item_semantics(item: dict[str, Any]) -> None:
    if item.get("annotation_unit_type") != "QC_WINDOW_WITH_CONTEXT":
        raise AnnotationContractError("random/contextless crop forbidden")

    wc = item["window_context"]
    if not (
        wc["context_start_sample"] <= wc["start_sample"]
        < wc["end_sample_exclusive"] <= wc["context_end_sample_exclusive"]
    ):
        raise AnnotationContractError("WindowIdentity context/sample bounds are inconsistent")

    if item["presentation"]["waveform_context_visible"] is not True:
        raise AnnotationContractError("waveform context must be visible for annotation")
    if item["presentation"]["direct_identifiers_present"] is not False:
        raise AnnotationContractError("direct identifiers are forbidden")
    if item["presentation"]["diagnostic_suggestion_present"] is not False:
        raise AnnotationContractError("diagnostic suggestion is forbidden")

    tier = item["evidence_tier"]
    human = item.get("human_annotation")
    adjudication = item.get("adjudication")
    synthetic = item.get("synthetic_truth")

    if tier == "SYNTHETIC_KNOWN_TRUTH":
        if synthetic is None or human is not None or adjudication is not None:
            raise AnnotationContractError("synthetic truth cannot masquerade as human evidence")
        if synthetic.get("clinical_truth_claim") is not False:
            raise AnnotationContractError("synthetic truth cannot claim clinical truth")

    if tier == "WEAK_LABEL_CANDIDATE":
        if not item.get("machine_evidence") or human is not None or adjudication is not None:
            raise AnnotationContractError("weak-label tier must remain machine candidate evidence")

    if tier == "EXPERT_ANNOTATION":
        if human is None or human.get("reviewer_class") not in EXPERT_REVIEWER_CLASSES:
            raise AnnotationContractError("expert tier requires a qualified expert reviewer")
        if adjudication is not None:
            raise AnnotationContractError("single expert annotation is not adjudication")

    if tier == "ADJUDICATED_REFERENCE":
        if adjudication is None:
            raise AnnotationContractError("adjudicated tier requires adjudication record")
        refs = adjudication.get("expert_annotation_refs", [])
        if len(set(refs)) < 2:
            raise AnnotationContractError("adjudication requires >=2 independent expert refs")

    for evidence in item.get("machine_evidence", []):
        if evidence.get("ground_truth_claim") is not False:
            raise AnnotationContractError("weak label cannot claim ground truth")
        if evidence.get("expert_label_claim") is not False:
            raise AnnotationContractError("weak label cannot claim expert annotation")
        if wc["window_id"] not in evidence.get("evidence_refs", []):
            raise AnnotationContractError("machine evidence must reference DAY22 window_id")

    if item.get("claim_scope") != "RESEARCH_ONLY":
        raise AnnotationContractError("DAY32 package supports research-only claim scope")
