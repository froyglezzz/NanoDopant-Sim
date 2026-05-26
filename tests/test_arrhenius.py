import math
import pytest
from physics_engine.arrhenius import compute_diffusivity, K_B


def test_boron_at_1000C_matches_formula():
    D = compute_diffusivity("B", 1000.0)
    T_K = 1273.15
    expected = 0.76 * math.exp(-3.46 / (K_B * T_K))
    assert abs(D - expected) / expected < 1e-10


def test_phosphorus_at_1000C_matches_formula():
    D = compute_diffusivity("P", 1000.0)
    T_K = 1273.15
    expected = 3.85 * math.exp(-3.66 / (K_B * T_K))
    assert abs(D - expected) / expected < 1e-10


def test_diffusivity_increases_with_temperature():
    D_low = compute_diffusivity("B", 900.0)
    D_high = compute_diffusivity("B", 1100.0)
    assert D_high > D_low


def test_all_dopants_yield_positive_D():
    for symbol in ["B", "P", "As", "Sb"]:
        assert compute_diffusivity(symbol, 1000.0) > 0


def test_boron_D_at_1000C_is_in_physical_range():
    # Literature: ~1e-14 cm²/s for B in Si at 1000°C
    D = compute_diffusivity("B", 1000.0)
    assert 1e-16 < D < 1e-12


def test_negative_temperature_raises():
    with pytest.raises(ValueError, match="Temperature"):
        compute_diffusivity("B", -1.0)
