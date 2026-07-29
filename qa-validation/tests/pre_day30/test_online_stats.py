import numpy as np

from streaming_signal_eda import OnlineStats


def test_online_stats_matches_numpy():
    x = np.array([1.0, 2.0, 3.0, 4.0, np.nan])
    s = OnlineStats()
    s.update(x[:2])
    s.update(x[2:])
    out = s.finalize()
    finite = x[np.isfinite(x)]
    assert out['sample_count'] == 5
    assert out['finite_count'] == 4
    assert np.isclose(out['mean'], finite.mean())
    assert np.isclose(out['std'], finite.std(ddof=1))
    assert np.isclose(out['rms'], np.sqrt(np.mean(finite ** 2)))
    assert np.isclose(out['mav'], np.mean(np.abs(finite)))
