# Lớp Trí tuệ Lâm sàng về Mỏi cơ sEMG/MFCV

## Định vị
Kho lưu trữ này chứa lớp Trí tuệ Lâm sàng (Clinical Intelligence) ưu tiên xử lý ngoại tuyến (offline-first) dành cho các bằng chứng về tình trạng mỏi cơ dựa trên sEMG/MFCV. Hệ thống hoạt động dựa trên dữ liệu trích xuất từ Motion Lab/Noraxon, dữ liệu tổng hợp (synthetic data), và sau này là các quy trình lâm sàng đã được kiểm chứng. Đây không phải là thiết bị thu thập EMG và không thay thế cho phần mềm Noraxon/myoRESEARCH.

## Nguyên tắc MVP
- Ưu tiên chất lượng tín hiệu trước khi áp dụng AI hay suy luận mỏi cơ.
- Sử dụng các quy tắc có thể giải thích được (explainable rules) thay vì các mô hình hộp đen (black-box models).
- Yêu cầu con người đánh giá (human review) trước khi đưa ra bất kỳ báo cáo lâm sàng nào.
- Từ chối đưa ra kết luận (abstention) nếu dữ liệu không an toàn hoặc không đủ cơ sở.
- Chỉ tính toán MFCV/CV khi hình học điện cực, thứ tự kênh đo, tần số lấy mẫu và tính hợp lệ của phác đồ đo được xác nhận.

## Chức năng của sản phẩm
- Nhập (import) các tệp phiên sEMG tổng hợp hoặc xuất từ thiết bị.
- Xác thực siêu dữ liệu (metadata), bối cảnh phác đồ (protocol context), và chất lượng tín hiệu.
- Trích xuất các đặc trưng liên quan đến mỏi cơ như RMS, MAV, MDF, MNF, độ dốc (slopes), và tùy chọn tính toán MFCV/CV khi đủ điều kiện.
- Tạo ra các bằng chứng có cấu trúc phục vụ cho việc đánh giá kỹ thuật và lâm sàng.
- Sinh ra từ ngữ báo cáo mang tính thận trọng, có nêu rõ giới hạn và các mã lý do (reason codes).

## Những gì sản phẩm không làm
- Không điều khiển thiết bị trực tiếp.
- Không tự động chẩn đoán bệnh.
- Không tự động kê đơn hay chỉ định điều trị.
- Không tự động cấp phép trở lại thi đấu (return-to-play clearance).
- Không phải hệ thống cảnh báo thời gian thực đạt chuẩn lâm sàng trong giai đoạn MVP-0.
- Không lưu trữ tín hiệu gốc của bệnh nhân thực tế trong kho lưu trữ này.

## Tiến độ Day 1
Day 1 thiết lập ranh giới sản phẩm, mục đích sử dụng, ngôn ngữ an toàn, cổng kiểm soát chất lượng, hành vi từ chối kết luận, và quy tắc bắt buộc có con người tham gia (human-in-the-loop) cho phiên bản MVP-0.

## Tiến độ Day 2
Day 2 thiết lập hợp đồng nhập dữ liệu (CSV chung + Tệp tin manifest định dạng JSON đi kèm) và phiên bản phác đồ lâm sàng đầu tiên (`quad-isometric-60s`). Nó triển khai quy trình xác thực tín hiệu nhiều lớp và cổng chất lượng (L0-L4) để chặn dữ liệu không hợp lệ một cách dứt khoát, cũng như tách biệt tính đủ điều kiện của sEMG cơ bản khỏi phân tích MFCV nâng cao.

## Tiến độ Day 3
Day 3 triển khai quy trình (pipeline) nhập CSV chung và hợp đồng tín hiệu chuẩn hóa tiêu chuẩn (`NormalizedSignal`). Hệ thống buộc các mảng dữ liệu (arrays) phải ở chế độ chỉ đọc (read-only) sau khi khởi tạo, loại bỏ dữ liệu gốc khỏi tệp tóm tắt JSON đầu ra, và xác minh định dạng tệp, siêu dữ liệu, cũng như hàm băm nguồn (source hashing) có tính xác định (deterministic) trước khi chuyển sang quá trình xử lý tiếp theo (downstream processing).

## Tiến độ Day 4
Day 4 triển khai mô-đun Cổng kiểm soát chất lượng tín hiệu (Signal Quality Gate - QC) để đánh giá tín hiệu dựa trên các tiêu chí vô hiệu hóa như Flatline (phẳng), Clipping (cắt xén), Nhiễu điện lưới (Powerline Noise), và Nhiễu chuyển động (Motion Artifact). Nó hoàn thiện lớp tích hợp dữ liệu và thiết lập chính sách từ chối xử lý sớm (fail-fast abstention) đối với dữ liệu không an toàn.

## Tiến độ Day 5
Day 5 xây dựng lõi quy trình xử lý tín hiệu và điều phối dịch vụ. Triển khai luồng tiền xử lý nhiều giai đoạn (lọc băng thông và lọc Notch động), tích hợp trực tiếp với Cổng QC để chỉ áp dụng bộ lọc khi phát hiện các cờ nhiễu cụ thể nhằm bảo toàn tối đa dữ liệu gốc.

## Tiến độ Day 6
Day 6 tập trung vào việc xác minh thực nghiệm (empirical verification) quy trình tiền xử lý tín hiệu đa tần số. Nó xác nhận cấu hình các bộ lọc thông qua một mảng tín hiệu mẫu xác định để đối chiếu với các kỳ vọng lý thuyết về rò rỉ phổ và đáp ứng tần số, qua đó hoàn thiện báo cáo kiểm chứng tiền xử lý.

## Tiến độ Day 7
Day 7 triển khai logic phân đoạn và chia cửa sổ (segmentation & windowing) bám sát phác đồ lâm sàng. Hệ thống buộc phải đối chiếu chặt chẽ giữa phác đồ và cấu hình trích xuất đặc trưng, tự động từ chối xử lý nếu phát hiện cấu hình không khớp.

## Tiến độ Day 8
Day 8 xây dựng mô-đun trích xuất đặc trưng miền thời gian (time-domain features). Triển khai logic tính toán RMS và MAV mang tính xác định (deterministic), kết hợp cùng các schema và báo cáo kiểm chứng để đảm bảo tính chính xác toán học.

## Tiến độ Day 9
Day 9 triển khai quy trình ước lượng phổ (spectral estimation) sử dụng phương pháp Welch. Xây dựng cơ sở tính toán Mật độ Phổ Công suất (PSD - Power Spectral Density) và xử lý các giới hạn độ phân giải tần số theo chuẩn phác đồ lâm sàng.

## Tiến độ Day 10
Day 10 giới thiệu phân hệ trích xuất đặc trưng miền tần số (frequency-domain features). Tính toán Tần số Trung vị (MDF) và Tần số Trung bình (MNF) dựa trên PSD, áp dụng các công thức toán học tiêu chuẩn và các schema kiểm định khắt khe.

## Tiến độ Day 11
Day 11 triển khai mô-đun trích xuất đặc trưng Khuynh hướng (Trend Features). Tính toán độ dốc hồi quy tuyến tính (slopes) cho RMS, MAV, MDF và MNF theo thời gian. Áp dụng chính sách kiểm soát nghiêm ngặt chỉ cung cấp số liệu thống kê mô tả (descriptive), loại bỏ hoàn toàn các chỉ số thống kê suy diễn (như p-value hay khoảng tin cậy) nhằm ngăn chặn việc kết luận lâm sàng vội vã.

## Tiến độ Day 12
Day 12 xây dựng Mô-đun Bằng chứng Mỏi cơ (`FatigueEvidenceEngine`). Chuyển đổi các chỉ số miền thời gian, miền tần số và khuynh hướng thành đối tượng bằng chứng có cấu trúc (`FatigueEvidenceResult v0.1`), tách biệt hoàn toàn giữa quan sát/bằng chứng với phân loại và quyết định lâm sàng.

## Tiến độ Day 13
Day 13 triển khai Động cơ Quy tắc Giải thích được (`ExplainableRuleEngine`). Đánh giá bằng chứng mỏi cơ dựa trên các bảng quy tắc có phiên bản để sinh ra kết luận quy tắc xác định (`FatigueRuleResult v0.1`), sự đồng thuận đa kênh, cơ sở quyết định, bằng chứng đối lập, và chính sách từ chối xử lý (abstention-first).

## Tiến độ Day 14
Day 14 triển khai tính toán Độ tin cậy Kỹ thuật (`EngineeringConfidenceCalculator`) và Rào chắn An toàn Từ ngữ (`WordingGuard`). Đánh giá chất lượng đường ống xử lý nội bộ, tạo tóm tắt khả năng giải thích, và chặn đứng các từ ngữ tuyên bố quá đà hoặc không an toàn.

## Tiến độ Day 15
Day 15 điều phối hoàn chỉnh quy trình phân tích ngoại tuyến (`run_offline_analysis.py`). Tích hợp Day 1–14 thành một lệnh ngoại tuyến độc lập, sinh ra 11 tệp tin thành phần giai đoạn, siêu dữ liệu chứng thực, mã băm nguồn SHA-256, và gói phân tích ngoại tuyến.

## Tiến độ Day 16
Day 16 hoàn thiện Báo cáo Kiểm chứng Thống kê & Hồi quy Chuẩn (`day16-mvp0-regression-report.md`). Xác nhận độ ổn định của quy trình xử lý trên ma trận dữ liệu mẫu tổng hợp, khóa hành vi an toàn và đóng băng baseline `mvp0_baseline_v0.1.json`.

## Tiến độ Day 17
Day 17 triển khai Schema Đầu ra Chuẩn hóa (`SessionAnalysisSummary v0.1`) và Hợp đồng OpenAPI (`openapi.yaml`). Thiết lập hợp đồng giao tiếp phiên bản giữa gói phân tích ngoại tuyến với hệ thống backend/frontend.

## Tiến độ Day 18
Day 18 hoàn thành Hệ thống Giao diện UI/UX & Kiểm toán Liên tục Frontend (`apps/web-portal`) sử dụng Next.js 14 App Router, TypeScript strict mode, và tiêu chuẩn truy cập WCAG 2.2 AA. Hệ thống hỗ trợ 4 hướng ứng dụng Use Case, quy trình Bác sĩ ký duyệt lâm sàng, trọng tài dán nhãn ML, quản lý sự cố chất lượng dữ liệu, và kịch bản E2E Playwright test với điểm kiểm toán **100/100 PASS**.

### 🚀 Hướng dẫn khởi chạy giao diện UI Portal (Running the UI Portal)

#### Yêu cầu môi trường
- Node.js >= 18.0.0
- npm hoặc pnpm

#### 1. Khởi chạy ở Chế độ Phát triển (Development Mode)
Từ thư mục gốc dự án:
```bash
npm --prefix apps/web-portal run dev
```
Hoặc truy cập trực tiếp vào thư mục `apps/web-portal`:
```bash
cd apps/web-portal && npm run dev
```
Mở trình duyệt truy cập: [http://localhost:3100](http://localhost:3100).

#### 2. Khởi chạy ở Chế độ Sản xuất (Production Build & Start)
Từ thư mục gốc dự án:
```bash
# Biên dịch ứng dụng Next.js
npm --prefix apps/web-portal run build

# Khởi chạy server Production
npm --prefix apps/web-portal run start
```
Mở trình duyệt truy cập: [http://localhost:3100](http://localhost:3100).

#### 3. Lệnh kiểm tra kiểu & Linter
```bash
npm --prefix apps/web-portal run type-check
npm --prefix apps/web-portal run lint
```

#### 4. Tài khoản thử nghiệm nhanh (Demo User Roles)
Tại màn hình Đăng nhập (`/login`), nhấp chọn các vai trò thử nghiệm có sẵn:
- **Bác sĩ (Doctor):** Xem kết luận AI, chọn Override policy, ký duyệt Clinical Sign-off và xuất báo cáo (`/sessions/[id]/review`).
- **Kỹ thuật viên (KTV):** Tạo phiên, tải tệp, gán kênh (mapping), chạy QC Gate & Analysis.
- **Trọng tài ML (Researcher):** Hộp thư phản hồi dán nhãn & ML Adjudication (`/feedback/inbox`).
- **Bệnh nhân (Patient):** Giao diện biofeedback cử chỉ (`/uc1/session/[id]`).

