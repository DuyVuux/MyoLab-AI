from copy import deepcopy
from pathlib import Path
import pytest,yaml
from trend_feature_config import TrendFeatureConfigError,load_trend_feature_config,validate_trend_feature_config
P=Path('services/feature-extraction-service/configs/trend_features_v0.1.yaml')
def test_load(): assert load_trend_feature_config(P)['config_id']=='trend_features_v0.1'
def test_reject_window_index_time():
    raw=yaml.safe_load(P.read_text()); bad=deepcopy(raw); bad['fit']['use_window_index_as_time']=True
    with pytest.raises(TrendFeatureConfigError): validate_trend_feature_config(bad)
def test_reject_pvalue():
    raw=yaml.safe_load(P.read_text()); bad=deepcopy(raw); bad['fit']['emit_p_value']=True
    with pytest.raises(TrendFeatureConfigError): validate_trend_feature_config(bad)
