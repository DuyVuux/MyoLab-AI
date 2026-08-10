# Unlabeled Corpus Retention Policy v0.1

## 1. Status
Technology-augmentation contract/readiness artifact for DAY11. Đây **không** phải authorization để train Self-Supervised Learning (SSL) hoặc OOD model.

## 2. Principle
Raw layer phải giữ provenance đủ để sau này biết corpus đến từ domain/source nào, nhưng không được thay đổi raw chỉ để phục vụ AI. `Có raw sEMG` không đồng nghĩa `được phép dùng cho pretraining`.

## 3. Eligibility state
Mỗi SourceRecord có:
- `governance_status`;
- `deidentification_status`;
- `research_reuse_eligible: true | false | null`;
- `retention_class` nếu đã được policy phê duyệt.

Decision rule:
```text
research_reuse_eligible == true
AND governance_status explicitly approved
AND de-identification/access purpose compatible
→ MAY ENTER a future research-corpus selection workflow

otherwise
→ NOT AUTHORIZED FOR RESEARCH REUSE
```

`null`, `UNKNOWN`, `NOT_VERIFIED` tuyệt đối không được coerce thành `true`.

## 4. Domain provenance at DAY11
DAY11 chỉ giữ source-level facts có bằng chứng như device/software/export family. Rich `DomainContext` (protocol, layout, task, load/speed, context category) thuộc DAY12/DAY14. Không invent những field đó ở DAY11.

## 5. Forbidden shortcuts
- Không resample raw để tất cả corpus cùng Fs.
- Không filter/notch/rectify raw để “clean corpus”.
- Không convert V↔uV trong raw storage.
- Không merge subjects/sessions vì filename giống nhau.
- Không dùng public healthy data để claim Vinmec clinical support.
- Không pretrain SSL chỉ vì consent/licence chưa thấy cấm.
- Không coi OOD readiness là QC hoặc pathology detector.

## 6. Future reuse categories
| Category | DAY11 meaning |
|---|---|
| `ELIGIBLE_CANDIDATE` | governance explicitly supports defined research reuse; still requires future corpus selection |
| `NOT_ELIGIBLE` | policy/licence/purpose forbids reuse |
| `UNKNOWN` | evidence missing; fail closed |
| `REGRESSION_REFERENCE_ONLY` | retained for engineering reference but not training corpus |

DAY11 SourceRecord keeps the primitive governance facts; catalog-level category can be derived later by an approved process.

## 7. OOD/distribution readiness
Provenance should enable future grouping by source/device/software/export family without changing source bytes. Actual domain-support/OOD contract is intentionally deferred to DAY12/DAY14 and validation later.

## 8. Retention and deletion
Retention duration and deletion mechanism are site/governance policy, not invented here. If retention expires, deletion from approved storage must not rewrite historical analytical claims as if the source never existed; audit/provenance handling requires approved governance design. Status: `TBD / governance-controlled`.

## 9. Safety statement
This policy is data-readiness only. It does not authorize model training, clinical validation, domain adaptation, test-time adaptation, or autonomous use.
