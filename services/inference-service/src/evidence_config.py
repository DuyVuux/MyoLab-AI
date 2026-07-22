"""Nạp và kiểm tra fatigue_evidence_v0.1.yaml."""
from __future__ import annotations
from collections.abc import Mapping
from pathlib import Path
from typing import Any
import yaml
class EvidenceConfigError(ValueError): pass
def _m(v,n):
 if not isinstance(v,Mapping): raise EvidenceConfigError(f'{n} phải map')
 return v
def validate_evidence_config(raw:Mapping[str,Any])->dict[str,Any]:
 c=dict(_m(raw,'config'))
 if c.get('schema_version')!='fatigue-evidence-config.v0.1' or c.get('config_id')!='fatigue_evidence_v0.1': raise EvidenceConfigError('Sai schema/config id')
 if c.get('clinical_validation_status')!='not_validated': raise EvidenceConfigError('Phải not_validated')
 i=_m(c.get('input_contract'),'input_contract')
 exp={'require_trend_downstream_allowed':True,'required_trend_config_id':'trend_features_v0.1','required_trend_schema_version':'trend-feature-extraction-result.v0.1','required_features':['rms','mav','mdf','mnf'],'require_complete_channel':True,'upstream_block_policy':'abstain'}
 for k,v in exp.items():
  if i.get(k)!=v: raise EvidenceConfigError(f'input_contract.{k} phải {v!r}')
 q=_m(c.get('trend_quality'),'trend_quality')
 if not (0<=float(q.get('minimum_r_squared'))<=1): raise EvidenceConfigError('R2 threshold lỗi')
 if int(q.get('minimum_point_count'))<3 or float(q.get('minimum_duration_s'))<=0: raise EvidenceConfigError('quality threshold lỗi')
 th=_m(c.get('provisional_thresholds'),'provisional_thresholds')
 expected={'rms':('amplitude','increase'),'mav':('amplitude','increase'),'mdf':('frequency','decrease'),'mnf':('frequency','decrease')}
 for name,(domain,direction) in expected.items():
  x=_m(th.get(name),name)
  if x.get('domain')!=domain or x.get('expected_direction')!=direction: raise EvidenceConfigError(f'{name} direction/domain lỗi')
  if float(x.get('minimum_percent_change'))<=0 or float(x.get('minimum_normalized_slope_percent_per_min'))<=0: raise EvidenceConfigError(f'{name} threshold phải >0')
 a=_m(c.get('aggregation'),'aggregation')
 if a.get('output_probability') is not False or a.get('output_score') is not False or a.get('output_fatigue_status') is not False: raise EvidenceConfigError('Evidence engine không được output inference')
 future=_m(c.get('future_stages'),'future_stages')
 for n,x in future.items():
  if _m(x,n).get('enabled') is not False: raise EvidenceConfigError(f'{n} phải disabled')
 s=_m(c.get('safety'),'safety')
 for k in ('abstention_is_first_class_output','do_not_output_fatigue_detected','do_not_output_no_fatigue','do_not_output_probability','do_not_generate_frs','do_not_generate_clinical_recommendation','require_human_review_for_future_clinical_workflow','synthetic_data_is_not_clinical_evidence'):
  if s.get(k) is not True: raise EvidenceConfigError(f'safety.{k} phải true')
 return c
def load_evidence_config(path:Path|str)->dict[str,Any]:
 p=Path(path)
 try: raw=yaml.safe_load(p.read_text(encoding='utf-8'))
 except (OSError,yaml.YAMLError) as e: raise EvidenceConfigError(str(e)) from e
 return validate_evidence_config(_m(raw,'config'))
