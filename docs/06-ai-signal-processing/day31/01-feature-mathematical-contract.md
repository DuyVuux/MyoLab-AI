# Day 31 mathematical contract

Let `x[i]` be a finite, one-dimensional, upstream DC-removed window of `N`
samples. Let:

```text
X[k] = rfft(x, n=N)
P[k] = abs(X[k])²/N
f[k] = rfftfreq(N, 1/fs)
```

The time-domain contract is RMS, MAV, adjusted Fisher–Pearson skewness,
Fisher excess kurtosis, signed maximum/minimum, sample standard deviation
with `ddof=1`, and arithmetic mean.

The spectral contract is minimum, maximum, and sample standard deviation of
`P`; MDF as the first bin whose cumulative power is at least 50% of total
power; MNF as `sum(fP)/sum(P)`; and entropy as `-sum(p log2 p)` over strictly
positive probabilities.

All finite DC and Nyquist bins are included. Interior bins are not doubled.
The result is a periodogram power proxy rather than a calibrated physical PSD.

## Invariants

- Positive amplitude scaling by `a` scales amplitude features by `a`.
- Spectral min/max/std scale by `a²`.
- Skewness, kurtosis, MDF, MNF, and entropy are invariant to positive scale.
- Sign inversion negates mean and skewness, swaps signed extrema, and leaves
  power-derived features unchanged.
- Zero power yields missing MDF/MNF/entropy with `zero_power_window`.

MDF and MNF are descriptive signal features. They are not fatigue labels or
clinical conclusions.
