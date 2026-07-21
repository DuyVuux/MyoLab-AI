# Đặc tả kiểm chứng `preprocess_v0.1`

## 1. Mục đích

Xác minh hành vi số học của preprocessing offline trước khi sử dụng output cho windowing và feature extraction.

## 2. Phạm vi

- Fs được verify trong Day 6: 1000 Hz.
- Butterworth band-pass 20–400 Hz, order 4, SOS, `sosfiltfilt`.
- Notch 50 Hz, Q=30, chỉ khi policy bật.
- Synthetic deterministic signals.

## 3. Các tầng kiểm chứng

### 3.1. Đáp ứng lý thuyết

Dùng `sosfreqz` trên hệ số filter. Với zero-phase forward/backward, biên độ hiệu dụng bằng bình phương biên độ one-pass.

### 3.2. Đáp ứng thực nghiệm

Dùng multi-tone signal và sinusoidal projection để đo biên độ từng thành phần trước/sau lọc trong vùng nội bộ.

### 3.3. Pha bằng không

Dùng centered impulse; peak không được dịch và impulse response phải đối xứng trong tolerance.

### 3.4. Hành vi tại biên

Dùng sine ổn định; fit vùng nội bộ rồi so RMSE edge với interior.

### 3.5. Tính xác định

Chạy cùng input ba lần trong cùng environment và so output SHA-256.

## 4. Failure behavior

Bất kỳ critical criterion nào fail:

```text
verification overall = fail
registry freeze = không được tạo/cập nhật trạng thái pass
Day 7 = blocked
```

## 5. Giới hạn

- Không thay thế validation trên dữ liệu thiết bị thật.
- Không chứng minh clinical usefulness.
- Không xác nhận causal/realtime behavior.
- Không xác nhận mọi sampling rate.
