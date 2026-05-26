import numpy as np
from scipy.special import erfc as scipy_erfc

from physics_engine.models import DiffusionParams, DiffusionResult
from physics_engine.arrhenius import compute_diffusivity

N_SNAPSHOTS = 20
BACKGROUND_CONC = 1e16  # cm⁻³, typical Si background doping


def _junction_depth(depth_um: np.ndarray, concentration: np.ndarray) -> float:
    """Return depth (µm) where concentration first drops below BACKGROUND_CONC."""
    indices = np.where(concentration >= BACKGROUND_CONC)[0]
    return float(depth_um[indices[-1]]) if len(indices) > 0 else 0.0


def solve_analytic(params: DiffusionParams) -> DiffusionResult:
    """Closed-form solution: erfc (infinite source) or Gaussian (finite dose)."""
    D = compute_diffusivity(params.dopant, params.temperature_C)
    x_cm = np.linspace(0.0, params.depth_um * 1e-4, params.n_points)
    time_points = np.linspace(params.time_s / N_SNAPSHOTS, params.time_s, N_SNAPSHOTS)

    snapshots = []
    for t in time_points:
        if params.profile == "erfc":
            C = params.surface_conc * scipy_erfc(x_cm / (2.0 * np.sqrt(D * t)))
        else:  # gaussian
            C = (params.surface_conc / np.sqrt(np.pi * D * t)) * np.exp(
                -(x_cm ** 2) / (4.0 * D * t)
            )
        snapshots.append(C)

    final_C = snapshots[-1]
    depth_um = x_cm * 1e4

    return DiffusionResult(
        depth=depth_um,
        concentration=final_C,
        time_snapshots=snapshots,
        time_points=time_points,
        D_eff=D,
        junction_depth_um=_junction_depth(depth_um, final_C),
        params=params,
    )


def solve_fdm(params: DiffusionParams) -> DiffusionResult:
    """Placeholder — implemented in Task 6."""
    raise NotImplementedError("FDM solver not yet implemented")
