# Day 22 — Math notes

## 1. Activity threshold

```text
T_a = μ_rest + kσ_rest
T_r = rT_a
T_u = (1-u)T_a
```

Trong đó:

- `μ_rest`: rest RMS theo session;
- `σ_rest`: độ phân tán RMS trong calibration;
- `k > 0`: engineering multiplier có version;
- `0 < r < 1`: release ratio;
- `0 <= u < 1`: uncertainty-band ratio.

Known answer:

```text
μ_rest = 4.2 µV
σ_rest = 0.8 µV
k = 3
r = 0.8
u = 0.1

T_a = 4.2 + 3×0.8 = 6.6 µV
T_r = 6.6×0.8 = 5.28 µV
T_u = 6.6×0.9 = 5.94 µV
```

Boundary:

```text
new activation: rms >= T_a
hold active:    previous_active and rms >= T_r
uncertain:      not held/activated and rms >= T_u
inactive:       otherwise
```

Thứ tự condition quan trọng. Với previous active, `5.5 µV` được hold mặc dù
thấp hơn `T_u`; nếu kiểm uncertainty trước hysteresis thì kết quả sẽ sai.

## 2. Window coordinates

Với sample rate `F_s`, first sample `s_0`, window length `N` và hop `H`:

```text
s_i = s_0 + iH
e_i = s_i + N
W_i = [s_i, e_i)
|W_i| = e_i - s_i = N
t_i,start = s_i / F_s
t_i,end   = e_i / F_s
duration  = N / F_s
```

Protocol fixture `F_s=1000 Hz`, `N=1000`, `H=250` tương ứng window 1 s, hop
0.25 s và overlap 75%.

Không dùng `(e-s+1)` vì end-exclusive. Feedback phải giữ nguyên các endpoint,
không round-trip qua formatted time để tính lại sample.

## 3. Latency

```text
L_total = L_acquisition + L_window + L_preprocess
        + L_inference + L_transport_render
```

Known answer:

```text
10 + 200 + 18 + 14 + 28 = 270 ms
```

Nearest-rank:

```text
x = sort(values)
rank(p) = ceil(pn), p ∈ (0,1]
P_p = x[rank(p)-1]
```

Với `[100,200,300,400]`:

```text
p50: ceil(0.50×4)=2 → 200
p95: ceil(0.95×4)=4 → 400
```

Không linear-interpolate. Với `n=1`, mọi percentile hợp lệ trả phần tử duy nhất.
Empty set không có percentile và utility phải reject; replay summary zero-window
dùng `null` thay vì gọi utility.

## 4. Confidence ordering

Ordinal engineering ranks dùng cho policy:

```text
very_low=1 < low=2 < moderate=3 < high=4
```

`not_available` có thể dùng sentinel rank nội bộ để validate, nhưng về semantics
nó không phải confidence level. Fatigue warning yêu cầu:

```text
rank(final) < rank(base)
```

Fixture chuẩn:

```text
base = engineering_high
cap  = engineering_moderate
final = min_by_rank(base, cap) = engineering_moderate
```

Không chuyển rank thành phần trăm hoặc probability.

## 5. Canonical public hash

```text
H = SHA256(
  UTF8(
    canonical_json(public_window without resultHashSha256)
  )
)
```

Project canonical JSON:

- sort object keys;
- compact separators `,` và `:`;
- giữ Unicode, không ASCII-escape bắt buộc;
- cấm NaN/Infinity;
- giữ nguyên array order.

Do đó reorder object keys không đổi `H`; đổi value hoặc array order phải đổi
`H`. Digest là 64 lowercase hexadecimal characters.
