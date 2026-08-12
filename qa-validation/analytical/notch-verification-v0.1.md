# Notch Analytical Verification v0.1

Status: **PASS**

Explicit synthetic research case: 50 Hz mains, Q=30, Fs=2000 Hz. No
site/default mains frequency is inferred.

- 50 Hz attenuation: 31.911 dB (required >25 dB).
- Unrelated 173 Hz amplitude ratio: 0.999911 (required >0.95).
- Pre-notch evidence ref: `spev_sha256_389ba54d4f31526d0cba881045886215a7101223ced91ece2b30ebd63669559f`.

The evidence reference is computed before modification and persists in result
provenance. Harmonics are filtered only when explicitly listed.
