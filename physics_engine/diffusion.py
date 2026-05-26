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
    """Explicit finite-difference solver (Fick's Second Law). CFL enforced automatically."""
    D = compute_diffusivity(params.dopant, params.temperature_C)
    depth_cm = params.depth_um * 1e-4
    dx = depth_cm / (params.n_points - 1)

    # CFL stability: D*dt/dx² <= 0.5 — use 0.4 for safety margin
    dt = 0.4 * dx ** 2 / D
    n_steps = max(1, int(params.time_s / dt))
    snapshot_interval = max(1, n_steps // N_SNAPSHOTS)

    x_cm = np.linspace(0.0, depth_cm, params.n_points)

    # Initial condition
    if params.profile == "erfc":
        C = np.zeros(params.n_points)
        C[0] = params.surface_conc
    else:  # gaussian: all dose concentrated in first cell
        C = np.zeros(params.n_points)
        C[0] = params.surface_conc / dx

    snapshots: list[np.ndarray] = []
    time_list: list[float] = []
    t = 0.0
    r = D * dt / dx ** 2  # Fourier number (constant since D, dt, dx are fixed)

    for step in range(n_steps):
        if step % snapshot_interval == 0:
            snapshots.append(C.copy())
            time_list.append(t)

        C_new = C.copy()
        C_new[1:-1] = C[1:-1] + r * (C[2:] - 2.0 * C[1:-1] + C[:-2])

        if params.profile == "erfc":
            C_new[0] = params.surface_conc   # Dirichlet BC: constant surface source
        else:
            C_new[0] = C_new[1]              # Neumann BC: zero flux at surface

        C_new[-1] = C_new[-2]                # Neumann BC: zero flux at bottom
        C = C_new
        t += dt

    snapshots.append(C.copy())
    time_list.append(params.time_s)

    depth_um = x_cm * 1e4
    return DiffusionResult(
        depth=depth_um,
        concentration=C,
        time_snapshots=snapshots,
        time_points=np.array(time_list),
        D_eff=D,
        junction_depth_um=_junction_depth(depth_um, C),
        params=params,
    )
