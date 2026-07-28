# Day 26 — Search Strategy và Evidence Handling

## Mục tiêu

Chuẩn hóa cách sử dụng các review Day 26 mà không mở lại inventory Day 25 hoặc tự so sánh leaderboard giữa các paper không tương thích.

## Source hierarchy

1. Official standards, official documentation, official repositories/license texts.
2. Original peer-reviewed methodological studies.
3. Systematic/methodological reviews.
4. Internal project artifacts để khóa scope/terminology.
5. Preprints chỉ khi chưa có nguồn mạnh hơn.
6. Blog/marketing chỉ dùng discovery.

## Evidence states

```text
OFFICIAL_VERIFIED
PEER_REVIEWED_VERIFIED
REPOSITORY_VERIFIED
SITE_VERIFIED
PROJECT_LOCKED
INFERRED
NOT_VERIFIED
CONFLICTING
```

## Critical flaw flags

- subject/session/repetition leakage;
- random-window headline split;
- feature selection/scaling/calibration outside fold;
- outer-test threshold/model selection;
- missing label provenance;
- incompatible population/montage/task used for direct metric comparison;
- public healthy performance presented as Vinmec/stroke performance;
- raw score called probability;
- Task B circular fatigue label construction.

## Stop rule

Một study có critical flaw không được dùng để khóa benchmark/model decision, dù metric được báo cao.
