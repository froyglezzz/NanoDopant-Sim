import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import matplotlib.animation as anim_mod

from physics_engine.models import DiffusionResult


def plot_animation_html(result: DiffusionResult, output_path: str) -> None:
    """Plotly animation with play/pause and time slider."""
    frames = []
    for i, (t, C) in enumerate(zip(result.time_points, result.time_snapshots)):
        mask = C > 0
        frames.append(
            go.Frame(
                data=[go.Scatter(
                    x=result.depth[mask],
                    y=np.log10(C[mask]),
                    mode="lines",
                    line=dict(color="royalblue", width=2),
                )],
                name=str(i),
                layout=go.Layout(title_text=f"t = {t:.0f} s"),
            )
        )

    C0 = result.time_snapshots[0]
    mask0 = C0 > 0
    fig = go.Figure(
        data=[go.Scatter(
            x=result.depth[mask0],
            y=np.log10(C0[mask0]),
            mode="lines",
            line=dict(color="royalblue", width=2),
        )],
        frames=frames,
    )

    fig.update_layout(
        title=f"{result.params.dopant} in Si — Diffusion Profile Evolution",
        xaxis_title="Depth (µm)",
        yaxis_title="log₁₀(C [cm⁻³])",
        template="plotly_white",
        font=dict(size=13),
        updatemenus=[dict(
            type="buttons",
            showactive=False,
            y=1.15,
            buttons=[
                dict(label="▶ Play", method="animate",
                     args=[None, dict(frame=dict(duration=100), fromcurrent=True)]),
                dict(label="⏸ Pause", method="animate",
                     args=[[None], dict(mode="immediate")]),
            ],
        )],
        sliders=[dict(
            steps=[
                dict(
                    args=[[f.name], dict(mode="immediate", frame=dict(duration=0))],
                    method="animate",
                    label=f"{t:.0f}s",
                )
                for f, t in zip(frames, result.time_points)
            ],
            transition=dict(duration=0),
            x=0, y=0,
            currentvalue=dict(prefix="Time: ", suffix=" s", font=dict(size=12)),
        )],
    )

    fig.write_html(output_path, include_plotlyjs="cdn")


def plot_animation_gif(result: DiffusionResult, output_path: str) -> None:
    """Matplotlib GIF animation for README embedding."""
    all_nonzero = np.concatenate(
        [C[C > 0] for C in result.time_snapshots if np.any(C > 0)]
    )
    y_min = np.log10(all_nonzero.min()) - 0.5
    y_max = np.log10(all_nonzero.max()) + 0.5

    fig, ax = plt.subplots(figsize=(8, 5))
    (line,) = ax.plot([], [], "b-", linewidth=2)
    time_text = ax.text(0.68, 0.92, "", transform=ax.transAxes, fontsize=11)

    ax.set_xlim(0, result.depth[-1])
    ax.set_ylim(y_min, y_max)
    ax.set_xlabel("Depth (µm)", fontsize=12)
    ax.set_ylabel("log₁₀(C [cm⁻³])", fontsize=12)
    ax.set_title(
        f"{result.params.dopant} in Si  |  T = {result.params.temperature_C:.0f}°C",
        fontsize=12,
    )
    ax.grid(True, alpha=0.3)

    def _update(i: int):
        C = result.time_snapshots[i]
        mask = C > 0
        if np.any(mask):
            line.set_data(result.depth[mask], np.log10(C[mask]))
        time_text.set_text(f"t = {result.time_points[i]:.0f} s")
        return line, time_text

    animation = anim_mod.FuncAnimation(
        fig, _update, frames=len(result.time_snapshots), interval=100, blit=True
    )
    animation.save(output_path, writer="pillow", fps=10)
    plt.close(fig)
