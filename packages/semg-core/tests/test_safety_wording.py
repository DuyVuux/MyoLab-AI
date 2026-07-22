from semg_core.safety_wording import safe_summary, scan_prohibited_phrases


def test_safe_summaries_and_scanner():
    summary = safe_summary("supported_pattern")
    hits = scan_prohibited_phrases([summary], ["chẩn đoán mỏi cơ", "bắt buộc dừng bài tập"])
    assert hits == ()
    assert scan_prohibited_phrases(["Bắt buộc dừng bài tập"], ["bắt buộc dừng bài tập"])
