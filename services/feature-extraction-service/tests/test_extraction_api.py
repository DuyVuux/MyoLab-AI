from fastapi.testclient import TestClient
import numpy as np

from app import app
from schemas.api_schemas import TimeDomainMathRequest, FrequencyDomainMathRequest

client = TestClient(app)

def test_time_domain_api():
    # Generate a simple sine wave for testing
    fs = 1000
    t = np.arange(0, 1, 1/fs)
    samples = np.sin(2 * np.pi * 50 * t).tolist()
    
    request = TimeDomainMathRequest(samples_uv=samples, amplitude_unit="V")
    response = client.post("/api/v1/features/time-domain", json=request.model_dump())
    
    assert response.status_code == 200
    data = response.json()
    assert "rms" in data
    assert "mav" in data
    assert "sample_count" in data
    assert data["sample_count"] == 1000
    # RMS of sine wave with amplitude A=1 is ~0.707
    assert np.isclose(data["rms"], 0.707, atol=1e-2)

def test_frequency_domain_api():
    # Simple PSD with a peak at 50Hz
    frequencies = np.linspace(0, 100, 101) # 0 to 100Hz
    psd = np.zeros_like(frequencies)
    psd[50] = 1.0 # Peak at 50Hz
    
    request = FrequencyDomainMathRequest(
        frequencies_hz=frequencies.tolist(),
        psd_uv2_per_hz=psd.tolist(),
        minimum_power_uv2=0.0
    )
    response = client.post("/api/v1/features/frequency-domain", json=request.model_dump())
    
    assert response.status_code == 200
    data = response.json()
    assert "mdf_hz" in data
    assert "mnf_hz" in data
    assert data["mdf_hz"] == 50.0
    assert data["mnf_hz"] == 50.0

def test_time_domain_error_handling():
    # Pass invalid data (empty array)
    request = {"samples_uv": [], "amplitude_unit": "V"}
    response = client.post("/api/v1/features/time-domain", json=request)
    assert response.status_code == 400

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
