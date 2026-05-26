import math
from physics_engine.dopants import get_dopant

K_B = 8.617333e-5  # Boltzmann constant [eV/K]


def compute_diffusivity(dopant_symbol: str, temperature_C: float) -> float:
    """Return D = D0 * exp(-Ea / kB*T) for the given dopant at temperature_C."""
    if temperature_C < 0:
        raise ValueError(f"Temperature must be >= 0°C, got {temperature_C}")
    dopant = get_dopant(dopant_symbol)
    T_K = temperature_C + 273.15
    return dopant.D0 * math.exp(-dopant.Ea / (K_B * T_K))
