from copy import deepcopy
from pathlib import Path
import pytest,yaml
from evidence_config import EvidenceConfigError,load_evidence_config,validate_evidence_config
P=Path('services/inference-service/evidence/fatigue_evidence_v0.1.yaml')
def test_load(): assert load_evidence_config(P)['config_id']=='fatigue_evidence_v0.1'
def test_reject_probability():
 r=yaml.safe_load(P.read_text()); b=deepcopy(r); b['aggregation']['output_probability']=True
 with pytest.raises(EvidenceConfigError): validate_evidence_config(b)
def test_reject_clinical_validation():
 r=yaml.safe_load(P.read_text()); b=deepcopy(r); b['clinical_validation_status']='validated'
 with pytest.raises(EvidenceConfigError): validate_evidence_config(b)
