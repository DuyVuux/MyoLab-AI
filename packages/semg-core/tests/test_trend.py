import numpy as np
import pytest
from semg_core.trend import TrendFeatureError, fit_linear_trend

def test_exact_linear_series():
    t=np.arange(0.0,60.0,1.0); y=2.0+3.0*t
    m=fit_linear_trend(t,y,minimum_point_count=20,minimum_duration_s=30)
    assert m.slope_per_s==pytest.approx(3.0)
    assert m.slope_per_min==pytest.approx(180.0)
    assert m.intercept==pytest.approx(2.0)
    assert m.r_squared==pytest.approx(1.0)
    assert m.rmse==pytest.approx(0.0,abs=1e-12)

def test_constant_series():
    t=np.arange(0.0,60.0,1.0); y=np.ones_like(t)*10
    m=fit_linear_trend(t,y,minimum_point_count=20,minimum_duration_s=30)
    assert m.slope_per_s==pytest.approx(0.0,abs=1e-15)
    assert m.r_squared==pytest.approx(1.0)
    assert m.percent_change==pytest.approx(0.0)

def test_irregular_time_uses_real_time():
    t=np.array([0.,1.,3.,6.,10.,15.,21.,28.,36.,45.,55.]); y=5+0.5*t
    m=fit_linear_trend(t,y,minimum_point_count=10,minimum_duration_s=30)
    assert m.slope_per_s==pytest.approx(0.5)

def test_zero_reference_yields_null_normalized_change():
    t=np.arange(0.,60.); y=np.linspace(-1,1,60)
    m=fit_linear_trend(t,y,minimum_point_count=20,minimum_duration_s=30,early_fraction=0.01,minimum_reference_abs=10)
    assert m.percent_change is None
    assert m.normalized_slope_percent_per_min is None

def test_non_increasing_time_rejected():
    with pytest.raises(TrendFeatureError): fit_linear_trend([0,1,1,2],[1,2,3,4],minimum_point_count=2,minimum_duration_s=1)

def test_insufficient_duration_rejected():
    with pytest.raises(TrendFeatureError): fit_linear_trend(np.arange(20.),np.arange(20.),minimum_point_count=10,minimum_duration_s=30)
