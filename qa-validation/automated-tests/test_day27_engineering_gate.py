from __future__ import annotations
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ai-core"))

from data.day27.engineering_gate import build_engineering_gate
from data.day27.group_split import build_subject_split


def _inputs():
    rows = [{"subject_id":f"S{i:02d}"} for i in range(12)]
    return {
      "sourceVerification":{"status":"VERIFIED"},
      "retrievalReceipt":{"sha256":"a"*64,"licenseAccepted":True},
      "archiveInventory":{"safeToExtract":True},
      "adapterProfile":{"verificationStatus":"VERIFIED","signal":{"samplingRateHz":1000,"sourceUnit":"uV","channels":[1,2,3,4]}},
      "labelMappingReport":{"status":"VERIFIED"},
      "canonicalSmokeReport":{"status":"PASS"},
      "groupSplit":build_subject_split(rows,dataset_id="FIXTURE"),
      "experimentEligibility":{"status":"MAPPED"},
      "trainingExecutionAllowed":False,
      "motionLabTransferVerified":False,
      "clinicalUseAllowed":False,
    }


def test_gate_can_pass_but_training_stays_false():
    report = build_engineering_gate(_inputs())
    assert report["status"] == "GO_FOR_DAY28_EDA"
    assert report["publicBaselineTrainingEligible"] is True
    assert report["trainingExecutionAllowed"] is False


def test_gate_fails_if_test_opened():
    inputs = _inputs(); inputs["groupSplit"]["testOpened"] = True
    report = build_engineering_gate(inputs)
    assert report["status"] == "BLOCKED_SOURCE_OR_SCHEMA"
