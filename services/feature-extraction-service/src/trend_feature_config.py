"""Nạp và kiểm tra trend_features_v0.1.yaml."""
from __future__ import annotations
from collections.abc import Mapping
from pathlib import Path
from typing import Any
import yaml

class TrendFeatureConfigError(ValueError):
    pass

def _mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TrendFeatureConfigError(f"{name} phải là object/map")
    return value

def validate_trend_feature_config(raw: Mapping[str, Any]) -> dict[str, Any]:
    c=dict(_mapping(raw,'trend config'))
    if c.get('schema_version')!='trend-feature-config.v0.1': raise TrendFeatureConfigError('Sai schema_version')
    if c.get('config_id')!='trend_features_v0.1': raise TrendFeatureConfigError('Sai config_id')
    if c.get('clinical_validation_status')!='not_validated': raise TrendFeatureConfigError('Phải not_validated')
    contract=_mapping(c.get('input_contract'),'input_contract')
    expected={
      'require_time_domain_downstream_allowed':True,
      'required_time_domain_config_id':'features_semg_v0.1',
      'required_time_domain_schema_version':'time-domain-feature-extraction-result.v0.1',
      'require_frequency_domain_downstream_allowed':True,
      'required_frequency_domain_config_id':'frequency_features_v0.1',
      'required_frequency_domain_schema_version':'frequency-feature-extraction-result.v0.1',
      'require_same_session_id':True,
      'require_same_preprocess_config_id':'preprocess_v0.1',
      'require_same_window_plan_hash':True,
      'require_same_source_signal_hash':True,
      'required_features':['rms','mav','mdf','mnf'],
      'missing_required_feature_policy':'channel_not_computed',
    }
    for k,v in expected.items():
        if contract.get(k)!=v: raise TrendFeatureConfigError(f'input_contract.{k} phải bằng {v!r}')
    fit=_mapping(c.get('fit'),'fit')
    if fit.get('method')!='ordinary_least_squares': raise TrendFeatureConfigError('method phải OLS')
    if fit.get('independent_variable')!='center_time_s' or fit.get('use_window_index_as_time') is not False: raise TrendFeatureConfigError('Phải dùng center_time_s')
    if int(fit.get('minimum_point_count'))<3: raise TrendFeatureConfigError('minimum_point_count quá thấp')
    if float(fit.get('minimum_duration_s'))<=0: raise TrendFeatureConfigError('minimum_duration_s phải >0')
    early=float(fit.get('early_fraction')); late=float(fit.get('late_fraction'))
    if not (0<early<=0.5 and 0<late<=0.5 and early+late<=1): raise TrendFeatureConfigError('early/late fraction không hợp lệ')
    if fit.get('emit_p_value') is not False or fit.get('emit_confidence_interval') is not False: raise TrendFeatureConfigError('Không được emit inferential stats')
    units=_mapping(c.get('feature_units'),'feature_units')
    if dict(units)!={'rms':'uV','mav':'uV','mdf':'Hz','mnf':'Hz'}: raise TrendFeatureConfigError('feature_units không đúng')
    future=_mapping(c.get('future_stages'),'future_stages')
    for name,item in future.items():
        if _mapping(item,name).get('enabled') is not False: raise TrendFeatureConfigError(f'{name} phải disabled')
    safety=_mapping(c.get('safety'),'safety')
    for k in ('block_if_no_complete_channel','do_not_treat_windows_as_independent_subjects','do_not_emit_inferential_statistics','do_not_interpret_fatigue','do_not_generate_frs','do_not_train_ml','synthetic_data_is_not_clinical_evidence'):
        if safety.get(k) is not True: raise TrendFeatureConfigError(f'safety.{k} phải true')
    return c

def load_trend_feature_config(path: Path|str)->dict[str,Any]:
    p=Path(path)
    try: raw=yaml.safe_load(p.read_text(encoding='utf-8'))
    except (OSError,yaml.YAMLError) as exc: raise TrendFeatureConfigError(f'Không đọc được config: {exc}') from exc
    return validate_trend_feature_config(_mapping(raw,'trend config'))
