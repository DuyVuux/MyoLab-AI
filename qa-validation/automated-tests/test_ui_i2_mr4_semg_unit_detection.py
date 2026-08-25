from types import SimpleNamespace
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SRC = REPO / "services/api-server/src"
sys.path.insert(0, str(SRC))

from ui_i2.live_backend import _is_mr4_semg_signal, _muscle_for_vendor_name


def signal(name, unit="uV", role="SEMG_VENDOR_CHANNEL"):
    return SimpleNamespace(vendor_name=name, unit=unit, semantic_role=role)


def test_mr4_semg_detection_accepts_explicit_microvolt_units():
    assert _is_mr4_semg_signal(signal("RT RECTUS FEM. (uV)"))
    assert _is_mr4_semg_signal(signal("LT RECTUS FEM. (µV)"))
    assert _is_mr4_semg_signal(signal("LT RECTUS FEM. (μV)"))


def test_mr4_semg_detection_rejects_explicit_force_and_pressure_units():
    assert not _is_mr4_semg_signal(signal("LT Force (N)"))
    assert not _is_mr4_semg_signal(signal("LT Max Pressure (N/cm²)"))


def test_mr4_muscle_name_strips_unit_suffix():
    assert _muscle_for_vendor_name("RT RECTUS FEM. (uV)") == "rectus_femoris"
