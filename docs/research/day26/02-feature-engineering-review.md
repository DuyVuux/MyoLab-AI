# Day 26 sEMG Clinical Intelligence Feature Engineering Review

## Phạm vi và phương pháp

Bản review này khóa **feature research blueprint** cho sEMG sparse-channel 4–16 kênh trong phạm vi Day 26, nghĩa là chỉ chốt **candidate families, windowing grid, normalization rules, feature-selection hygiene, và ranh giới sparse vs HD-sEMG**, chứ **không** huấn luyện, không chọn “feature winner”, không dùng test set, và không gộp Task A/B/C thành một lane kỹ thuật duy nhất. Các ràng buộc đó bám trực tiếp theo Day 26 protocol nội bộ hiện truy hồi được trong phiên này, trong đó Day 26 được định nghĩa là **protocol-level artifact**, `trainingAllowed=false`, human review bắt buộc, và mọi bước học từ dữ liệu phải nằm gọn trong fold huấn luyện/inner-validation. fileciteturn0file0

Về standards và appraisal backbone, blueprint này bám theo CEDE-Check và SENIAM cho reporting/preprocessing EMG; theo BMJ/TRIPOD+AI/PROBAST+AI cho prediction-model methodology, risk-of-bias và reporting; và theo literature về participant-aware validation trong dữ liệu repeated measures để tránh leakage khi segment bằng sliding windows. CEDE-Check nhấn mạnh bốn nhóm phải report rõ: task, electrode placement, recording characteristics, và acquisition/pre-processing; PROBAST+AI tách riêng chất lượng phát triển mô hình với risk of bias của đánh giá hiệu năng; còn BMJ 2024 series nhấn mạnh rằng development, internal-external validation và external validation không được nhập nhằng thành một con số “accuracy” duy nhất. citeturn2search2turn2search5turn0search0turn0search3turn1search1turn1search2turn0search0

Một giới hạn quan trọng của phiên nghiên cứu này là: trong `internal source pack` được nêu trong prompt, **chỉ có Day 26 protocol nội bộ là đang truy hồi được ở session hiện tại**; các file nội bộ còn lại được xem là **NOT_VERIFIED trong phiên này** nếu cần đối chiếu câu chữ hoặc artifact tree chính xác. Vì vậy, mọi claim khoa học bên dưới chỉ được nâng hạng khi có nguồn **official, peer-reviewed hoặc repository/offical documentation**; các suy luận kỹ thuật từ kinh nghiệm ML/sEMG sẽ được ghi rõ là **INFERRED** hoặc **NOT_VERIFIED** khi cần. fileciteturn0file0

## Search và screening log

Tôi đã chạy tìm kiếm seed-stage đến ngày **2026-07-27** trên BMJ, PubMed, CEDE/SENIAM, JMLR và official/repository documentation để khóa methodology. Vì giao diện web không luôn trả về tổng hit-count của database, các ô “records screened” dưới đây ghi theo **top surfaced records đã rà trong seed stage**; nơi không có tổng số database hit, tôi đánh dấu **NOT_VERIFIED** thay vì điền số giả. Các query được thiết kế quanh năm trục: feature definitions, robustness/stability, windowing-delay trade-off, normalization, feature selection leakage, và sparse-vs-HD-sEMG. citeturn2search2turn2search5turn1search1turn0search0turn0search3

| Database/site | Exact query | Search date | Records screened | Inclusion reason | Exclusion reason | Full-text availability | Final decision |
|---|---|---:|---:|---|---|---|---|
| BMJ | `TRIPOD+AI BMJ 2024 official prediction model AI` | 2026-07-27 | 4 surfaced hits | Official reporting guidance for AI prediction models | Rapid responses / duplicate BMJ mirrors | Yes | INCLUDE citeturn1search1turn0search0 |
| BMJ | `PROBAST+AI BMJ 2025 official` | 2026-07-27 | 4 surfaced hits | Official appraisal tool for bias/applicability | Non-article response pages | Yes | INCLUDE citeturn0search0turn0search3 |
| CEDE / SENIAM | `CEDE Check surface EMG checklist journal official`; `SENIAM surface EMG recommendations official pdf` | 2026-07-27 | 4 surfaced hits | Primary methodological standards for EMG reporting and placement | Non-official reps without provenance | Yes | INCLUDE citeturn2search2turn2search5 |
| PubMed / PMC | `Study of stability of time-domain features for electromyographic pattern recognition`; `electrode shift myoelectric pattern recognition` | 2026-07-27 | 6 surfaced hits | Direct evidence on shift/effort/fatigue robustness of features | Pure benchmark papers without robustness focus | Yes | INCLUDE citeturn7search1turn7search2turn7search0 |
| PubMed / Reviews | `Application of Surface Electromyography in Exercise Fatigue review`; `A statistical analysis of the spectral moments used in EMG tests of endurance` | 2026-07-27 | 5 surfaced hits | Direct evidence on fatigue-sensitive spectral behavior and record-length effects | Papers without explicit spectral-feature interpretation | Yes | INCLUDE citeturn8search0turn14search0 |
| PubMed | `Determining the optimal window length for pattern recognition-based myoelectric control`; `The optimal controller delay for myoelectric prostheses` | 2026-07-27 | 5 surfaced hits | Primary evidence for accuracy-delay trade-off | Papers without real-time/controller-delay framing | Yes | INCLUDE citeturn5search2turn5search7 |
| PubMed / JEK / Sensors | `How should we normalize electromyograms obtained from healthy participants`; `Sliding-Window Normalization to Improve the Performance... EMG` | 2026-07-27 | 6 surfaced hits | Direct evidence for normalization feasibility and calibration burden | Pure DL papers with unreported split regime | Yes | INCLUDE / CONDITIONAL citeturn9search0turn15search1turn16search0 |
| PubMed / JMLR / official docs | `Selection bias in gene extraction`; `Measuring the bias of incorrect application of feature selection`; `On the Stability of Feature Selection Algorithms`; `mRMR 2005` | 2026-07-27 | 8 surfaced hits | Decision-grade evidence for nested selection, bias and stability analysis | Non-primary summaries | Yes | INCLUDE citeturn10search7turn10search2turn10search0turn17search0turn17search5 |
| PubMed / HD-sEMG reviews | `Analysis of motor units with high-density surface electromyography`; `High density surface electromyography review spatial maps` | 2026-07-27 | 4 surfaced hits | Distinguish sparse-channel features from HD-only spatial features | Reviews without explicit grid/spatial discussion | Yes | INCLUDE citeturn13search2turn12search0 |

Từ screening này, ba nguyên tắc phương pháp luận được khóa sớm. Thứ nhất, **không dùng direct paper-to-paper accuracy comparison** giữa các protocol khác population, channel geometry, split unit hay session structure. Thứ hai, **participant/session-aware validation** là nền bắt buộc trước khi bàn feature. Thứ ba, **feature engineering phải được tách thành baseline nhóm nhỏ, có lý do sinh lý/tín hiệu học**, không mở kiểu “càng nhiều càng tốt” vì redundancy của sEMG features đã được chỉ ra nhiều lần trong literature. citeturn11search0turn19search6turn23search4turn10search2turn10search7

## Feature candidate catalog

Điểm khóa cho Day 26 là: **baseline sparse-channel nên ưu tiên feature families rẻ tính toán, định nghĩa rõ, tương thích 4–16 kênh, có khả năng giải thích và có ít dependency vào metadata chưa site-verified**. Evidence hiện có hỗ trợ mạnh nhất cho nhóm time-domain amplitude/complexity và low-order autoregressive coefficients; frequency-domain features có ích nhưng nhạy hơn với duration, force và spectral estimation regime; còn các feature thật sự “spatial” theo nghĩa bản đồ không gian 2D, propagation vectors, conduction velocity hoặc motor-unit decomposition thuộc về **HD-sEMG/grid regime**, không nên trộn vào sparse-channel baseline. citeturn3search2turn7search1turn7search0turn23search4turn24search6turn13search2turn12search0

Bảng dưới đây dùng quy ước chung: \(x[n]\) là tín hiệu trong một window dài \(N\) mẫu; \(P(f)\) là power spectrum/PSD; “sign invariance” là bất biến khi đảo dấu \(x \rightarrow -x\); các cột “Amp scale / Shift / Force / Fatigue / Window” dùng mức **Low / Med / High** để mô tả độ nhạy kỳ vọng. Những đánh giá này là tổng hợp từ Hudgins 1993; Tkach 2010; Young 2011; Phinyomark 2012–2014; Hary 1982; Sun 2022; Merletti 2008; CEDE/SENIAM; với các mục mà literature trực tiếp còn mỏng được ghi rõ là **INFERRED** trong diễn giải phía sau. citeturn3search2turn7search1turn7search0turn23search4turn24search6turn14search0turn8search0turn13search2turn2search2turn2search5

| Feature | Formula | Unit | Sign invariance | Minimum signal/window requirements | Amp scale | Electrode shift | Force level | Fatigue | Window duration | Sparse 4–16ch eligibility | HD-sEMG-only | Expected computational cost | Interpretability | Known failure modes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| RMS | \(\sqrt{\frac{1}{N}\sum x[n]^2}\) | µV | Yes | Stable sampling; works in short windows | High | Med | High | Med | Low–Med | Yes | No | Low | High | Conflates effort, gain, skin impedance, contact quality |
| MAV | \(\frac{1}{N}\sum |x[n]|\) | µV | Yes | Stable sampling; works in short windows | High | Med | High | Med | Low–Med | Yes | No | Low | High | Redundant with RMS/IEMG in many settings |
| Mean | \(\frac{1}{N}\sum x[n]\) | µV | No | Requires DC control/high-pass and artifact control | High | Med | Low | Low | Low | Yes | No | Low | Low–Med | Dominated by offset, motion artifact, baseline drift |
| Standard deviation | \(\sqrt{\frac{1}{N-1}\sum (x[n]-\bar x)^2}\) | µV | Yes | Adequate N; stable centering | High | Med | High | Med | Low–Med | Yes | No | Low | High | Near-redundant with RMS if mean ≈ 0 |
| Waveform Length | \(\sum_{n=1}^{N-1}|x[n+1]-x[n]|\) | µV per window | Yes | SNR sufficient; same N across windows | High | Med | High | Med | High | Yes | No | Low | High | Scales strongly with window size and noise |
| Zero Crossing | \(\sum \mathbf{1}[x_n x_{n+1}<0 \land |x_n-x_{n+1}|\ge \epsilon]\) | count | Yes, if symmetric threshold | Needs centering, threshold \(\epsilon\), adequate SNR | Med | Med | Med | Med | Med | Yes | No | Low | Med | Noise-floor dependent; threshold tuning can leak |
| Slope Sign Change | \(\sum \mathbf{1}[(x_n-x_{n-1})(x_n-x_{n+1})\ge \epsilon]\) | count | Yes, if symmetric threshold | Needs threshold and moderate SNR | Med | Med | Med | Med | Med | Yes | No | Low | Med | Very noise sensitive without thresholding |
| Willison Amplitude | \(\sum \mathbf{1}[|x[n+1]-x[n]|\ge \epsilon]\) | count | Yes | Needs threshold and stable gain | High | Med | Med | Med | Med | Yes | No | Low | Med | Threshold tied to gain/noise level |
| Integrated EMG | \(\sum |x[n]|\Delta t\) or \(\sum |x[n]|\) | µV·s or µV·sample | Yes | Stable window length and sampling rate | High | Med | High | Med | High | Yes | No | Low | High | Strongly window-length dependent; redundant with MAV |
| Skewness | \(\frac{1}{N}\sum \left(\frac{x[n]-\bar x}{s}\right)^3\) | dimensionless | No | Needs larger N and outlier control | Low | Med | Low | Low | High | Yes | No | Low | Low | Extremely sensitive to spikes/outliers |
| Kurtosis | \(\frac{1}{N}\sum \left(\frac{x[n]-\bar x}{s}\right)^4\) | dimensionless | Yes | Needs larger N and outlier control | Low | Med | Low | Low | High | Yes | No | Low | Low | Tail/outlier dominated; unstable in short windows |
| Median Frequency | \(f_m: \sum_{f\le f_m}P(f)=\frac{1}{2}\sum P(f)\) | Hz | Yes | Prefer ≥250–500 ms for stable PSD | Low for relative PSD | Med | High | High | High | Yes | No | Med | Med | Short-window PSD instability; force confounding |
| Mean Frequency | \(\frac{\sum fP(f)}{\sum P(f)}\) | Hz | Yes | Prefer ≥250–500 ms | Low for relative PSD | Med | High | High | High | Yes | No | Med | Med | More noise-sensitive than MDF in some settings |
| Spectral entropy | \(-\sum p_f\log p_f,\; p_f=P(f)/\sum P(f)\) | dimensionless | Yes | Stable PSD and declared band limits | Low | Med | Med | Med | High | Yes | No | Med | Med | Band-definition sensitive; noisy with short windows |
| Spectral moments | \(m_k=\sum f^kP(f)\) | power·Hz\(^k\) or ratio-specific | Yes | Stable PSD; high-order moments need longer N | Low–Med | Med | Med–High | Med–High | High | Yes | No | Med | Med | High-order moments unstable, noise-amplifying |
| Band power | \(\sum_{f\in B}P(f)\) | µV² or % total power | Yes | Declared band edges; PSD stable | High if absolute, Low if relative | Med | High | High | High | Yes | No | Med | High | Absolute power confounded by gain/contact |
| Peak frequency | \(\arg\max_f P(f)\) | Hz | Yes | Stable PSD, smoothing usually needed | Low | Med | Med | Med–High | High | Yes | No | Med | Med | Bin-resolution and local-noise sensitive |
| STFT summaries | Summary of \(|\mathrm{STFT}(t,f)|^2\) over time/freq bins | summary-dependent | Usually yes | Requires declared frame length/hop/window function | Low–Med | Med | Med | High | Med–High | Yes | No | Med | Med | Parameter proliferation; hidden tuning risk |
| Wavelet coefficients | \(W(a,b)=\frac{1}{\sqrt{|a|}}\int x(t)\psi^*\left(\frac{t-b}{a}\right)dt\) | implementation-dependent | Usually yes | Mother wavelet and scale set must be declared | Med | Med | Med | High | Med | Yes | No | Med–High | Med | Sensitive to mother wavelet and boundary effects |
| Wavelet packet energy | \(E_k=\sum |c_k|^2\) for packet \(k\) | signal² units | Yes | Declared packet tree and daubechies/order etc. | Med | Med | Med | High | Med | Yes | No | High | Med | High dimensional; selection instability risk |
| AR coefficients | \(x[n]=\sum_{k=1}^{p}a_kx[n-k]+e[n]\) | dimensionless | Yes after centering | Need \(N \gg p\); low-order \(p=4\) or \(6\) for short windows | Low | Low–Med | Med | Med | Med | Yes | No | Low–Med | Med | Order-selection sensitivity; unstable if too short/noisy |
| Channel activation ratios | \(r_i=\mathrm{RMS}_i/\sum_j\mathrm{RMS}_j\) or pairwise ratios | dimensionless | Usually yes | ≥2 simultaneous channels; fixed montage | Low if common scaling, High if per-channel gain differs | High | Med | Med | Low–Med | Conditional | No | Low | High | Not comparable if montage/order changes |
| Inter-channel covariance | \(\mathrm{Cov}(x_i,x_j)\) | µV² | No | ≥2 channels; simultaneous acquisition; adequate N | High | High | Med | Med | Med | Conditional | No | Low–Med | Med | Dominated by gain and common-mode artifacts |
| Correlation structure | \(\rho_{ij}=\frac{\mathrm{Cov}(x_i,x_j)}{\sigma_i\sigma_j}\) | dimensionless | Yes | Same as above; stable N | Low | High | Med | Med | Med | Conditional | No | Low–Med | Med | Undervalues amplitude texture; unstable if low variance |
| Co-contraction index | One common Rudolph-type form: \(\frac{1}{n}\sum \frac{\text{lowerEMG}_i}{\text{higherEMG}_i}\frac{\text{lowerEMG}_i+\text{higherEMG}_i}{2}\times100\) | dimensionless | No | Requires antagonist-pair mapping and envelope definition | High | High | High | High | Med | Conditional | No | Low | High | Formula variant-dependent; normalization method changes value materially |
| Channel-order patterns | Rank order of per-channel amplitudes | ordinal / unitless | Yes | Fixed channel order and repeated placement | Low | High | Med | Med | Low | Conditional | No | Low | Med | Breaks under electrode re-ordering/repositioning |
| Spatial moments | \(m_{pq}=\sum x_i^py_i^q a_i\) over 2D channel coordinates | order-dependent | Usually yes | Requires known 2D geometry and adequate spatial sampling | Med | Very High | Med | Med | Med | No for sparse baseline | Yes | Low–Med | Med | Unstable or ill-posed on sparse/nonuniform montages |

Từ bảng này, recommendation ở mức **evidence-supported** cho sparse baseline là: ưu tiên **RMS, WL, và low-order AR coefficients** như lõi ban đầu; giữ **MAV/IEMG/SD** ở vai trò comparator chứ không gom hết vào baseline vì redundancy cao; dùng **ZC/SSC/WAMP** theo chế độ optional vì thresholding và noise-floor dễ trở thành hidden hyperparameter; còn **MDF/MNF/band power** chỉ vào grid khi đã khai báo window dài hơn và mục tiêu có ý nghĩa phổ rõ ràng. Điều này phù hợp với Hudgins 1993, Tkach 2010, Young 2011, Phinyomark 2012–2014 và các review về robust feature behavior. citeturn3search2turn7search1turn7search2turn7search0turn24search6turn23search4

Recommendation ở mức **engineering hypothesis** là: spectral entropy, spectral moments, STFT summaries, wavelet packet energies, covariance/correlation-structure và channel-order patterns có thể hữu ích cho later experiments, nhưng chỉ khi được khóa rõ preprocessing, band definition, montage geometry và nested selection. Recommendation ở mức **site verification required** là: co-contraction features cần cặp agonist–antagonist, linear envelope recipe và normalization regime được chuẩn hóa tại site; spatial moments và toàn bộ “activation map / propagation / conduction velocity / motor-unit decomposition” là **HD-sEMG-only**, không nên đưa vào sparse-channel baseline từ Day 26. citeturn26search4turn25search1turn13search2turn12search0

## Windowing blueprint

Evidence về windowing trong myoelectric control nhất quán ở một điểm: **window càng dài thì feature/classification thường ổn định hơn, nhưng controller delay cũng tăng**. Farrell và Weir cho thấy controller delay tối ưu trong bài toán prosthetic control nằm khoảng 100–125 ms; Englehart/Hudgins và review prosthetic-control đều nhấn mạnh 100–250 ms là miền sử dụng phổ biến; còn bài toán cân bằng lỗi phân loại và controllability cho thấy **150–250 ms** là vùng tối ưu hợp lý cho hệ pattern-recognition cụ thể được khảo sát. Đồng thời, literature về spectral moments chỉ ra record length dài hơn cải thiện signal-to-noise ratio của spectral estimates; vì vậy những feature phổ/tfatigue-oriented không nên bị “ép” vào cùng một window rất ngắn chỉ vì thói quen gesture recognition. citeturn5search7turn5search0turn5search2turn6search1turn14search0turn8search0

| Window | Approx. FFT bin spacing at 1 kHz | Strength | Main risks | Task fit | Day 26 role |
|---|---:|---|---|---|---|
| 150 ms | 6.7 Hz | Fastest among requested set; good for low-latency gesture updates | Weak spectral stability; higher transition contamination | Task A strongest; Task B/C weak | Mandatory candidate |
| 200 ms | 5 Hz | Good compromise between latency and feature stability | Still limited for fatigue/spectral metrics | Task A primary; Task B conditional | Mandatory candidate |
| 250 ms | 4 Hz | Strong literature support for accuracy–delay trade-off | Slightly higher lag than 150–200 ms | Task A primary; Task B conditional | Mandatory candidate |
| 500 ms | 2 Hz | Better PSD stability; more suitable for fatigue context and quantitative summaries | More mixed-state windows; higher delay | Task B/C stronger; Task A secondary | Mandatory candidate |
| 1000 ms | 1 Hz | Strongest spectral stability of requested set | Poor real-time responsiveness; transition mixing | Task B/C strongest; Task A mainly as stress test | Mandatory candidate |
| 100–125 ms | 8–10 Hz | Literature-supported fast-control alternative | Too short for robust spectral summaries | Task A only | Optional literature-supported alternative |
| 300 ms | 3.3 Hz | Intermediate stress-test between 250 and 500 ms | Still noticeable lag | Task A/B bridge window | Optional literature-supported alternative |

Vì overlapping windows tạo tương quan rất mạnh giữa samples, **split-first, segment-second** là rule bắt buộc. Nói cách khác: subject/session/trial partition phải được khóa trước; sau đó mới segmentation trong từng partition; tuyệt đối không được tạo toàn bộ windows trước rồi random split. Literature repeated-measures trong digital health/human participants cho thấy record-wise split gây identity confounding, còn literature HAR cho thấy overlapping windows thường chỉ “có vẻ” cải thiện khi validation bị subject-dependent leakage; khi evaluation là subject-independent, lợi thế overlap giảm rất mạnh hoặc biến mất trong khi chi phí tính toán và storage tăng lên đáng kể. citeturn11search0turn19search2turn19search6

Vì vậy, Day 26 nên khóa **experiment grid cho overlap theo increment**, không khóa một tỷ lệ duy nhất. Tôi đề xuất grid dưới đây:

| Analysis window | Candidate increments | Equivalent overlap |
|---|---|---|
| 150 ms | 25, 50, 75, 150 ms | 83%, 67%, 50%, 0% |
| 200 ms | 25, 50, 100, 200 ms | 88%, 75%, 50%, 0% |
| 250 ms | 25, 50, 125, 250 ms | 90%, 80%, 50%, 0% |
| 500 ms | 50, 100, 250, 500 ms | 90%, 80%, 50%, 0% |
| 1000 ms | 100, 250, 500, 1000 ms | 90%, 75%, 50%, 0% |

Grid này cho phép tách bạch ba câu hỏi khác nhau mà literature thường trộn lẫn. Thứ nhất là **buffer length** để tính feature. Thứ hai là **update interval** để ra quyết định mới. Thứ ba là **label contamination near transitions**. Với Task A, nên đánh giá tối thiểu hai label regimes: **steady-state windows only** và **transition-inclusive windows with explicit label rule**. Với Task B, 500–1000 ms nên được ưu tiên hơn vì fatigue/context features thường cần độ ổn định phổ tốt hơn. Với Task C, 250–1000 ms là hợp lý hơn 150–200 ms nếu mục tiêu là quantitative assessment chứ không phải phản hồi điều khiển tức thì. citeturn5search2turn5search4turn8search0turn14search0

## Normalization và feature selection

Normalization là chỗ dễ phát sinh leakage nhất sau split regime. Burden nhấn mạnh rằng EMG normalization là cần thiết nếu so sánh giữa lần gắn lại điện cực, giữa cơ hay giữa cá thể; đồng thời ông cũng lưu ý rằng không có một normalization reference duy nhất bảo đảm phản ánh “maximal activation capacity” trong mọi bối cảnh. Cùng lúc đó, literature mới hơn về EMG motion prediction cho thấy các biến thể z-score/causal sliding-window normalization có thể cải thiện usability khi không muốn yêu cầu calibration nặng trước mỗi lần dùng. Chính vì vậy, Day 26 không nên chọn một normalization winner, mà nên khóa **eligibility rules + leakage rules + deployment assumptions** cho từng họ normalization. citeturn9search0turn22search4turn15search1turn16search0

| Normalization method | Information required | Leakage risk if misused | Cross-session suitability | Clinical feasibility | Behavior when calibration is poor | Deployment-time requirement | Evidence status | Day 26 status |
|---|---|---|---|---|---|---|---|---|
| No normalization | None | Low | Poor across re-application/session | Highest | Fragile to gain/contact drift | None | PEER_REVIEWED_VERIFIED / INFERRED | Mandatory comparator |
| Per-channel z-score | Mean and SD per channel | **High** if fit globally before CV | Moderate if source/target reasonably aligned | Moderate | Sensitive to drifting mean/variance unless causal/adaptive | Stored training stats or calibration segment | PEER_REVIEWED_VERIFIED | Optional baseline |
| Robust scaling | Median and IQR per channel | **High** if fit globally | Moderate; more outlier-robust than z-score | Moderate | Better under spikes/artifacts; still drift-sensitive | Stored robust stats or calibration segment | INFERRED for EMG-specific superiority | Optional baseline |
| Rest-baseline normalization | Standardized quiet-rest segment | Med–High if estimated from future/full session | Conditional | Variable; depends on patient ability to relax | Fails when rest is contaminated or tone is abnormal | Reliable rest capture at deployment | NOT_VERIFIED for this project population | Site-confirmed optional only |
| MVC normalization | Standardized MVC/MVIC protocol | Low if protocol external to model fitting; high if chosen opportunistically | Potentially good if protocol repeatable | Sometimes poor in rehab/clinical populations | Fails when effort inconsistent, painful, weak, or unsafe | Repeatable MVC acquisition | PEER_REVIEWED_VERIFIED, but site feasibility required | Prohibited as default; conditional only |
| Per-session statistics | Calibration segment each session | **High** if full session or future samples are used | Good for session alignment | Moderate if short calibration is acceptable | Can recover session drift; hurts zero-calibration workflow | Declared pre-use session buffer | INFERRED / partial EMG support | Later experiment |
| Per-channel maximum / dynamic-contraction normalization | Reference maximal/dynamic amplitude | Med–High if reference estimated opportunistically | Variable | Lower usability than no-calibration methods | Highly unstable across days/users | Reference capture each use | PEER_REVIEWED_VERIFIED / project-transfer-limited | Optional comparator only |
| Training-population normalization | Population-level stats from training folds | **High** if fit on all data | Useful only when deployment domain resembles training | High operational simplicity | Mis-scales under domain shift | Fixed stored transform | INFERRED / generic ML + limited EMG support | Optional baseline |
| Domain / adaptive normalization | Unlabeled target-domain stream or calibration buffer | **Very High** if future/held-out data are consumed improperly | Potentially best for drift-heavy deployment | Depends on implementation | Can help drift, but adds governance complexity | Causal target stats or adaptation mechanism | PEER_REVIEWED_VERIFIED for sliding-window z-score; broader DA claims mixed | Later experiment |

Từ bảng trên, bốn leakage rules nên được khóa ngay. Một là: **mọi training-population stat, scaler, robust scaler, feature normalizer đều phải fit bên trong training/inner-validation fold**. Hai là: nếu dùng **per-session** hoặc **adaptive/sliding-window normalization** trong evaluation, statistic chỉ được tính từ **deployment-available calibration buffer hoặc causal past window**, tuyệt đối không dùng toàn bộ session hậu nghiệm. Ba là: **MVC/rest-based normalization không được dùng làm default** vì nó thêm burden protocol, dễ thiếu nhất quán ở rehab setting, và có thể không khả thi ở population có yếu cơ, đau hoặc motor impairment. Bốn là: normalization recipe phải được log như một phần của deployment contract, không được “ẩn” trong notebook preprocessing. citeturn10search2turn10search7turn9search0turn15search1turn16search0

Feature selection cũng phải bị khóa bằng nested validation chặt chẽ. Ambroise–McLachlan cho thấy selection bias xuất hiện ngay khi chọn feature trước cross-validation; Demircioğlu cho thấy việc áp dụng feature selection sai vị trí có thể tạo bias lớn ở AUC/accuracy; còn Nogueira nhấn mạnh rằng feature selection phải được đánh giá không chỉ bằng performance mà còn bằng **stability**. Vì vậy, vị trí hợp lệ duy nhất của feature selection trong Day 26 blueprint là **bên trong inner training fold**, sau khi outer split đã khóa và trước khi outer test được mở ra. citeturn10search7turn10search2turn10search0

| Selector | Core mechanism | Interaction with scaler | Interaction with correlated features | Stability expectation | Recommended role | Leakage-safe use |
|---|---|---|---|---|---|---|
| mRMR | Max relevance + min redundancy, thường dựa trên MI | Usually mild, but estimator/discretization dependent | Better than pure MI at redundancy control | Moderate | Strong first-stage filter for wide handcrafted space | Fit only in inner fold; selected-k chosen in inner loop |
| Mutual information ranking | Rank each feature by MI to target | Depends on estimator/discretization | Poor redundancy control | Low–Moderate | Simple screen, not final selector alone | Inner fold only; follow with redundancy control |
| L1 / LASSO-type embedded selection | Shrinks coefficients; zeroes some features | **Scale-sensitive** | Tends to select one among correlated family arbitrarily | Often unstable under collinearity | Good if tied to sparse linear baseline, not universal truth | Alpha tuned in inner loop; refit only on outer-train |
| Sequential selection | Wrapper adding/removing features using model score | Depends on wrapped estimator | Can exploit interactions, but overfits easily | Low on small n / repeated measures | Later experiment only | Inner fold only; computational budget must be capped |
| Permutation importance | Model-specific score drop after shuffling feature | Uses already-scaled fitted model | Underestimates importance when features are correlated | Moderate for auditing, weak as sole selector | Best as inspection/audit, secondary selector | Compute on validation data inside inner loop, not outer test |
| Model-native importance | Embedded importance from fitted estimator, e.g. trees | Depends on estimator | Often biased by correlation / feature cardinality | Variable | Exploratory only | Never sole decision-maker; if used, must be inner-fold only |

Day 26 nên khóa thêm một **stability analysis bundle** cho selection: selection frequency of each feature across inner folds, median selected subset size, outer-fold reproducibility, và một stability metric có nền tảng thống kê như Nogueira stability. Nếu một feature chỉ xuất hiện rải rác hoặc đảo hạng mạnh theo fold/session split, feature đó không nên được nâng lên thành “mandatory baseline” chỉ vì score tức thời của một run. Đồng thời, permutation importance và tree-native importance không được dùng như “bằng chứng bản chất” của feature value; chúng chỉ phản ánh mức độ phụ thuộc của **một fitted model cụ thể** vào feature đó, và literature/official docs đều cảnh báo chúng bị méo dưới multicollinearity. citeturn10search0turn18search2turn17search3

Một pipeline hợp lệ cho Day 26 có thể viết ngắn gọn như sau:

```yaml
schema_version: "1.0"
status: "PROVISIONAL"
rationale: >
  Feature selection, scaling, calibration and thresholding must be nested inside
  grouped training/inner-validation only.
evidence_ids:
  - FS-AMBROISE-2002
  - FS-DEMIRCIOGLU-2021
  - FS-NOGUEIRA-2018
  - VAL-BMJ-2024
open_questions:
  - "What is the final split unit: subject, session, or subject-within-session?"
  - "Will any deployment-time calibration buffer be allowed?"
pipeline_contract:
  outer_split: "group-aware by subject/session/trial before windowing"
  inner_loop:
    - "fit scaler on inner-train only"
    - "fit selector on inner-train only"
    - "tune selector hyperparameters and model hyperparameters on inner-val only"
    - "if needed, fit calibration/abstention thresholds on inner-val only"
  outer_evaluation:
    - "refit locked pipeline on outer-train"
    - "evaluate once on outer-test"
  prohibited:
    - "global feature selection before cross-validation"
    - "global z-score/robust scaling before grouped split"
    - "permutation importance on outer-test for selection decisions"
```

## Handoff cho Day 26 Experiment Blueprint

Phần này là handoff ở mức **Go-with-conditions** cho workstream feature engineering. Kết luận ngắn gọn là: sparse-channel baseline nên bắt đầu hẹp, giải thích được, và leakage-safe; mọi thứ giống “spatial map” theo nghĩa 2D grid phải bị tách ra khỏi sparse baseline; normalization không có winner mặc định; feature selection bắt buộc nằm trong nested validation; và overlap chỉ là một dimension của experiment grid chứ không phải benchmark regime. Những kết luận này được hỗ trợ mạnh bởi literature về EMG feature robustness, window-length trade-off, normalization burden, selection bias và HD-sEMG applications. citeturn7search1turn7search0turn24search6turn5search2turn9search0turn15search1turn10search7turn10search2turn13search2turn12search0

### Provisional decisions

| Area | Provisional decision | Evidence class |
|---|---|---|
| Sparse-channel mandatory baseline | Start with **RMS + WL + AR4** as core sparse baseline; keep baseline intentionally small | evidence-supported citeturn7search1turn7search0turn24search6 |
| Sparse-channel optional baseline | Add **MAV, SD, IEMG, ZC, SSC, WAMP, MDF, MNF, band power, channel activation ratios** as controlled comparators | evidence-supported / conditional citeturn3search2turn23search4turn8search0 |
| Later experiments | **Spectral entropy, spectral moments, STFT summaries, wavelet coefficients, wavelet packet energy, inter-channel covariance/correlation, co-contraction, channel-order patterns** | engineering hypothesis / conditional citeturn14search0turn14search2turn26search4turn25search4 |
| HD-sEMG only | **Spatial moments, activation heat maps, propagation vectors, conduction velocity, innervation zone localization, motor-unit decomposition metrics** | evidence-supported citeturn13search2turn12search0 |
| Window candidates | Mandatory: 150, 200, 250, 500, 1000 ms; optional: 100–125 and 300 ms | evidence-supported citeturn5search2turn5search7turn5search0 |
| Overlap regime | Use increment grid; do not lock a single overlap value; split-before-windowing mandatory | evidence-supported citeturn19search2turn11search0turn19search6 |
| Normalization | No default winner; keep no-normalization comparator; z-score/robust/per-session/MVC as separate regimes with deployment contracts | evidence-supported / conditional citeturn9search0turn15search1turn16search0 |
| Feature selection | mRMR or MI as first filter; L1 as embedded sparse comparator; wrappers later only; all nested | evidence-supported citeturn17search0turn17search5turn17search2turn10search7turn10search2 |

### Rejected alternatives và lý do

| Rejected alternative | Reason |
|---|---|
| “Đưa toàn bộ feature vào baseline rồi để model tự chọn” | Trái nguyên tắc anti-redundancy và làm tăng selection bias/leakage risk; EMG literature đã chỉ ra redundancy mạnh giữa nhiều handcrafted features. citeturn23search4turn10search7turn10search2 |
| Dùng random-window split làm benchmark chính | Repeated-measures leakage và identity confounding có thể làm metric bị thổi phồng. citeturn11search0turn19search2turn19search6 |
| Chọn overlap cao mặc định vì “literature hay dùng” | Overlap chủ yếu tăng update density và tương quan sample; không có lý do đủ mạnh để khóa thành benchmark setting duy nhất. citeturn6search1turn19search2 |
| Dùng MVC normalization mặc định cho toàn bộ project | Khó khả thi đồng đều trong rehab/clinical setting; effort inconsistency làm reference kém tin cậy. citeturn9search0turn22search1 |
| Dùng permutation importance hoặc tree-native importance làm selector chính | Quá phụ thuộc model cụ thể và méo dưới multicollinearity. citeturn18search2turn17search3 |
| Trộn spatial-moment features của HD-sEMG vào sparse 4–16 kênh baseline | Vi phạm ranh giới hình học và sampling density; dễ tạo pseudo-spatial claims trên montage không đủ dày. citeturn13search2turn12search0 |

### NOT_VERIFIED items

| Item | Status |
|---|---|
| Exact content của các internal source files ngoài Day 26 protocol đang nêu trong prompt | NOT_VERIFIED |
| Final Noraxon/myoRESEARCH export fields tại site đủ cho co-contraction, per-session baseline, hay channel-coordinate metadata | NOT_VERIFIED |
| Final sparse montage geometry của project có cố định đủ để dùng channel-order patterns hoặc spatial-like ratios nhất quán hay không | NOT_VERIFIED |
| Final Task C label provenance và whether normalization references được thu nhất quán tại site | NOT_VERIFIED |
| Feasibility của MVC/rest-baseline protocol trong Vinmec/clinical workflow thực tế | NOT_VERIFIED |
| Eligibility của mọi fatigue-context feature cho population có neurological impairment | NOT_VERIFIED |

### Evidence matrix rows

Các row dưới đây là **selected evidence rows** cho workstream này. Tôi giữ đúng schema yêu cầu, điền `NOT_APPLICABLE` hoặc `NOT_VERIFIED` khi trường không phù hợp hay không được source report trực tiếp. Các decision-grade rows ở đây đại diện cho nguồn “xương sống” của blueprint, không phải toàn bộ bibliography. citeturn3search2turn7search1turn7search0turn5search2turn9search0turn15search1turn10search7turn10search2turn10search0turn13search2turn12search0

```yaml
selected_evidence_matrix_rows:
  - evidence_id: FEAT-HUDGINS-1993
    workstream: feature_engineering
    research_question: "Which classical short-window features are canonical for sparse-channel myoelectric pattern recognition?"
    claim: "Classical time-domain features are a legitimate starting point for sparse-channel gesture decoding."
    decision_implication: "Supports a small classical sparse baseline before any deep or high-dimensional expansion."
    source_title: "A new strategy for multifunction myoelectric control"
    source_type: "PEER_REVIEWED_PRIMARY"
    authors: "Hudgins B, Parker P, Scott RN"
    year: 1993
    doi_or_official_url: "10.1109/10.204774"
    population: "Human myoelectric control users"
    n_subjects: "NOT_VERIFIED_FROM_ABSTRACT"
    clinical_or_healthy: "Mixed / NOT_VERIFIED"
    muscle_or_anatomical_region: "Upper limb residual/forearm myoelectric sites"
    task_or_protocol: "Multifunction myoelectric control"
    device: "Surface EMG"
    channel_count: "Single to few channels"
    electrode_geometry: "Sparse"
    n_sessions_or_days: "NOT_VERIFIED"
    window_length: "Short segmented windows"
    overlap: "NOT_VERIFIED"
    feature_set: "Canonical time-domain feature family"
    model: "ANN in original study"
    split_unit: "NOT_VERIFIED"
    validation_regime: "Historical pattern-recognition study"
    metric: "Control/classification performance"
    main_finding: "Canonical TD family became the classical starting point for myoelectric control."
    limitations: "Old study; reporting not aligned to current split-hygiene expectations."
    project_transferability: "High as historical baseline rationale, low for direct metric comparison."
    evidence_status: "PEER_REVIEWED_VERIFIED"
    reviewer_note: "Use for feature-family provenance, not for benchmarking."

  - evidence_id: FEAT-TKACH-2010
    workstream: feature_engineering
    research_question: "Which features are more robust to electrode shift, effort variation, and fatigue?"
    claim: "Electrode shift and effort variation degrade many features more than fatigue; AR/cepstral families showed greater robustness than many isolated TD features."
    decision_implication: "Justifies including low-order AR as baseline-eligible and avoiding an all-TD-only baseline."
    source_title: "Study of stability of time-domain features for electromyographic pattern recognition"
    source_type: "PEER_REVIEWED_PRIMARY"
    authors: "Tkach D, Huang H, Kuiken TA"
    year: 2010
    doi_or_official_url: "10.1186/1743-0003-7-21"
    population: "Human participants"
    n_subjects: "NOT_VERIFIED_FROM_SNIPPET"
    clinical_or_healthy: "Healthy"
    muscle_or_anatomical_region: "Biceps and triceps region"
    task_or_protocol: "Motion classification under induced disturbances"
    device: "Surface EMG grids with derived channel pairs"
    channel_count: "Multichannel derived to SD pairs"
    electrode_geometry: "Grid-derived sparse pairs"
    n_sessions_or_days: "Single study with disturbance conditions"
    window_length: "N-sample windows"
    overlap: "NOT_VERIFIED"
    feature_set: "11 TD features plus combined feature sets"
    model: "LDA"
    split_unit: "Condition-wise train/test"
    validation_regime: "Disturbance robustness study"
    metric: "Classification accuracy and stability index"
    main_finding: "Muscle fatigue had smaller impact than electrode shift and effort; robust combined feature sets outperformed unstable ones."
    limitations: "Upper-limb healthy data; not site-specific."
    project_transferability: "High for robustness ranking logic, moderate for exact feature set transfer."
    evidence_status: "PEER_REVIEWED_VERIFIED"
    reviewer_note: "Important for sparse baseline design and robustness framing."

  - evidence_id: FEAT-YOUNG-2011
    workstream: feature_engineering
    research_question: "How does electrode shift affect feature-set choice in sparse-channel pattern recognition?"
    claim: "AR feature sets reduced sensitivity to electrode shift versus traditional TD set; four to six channels were sufficient in that study."
    decision_implication: "Supports AR eligibility and avoids assuming more channels automatically solve robustness."
    source_title: "Improving myoelectric pattern recognition robustness to electrode shift by changing interelectrode distance and electrode configuration"
    source_type: "PEER_REVIEWED_PRIMARY"
    authors: "Young AJ, Hargrove LJ, Kuiken TA"
    year: 2011
    doi_or_official_url: "10.1109/TBME.2011.2177662"
    population: "Human participants"
    n_subjects: "NOT_VERIFIED_FROM_SNIPPET"
    clinical_or_healthy: "Healthy / amputee-context transfer question"
    muscle_or_anatomical_region: "Upper limb"
    task_or_protocol: "Pattern recognition under electrode shift"
    device: "Surface EMG"
    channel_count: "4–6 channels among tested configurations"
    electrode_geometry: "Sparse multichannel"
    n_sessions_or_days: "Shift conditions"
    window_length: "NOT_VERIFIED"
    overlap: "NOT_VERIFIED"
    feature_set: "Traditional TD versus AR set"
    model: "LDA"
    split_unit: "Shift-condition train/test"
    validation_regime: "Robustness experiment"
    metric: "Classification error and controllability"
    main_finding: "AR set significantly reduced sensitivity to electrode shift compared with traditional TD set."
    limitations: "Not a clinical rehabilitation validation study."
    project_transferability: "High for robustness logic; moderate for exact channel-count inference."
    evidence_status: "PEER_REVIEWED_VERIFIED"
    reviewer_note: "Do not overgeneralize the 4–6 channel finding outside similar protocols."

  - evidence_id: WIN-FARRELL-2011
    workstream: windowing
    research_question: "Which analysis windows best trade off error and delay for myoelectric control?"
    claim: "Longer windows reduce classification error but worsen delay; in the studied system the optimal range was 150–250 ms."
    decision_implication: "Makes 150/200/250 ms mandatory candidates for Task A."
    source_title: "Determining the optimal window length for pattern recognition-based myoelectric control: balancing the competing effects of classification error and controller delay"
    source_type: "PEER_REVIEWED_PRIMARY"
    authors: "Farrell TR, et al."
    year: 2011
    doi_or_official_url: "10.1088/1741-2560/8/3/036005"
    population: "Able-bodied subjects"
    n_subjects: 13
    clinical_or_healthy: "Healthy"
    muscle_or_anatomical_region: "Upper limb myoelectric control context"
    task_or_protocol: "Virtual prosthesis controllability"
    device: "Surface EMG"
    channel_count: "2 or 4"
    electrode_geometry: "Sparse"
    n_sessions_or_days: "Multiple sessions"
    window_length: "50–550 ms studied"
    overlap: "Window increment considered"
    feature_set: "Pattern-recognition feature pipeline"
    model: "Pattern classifier family"
    split_unit: "Within-study protocol"
    validation_regime: "Offline and real-time controllability"
    metric: "Classification error and TAC performance"
    main_finding: "Optimal trade-off in that system was between 150 and 250 ms."
    limitations: "Specific hardware, tasks and population."
    project_transferability: "High for experiment-grid design, not for choosing a universal single window."
    evidence_status: "PEER_REVIEWED_VERIFIED"
    reviewer_note: "Use as grid justification, not as a one-value lock."

  - evidence_id: NORM-BURDEN-2010
    workstream: normalization
    research_question: "What are the trade-offs of EMG amplitude normalization methods?"
    claim: "Normalization is needed for comparisons across electrode reapplication, muscles and individuals; isometric MVC is endorsed in healthy participants, but no method guarantees true maximal activation interpretation."
    decision_implication: "MVC normalization can be conditionally studied but not assumed default or universally feasible."
    source_title: "How should we normalize electromyograms obtained from healthy participants? What we have learned from over 25 years of research"
    source_type: "PEER_REVIEWED_REVIEW"
    authors: "Burden A"
    year: 2010
    doi_or_official_url: "10.1016/j.jelekin.2010.07.004"
    population: "Healthy participants"
    n_subjects: "Review"
    clinical_or_healthy: "Healthy"
    muscle_or_anatomical_region: "Multiple muscles"
    task_or_protocol: "Normalization methods review"
    device: "Surface EMG"
    channel_count: "Multiple"
    electrode_geometry: "Multiple"
    n_sessions_or_days: "Review"
    window_length: "NOT_APPLICABLE"
    overlap: "NOT_APPLICABLE"
    feature_set: "Normalization reference methods"
    model: "NOT_APPLICABLE"
    split_unit: "NOT_APPLICABLE"
    validation_regime: "Review of methodological studies"
    metric: "Reliability, inter-individual variability, comparability"
    main_finding: "Normalization is necessary for many comparison tasks; MVC methods are often reliable in healthy settings."
    limitations: "Healthy-focused; not a rehabilitation-specific feasibility paper."
    project_transferability: "Moderate; needs site confirmation for clinical workflow."
    evidence_status: "PEER_REVIEWED_VERIFIED"
    reviewer_note: "Use for feasibility framing, not as blanket instruction to use MVC."

  - evidence_id: NORM-TANAKA-2022
    workstream: normalization
    research_question: "Can calibration-light normalization improve usability in EMG motion prediction?"
    claim: "Sliding-window z-score normalization improved performance over non-normalized and simple z-score comparators in the studied elbow-motion task."
    decision_implication: "Adaptive/domain normalization is eligible for later experiments but should not replace simple baselines on Day 26."
    source_title: "Sliding-Window Normalization to Improve the Performance of Machine-Learning Models for Real-Time Motion Prediction Using Electromyography"
    source_type: "PEER_REVIEWED_PRIMARY"
    authors: "Tanaka T, Nambu I, Maruyama Y, Wada Y"
    year: 2022
    doi_or_official_url: "10.3390/s22135005"
    population: "Human participants"
    n_subjects: "NOT_VERIFIED_FROM_SNIPPET"
    clinical_or_healthy: "Healthy"
    muscle_or_anatomical_region: "Elbow-related EMG"
    task_or_protocol: "Real-time motion prediction"
    device: "Surface EMG"
    channel_count: "NOT_VERIFIED_FROM_SNIPPET"
    electrode_geometry: "Sparse"
    n_sessions_or_days: "NOT_VERIFIED"
    window_length: "Sliding-window real-time processing"
    overlap: "Sliding windows"
    feature_set: "Normalization-focused pipeline"
    model: "Machine-learning classifier"
    split_unit: "Subject-own and other-subject models"
    validation_regime: "Offline performance study"
    metric: "Accuracy"
    main_finding: "Sliding-window normalization improved performance and reduced calibration burden in that setup."
    limitations: "Single-joint task and limited protocol generalizability."
    project_transferability: "Moderate for later experiments; not enough to make it default for all tasks."
    evidence_status: "PEER_REVIEWED_VERIFIED"
    reviewer_note: "Treat as adaptive-normalization evidence, not universal best practice."

  - evidence_id: FS-LEAKAGE-2002-2021
    workstream: feature_selection
    research_question: "Where must feature selection occur to avoid leakage?"
    claim: "Feature selection before cross-validation produces optimistic bias; selection must be nested within training folds."
    decision_implication: "Locks selector placement inside inner folds only."
    source_title: "Selection bias in gene extraction on the basis of microarray gene-expression data; Measuring the bias of incorrect application of feature selection when using cross-validation in radiomics"
    source_type: "PEER_REVIEWED_PRIMARY_AND_METHOD_PAPER"
    authors: "Ambroise C, McLachlan G; Demircioğlu A"
    year: "2002; 2021"
    doi_or_official_url: "10.1073/pnas.102102699; 10.1186/s13244-021-01115-1"
    population: "Biomedical ML datasets"
    n_subjects: "Dataset-dependent"
    clinical_or_healthy: "Mixed biomedical data"
    muscle_or_anatomical_region: "NOT_APPLICABLE"
    task_or_protocol: "Feature-selection methodology"
    device: "NOT_APPLICABLE"
    channel_count: "NOT_APPLICABLE"
    electrode_geometry: "NOT_APPLICABLE"
    n_sessions_or_days: "NOT_APPLICABLE"
    window_length: "NOT_APPLICABLE"
    overlap: "NOT_APPLICABLE"
    feature_set: "High-dimensional feature spaces"
    model: "Multiple"
    split_unit: "Cross-validation folds"
    validation_regime: "Methodological bias studies"
    metric: "Bias in AUC/accuracy and generalization estimates"
    main_finding: "Incorrect selector placement can substantially inflate performance estimates."
    limitations: "Not EMG-specific, but directly applicable to handcrafted-feature ML."
    project_transferability: "Very high."
    evidence_status: "PEER_REVIEWED_VERIFIED"
    reviewer_note: "Decision-grade methodological evidence."

  - evidence_id: FS-STABILITY-2018
    workstream: feature_selection
    research_question: "How should feature-selection stability be assessed?"
    claim: "Feature selection quality should include stability, not only predictive score; stability can be quantified rigorously with confidence intervals and hypothesis tests."
    decision_implication: "Locks selection-frequency and stability reporting into the blueprint."
    source_title: "On the Stability of Feature Selection Algorithms"
    source_type: "PEER_REVIEWED_METHOD_PAPER"
    authors: "Nogueira S, Sechidis K, Brown G"
    year: 2018
    doi_or_official_url: "JMLR 18(174):1-54"
    population: "Methodological paper"
    n_subjects: "NOT_APPLICABLE"
    clinical_or_healthy: "NOT_APPLICABLE"
    muscle_or_anatomical_region: "NOT_APPLICABLE"
    task_or_protocol: "Feature-selection stability theory"
    device: "NOT_APPLICABLE"
    channel_count: "NOT_APPLICABLE"
    electrode_geometry: "NOT_APPLICABLE"
    n_sessions_or_days: "NOT_APPLICABLE"
    window_length: "NOT_APPLICABLE"
    overlap: "NOT_APPLICABLE"
    feature_set: "Generic feature-selection algorithms"
    model: "Generic"
    split_unit: "Repeated resamples/folds"
    validation_regime: "Methodological"
    metric: "Stability measure with desirable axiomatic properties"
    main_finding: "Stability is a formal property and can be compared statistically."
    limitations: "Generic ML rather than EMG-specific."
    project_transferability: "High."
    evidence_status: "PEER_REVIEWED_VERIFIED"
    reviewer_note: "Use for reporting bundle, not algorithm choice."

  - evidence_id: HD-BOUNDARY-2008-2026
    workstream: feature_engineering
    research_question: "Which spatial features require HD-sEMG rather than sparse multichannel sEMG?"
    claim: "Motor-unit analysis, conduction velocity, activation maps and propagation vectors depend on dense, geometrically explicit arrays and should not be presumed sparse-channel baseline features."
    decision_implication: "Separates hd_semg_only from sparse 4–16 channel feature groups."
    source_title: "Analysis of motor units with high-density surface electromyography; High density surface electromyography: A review of technology and its applications"
    source_type: "PEER_REVIEWED_REVIEW"
    authors: "Merletti R, Holobar A, Farina D; Moreno Jiménez J, Hernández Zavala A, Morales Hernández AG"
    year: "2008; 2026"
    doi_or_official_url: "10.1016/j.jelekin.2008.09.002; 10.1177/00202940251396753"
    population: "HD-sEMG methodology literature"
    n_subjects: "Review"
    clinical_or_healthy: "Mixed"
    muscle_or_anatomical_region: "Multiple muscles"
    task_or_protocol: "HD-sEMG analysis and reporting"
    device: "High-density surface EMG arrays"
    channel_count: "Dense arrays, often tens to hundreds of electrodes"
    electrode_geometry: "Linear arrays and 2D grids"
    n_sessions_or_days: "Review"
    window_length: "Application-dependent"
    overlap: "Application-dependent"
    feature_set: "Regional activation, conduction velocity, innervation zones, motor-unit decomposition"
    model: "Signal processing / decomposition"
    split_unit: "NOT_APPLICABLE"
    validation_regime: "Methodological reviews"
    metric: "Technical capability and reporting needs"
    main_finding: "These spatial/motor-unit analyses require dense spatial sampling and known geometry."
    limitations: "Does not imply clinical utility in this project population."
    project_transferability: "High for boundary-setting; low for direct sparse transfer."
    evidence_status: "PEER_REVIEWED_VERIFIED"
    reviewer_note: "Use to fence off HD-only features."
```

### Open questions

| Open question | Dependency |
|---|---|
| Final sparse montage geometry có cố định đủ để cho phép channel-order patterns hoặc activation ratios so sánh qua session không? | Site verification |
| Task A có cần separate steady-state và transition benchmark hay chỉ một benchmark chính + một stress test? | Validation workstream |
| Task B cho phép window dài 500–1000 ms như context lane độc lập hay phải chia sẻ cùng segmentation backbone với Task A? | Cross-task architecture decision |
| Task C có dùng amplitude-preserving normalization-free comparator hay bắt buộc normalized features? | Label/protocol clarification |
| Có chấp nhận calibration buffer ngắn trước deployment không? | Clinical workflow decision |
| Antagonist muscle pairs cho co-contraction có được gắn kênh ổn định và ghi metadata đầy đủ không? | Site verification |

### Dependencies cho workstream tiếp theo

| Next workstream dependency | Why it matters |
|---|---|
| Validation policy | Needed to finalize split-first, segment-second implementation and nested selector placement |
| Site protocol verification | Needed for MVC/rest/co-contraction eligibility and montage-dependent spatial ratios |
| Task B operating concept | Needed to decide whether long-window fatigue/context features are first-class or auxiliary |
| Task C label governance | Needed to decide whether amplitude-preserving or normalized feature regimes are primary |

### YAML fragment cho `ai-core/configs/feature_groups.research.yaml`

```yaml
schema_version: "1.0"
status: "PROVISIONAL_DAY26_RESEARCH"
rationale: >
  Sparse-channel baseline should stay narrow, interpretable, leakage-safe, and
  separate from HD-sEMG-specific spatial analyses. No feature winner is declared
  before grouped nested experiments.
evidence_ids:
  - FEAT-TKACH-2010
  - FEAT-YOUNG-2011
  - WIN-FARRELL-2011
  - NORM-BURDEN-2010
  - NORM-TANAKA-2022
  - FS-LEAKAGE-2002-2021
  - FS-STABILITY-2018
  - HD-BOUNDARY-2008-2026
open_questions:
  - "Final sparse montage geometry and channel order"
  - "Whether session calibration buffer is allowed at deployment"
  - "Task B long-window context lane eligibility"
mandatory_baseline:
  - name: "RMS"
    status: "EVIDENCE_SUPPORTED"
    rationale: "Low cost, interpretable, sparse-eligible amplitude/power proxy."
    evidence_ids: ["FEAT-HUDGINS-1993", "FEAT-TKACH-2010"]
    open_questions: []
  - name: "WaveformLength"
    status: "EVIDENCE_SUPPORTED"
    rationale: "Captures waveform complexity with low computational cost."
    evidence_ids: ["FEAT-HUDGINS-1993", "FEAT-TKACH-2010"]
    open_questions: []
  - name: "AR4"
    status: "EVIDENCE_SUPPORTED"
    rationale: "Low-order AR is sparse-eligible and more robust to shift than many traditional TD sets."
    evidence_ids: ["FEAT-TKACH-2010", "FEAT-YOUNG-2011"]
    open_questions:
      - "Confirm AR order grid {4,6} in inner loop only"

optional_baseline:
  - name: "MAV"
    status: "EVIDENCE_SUPPORTED"
    rationale: "Canonical comparator; amplitude-like and easy to compute."
    evidence_ids: ["FEAT-HUDGINS-1993"]
    open_questions: []
  - name: "StandardDeviation"
    status: "EVIDENCE_SUPPORTED"
    rationale: "Amplitude dispersion comparator when centering is controlled."
    evidence_ids: ["FEAT-TKACH-2010"]
    open_questions: []
  - name: "IEMG"
    status: "EVIDENCE_SUPPORTED"
    rationale: "Simple cumulative amplitude comparator; window-length dependence must be declared."
    evidence_ids: ["FEAT-HUDGINS-1993"]
    open_questions: []
  - name: "ZC"
    status: "CONDITIONAL"
    rationale: "Useful count feature but threshold/noise handling must be fixed inside training."
    evidence_ids: ["FEAT-HUDGINS-1993", "FEAT-TKACH-2010"]
    open_questions:
      - "Thresholding rule relative to noise floor"
  - name: "SSC"
    status: "CONDITIONAL"
    rationale: "Useful but noise-sensitive; requires threshold governance."
    evidence_ids: ["FEAT-HUDGINS-1993", "FEAT-TKACH-2010"]
    open_questions:
      - "Thresholding rule relative to noise floor"
  - name: "WAMP"
    status: "CONDITIONAL"
    rationale: "Potentially useful in fewer-channel dynamic contractions but threshold-dependent."
    evidence_ids: ["FEAT-TKACH-2010", "FEAT-YOUNG-2011"]
    open_questions:
      - "Thresholding rule relative to gain/noise"
  - name: "MDF"
    status: "CONDITIONAL"
    rationale: "Eligible when longer windows are explicitly tested; not a mandatory short-window baseline."
    evidence_ids: ["WIN-FARRELL-2011", "FEAT-TKACH-2010"]
    open_questions:
      - "Minimum window setting for stable PSD in project sample rate"
  - name: "MNF"
    status: "CONDITIONAL"
    rationale: "Frequency-summary comparator for longer windows."
    evidence_ids: ["WIN-FARRELL-2011"]
    open_questions:
      - "Minimum window setting for stable PSD in project sample rate"
  - name: "BandPower"
    status: "CONDITIONAL"
    rationale: "Requires declared band edges and decision on absolute vs relative power."
    evidence_ids: ["WIN-FARRELL-2011"]
    open_questions:
      - "Band definitions and normalization variant"
  - name: "ChannelActivationRatios"
    status: "CONDITIONAL"
    rationale: "Sparse-eligible only if channel order and montage are fixed across acquisitions."
    evidence_ids: ["FEAT-YOUNG-2011"]
    open_questions:
      - "Montage stability across sessions"

later_experiments:
  - name: "SpectralEntropy"
    status: "ENGINEERING_HYPOTHESIS"
    rationale: "Potentially informative summary of spectral spread, but strongly regime-dependent."
    evidence_ids: ["WIN-FARRELL-2011"]
    open_questions: ["Band limits and PSD estimator"]
  - name: "SpectralMoments"
    status: "ENGINEERING_HYPOTHESIS"
    rationale: "Historically relevant to fatigue/endurance; needs longer records and careful interpretation."
    evidence_ids: ["WIN-FARRELL-2011"]
    open_questions: ["Which moment orders or ratios are worth testing"]
  - name: "STFTSummaries"
    status: "ENGINEERING_HYPOTHESIS"
    rationale: "Useful for non-stationary analysis, especially Task B/C."
    evidence_ids: ["WIN-FARRELL-2011"]
    open_questions: ["Frame size, hop, and summary statistics"]
  - name: "WaveletCoefficients"
    status: "ENGINEERING_HYPOTHESIS"
    rationale: "Promising for non-stationary content but parameter-rich."
    evidence_ids: ["WIN-FARRELL-2011"]
    open_questions: ["Mother wavelet and decomposition level"]
  - name: "WaveletPacketEnergy"
    status: "ENGINEERING_HYPOTHESIS"
    rationale: "Candidate high-dimensional time-frequency family."
    evidence_ids: ["WIN-FARRELL-2011", "FS-STABILITY-2018"]
    open_questions: ["Need dimensionality cap before nested selection"]
  - name: "InterChannelCovariance"
    status: "CONDITIONAL"
    rationale: "May capture multichannel structure but is montage-sensitive."
    evidence_ids: ["HD-BOUNDARY-2008-2026"]
    open_questions: ["Montage metadata and common-mode artifact handling"]
  - name: "CorrelationStructure"
    status: "CONDITIONAL"
    rationale: "Model-auditable multichannel structure, but unstable under montage changes."
    evidence_ids: ["HD-BOUNDARY-2008-2026"]
    open_questions: ["Montage metadata and minimum channel count"]
  - name: "CoContractionIndex"
    status: "SITE_CONFIRMATION_REQUIRED"
    rationale: "Requires antagonist-pair mapping, envelope recipe, and normalization protocol."
    evidence_ids: ["HD-BOUNDARY-2008-2026"]
    open_questions: ["Which formula variant and which muscle pairs"]
  - name: "ChannelOrderPatterns"
    status: "SITE_CONFIRMATION_REQUIRED"
    rationale: "Only meaningful if channel order and placement are stable across sessions."
    evidence_ids: ["FEAT-YOUNG-2011"]
    open_questions: ["Montage reproducibility"]

hd_semg_only:
  - name: "SpatialMoments"
    status: "EVIDENCE_SUPPORTED"
    rationale: "Requires explicit 2D coordinates and sufficiently dense spatial sampling."
    evidence_ids: ["HD-BOUNDARY-2008-2026"]
    open_questions: []
  - name: "ActivationHeatMaps"
    status: "EVIDENCE_SUPPORTED"
    rationale: "Grid-based spatial summaries are HD-sEMG constructs."
    evidence_ids: ["HD-BOUNDARY-2008-2026"]
    open_questions: []
  - name: "PropagationVectors"
    status: "EVIDENCE_SUPPORTED"
    rationale: "Depends on dense spatial sampling and clear fiber direction."
    evidence_ids: ["HD-BOUNDARY-2008-2026"]
    open_questions: []
  - name: "ConductionVelocity"
    status: "EVIDENCE_SUPPORTED"
    rationale: "HD/array methodology, not sparse baseline."
    evidence_ids: ["HD-BOUNDARY-2008-2026"]
    open_questions: []
  - name: "MotorUnitDecompositionMetrics"
    status: "EVIDENCE_SUPPORTED"
    rationale: "Belongs to HD-sEMG analysis lane."
    evidence_ids: ["HD-BOUNDARY-2008-2026"]
    open_questions: []

prohibited_without_metadata:
  - name: "MVCNormalization"
    status: "CONDITIONAL_PROHIBITED"
    rationale: "Do not use unless the MVC protocol is standardized, repeatable, and clinically feasible."
    evidence_ids: ["NORM-BURDEN-2010"]
    open_questions: ["Site feasibility in intended population"]
  - name: "RestBaselineNormalization"
    status: "CONDITIONAL_PROHIBITED"
    rationale: "Do not use unless rest acquisition protocol and contamination checks are standardized."
    evidence_ids: ["NORM-BURDEN-2010"]
    open_questions: ["Can reliable rest be collected in all intended users"]
  - name: "CoContraction"
    status: "CONDITIONAL_PROHIBITED"
    rationale: "Do not compute without explicit antagonist-pair metadata and envelope recipe."
    evidence_ids: ["HD-BOUNDARY-2008-2026"]
    open_questions: ["Muscle-pair ontology"]
  - name: "SpatialLikeFeaturesWithoutCoordinates"
    status: "PROHIBITED"
    rationale: "No spatial moments or map descriptors without explicit channel geometry."
    evidence_ids: ["HD-BOUNDARY-2008-2026"]
    open_questions: []
  - name: "GlobalPreSplitNormalizationOrSelection"
    status: "PROHIBITED"
    rationale: "Global fit before grouped CV creates leakage."
    evidence_ids: ["FS-LEAKAGE-2002-2021"]
    open_questions: []
```

### Mapping sang requested artifacts

| Target artifact | What should go into it |
|---|---|
| `docs/06-ai-signal-processing/feature-candidate-catalog.md` | Bảng feature ở trên, sparse-vs-HD decision matrix, sign/unit/formula constraints |
| `docs/06-ai-signal-processing/feature-normalization-research.md` | Normalization comparison table, leakage rules, deployment contracts, site-required items |
| `docs/06-ai-signal-processing/feature-selection-research.md` | Selector comparison, nested-CV placement, stability bundle, anti-leakage SOP |
| `docs/research/day26/03-feature-engineering-review.md` | Executive synthesis cho Day 26, window grid, sparse-vs-HD boundary, provisional decisions |
| `ai-core/configs/feature_groups.research.yaml` | YAML fragment trên sau khi chuẩn hóa naming conventions và evidence IDs |

### Go status

**Go-with-conditions** cho việc đưa nội dung này vào Day 26 Experiment Blueprint.

Điều kiện là:  
thứ nhất, giữ nguyên ranh giới **sparse-channel baseline ≠ HD-sEMG lane**;  
thứ hai, không biến bất kỳ optional/later-experiment feature nào thành “winner” trước grouped nested experiments;  
thứ ba, mọi normalization/selection/calibration/threshold đều phải là **fold-contained**;  
thứ tư, các mục đã đánh dấu **NOT_VERIFIED** hoặc **SITE_CONFIRMATION_REQUIRED** không được lấp bằng giả định. citeturn13search2turn12search0turn10search7turn10search2turn1search1turn0search0