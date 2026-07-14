# TEAM OPERATING MODEL — SINGLE-OPERATOR EXECUTION

**Project:** sEMG/MFCV Fatigue Clinical Intelligence Layer  
**Repository path:** `docs/11-operations/team-operating-model.md`  
**Document status:** Active  
**Effective from:** Day 2 — 2026-07-14  
**Document owner:** Project Lead  
**Review mode:** Structured self-review + external clinical review where required  
**Version:** v0.2

---

## 1. Purpose

Tài liệu này định nghĩa mô hình vận hành của dự án kể từ Day 2, sau khi team chuyển từ mô hình hai người gồm **Duy và Quân** sang mô hình **single operator**.

Mục tiêu là bảo đảm rằng dù chỉ còn một người trực tiếp thực hiện, dự án vẫn duy trì:

- trách nhiệm rõ ràng;
- thứ tự công việc có kiểm soát;
- review có cấu trúc;
- không tự phê duyệt các quyết định lâm sàng vượt thẩm quyền;
- không biến tốc độ thực thi thành lý do bỏ qua quality gate, safety gate hoặc documentation;
- hạn chế quá tải và context switching bằng WIP limit.

Tài liệu này không xóa hoặc viết lại lịch sử Day 1. Các phân công Quân/Duy trong Day 1 vẫn được giữ nguyên như bằng chứng lịch sử dự án. Mô hình mới chỉ có hiệu lực đối với các task, artifact và quyết định phát sinh từ Day 2 trở đi.

---

## 2. Operating model decision

Từ Day 2, dự án sử dụng mô hình:

> **Single-operator serialized workflow with structured self-review and mandatory external clinical approval for clinical/pilot decisions.**

Điều này có nghĩa:

1. **Project Lead là primary owner** của toàn bộ task mới.
2. Công việc được thực hiện tuần tự theo từng vai trò hoặc “mũ” chuyên môn, không giả định có người thứ hai thực hiện song song.
3. Review nội bộ được thực hiện bằng structured self-review, có checklist, evidence và separation of concerns theo thời điểm.
4. Các quyết định cần thẩm quyền lâm sàng vẫn phải được review hoặc approve bởi người bên ngoài dự án có chuyên môn phù hợp.
5. Project Lead **không được tự approve pilot**, không được tự xác nhận clinical readiness và không được thay thế clinical sign-off.
6. WIP limit tối đa là **2 task đang mở đồng thời**.

---

## 3. Scope of authority

### 3.1. Project Lead có quyền tự quyết

Project Lead có thể tự quyết và tự chịu trách nhiệm đối với:

- cấu trúc repository;
- architecture draft;
- technical specification;
- code implementation;
- test automation;
- synthetic data generation;
- offline pipeline;
- API contract draft;
- dashboard prototype;
- documentation format;
- sprint planning;
- issue prioritization;
- technical spike;
- internal demo wording ở mức draft;
- risk identification;
- go/no-go nội bộ cho bước kỹ thuật tiếp theo, với điều kiện không được hiểu là clinical approval.

### 3.2. Project Lead không được tự approve

Project Lead không được tự phê duyệt các hạng mục sau:

- intended use cuối cùng dùng cho pilot thực tế;
- clinical protocol dùng trên người bệnh hoặc vận động viên;
- electrode placement protocol cho vận hành lâm sàng;
- ngưỡng lâm sàng dùng để đưa ra kết luận hoặc gợi ý điều chỉnh tải tập;
- report wording có thể được hiểu là chẩn đoán, chỉ định hoặc khuyến nghị điều trị;
- pilot readiness;
- clinical usefulness;
- patient safety acceptance;
- consent, data governance hoặc workflow approval tại cơ sở triển khai;
- return-to-play decision logic;
- clinical validation conclusion;
- triển khai trên dữ liệu bệnh nhân thật ngoài phạm vi được phê duyệt.

Những mục này phải được đánh dấu:

```text
EXTERNAL_REVIEW_REQUIRED
```

hoặc:

```text
EXTERNAL_APPROVAL_REQUIRED
```

---

## 4. Role model for a single operator

Project Lead luân phiên thực hiện các “mũ” sau. Mỗi mũ có mục tiêu và output khác nhau.

| Operating hat | Trách nhiệm chính | Không được làm đồng thời với |
|---|---|---|
| Product / Program Management | Chốt scope, dependency, deadline, decision log, backlog | Tự coi product assumption là clinical fact |
| Biomedical Signal Processing | Định nghĩa sampling, QC, preprocessing, windowing, feature | Tự phê duyệt clinical threshold |
| AI/ML Engineering | Rule engine, feature pipeline, baseline model, evaluation | Train/publish model khi label chưa usable |
| Software Architecture | Module boundary, interfaces, versioning, deployment | Bỏ qua safety requirement để đơn giản hóa code |
| Implementation | Viết code, config, schema, tests | Tự nghiệm thu ngay sau khi vừa code xong |
| QA / Safety | Chạy checklist, negative tests, review wording, inspect failure behavior | Thay thế external clinical approval |
| Documentation / Evidence | Ghi spec, evidence, limitation, decision, traceability | Xóa hoặc sửa lịch sử để làm tài liệu “đẹp hơn” |

### 4.1. Serialized workflow

Các mũ phải được thực hiện tuần tự:

```text
Plan
→ Draft specification
→ Implement
→ Pause / context reset
→ Structured self-review
→ Run tests
→ Record evidence
→ Decide next step
```

Không sử dụng quy trình:

```text
Implement
→ tự thấy hợp lý
→ mark Done
```

---

## 5. Primary ownership rule

Từ Day 2:

- Owner mặc định của artifact mới là `Project Lead`.
- Có thể dùng `Single Operator` cho các checklist hoặc log vận hành.
- Không giao task mới cho Quân.
- Không thêm Quân vào owner, reviewer hoặc approver của artifact mới.
- Không thay đổi owner lịch sử trong artifact Day 1 nếu artifact đó phản ánh đúng tình trạng lúc được tạo.
- Nếu tài liệu cũ cần cập nhật, phải ghi rõ thay đổi có hiệu lực từ Day 2 thay vì rewrite lịch sử.

### 5.1. Naming convention

Dùng một trong hai giá trị:

```yaml
owner: Project Lead
```

hoặc:

```yaml
owner: Single Operator
```

Đối với nội dung cần clinical review:

```yaml
owner: Project Lead
reviewer: External Clinical Reviewer
approval_status: pending_external_review
```

---

## 6. Structured self-review model

Do không còn reviewer nội bộ thứ hai, review phải dựa trên quy trình có cấu trúc và evidence có thể kiểm tra lại.

### 6.1. Bốn lớp self-review

#### Layer 1 — Completeness review

Kiểm tra:

- output có đúng file path không;
- task có đáp ứng input/output đã định nghĩa không;
- dependency đã được xử lý chưa;
- artifact có owner, version, status và date không;
- acceptance criteria đã được liệt kê chưa.

#### Layer 2 — Technical review

Kiểm tra:

- assumptions có được ghi rõ không;
- schema/config có validate được không;
- code có deterministic không;
- error path có được test không;
- version metadata có được ghi lại không;
- module có tuân thủ architecture đã chốt không.

#### Layer 3 — Safety and overclaim review

Kiểm tra:

- QC fail có block analysis không;
- abstention có được coi là output hợp lệ không;
- MFCV/CV có bị tính khi chưa đủ eligibility không;
- wording có biến hỗ trợ quyết định thành chẩn đoán hoặc điều trị không;
- synthetic output có được ghi rõ là synthetic không;
- có claim realtime, clinical validation hoặc accuracy vượt bằng chứng không.

#### Layer 4 — Reproducibility and evidence review

Kiểm tra:

- command có chạy lại được không;
- test result có được lưu không;
- input fixture có version không;
- expected output có được lưu không;
- decision và limitation có được ghi vào log không.

### 6.2. Time separation rule

Không tự nghiệm thu ngay lập tức sau khi vừa hoàn thành implementation.

Áp dụng ít nhất một trong các cơ chế:

- nghỉ 15–30 phút trước khi review;
- chuyển sang một task documentation ngắn rồi quay lại review;
- review vào cuối buổi với checklist độc lập;
- chạy automated checker trước khi đọc lại thủ công.

Mục đích là giảm confirmation bias.

### 6.3. Review evidence

Mỗi review quan trọng phải để lại ít nhất một artifact:

- checklist đã tick;
- test output;
- decision-log entry;
- risk-register update;
- validation report;
- issue hoặc TODO có owner và deadline;
- `EXTERNAL_REVIEW_REQUIRED` marker.

---

## 7. Clinical approval model

### 7.1. External clinical review remains mandatory

Việc dự án chỉ còn một người không làm giảm yêu cầu về clinical governance.

Các hạng mục sau phải có reviewer bên ngoài phù hợp:

| Hạng mục | Reviewer tối thiểu |
|---|---|
| Intended use / product boundary | Clinical lead hoặc bác sĩ phụ trách use case |
| Protocol thu nhận | Bác sĩ/KTV Motion Lab hoặc chuyên gia sEMG |
| Electrode placement | KTV hoặc chuyên gia có kinh nghiệm sEMG |
| Clinical report wording | Bác sĩ/KTV sử dụng report |
| Pilot workflow | Clinical lead + site owner/operations |
| Validation plan | Clinical lead + signal/AI reviewer nếu có |
| Pilot go/no-go | Clinical owner/site governance, không phải Project Lead một mình |

### 7.2. Clinical review debt

Mọi nội dung chưa được review bên ngoài nhưng có ảnh hưởng lâm sàng phải được ghi là **clinical review debt**.

Clinical review debt phải có:

- ID;
- artifact liên quan;
- câu hỏi cần review;
- loại reviewer cần có;
- mức độ ảnh hưởng;
- deadline mong muốn;
- trạng thái.

Ví dụ:

```text
CRD-001
Artifact: clinical/protocols/quad-isometric-60s.v0.1.yaml
Question: Protocol duration, contraction target và rest period có phù hợp use case pilot không?
Reviewer needed: Motion Lab KTV + Clinical Lead
Impact: High
Status: Open
```

### 7.3. No self-approval of pilot

Project Lead có thể chuẩn bị:

- pilot protocol draft;
- checklist;
- demo;
- technical readiness evidence;
- risk register;
- training material;
- validation plan.

Nhưng Project Lead không được tự đổi trạng thái từ:

```text
pilot_candidate
```

sang:

```text
pilot_approved
```

Trạng thái hợp lệ trước external approval là:

```text
pilot_not_approved
pilot_candidate
pending_external_clinical_review
pending_site_approval
```

---

## 8. WIP policy

### 8.1. WIP limit

WIP limit tối đa:

```text
2 active tasks
```

Một task được tính là active khi:

- đã bắt đầu nhưng chưa đạt Done criteria;
- đang chờ implementation hoặc review nội bộ;
- đang bị blocker nhưng chưa được chuyển sang trạng thái `Blocked` rõ ràng.

### 8.2. Các trạng thái task

```text
Backlog
Ready
Active
Self-review
Blocked
External review
Done
Deferred
```

Task ở trạng thái `External review` không tính vào WIP implementation, nhưng phải được theo dõi trong clinical review debt hoặc external-dependency log.

### 8.3. Quy tắc mở task mới

Chỉ được mở task thứ ba khi ít nhất một task đang active được chuyển sang:

- `Done`;
- `Blocked` có blocker rõ và next action rõ;
- `External review`;
- `Deferred` có decision log.

### 8.4. Ưu tiên khi WIP đầy

Khi đã có hai task active:

1. Không mở thêm task mới.
2. Chọn task gần Done nhất để đóng.
3. Nếu bị block, ghi blocker và chuyển trạng thái đúng.
4. Nếu cả hai task đều quá lớn, chia nhỏ task theo output kiểm chứng được.

---

## 9. Daily operating cadence

### 9.1. Start-of-day planning — 10 phút

Ghi rõ:

- tối đa hai task active;
- output cụ thể của từng task;
- dependency;
- acceptance criteria;
- clinical/safety concern;
- artifact path.

### 9.2. Midday checkpoint — 5 đến 10 phút

Kiểm tra:

- WIP có vượt 2 không;
- có task nào cần chia nhỏ không;
- có assumption nào đang bị biến thành fact không;
- có external review debt mới không;
- có cần cập nhật risk register không.

### 9.3. End-of-day review — 20 đến 30 phút

Thực hiện:

- structured self-review;
- chạy test/checker;
- cập nhật decision log;
- cập nhật daily summary;
- ghi blocker;
- ghi clinical review debt;
- xác định tối đa hai task đầu tiên của ngày tiếp theo.

---

## 10. Definition of Done for single-operator tasks

Một task chỉ được đánh dấu `Done` khi:

- [ ] Output nằm đúng path trong skeleton.
- [ ] Owner là `Project Lead` hoặc `Single Operator`.
- [ ] Input, output và dependency được ghi rõ.
- [ ] Acceptance criteria được đáp ứng.
- [ ] Structured self-review đã hoàn thành.
- [ ] Test hoặc validation tương ứng đã chạy.
- [ ] Failure path hoặc negative case đã được xem xét.
- [ ] Safety/overclaim review đã hoàn thành nếu liên quan.
- [ ] Clinical review debt đã được ghi nếu cần external review.
- [ ] Không có pilot/clinical approval tự cấp.
- [ ] Decision log hoặc changelog đã được cập nhật nếu có thay đổi quyết định.
- [ ] Artifact đã được commit hoặc lưu đúng nơi quy định.

---

## 11. Historical integrity rule

### 11.1. Day 1 history must remain unchanged

Không xóa hoặc rewrite:

- phân chia Quân/Duy trong kế hoạch Day 1;
- owner/reviewer của artifact Day 1;
- decision log mô tả mô hình hai người tại thời điểm đó;
- lịch sử commit đã phản ánh mô hình cũ.

### 11.2. Effective change from Day 2

Thay đổi được ghi theo nguyên tắc:

```text
Day 1: two-person operating assumption
Day 2 onward: single-operator serialized workflow
```

Nếu một artifact Day 1 cần chỉnh sửa sau Day 2, thêm changelog hoặc note:

```text
Operating model updated from Day 2. Historical Day 1 ownership retained.
```

---

## 12. Decision rights matrix

| Decision | Project Lead | External reviewer/approver |
|---|---:|---:|
| Repo structure | A/R | I |
| Technical architecture draft | A/R | C khi cần |
| Offline pipeline implementation | A/R | I |
| QC implementation | A/R | C cho clinical implications |
| Feature formula implementation | A/R | C nếu dùng cho clinical claim |
| Synthetic demo | A/R | I |
| Clinical wording draft | R | A/C |
| Protocol draft | R | A/C |
| MFCV eligibility technical check | R | C từ Motion Lab/sEMG expert |
| Pilot readiness package | R | A bởi external clinical/site owner |
| Pilot go/no-go | C/R evidence | A external |
| Clinical validation conclusion | R analysis | A external clinical governance |

Trong bảng:

- `R`: Responsible;
- `A`: Accountable/approver;
- `C`: Consulted;
- `I`: Informed.

Trong mô hình một người, Project Lead có thể đồng thời là R và A đối với task kỹ thuật nội bộ, nhưng không được đồng thời là R và A đối với quyết định clinical/pilot cần độc lập.

---

## 13. Required update to stakeholder decision log

Thêm một dòng vào:

```text
docs/00-executive/stakeholder-decision-log.md
```

Dòng đề xuất:

| ID | Date | Decision area | Options considered | Decision | Owner | Review method | Status | Follow-up |
|---|---|---|---|---|---|---|---|---|
| D-007 | 2026-07-14 | Team operating model | Two-person / single operator | Single-operator serialized workflow; external clinical review remains required | Project Lead | Structured self-review | Active | Update roadmap/RACI later; retain Day 1 Quân/Duy history |

Không sửa hoặc xóa các dòng trước đó liên quan đến Quân/Duy.

---

## 14. Clinical review debt register requirement

Tạo hoặc cập nhật một trong các file sau:

```text
docs/02-clinical/clinical-review-debt.md
```

hoặc:

```text
docs/00-executive/assumptions-and-open-questions.md
```

Mẫu bảng:

| Debt ID | Artifact | Review question | Reviewer needed | Impact | Owner | Status | Target date |
|---|---|---|---|---|---|---|---|
| CRD-001 | `clinical/protocols/quad-isometric-60s.v0.1.yaml` | Protocol có phù hợp cho pilot thực tế không? | Clinical Lead + Motion Lab KTV | High | Project Lead | Open | TBD |
| CRD-002 | `docs/02-clinical/quality-escalation-policy.md` | Khi nào phải đo lại hoặc dừng phân tích? | Clinical Lead/KTV | High | Project Lead | Open | TBD |
| CRD-003 | `reports/templates/clinical_report_v0.1.md` | Wording có an toàn và dễ hiểu không? | Clinician/KTV reviewer | High | Project Lead | Open | TBD |

---

## 15. Anti-patterns prohibited from Day 2

Không được:

- giao task mới cho Quân;
- ghi Quân là reviewer hình thức khi Quân không còn tham gia;
- tự đóng clinical review debt mà không có external review;
- tự approve pilot;
- có hơn hai task active;
- dùng “self-review” như lý do bỏ test;
- thay đổi lịch sử Day 1 để làm tài liệu nhất quán giả tạo;
- coi paper threshold là threshold lâm sàng của sản phẩm;
- coi synthetic demo là validation;
- coi technical pass là clinical pass;
- coi absence of detected fatigue là bằng chứng người bệnh an toàn;
- coi `MFCV unavailable` là system failure nếu basic sEMG analysis vẫn đủ điều kiện.

---

## 16. Done criteria for this operating-model update

Bước cập nhật mô hình một người được xem là hoàn thành khi:

- [ ] `docs/11-operations/team-operating-model.md` tồn tại và có status `Active`.
- [ ] Tài liệu ghi rõ Project Lead là primary owner.
- [ ] Structured self-review được định nghĩa thành quy trình cụ thể.
- [ ] External clinical approval vẫn là bắt buộc.
- [ ] Có quy tắc cấm tự approve pilot.
- [ ] WIP limit được đặt tối đa 2 task.
- [ ] Không còn task mới giao cho Quân từ Day 2.
- [ ] Artifact mới dùng owner `Project Lead` hoặc `Single Operator`.
- [ ] Clinical review debt được ghi rõ và có nơi theo dõi.
- [ ] Decision log có dòng D-007 hoặc tương đương.
- [ ] Lịch sử Quân/Duy trong Day 1 được giữ nguyên.
- [ ] Roadmap và RACI được đưa vào follow-up để cập nhật sau, không cần rewrite ngay trong bước này.

---

## 17. Immediate follow-up actions

Sau khi lưu tài liệu này:

1. Cập nhật `docs/00-executive/stakeholder-decision-log.md` với D-007.
2. Tạo `docs/02-clinical/clinical-review-debt.md` nếu chưa tồn tại.
3. Từ task tiếp theo, dùng owner `Project Lead`.
4. Chuyển toàn bộ task mới của Day 2 sang serialized workflow.
5. Kiểm tra sprint board và bảo đảm không có hơn hai task ở trạng thái `Active`.
6. Để nguyên lịch sử Day 1.
7. Lập issue riêng: `Update roadmap and RACI for single-operator model`.

---

## 18. Document change history

| Version | Date | Change | Owner |
|---|---|---|---|
| v0.1 | Day 1 | Two-person operating assumption: Duy + Quân | Duy / Quân |
| v0.2 | 2026-07-14 | Single-operator serialized workflow effective from Day 2; external clinical review retained | Project Lead |
