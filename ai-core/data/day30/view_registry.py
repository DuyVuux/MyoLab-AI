from __future__ import annotations

from typing import Any


def build_view_registry(common_ontology: dict[str, Any]) -> dict[str, Any]:
    intersection = common_ontology.get("intersection")
    mendeley = common_ontology.get("mendeley_supported")
    grabmyo = common_ontology.get("grabmyo_supported")
    if not isinstance(intersection, list) or not intersection:
        raise ValueError("No verified class intersection")
    if not isinstance(mendeley, list) or not mendeley:
        raise ValueError("No supported Mendeley classes")
    if not isinstance(grabmyo, list) or not grabmyo:
        raise ValueError("No supported GRABMyo classes")
    return {
        "schema_version": "day30-dataset-view-registry.v1",
        "pooled_training_allowed": False,
        "views": [
            {
                "view_id": "mendeley_core4_primary_v1",
                "dataset_ids": ["mendeley-4channel-hand-gesture-v2"],
                "classes": mendeley,
                "channel_policy_id": "mendeley-ch123-primary-v1",
                "role": "primary_source_specific",
                "pooled_training_allowed": False,
            },
            {
                "view_id": "mendeley_core4_ch4_sensitivity_v1",
                "dataset_ids": ["mendeley-4channel-hand-gesture-v2"],
                "classes": mendeley,
                "channel_policy_id": "mendeley-ch1234-sensitivity-v1",
                "role": "sensitivity_only",
                "pooled_training_allowed": False,
            },
            {
                "view_id": "grabmyo_project_subset_native28_v1",
                "dataset_ids": ["grabmyo-v1.1.0"],
                "classes": grabmyo,
                "channel_policy_id": "grabmyo-fw28-primary-v1",
                "role": "primary_source_specific",
                "pooled_training_allowed": False,
            },
            {
                "view_id": "cross_source_intersection_summary_v1",
                "dataset_ids": [
                    "mendeley-4channel-hand-gesture-v2",
                    "grabmyo-v1.1.0",
                ],
                "classes": intersection,
                "channel_policy_id": "channel-summary-v1",
                "role": "contract_and_later_comparator",
                "pooled_training_allowed": False,
            },
        ],
    }

