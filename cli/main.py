import argparse
import os
import sys

from physics_engine.models import DiffusionParams
from physics_engine.diffusion import solve_analytic, solve_fdm
from visualizer.static_plots import plot_profile
from visualizer.heatmap import plot_heatmap
from visualizer.animation import plot_animation_html, plot_animation_gif


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nanodopant-sim",
        description="TCAD-grade dopant diffusion simulator for silicon substrates.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--dopant", required=True, choices=["B", "P", "As", "Sb"],
                        help="Dopant species")
    parser.add_argument("--temp", type=float, required=True, metavar="CELSIUS",
                        help="Annealing temperature in C (valid range: 700-1200)")
    parser.add_argument("--time", type=float, required=True, metavar="SECONDS",
                        help="Annealing time in seconds")
    parser.add_argument("--profile", choices=["erfc", "gaussian"], default="erfc",
                        help="Diffusion profile model")
    parser.add_argument("--output", choices=["html", "gif", "png", "all"], default="all",
                        help="Output format(s) to generate")
    parser.add_argument("--solver", choices=["analytic", "fdm"], default="analytic",
                        help="Solver: closed-form analytical or finite-difference (FDM)")
    parser.add_argument("--depth", type=float, default=1.0, metavar="MICROMETERS",
                        help="Simulation depth in um")
    parser.add_argument("--conc", type=float, default=1e20, metavar="VALUE",
                        help="Surface concentration [cm^-3] (erfc) or implant dose [cm^-2] (gaussian)")
    return parser


def validate_args(args: argparse.Namespace) -> None:
    if not (700.0 <= args.temp <= 1200.0):
        print(f"Error: --temp must be 700-1200 C, got {args.temp}", file=sys.stderr)
        sys.exit(1)
    if args.time <= 0:
        print(f"Error: --time must be positive, got {args.time}", file=sys.stderr)
        sys.exit(1)
    if args.depth <= 0:
        print(f"Error: --depth must be positive, got {args.depth}", file=sys.stderr)
        sys.exit(1)
    if args.conc <= 0:
        print(f"Error: --conc must be positive, got {args.conc}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    validate_args(args)

    params = DiffusionParams(
        dopant=args.dopant,
        temperature_C=args.temp,
        time_s=args.time,
        profile=args.profile,
        depth_um=args.depth,
        surface_conc=args.conc,
    )

    try:
        solver = solve_analytic if args.solver == "analytic" else solve_fdm
        result = solver(params)
    except Exception as exc:
        print(f"Physics error: {exc}", file=sys.stderr)
        sys.exit(2)

    print(f"\nNanoDopant-Sim Results")
    print("-" * 35)
    print(f"  Dopant:          {result.params.dopant}")
    print(f"  Temperature:     {result.params.temperature_C:.0f} C")
    print(f"  Annealing time:  {result.params.time_s:.0f} s")
    print(f"  Profile:         {result.params.profile}")
    print(f"  Solver:          {args.solver}")
    print(f"  D_eff:           {result.D_eff:.3e} cm2/s")
    print(f"  Junction depth:  {result.junction_depth_um:.4f} um")

    output_dir = f"output_{args.dopant}_{int(args.temp)}C_{int(args.time)}s"
    os.makedirs(output_dir, exist_ok=True)

    if args.output in ("png", "all"):
        path = os.path.join(output_dir, "profile.png")
        plot_profile(result, path)
        print(f"\n  -> {path}")

    if args.output in ("html", "all"):
        path = os.path.join(output_dir, "heatmap.html")
        plot_heatmap(result, path)
        print(f"  -> {path}")

        path = os.path.join(output_dir, "animation.html")
        plot_animation_html(result, path)
        print(f"  -> {path}")

    if args.output in ("gif", "all"):
        path = os.path.join(output_dir, "animation.gif")
        plot_animation_gif(result, path)
        print(f"  -> {path}")

    print()


if __name__ == "__main__":
    main()
