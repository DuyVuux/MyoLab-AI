# Task B — Data Specification cho Fatigue Context / Compensation

## Framing

Task B trước tiên là một context engine:

```text
feature trends
+ elapsed time
+ QC
+ protocol
→ fatigue context
→ confidence adjustment
→ abstention decision
```

Không bắt buộc là classifier fatigue/non-fatigue.

## Required inputs

- RMS/MAV windows và trends;
- MDF/MNF PSD-based features và trends;
- task elapsed time;
- force/MVC/RPE khi có;
- protocol phase;
- signal-quality flags;
- electrode/channel setup;
- MFCV only if eligibility gate passes.

## Public-data role

- Cerqueira fatigue: primary free/open engineering corpus.
- Hyser MVC/force: support contract, không phải direct fatigue ground truth.
- Các Zenodo fatigue records khác: TO_VERIFY nếu DOI/sample rate không rõ.

## Label provenance levels

```text
L0 — no fatigue label
L1 — self-perceived/RPE
L2 — protocol proxy/elapsed time
L3 — force decline or performance criterion
L4 — clinician/KTV adjudicated
```

Không trộn các mức thành cùng một ground-truth label mà không ghi provenance.

## MFCV boundary

MFCV chỉ dùng khi có:

```text
linear array
+ known IED
+ known order
+ fibre alignment
+ compatible raw signals
+ propagation evidence
```

Nếu thiếu:

```text
mfcv.status = ineligible
value = null
```
