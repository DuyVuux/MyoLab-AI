# Day 02 — Math Notes

## 1. Sampling

\[
x[n] = x(n/F_s), \qquad \Delta t = 1/F_s
\]

Ví dụ `Fs = 1000 Hz`:
- `Δt = 0.001 s = 1 ms`
- 60 giây có xấp xỉ `60,000` mẫu.

## 2. Nyquist

\[
f_N = F_s/2
\]

Với `Fs = 1000 Hz`, `f_N = 500 Hz`.  
Không đặt cutoff sát Nyquist nếu filter cần transition band.

## 3. Ước lượng sampling rate

\[
\Delta t_n = t_n-t_{n-1}
\]

\[
F_{s,\mathrm{est}} = 1/\operatorname{median}(\Delta t_n)
\]

Median giúp giảm ảnh hưởng của jitter nhỏ.

## 4. Windowing

\[
L = T_wF_s
\]

\[
H = L(1-r)
\]

\[
N_w = \left\lfloor\frac{N-L}{H}\right\rfloor + 1
\]

Ví dụ: 60 s, 1000 Hz, window 1 s, overlap 50%:
- `L = 1000`
- `H = 500`
- `Nw = 119`

## 5. Conduction velocity

\[
CV = d/\theta
\]

- `d`: khoảng cách điện cực.
- `θ`: độ trễ lan truyền.
- Thiếu `d` hoặc `θ` đáng tin cậy thì không tính CV.