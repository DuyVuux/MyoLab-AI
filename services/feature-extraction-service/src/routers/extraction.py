from fastapi import APIRouter, HTTPException, status
import numpy as np

from semg_core.features import extract_time_domain_features, FeatureExtractionError
from semg_core.spectral_features import extract_frequency_features, FrequencyFeatureError

from schemas.api_schemas import (
    TimeDomainMathRequest,
    TimeDomainMathResponse,
    FrequencyDomainMathRequest,
    FrequencyDomainMathResponse,
)

router = APIRouter(prefix="/api/v1/features", tags=["features"])


@router.post(
    "/time-domain",
    response_model=TimeDomainMathResponse,
    status_code=status.HTTP_200_OK,
    summary="Extract time domain features (RMS, MAV)",
)
def extract_time_domain(request: TimeDomainMathRequest):
    """
    Computes RMS and MAV for a given set of samples.
    Delegates to the `semg_core.features` pure mathematical functions.
    """
    try:
        samples = np.array(request.samples_uv, dtype=np.float64)
        result = extract_time_domain_features(
            samples, amplitude_unit=request.amplitude_unit
        )
        return TimeDomainMathResponse(
            rms=result.rms,
            mav=result.mav,
            sample_count=result.sample_count,
            amplitude_unit=result.amplitude_unit,
        )
    except FeatureExtractionError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/frequency-domain",
    response_model=FrequencyDomainMathResponse,
    status_code=status.HTTP_200_OK,
    summary="Extract frequency domain features (MDF, MNF)",
)
def extract_frequency_domain(request: FrequencyDomainMathRequest):
    """
    Computes Median Frequency (MDF) and Mean Frequency (MNF) from a Power Spectral Density (PSD).
    Delegates to the `semg_core.spectral_features` pure mathematical functions.
    """
    try:
        frequencies = np.array(request.frequencies_hz, dtype=np.float64)
        psd = np.array(request.psd_uv2_per_hz, dtype=np.float64)
        
        result = extract_frequency_features(
            frequencies,
            psd,
            minimum_power_uV2=request.minimum_power_uv2,
            median_quantile=request.median_quantile,
        )
        return FrequencyDomainMathResponse(
            mdf_hz=result.mdf_hz,
            mnf_hz=result.mnf_hz,
            band_power_uv2=result.band_power_uV2,
            frequency_bin_count=result.frequency_bin_count,
            frequency_bin_spacing_hz=result.frequency_bin_spacing_hz,
        )
    except FrequencyFeatureError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
