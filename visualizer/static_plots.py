import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from physics_engine.models import DiffusionResult


def plot_profile(result: DiffusionResult, output_path: str) -> None:
    """Save C(x, t_final) on log scale with junction depth annotated."""
    fig, ax = plt.subplots(figsize=(8, 5))

    mask = result.concentration > 0
    ax.semilogy(result.depth[mask], result.concentration[mask], "b-", linewidth=2)

    if result.junction_depth_um > 0:
        ax.axvline(
            result.junction_depth_um,
            color="r",
            linestyle="--",
            linewidth=1.5,
            label=f"$x_j$ = {result.junction_depth_um:.3f} µm",
        )

    ax.set_xlabel("Depth (µm)", fontsize=12)
    ax.set_ylabel("Concentration (cm⁻³)", fontsize=12)
    ax.set_title(
        f"{result.params.dopant} in Si  |  "
        f"T = {result.params.temperature_C:.0f}°C  |  "
        f"t = {result.params.time_s:.0f} s",
        fontsize=12,
    )
    ax.legend(fontsize=11)
    ax.grid(True, which="both", alpha=0.3)
    ax.set_xlim(left=0)
    ax.yaxis.set_major_formatter(ticker.LogFormatterMathtext())

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
