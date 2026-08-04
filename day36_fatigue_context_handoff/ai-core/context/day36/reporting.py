def summary(state):
    mapping={
      "FATIGUE_CONTEXT_SUPPORTED":"Nhiều nguồn bằng chứng phù hợp với bối cảnh có thể ảnh hưởng hiệu năng; cần human review.",
      "POSSIBLE_FATIGUE_CONTEXT":"Có bằng chứng hạn chế về bối cảnh có thể ảnh hưởng hiệu năng.",
      "CONFLICTING_EVIDENCE":"Các nguồn bằng chứng không nhất quán; hệ thống không đưa kết luận.",
      "INSUFFICIENT_EVIDENCE":"Chưa đủ bằng chứng bối cảnh để hỗ trợ diễn giải.",
      "QUALITY_BLOCKED":"Chất lượng tín hiệu không đạt; không được diễn giải là không có mỏi.",
      "UNSUPPORTED_PROTOCOL":"Protocol chưa được hỗ trợ.",
      "NO_CONTEXT_EVIDENCE":"Không ghi nhận pattern bối cảnh đủ mạnh trong dữ liệu được hỗ trợ."
    }
    return mapping[state]
