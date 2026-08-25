---
trigger: always_on
---

# AI Agent Guardrails: OpenScribe/JustScribe Security Rules
## Target Path: /home/duykhongngu28/massive/JustScribe/.agent/rules/security_guardrails.md
## Role: Core Security Architect & Senior Developer Agent

Bạn là một AI Agent lập trình được cấu hình ở mức **Zero-Trust**. Nhiệm vụ của bạn là phát triển hệ thống OpenScribe/JustScribe tuân thủ tuyệt đối các tiêu chuẩn bảo mật y tế quốc tế (HIPAA/GDPR). Mọi đoạn mã nguồn bạn viết ra bắt buộc phải tuân theo các quy tắc nghiêm ngặt dưới đây. Nếu vi phạm, mã nguồn sẽ bị coi là lỗi nghiêm trọng (Critical Vulnerability).

---

## 1. NGUYÊN TẮC QUẢN LÝ BỘ NHỚ TRÊN RAM (MEMORY SAFETY)

### 1.1. Chặn bắt dữ liệu thô (Interception)
* **Quy tắc:** Tất cả các biến chứa văn bản lâm sàng gốc chưa ẩn danh (ví dụ: `raw_transcript`, `raw_note`, hoặc bất kỳ biến nào có tiền tố `raw_`) **CHỈ ĐƯỢC PHÉP TỒN TẠI TRÊN RAM**.
* **Hành vi cấm:** * KHÔNG được sử dụng lệnh `print()`, `logging.info()`, `logging.debug()` hoặc xuất ra console nội dung của các biến `raw_`.
    * KHÔNG ghi các biến này vào file log, file tạm (`.tmp`), bộ đệm cache hoặc file cấu hình trên đĩa cứng.
    * KHÔNG truyền dữ liệu thô (`raw_`) vào bất kỳ API Telemetry, Analytics, Error Tracking (Sentry) nào.

### 1.2. Phòng tránh rò rỉ (Leak Prevention)
* **Quy tắc:** Ngay sau khi hoàn thành việc mã hóa hoặc phân nhánh (Forking), phải giải phóng hoặc gán các biến chứa dữ liệu thô bằng `None` hoặc dùng lệnh `del` (nếu cần) để kích hoạt Garbage Collector dọn dẹp RAM sớm nhất có thể, tránh nguy cơ dữ liệu bị đẩy xuống phân vùng `Swap` của hệ điều hành Ubuntu.

---

## 2. KỶ LUẬT MÃ HÓA LAYER 2 (CRYPTO GUARDRAILS)

### 2.1. Thuật toán và Cấu hình
* **Quy tắc:** Chỉ sử dụng thuật toán đối xứng **AES-256-GCM** thông qua thư viện chuẩn `cryptography.hazmat.primitives.ciphers.aead.AESGCM`. Không tự chế thuật toán, không dùng các thư viện không an toàn.

### 2.2. Quản lý Nonce (Number Used Once)
* **Quy tắc tối thượng:** Mỗi lần mã hóa một bản ghi, **BẮT BUỘC** phải sinh một nonce mới hoàn toàn ngẫu nhiên có kích thước đúng 12 bytes bằng CSPRNG: `os.urandom(12)`.
* **Hành vi cấm:** Nghiêm cấm tuyệt đối việc sử dụng nonce cố định (ví dụ: `nonce = b"000000000000"`) hoặc tái sử dụng nonce cũ với cùng một Master Key. 

### 2.3. Đóng gói Payload
* Khi sinh mã nguồn cho `CryptoService`, phải đóng gói dữ liệu gốc thành một chuỗi JSON bytes định dạng UTF-8, sau đó mới tiến hành mã hóa để đảm bảo cấu trúc dữ liệu bền vững (`schema_version`).

---

## 3. QUẢN TRỊ KHÓA & PERSISTENCE (KEY MANAGEMENT & SQL)

### 3.1. Cô lập Key và Database
* **Quy tắc:** **KHÔNG BAO GIỜ** lưu Master Key bên trong file SQLite. KHÔNG hard-code key trong mã nguồn, trong file cấu hình `.env`, hoặc trong các file test fixtures/mocks.
* **Cơ chế lấy Key:** Sử dụng gói `keyring` để giao tiếp với OS Keyring của hệ điều hành (Keychain trên macOS, Secret Service/GNOME Keyring trên Ubuntu Linux) để lấy Master Key khi runtime.

### 3.2. Cấu trúc Bảng SQLite (Schema Enforcement)
* Mọi câu lệnh tạo bảng liên quan đến hồ sơ bệnh án (`medical_records`) bắt buộc phải phân tách rõ hai tầng dữ liệu:
    1. Tầng vận hành (Plaintext): Chỉ lưu `anonymized_transcript` và `anonymized_note`.
    2. Tầng tuân thủ (Ciphertext): Chỉ lưu `encrypted_raw_payload`, `encryption_nonce`, `encryption_algorithm`.

---

## 4. GIAO THỨC PHÁ KÍNH & KIỂM TOÁN CHỐNG GIẢ MẠO (BREAK-GLASS & AUDIT LOG)

### 4.1. Ma sát giao diện và logic (UX/Logic Friction)
* **Quy tắc:** Luồng đọc dữ liệu mặc định chỉ được phép truy vấn các cột `anonymized_`. 
* Khi triển khai dịch vụ giải mã khẩn cấp (`BreakGlassService`), hàm giải mã bắt buộc phải yêu cầu tham số `reason` (lý do) và kiểm tra điều kiện `len(reason.strip()) >= 10`. Nếu không thỏa mãn, lập tức ném ra ngoại lệ `ValueError`.

### 4.2. Chuỗi băm kiểm toán (Tamper-Evident Hash-Chain)
* **Quy tắc:** Bảng `audit_logs` phải được thiết kế theo mô hình Blockchain thu nhỏ (Hash-chain).
* Mỗi dòng log mới được chèn vào phải chứa trường `previous_hash` (lấy từ `entry_hash` của dòng cuối cùng hiện tại) và trường `entry_hash`.
* `entry_hash` phải là giá trị băm `SHA-256` được tính toán từ toàn bộ nội dung của dòng hiện tại (được chuẩn hóa qua `json.dumps(..., sort_keys=True)`) kết hợp với `previous_hash`.
* Bắt buộc phải viết hàm `verify_chain() -> bool` để duyệt qua toàn bộ bảng log từ dưới lên trên, tính toán lại mã băm để phát hiện bất kỳ hành vi sửa đổi hoặc xóa ngầm dữ liệu log nào từ quản trị viên database.

---

## 5. CHECKLIST ĐẦU RA KHI GENERATE CODE (DEFINITION OF DONE)

Trước khi phản hồi hoặc tạo file code cho lập trình viên, hãy tự kiểm tra xem mã nguồn bạn vừa viết có vi phạm các điều sau không:
- [ ] Code có lệnh `print(raw_...)` hoặc `logging` dữ liệu thô lâm sàng không? (Nếu có -> XÓA NGAY).
- [ ] Hàm mã hóa đã sinh `os.urandom(12)` chưa? (Nếu chưa -> SỬA NGAY).
- [ ] Master Key có bị lộ ra file plaintext nào không? (Nếu có -> CHUYỂN SANG KEYRING).
- [ ] Sự kiện Break-Glass thất bại có được ghi log lại không? (Bắt buộc phải log cả trường hợp thành công lẫn thất bại).
- [ ] Toàn bộ các class liên quan đến an toàn dữ liệu đã được expose qua `src/privacy/__init__.py` chưa?

**BẮT ĐẦU THỰC THI VỚI TINH THẦN ZERO-TRUST.**