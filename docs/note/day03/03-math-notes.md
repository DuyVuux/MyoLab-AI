# Day 3 Math Notes

## 1. Discrete time

```text
t[n] = n / Fs, n = 0, ..., N - 1
N = Fs × T
```

Example: `Fs=1000 Hz`, `T=70 s`:

```text
N = 70,000
last timestamp = 69.999 s
record span = 70.000 s
```

Explain why this is correct:

> TODO

## 2. Unit conversion

```text
1 V  = 1,000 mV = 1,000,000 uV
1 mV = 1,000 uV
```

Calculate:

- `0.002 mV = ____ uV`
- `25 uV = ____ mV`
- `3e-6 V = ____ uV`

## 3. Sampling-rate inference

```text
dt[n] = t[n] - t[n-1]
Fs_estimated = 1 / median(dt)
```

Why use median instead of mean?

> TODO

## 4. Timing jitter

```text
relative_jitter = median(|dt - median(dt)|) / median(dt)
```

Interpretation:

> TODO

## 5. Memory estimate

```text
bytes = samples × channels × bytes_per_value
```

Calculate time + 1 signal channel, float64, 70,000 samples:

> TODO

## 6. Synthetic active signal concept

```text
f_k(t) = f_k0 + (f_k1 - f_k0)t/T
phi_k(t) = 2π[f_k0 t + 0.5((f_k1-f_k0)/T)t²] + phi_k0
x(t) = A(t) Σ w_k sin(phi_k(t)) + noise(t)
```

This is an engineering simulation, not a physiological model. Explain the distinction:

> TODO
