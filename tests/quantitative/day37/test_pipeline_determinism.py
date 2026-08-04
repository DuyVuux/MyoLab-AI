from day37.repeatability import pair_repeatability


def test_pipeline_determinism():
    # Same inputs should produce exactly the same output dictionary
    res1 = pair_repeatability(1.0, 1.05)
    res2 = pair_repeatability(1.0, 1.05)
    assert res1 == res2
    
    res3 = pair_repeatability(2.0, 2.1)
    assert res3 != res1
