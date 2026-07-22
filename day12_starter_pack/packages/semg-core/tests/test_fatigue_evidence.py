from semg_core.fatigue_evidence import DirectionalThreshold,evaluate_directional_evidence,aggregate_domain_status,overall_pattern_category

def th(direction): return DirectionalThreshold(direction,5,5,0.2)
def test_supporting_decrease():
 a=evaluate_directional_evidence(feature_name='mdf',domain='frequency',percent_change=-10,normalized_slope_percent_per_min=-12,r_squared=.8,threshold=th('decrease')); assert a.support_status=='supporting'
def test_contradicting_decrease():
 a=evaluate_directional_evidence(feature_name='mdf',domain='frequency',percent_change=10,normalized_slope_percent_per_min=12,r_squared=.8,threshold=th('decrease')); assert a.support_status=='contradicting'
def test_low_r2_insufficient():
 a=evaluate_directional_evidence(feature_name='rms',domain='amplitude',percent_change=20,normalized_slope_percent_per_min=20,r_squared=.1,threshold=th('increase')); assert a.support_status=='insufficient'
def test_aggregate_and_overall():
 f=[evaluate_directional_evidence(feature_name=n,domain='frequency',percent_change=-10,normalized_slope_percent_per_min=-10,r_squared=.8,threshold=th('decrease')) for n in ('mdf','mnf')]
 a=[evaluate_directional_evidence(feature_name=n,domain='amplitude',percent_change=10,normalized_slope_percent_per_min=10,r_squared=.8,threshold=th('increase')) for n in ('rms','mav')]
 assert aggregate_domain_status(f)=='supporting'; assert aggregate_domain_status(a)=='supporting'; assert overall_pattern_category(frequency_status='supporting',amplitude_status='supporting')=='multi_domain_change_pattern_observed'
