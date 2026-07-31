from day32.aggregation import aggregate_window_labels
from day32.metrics import subject_macro_repetition_macro_f1

def test_repetition_aggregation_and_subject_metric():
    rows = aggregate_window_labels(
        predictions=["a","a","b","b","a","b"],
        repetition_ids=["r1","r1","r2","r2","r3","r3"],
        subject_ids=["s1","s1","s1","s1","s2","s2"],
        true_labels=["a","a","b","b","a","a"],
        class_order=["a","b"],
    )
    result = subject_macro_repetition_macro_f1(rows, ["a","b"])
    assert len(rows) == 3
    assert 0 <= result["subject_macro_repetition_macro_f1"] <= 1
