# Kế hoạch kiểm thử Day 7 — Segmentation & Windowing v0.1

## 1. Mục tiêu

Chứng minh rằng window geometry verified on synthetic fixture, hệ thống tạo ra một protocol-aligned window plan, đồng thời đảm bảo validity propagation, determinism và safety blocking hoạt động đúng, với bất kỳ invalid window excluded khỏi phân tích.

## 2. Phạm vi kiểm thử

### Unit

- giây sang mẫu;
- overlap sang hop;
- số full-length windows;
- half-open geometry;
- partial-window policy;
- invalid mask propagation;
- read-only lazy view.

### Analytical

- 60 giây tại 1000 Hz tạo 239 time-domain windows;
- 60 giây tại 1000 Hz tạo 119 frequency-domain windows;
- first/last window đúng phase boundary;
- hop nhất quán;
- không vượt phase.

### Pipeline

- completed với golden fixture;
- upstream block được propagate;
- missing phase bị block;
- phase quá ngắn bị block;
- preprocessing version mismatch bị block;
- protocol ref mismatch bị block;
- config/protocol mismatch bị block;
- invalid window excluded chính xác ở từng profile;
- JSON không chứa raw samples.

### Contract

- output validate JSON Schema;
- plan hash giống nhau ở hai lần chạy;
- profile set đúng hai phần tử;
- clinical validation status vẫn là `not_validated`.

## 3. Expected golden geometry

| Profile | L | H | K | First | Last |
|---|---:|---:|---:|---|---|
| time_domain | 500 | 250 | 239 | `[5000,5500)` | `[64500,65000)` |
| frequency_domain | 1000 | 500 | 119 | `[5000,6000)` | `[64000,65000)` |

## 4. Case invalid sample

Inject invalid mask tại index `5750`.

Expected:

```text
time_domain invalid windows      = [2, 3]
frequency_domain invalid windows = [0, 1]
```

## 5. Lệnh chạy

```bash
bash scripts/dev/run_day7_checks.sh
```

Full upstream regression:

```bash
DAY7_FULL_REGRESSION=1 bash scripts/dev/run_day7_checks.sh
```

## 6. Pass criteria

- Tất cả pytest pass.
- Geometry verification trả `pass`.
- Golden E2E có 239/119 windows và tất cả valid.
- JSON Schema pass.
- Hai lần chạy có cùng plan hash.
- Artifact checker pass.
- Không chứa raw array trong output.
