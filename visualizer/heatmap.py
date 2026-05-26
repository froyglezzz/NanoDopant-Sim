import numpy as np
import plotly.graph_objects as go

from physics_engine.models import DiffusionResult


def plot_heatmap(result: DiffusionResult, output_path: str) -> None:
    """Interactive Plotly heatmap: depth × time, color = log10(C)."""
    conc_matrix = np.array(result.time_snapshots)
    log_conc = np.log10(np.maximum(conc_matrix, 1.0))

    fig = go.Figure(
        data=go.Heatmap(
            z=log_conc,
            x=result.depth,
            y=result.time_points,
            colorscale="RdYlBu_r",
            colorbar=dict(title="log₁₀(C [cm⁻³])"),
            hovertemplate=(
                "Depth: %{x:.3f} µm<br>"
                "Time: %{y:.0f} s<br>"
                "C: 10^%{z:.2f} cm⁻³<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title=(
            f"{result.params.dopant} Diffusion in Si — "
            f"{result.params.temperature_C:.0f}°C, {result.params.profile} profile"
        ),
        xaxis_title="Depth (µm)",
        yaxis_title="Annealing Time (s)",
        template="plotly_white",
        font=dict(size=13),
    )

    fig.write_html(output_path, include_plotlyjs="cdn")
