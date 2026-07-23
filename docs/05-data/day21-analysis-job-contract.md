# Contract Analysis Job v0.1

`AnalysisJob` là trạng thái vận hành, không phải kết quả lâm sàng. `abstained` là kết quả domain hợp lệ; `failed` là lỗi kỹ thuật. Trường `progressMode=stage_only` ngăn UI suy diễn phần trăm khi backend không có phép đo tiến độ đáng tin cậy.

Safety invariant: `scoreIsProbability=false`, `clinicalUseAllowed=false`, `humanReviewRequired=true`, `rawSamplesIncluded=false`.
