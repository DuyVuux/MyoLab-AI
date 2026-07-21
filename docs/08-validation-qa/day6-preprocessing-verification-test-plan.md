# Kế hoạch kiểm thử Day 6 — Kiểm chứng phân tích preprocessing

## Nhóm kiểm thử

| Nhóm | Kiểm thử | Kết quả mong đợi |
|---|---|---|
| Kiểm thử hồi quy | Day 5 suite | Pass |
| Theoretical | 5 Hz | ≤ -40 dB |
| Theoretical | 30/80/200/350 Hz | Trong passband tolerance |
| Theoretical | 450 Hz | ≤ -30 dB |
| Notch | 50 Hz khi bật | ≤ -30 dB |
| Empirical | Multi-tone band-pass | Phù hợp profile |
| Empirical | Notch off/on | 50 Hz chỉ bị giảm mạnh khi notch on |
| Zero-phase | Centered impulse | Peak offset 0 |
| Zero-phase | Symmetry | Error ≤ tolerance |
| Edge | 80 Hz sine | Edge RMSE lớn hơn interior |
| Determinism | 3 lần chạy | Hash giống nhau |
| Governance | Registry | Chỉ freeze khi all_passed |
| Safety | Clinical status | `not_validated` |

## Dữ liệu kiểm thử

Toàn bộ test data được sinh trong bộ nhớ, deterministic, không PHI.

## Pass rule

Tất cả critical criteria phải pass. Không dùng average score để che một failure critical.
