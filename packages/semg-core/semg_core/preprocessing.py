"""Các hàm tiền xử lý sEMG thuần, xác định và có thể kiểm thử.

Phạm vi Day 5:
- chuẩn hóa DC bằng cách trừ trung bình;
- thiết kế Butterworth band-pass dạng SOS;
- notch 50/60 Hz tùy chọn dạng SOS;
- lọc zero-phase offline bằng ``sosfiltfilt``;
- tạo hash xác định cho mảng đầu ra.

Module này không biết về QC, protocol, fatigue feature hoặc diễn giải lâm sàng.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from typing import Any

import numpy as np
from scipy.signal import butter, iirnotch, sosfiltfilt, tf2sos


class PreprocessingError(ValueError):
    """Lỗi điều kiện đầu vào hoặc cấu hình tiền xử lý."""


@dataclass(frozen=True, slots=True)
class FilterDiagnostics:
    """Thông tin QA kỹ thuật; không phải fatigue feature lâm sàng."""

    input_mean_uV: float
    output_mean_uV: float
    input_std_uV: float
    output_std_uV: float
    sample_count: int
    output_hash_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "input_mean_uV": float(self.input_mean_uV),
            "output_mean_uV": float(self.output_mean_uV),
            "input_std_uV": float(self.input_std_uV),
            "output_std_uV": float(self.output_std_uV),
            "sample_count": int(self.sample_count),
            "output_hash_sha256": self.output_hash_sha256,
        }


@dataclass(frozen=True, slots=True)
class CorePreprocessResult:
    """Kết quả lọc một kênh ở mức core."""

    samples_uV: np.ndarray
    diagnostics: FilterDiagnostics
    notch_applied: bool

    def __post_init__(self) -> None:
        samples = np.ascontiguousarray(self.samples_uV, dtype=np.float64)
        if samples.ndim != 1:
            raise PreprocessingError("samples_uV phải là mảng một chiều")
        samples.setflags(write=False)
        object.__setattr__(self, "samples_uV", samples)


def _require_finite_1d(samples: np.ndarray) -> np.ndarray:
    array = np.ascontiguousarray(samples, dtype=np.float64)
    if array.ndim != 1:
        raise PreprocessingError("Tín hiệu phải là mảng một chiều")
    if array.size < 2:
        raise PreprocessingError("Tín hiệu cần ít nhất hai mẫu")
    if not np.isfinite(array).all():
        raise PreprocessingError(
            "Day 5 không nội suy NaN/Inf; tín hiệu phải hoàn toàn hữu hạn"
        )
    return array


def array_sha256_float64(samples: np.ndarray) -> str:
    """Hash byte canonical little-endian float64 để kiểm tra reproducibility."""

    array = np.asarray(samples, dtype="<f8", order="C")
    return hashlib.sha256(array.tobytes(order="C")).hexdigest()


def mean_center(samples: np.ndarray) -> np.ndarray:
    """Trừ trung bình toàn bản ghi của một kênh."""

    array = _require_finite_1d(samples)
    centered = array - float(np.mean(array))
    return np.ascontiguousarray(centered, dtype=np.float64)


def validate_bandpass(
    *,
    sampling_rate_hz: float,
    low_cut_hz: float,
    high_cut_hz: float,
    nyquist_margin_ratio: float,
) -> None:
    if not np.isfinite(sampling_rate_hz) or sampling_rate_hz <= 0:
        raise PreprocessingError("sampling_rate_hz phải dương và hữu hạn")
    if not (0 < low_cut_hz < high_cut_hz):
        raise PreprocessingError("Cần 0 < low_cut_hz < high_cut_hz")
    if not (0 < nyquist_margin_ratio < 1):
        raise PreprocessingError("nyquist_margin_ratio phải nằm trong (0, 1)")
    nyquist = sampling_rate_hz / 2.0
    maximum_allowed = nyquist * nyquist_margin_ratio
    if high_cut_hz >= maximum_allowed:
        raise PreprocessingError(
            "high_cut_hz phải nhỏ hơn Nyquist sau khi trừ biên chuyển tiếp: "
            f"high={high_cut_hz}, max_allowed={maximum_allowed}"
        )


def design_butterworth_bandpass_sos(
    *,
    sampling_rate_hz: float,
    low_cut_hz: float,
    high_cut_hz: float,
    order: int,
    nyquist_margin_ratio: float,
) -> np.ndarray:
    """Thiết kế Butterworth band-pass ở dạng second-order sections."""

    validate_bandpass(
        sampling_rate_hz=sampling_rate_hz,
        low_cut_hz=low_cut_hz,
        high_cut_hz=high_cut_hz,
        nyquist_margin_ratio=nyquist_margin_ratio,
    )
    if not isinstance(order, int) or order < 1:
        raise PreprocessingError("order phải là số nguyên >= 1")
    sos = butter(
        order,
        [low_cut_hz, high_cut_hz],
        btype="bandpass",
        fs=sampling_rate_hz,
        output="sos",
    )
    return np.ascontiguousarray(sos, dtype=np.float64)


def design_notch_sos(
    *,
    sampling_rate_hz: float,
    line_frequency_hz: float,
    q_factor: float,
) -> np.ndarray:
    """Thiết kế notch IIR và chuyển sang SOS."""

    if sampling_rate_hz <= 0 or not np.isfinite(sampling_rate_hz):
        raise PreprocessingError("sampling_rate_hz phải dương và hữu hạn")
    nyquist = sampling_rate_hz / 2.0
    if not (0 < line_frequency_hz < nyquist):
        raise PreprocessingError("line_frequency_hz phải nằm trong (0, Nyquist)")
    if not np.isfinite(q_factor) or q_factor <= 0:
        raise PreprocessingError("q_factor phải dương và hữu hạn")
    b, a = iirnotch(
        w0=line_frequency_hz,
        Q=q_factor,
        fs=sampling_rate_hz,
    )
    return np.ascontiguousarray(tf2sos(b, a), dtype=np.float64)


def apply_zero_phase_sos(samples: np.ndarray, sos: np.ndarray) -> np.ndarray:
    """Lọc tiến-lùi; phù hợp offline, không dùng cho streaming realtime."""

    array = _require_finite_1d(samples)
    sections = np.asarray(sos, dtype=np.float64)
    if sections.ndim != 2 or sections.shape[1] != 6:
        raise PreprocessingError("SOS phải có shape (n_sections, 6)")
    try:
        output = sosfiltfilt(sections, array)
    except ValueError as exc:
        raise PreprocessingError(
            "Không thể sosfiltfilt; bản ghi có thể quá ngắn cho padding"
        ) from exc
    if not np.isfinite(output).all():
        raise PreprocessingError("Lọc tạo ra giá trị không hữu hạn")
    return np.ascontiguousarray(output, dtype=np.float64)


def preprocess_channel(
    samples_uV: np.ndarray,
    *,
    sampling_rate_hz: float,
    mean_center_enabled: bool,
    bandpass_low_hz: float,
    bandpass_high_hz: float,
    bandpass_order: int,
    nyquist_margin_ratio: float,
    notch_enabled: bool,
    notch_frequency_hz: float,
    notch_q_factor: float,
) -> CorePreprocessResult:
    """Chạy pipeline core cho một kênh, giữ nguyên số mẫu và đơn vị uV."""

    source = _require_finite_1d(samples_uV)
    working = mean_center(source) if mean_center_enabled else source.copy()

    bandpass_sos = design_butterworth_bandpass_sos(
        sampling_rate_hz=sampling_rate_hz,
        low_cut_hz=bandpass_low_hz,
        high_cut_hz=bandpass_high_hz,
        order=bandpass_order,
        nyquist_margin_ratio=nyquist_margin_ratio,
    )
    working = apply_zero_phase_sos(working, bandpass_sos)

    if notch_enabled:
        notch_sos = design_notch_sos(
            sampling_rate_hz=sampling_rate_hz,
            line_frequency_hz=notch_frequency_hz,
            q_factor=notch_q_factor,
        )
        working = apply_zero_phase_sos(working, notch_sos)

    if working.size != source.size:
        raise PreprocessingError("Tiền xử lý không được thay đổi số mẫu trong MVP-0")

    diagnostics = FilterDiagnostics(
        input_mean_uV=float(np.mean(source)),
        output_mean_uV=float(np.mean(working)),
        input_std_uV=float(np.std(source)),
        output_std_uV=float(np.std(working)),
        sample_count=int(working.size),
        output_hash_sha256=array_sha256_float64(working),
    )
    return CorePreprocessResult(
        samples_uV=working,
        diagnostics=diagnostics,
        notch_applied=bool(notch_enabled),
    )
