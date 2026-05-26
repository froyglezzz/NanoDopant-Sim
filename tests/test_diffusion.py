import numpy as np
import pytest
from physics_engine.models import DiffusionParams
from physics_engine.diffusion import solve_analytic, solve_fdm

ERFC_PARAMS = DiffusionParams(
    dopant="B",
    temperature_C=1000.0,
    time_s=3600.0,
    profile="erfc",
    depth_um=1.0,
    surface_conc=1e20,
    n_points=200,
)

GAUSS_PARAMS = DiffusionParams(
    dopant="P",
    temperature_C=1000.0,
    time_s=3600.0,
    profile="gaussian",
    depth_um=2.0,
    surface_conc=1e14,  # dose Q in cm⁻²
    n_points=500,
)


def test_erfc_surface_equals_Cs():
    result = solve_analytic(ERFC_PARAMS)
    rel_err = abs(result.concentration[0] - ERFC_PARAMS.surface_conc) / ERFC_PARAMS.surface_conc
    assert rel_err < 1e-6


def test_erfc_profile_monotonically_decreasing():
    result = solve_analytic(ERFC_PARAMS)
    assert np.all(np.diff(result.concentration) <= 0)


def test_erfc_depth_array_shape():
    result = solve_analytic(ERFC_PARAMS)
    assert result.depth.shape == (ERFC_PARAMS.n_points,)
    assert result.concentration.shape == (ERFC_PARAMS.n_points,)


def test_erfc_has_correct_snapshot_count():
    result = solve_analytic(ERFC_PARAMS)
    assert len(result.time_snapshots) == 20
    assert len(result.time_points) == 20


def test_erfc_time_points_monotonically_increasing():
    result = solve_analytic(ERFC_PARAMS)
    assert np.all(np.diff(result.time_points) > 0)


def test_erfc_junction_depth_positive():
    result = solve_analytic(ERFC_PARAMS)
    assert result.junction_depth_um > 0


def test_erfc_D_eff_positive():
    result = solve_analytic(ERFC_PARAMS)
    assert result.D_eff > 0


def test_gaussian_conserves_dose():
    result = solve_analytic(GAUSS_PARAMS)
    dx_cm = (GAUSS_PARAMS.depth_um * 1e-4) / (GAUSS_PARAMS.n_points - 1)
    integrated = np.trapezoid(result.concentration, dx=dx_cm)
    rel_err = abs(integrated - GAUSS_PARAMS.surface_conc) / GAUSS_PARAMS.surface_conc
    assert rel_err < 0.05, f"Dose not conserved: {rel_err:.1%} error"


def test_gaussian_peak_at_surface():
    result = solve_analytic(GAUSS_PARAMS)
    assert result.concentration[0] == result.concentration.max()


def test_analytic_fdm_erfc_convergence():
    """FDM and analytic erfc must agree within 5% at quarter-depth."""
    params = DiffusionParams(
        dopant="B",
        temperature_C=1000.0,
        time_s=3600.0,
        profile="erfc",
        depth_um=1.0,
        surface_conc=1e20,
        n_points=200,
    )
    result_a = solve_analytic(params)
    result_n = solve_fdm(params)

    # Compare at index 50 (~quarter depth), away from boundaries
    idx = 50
    C_a = result_a.concentration[idx]
    C_n = np.interp(result_a.depth[idx], result_n.depth, result_n.concentration)

    if C_a > 1e10:
        rel_error = abs(C_a - C_n) / C_a
        assert rel_error < 0.05, f"Analytic/FDM diverge by {rel_error:.1%}"
