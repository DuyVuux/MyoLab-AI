from pathlib import Path
import sys
import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / 'packages/semg-core') not in sys.path:
    sys.path.insert(0, str(ROOT / 'packages/semg-core'))

from semg_core.quantitative_metrics import *  # noqa: E402,F401,F403


def test_known_answers():
    assert safe_percent_change(120, 100) == 20
    assert symmetry_ratio_percent(80, 100) == 80
    assert coefficient_of_variation_percent([10, 10, 10]) == 0
    assert co_contraction_index_percent(20, 30) == 80
    assert abs(cosine_similarity([1, 2, 3], [1, 2, 3]) - 1) < 1e-12


def test_not_computable():
    with pytest.raises(MetricNotComputable):
        safe_percent_change(1, 0)
    with pytest.raises(MetricNotComputable):
        coefficient_of_variation_percent([1])
