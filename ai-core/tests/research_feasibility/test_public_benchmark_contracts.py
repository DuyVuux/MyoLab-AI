import sys
import unittest
from pathlib import Path

AI_CORE_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(AI_CORE_ROOT))

from evaluation.public_benchmark_contracts import (  # noqa: E402
    ContractValidationError,
    PublicFeatureWindowRecord,
    ResearchExampleRecord,
    load_m5r_decision_ledger,
)


class PublicBenchmarkContractTests(unittest.TestCase):
    def test_feature_window_contract_keeps_ml_target_out(self):
        row = PublicFeatureWindowRecord(
            dataset_id="GRABMYO_V1_1_0",
            subject_id="grabmyo_subject_01",
            session_id="grabmyo_session_1",
            split="DEVELOPMENT",
            window_id="win_sha256_abc",
            channel_id="F1",
            task="gesture10_trial1",
            start_sample=0,
            end_sample=2048,
            fs_hz=2048.0,
            qc_status="QC_ELIGIBLE",
            qc_reason_codes=(),
            metric_eligible=True,
            rms=1.0e-5,
            mav=8.0e-6,
            mdf_hz=95.0,
            mnf_hz=101.0,
            processing_profile="public-benchmark-processing-v1.2",
            feature_registry_version="public-feature-registry-v1.2",
            source_hash="a" * 64,
        )

        serialized = row.to_dict()

        self.assertEqual(serialized["schema_version"], "PublicFeatureWindowRecord.v1.2")
        self.assertNotIn("target_label", serialized)
        self.assertNotIn("perturbation_type", serialized)
        self.assertNotIn("prediction", serialized)
        self.assertEqual(serialized["split"], "DEVELOPMENT")

    def test_feature_window_requires_source_provenance_and_split(self):
        with self.assertRaisesRegex(ContractValidationError, "split"):
            PublicFeatureWindowRecord(
                dataset_id="HYSER_V2_0_0",
                subject_id="hyser_subject_01",
                session_id="hyser_session_1",
                split="TRAIN",
                window_id="win_sha256_def",
                channel_id="HD001",
                task=None,
                start_sample=0,
                end_sample=2048,
                fs_hz=2048.0,
                qc_status="QC_ELIGIBLE",
                qc_reason_codes=(),
                metric_eligible=True,
                rms=1.0e-5,
                mav=8.0e-6,
                mdf_hz=95.0,
                mnf_hz=101.0,
                processing_profile="public-benchmark-processing-v1.2",
                feature_registry_version="public-feature-registry-v1.2",
                source_hash="b" * 64,
            )

    def test_research_example_preserves_no_injected_semantics(self):
        example = ResearchExampleRecord(
            example_id="ex_sha256_001",
            window_id="win_sha256_abc",
            perturbation_type="NO_INJECTED_CORRUPTION",
            perturbation_parameters={},
            perturbation_seed=260826,
            target_label="NO_INJECTED_CORRUPTION",
            split="DEVELOPMENT",
            group_id="GRABMYO_V1_1_0:grabmyo_subject_01",
            feature_table_version="public-feature-summary-v1.2",
            generator_version="known-truth-perturbation-generator-v1.0",
        )

        self.assertFalse(example.claims_clean_clinical_signal)
        self.assertEqual(example.to_dict()["label_semantics"], "NO_INJECTED_CORRUPTION_IS_NOT_CLEAN_SIGNAL")

    def test_research_example_rejects_clean_signal_target(self):
        with self.assertRaisesRegex(ContractValidationError, "CLEAN_SIGNAL"):
            ResearchExampleRecord(
                example_id="ex_sha256_bad",
                window_id="win_sha256_bad",
                perturbation_type="CLEAN_SIGNAL",
                perturbation_parameters={},
                perturbation_seed=260826,
                target_label="CLEAN_SIGNAL",
                split="DEVELOPMENT",
                group_id="GRABMYO_V1_1_0:grabmyo_subject_01",
                feature_table_version="public-feature-summary-v1.2",
                generator_version="known-truth-perturbation-generator-v1.0",
            )

    def test_decision_ledger_records_b_a_b(self):
        ledger = load_m5r_decision_ledger(REPO_ROOT / "docs/00-executive/remediation/M5-R-remediation-ledger-v1.0.md")

        self.assertEqual(ledger["DEC-M5R-01"], "ENABLE_KNOWN_TRUTH_SYNTHETIC_PERTURBATION_TARGET")
        self.assertEqual(ledger["DEC-M5R-02"], "PUBLIC_BENCHMARK_PRIMARY_EXECUTION_OFFLINE_BATCH")
        self.assertEqual(ledger["DEC-M5R-03"], "CREATE_PUBLIC_FEATURE_WINDOW_CONTRACT_V1_2")


if __name__ == "__main__":
    unittest.main()
