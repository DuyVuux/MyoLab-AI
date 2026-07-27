# Repository Reuse Shortlist

## Mục tiêu

Không copy nguyên một paper repository. Tách dependency theo lớp ingestion, DSP và evaluation.

| Repository | Vai trò | License theo báo cáo | Khuyến nghị |
|---|---|---|---|
| LibEMG | Data handling, features, evaluation harness | MIT | `BASELINE_CANDIDATE`; vẫn phải ép group-aware split |
| pyemgpipeline | Preprocessing/DSP provenance | GPL-3.0 | Research component; review copyleft trước phân phối |
| ezc3d | C3D I/O | MIT | `PRODUCTION_REUSE_CANDIDATE` nếu site C3D được xác minh |
| openhdemg | HD-sEMG/MU/CV research | BSD-3-Clause | Nhánh research, không chứng minh site MFCV |
| BioPatRec | Classical myoelectric research | LGPL | Reference/baseline; review dependency stack |
| pyomeca | Biomechanics processing | Apache | Candidate khi có synchronized biomechanics data |
| EMGFlow | sEMG processing | GPL-3.0 | Research-only nếu license không phù hợp distribution |
| Reach&Grasp repo | BIDS-like sidecar reference | MIT code reported | Data-contract reference, không backbone duy nhất |
| putEMG scripts | Dataset loader/examples | MIT scripts | Example-only; data vẫn CC BY-NC |

## Quy tắc reuse

```text
Explicit license present
+ canonical repository
+ active/reproducible enough
+ tests/examples
+ dependency review
= có thể shortlist
```

Không có explicit license:

```text
REJECT_FOR_CODE_REUSE
```

Dù code tải được công khai.
