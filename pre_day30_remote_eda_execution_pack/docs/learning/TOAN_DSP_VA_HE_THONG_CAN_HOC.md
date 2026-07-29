# Kiến thức cần học để tự hiểu và vận hành Pre-Day30 EDA

## 1. Học kỹ ngay

### A. Cấu trúc dữ liệu repeated measures

Phân biệt:

```text
sample < window < repetition < trial < session < day < subject
```

Window không phải đơn vị độc lập. Split phải đi từ subject/day/session/repetition trước windowing.

### B. Streaming algorithms

- Welford mean/variance;
- incremental RMS/MAV;
- merge sufficient statistics từ nhiều chunk;
- complexity `O(N)` time và `O(C)` memory với `C` là số kênh.

### C. Robust statistics

- median;
- MAD;
- IQR;
- vì mean/std nhạy với artifact.

Median/MAD chính xác toàn corpus khó hơn streaming mean; có thể dùng quantile sketch hoặc tính theo record rồi aggregate. Pack không giả định approximate quantile là exact.

### D. Sampling theorem

- sampling rate `fs`;
- Nyquist `fs/2`;
- aliasing;
- vì sao không resample tùy tiện;
- vì sao MDF/MNF vô nghĩa nếu `fs` hoặc preprocessing không rõ.

### E. HTTP và filesystem remote

- `HEAD`;
- `Content-Length`;
- `ETag`;
- `Last-Modified`;
- `Accept-Ranges: bytes`;
- seekable file abstraction;
- cache block và LRU.

### F. Compression/random access

- ZIP central directory;
- TAR.GZ sequential compression;
- HDF5 chunking;
- Parquet row groups;
- Zarr chunks.

## 2. Học trước khi full signal QC

- DC offset;
- flatline/dropout;
- clipping vs potential clipping;
- line noise 50 Hz;
- motion artifact low-frequency;
- Welch PSD;
- MDF/MNF definitions;
- effect of window length and overlap.

## 3. Học trước Day 30

- set intersection cho common ontology;
- domain shift;
- source confounding;
- channel representation mismatch;
- unit conversion;
- anti-aliasing filter;
- logical view vs physical copy.

## 4. Bài tập tự kiểm tra

1. Viết Welford cho 1D và so với `numpy.var`.
2. Chia một vector thành 10 chunk, tính RMS merge và so với RMS toàn vector.
3. Tạo một file CSV 5 triệu dòng, đọc chunksize 50k và đo RAM.
4. Thử `HEAD` một URL và giải thích `Accept-Ranges`.
5. Giải thích vì sao đọc 1 member trong `.tar.gz` có thể cần quét nhiều byte.
6. Chứng minh random-window split có thể để sibling windows ở train và test.
7. Giải thích tại sao GRABMyo day shift không phải nhãn fatigue.
