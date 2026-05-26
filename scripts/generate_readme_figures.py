"""Generate the demo figures embedded in README.md.

Run from project root:
    python scripts/generate_readme_figures.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np
import matplotlib.pyplot as plt

from physics_engine import DiffusionParams, solve_analytic
from visualizer import plot_profile, plot_animation_gif

OUT = ROOT / "docs" / "images"
OUT.mkdir(parents=True, exist_ok=True)

print("Generating Boron profile (1000 C, 3600 s)...")
params = DiffusionParams(
    dopant="B",
    temperature_C=1000.0,
    time_s=3600.0,
    profile="erfc",
    depth_um=0.5,
    surface_conc=1e20,
    n_points=500,
)
result = solve_analytic(params)
plot_profile(result, str(OUT / "boron_profile.png"))
print(f"  -> {OUT / 'boron_profile.png'}")

print("Generating diffusion animation (GIF)...")
plot_animation_gif(result, str(OUT / "boron_evolution.gif"))
print(f"  -> {OUT / 'boron_evolution.gif'}")

print("Generating anneal-condition comparison...")
scenarios = [
    ("RTP spike, 1050 C, 1 s",    1050, 1),
    ("RTP spike, 1050 C, 10 s",   1050, 10),
    ("Drive-in, 1000 C, 3600 s",  1000, 3600),
]
fig, ax = plt.subplots(figsize=(9, 5))
for label, temp, time in scenarios:
    p = DiffusionParams("B", temp, time, "erfc", 0.5, 1e20, n_points=500)
    r = solve_analytic(p)
    mask = r.concentration > 0
    ax.semilogy(
        r.depth[mask], r.concentration[mask],
        label=f"{label}  (x_j = {r.junction_depth_um:.4f} um)",
        linewidth=2,
    )
ax.axvline(0.010, color="k", linestyle=":", linewidth=1.5,
           label="2nm node target  x_j = 10 nm")
ax.axhline(1e16, color="gray", linestyle="--", linewidth=1, alpha=0.6,
           label="Background doping  10^16 cm^-3")
ax.set_xlabel("Depth (um)", fontsize=12)
ax.set_ylabel("Concentration (cm^-3)", fontsize=12)
ax.set_title("Boron in Si - Anneal Condition Comparison", fontsize=13)
ax.legend(fontsize=9)
ax.grid(True, which="both", alpha=0.3)
ax.set_xlim(0, 0.15)
plt.tight_layout()
plt.savefig(OUT / "anneal_comparison.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"  -> {OUT / 'anneal_comparison.png'}")

print("\nAll figures generated.")
