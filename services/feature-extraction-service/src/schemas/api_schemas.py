from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class TimeDomainMathRequest(StrictModel):
    """Payload to extract time domain features (RMS, MAV) for a single window."""
    samples_uv: list[float] = Field(..., description="Array of voltage samples in uV")
    amplitude_unit: str = Field(default="uV", description="Unit of the amplitude")


class FrequencyDomainMathRequest(StrictModel):
    """Payload to extract frequency domain features (MDF, MNF) for a single PSD window."""
    frequencies_hz: list[float] = Field(..., description="Array of frequency bins in Hz")
    psd_uv2_per_hz: list[float] = Field(..., description="Array of power spectral density values")
    minimum_power_uv2: float = Field(default=0.0, description="Minimum band power required")
    median_quantile: float = Field(default=0.5, description="Quantile for MDF calculation")


class TimeDomainMathResponse(StrictModel):
    rms: float
    mav: float
    sample_count: int
    amplitude_unit: str


class FrequencyDomainMathResponse(StrictModel):
    mdf_hz: float
    mnf_hz: float
    band_power_uv2: float
    frequency_bin_count: int
    frequency_bin_spacing_hz: float
