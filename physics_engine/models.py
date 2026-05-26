from dataclasses import dataclass
import numpy as np


@dataclass
class DiffusionParams:
    dopant: str           # "B" | "P" | "As" | "Sb"
    temperature_C: float  # annealing temperature in °C (converted to K internally)
    time_s: float         # annealing time in seconds
    profile: str          # "erfc" | "gaussian"
    depth_um: float       # total simulation depth in µm
    surface_conc: float   # C_s [cm⁻³] for erfc, or dose Q [cm⁻²] for gaussian
    n_points: int = 500   # spatial grid resolution


@dataclass
class DiffusionResult:
    depth: np.ndarray             # shape (n_points,), depth axis in µm
    concentration: np.ndarray     # shape (n_points,), C(x, t_final) in cm⁻³
    time_snapshots: list          # list of np.ndarray, one per snapshot time
    time_points: np.ndarray       # shape (N_SNAPSHOTS,), times in seconds
    D_eff: float                  # effective diffusivity at given T [cm²/s]
    junction_depth_um: float      # x_j where C drops to 1e16 cm⁻³ [µm]
    params: DiffusionParams
