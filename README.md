# NanoDopant-Sim

A TCAD-grade dopant diffusion simulator for silicon substrates, implementing Fick's Second Law with Arrhenius diffusivity, erfc and Gaussian profile models, an FDM numerical solver, interactive Plotly visualizations, and a full argparse CLI.

---

## Quick Start

```bash
pip install -r requirements.txt

# Boron drive-in at 1000 °C for 1 hour — generate all outputs
python -m cli.main --dopant B --temp 1000 --time 3600 --profile erfc --output all

# Phosphorus implant (Gaussian) with FDM solver, PNG only
python -m cli.main --dopant P --temp 950 --time 1800 --profile gaussian --solver fdm --output png
```

Outputs are written to a timestamped directory: `output_<DOPANT>_<TEMP>C_<TIME>s/`

---

## Physics Background

### Fick's Second Law

Dopant transport in a silicon lattice is governed by:

$$\frac{\partial C}{\partial t} = D \frac{\partial^2 C}{\partial x^2}$$

where $C(x, t)$ is the dopant concentration [cm⁻³], $x$ is depth [cm], $t$ is time [s], and $D$ is the diffusivity [cm²/s].

### Arrhenius Diffusivity

The temperature dependence of $D$ follows the Arrhenius relation:

$$D(T) = D_0 \, e^{-E_a / k_B T}$$

where $D_0$ is the pre-exponential factor [cm²/s], $E_a$ is the activation energy [eV], $k_B = 8.617 \times 10^{-5}$ eV/K is the Boltzmann constant, and $T$ is the absolute temperature [K].

### Erfc Profile (Constant Surface Source)

For an infinite surface supply (drive-in from a surface reservoir), the solution is:

$$C(x, t) = C_s \cdot \operatorname{erfc}\!\left(\frac{x}{2\sqrt{Dt}}\right)$$

where $C_s$ is the surface concentration [cm⁻³]. The junction depth $x_j$ is determined where $C(x_j, t) = C_{\text{bg}}$ (background doping, typically $10^{16}$ cm⁻³).

### Gaussian Profile (Limited Dose Implant)

For a fixed implant dose $Q$ [cm⁻²] driven into the substrate:

$$C(x, t) = \frac{Q}{\sqrt{\pi D t}} \exp\!\left(-\frac{x^2}{4Dt}\right)$$

The peak concentration at the surface decreases as $1/\sqrt{t}$ while conserving total dose.

---

## Dopant Parameters

| Dopant | Name | Type | D₀ (cm²/s) | Eₐ (eV) |
|--------|------|------|------------|---------|
| B | Boron | p-type | 0.76 | 3.46 |
| P | Phosphorus | n-type | 3.85 | 3.66 |
| As | Arsenic | n-type | 0.066 | 3.44 |
| Sb | Antimony | n-type | 0.214 | 3.65 |

All values are from the Sze & Ng tabulation for intrinsic diffusion in crystalline silicon.

---

## FDM Solver

The finite-difference method (FDM) solver discretizes Fick's Second Law on a uniform spatial grid using an explicit forward-time centered-space (FTCS) scheme. Time stepping respects the CFL stability criterion:

$$\Delta t \leq \frac{(\Delta x)^2}{2D}$$

Benchmarks against the closed-form analytic solution show < 5% relative error across the physically meaningful concentration range ($C > 10^{14}$ cm⁻³) for all four supported dopant species over the valid temperature range 700–1200 °C.

---

## CLI Reference

```
python -m cli.main [OPTIONS]
```

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--dopant` | choice | required | Dopant species: `B`, `P`, `As`, `Sb` |
| `--temp` | float | required | Annealing temperature in °C (700–1200) |
| `--time` | float | required | Annealing time in seconds (> 0) |
| `--profile` | choice | `erfc` | Diffusion profile model: `erfc` or `gaussian` |
| `--solver` | choice | `analytic` | Solver: `analytic` (closed-form) or `fdm` (finite-difference) |
| `--output` | choice | `all` | Output format: `png`, `html`, `gif`, or `all` |
| `--depth` | float | `1.0` | Simulation depth in µm (> 0) |
| `--conc` | float | `1e20` | Surface concentration [cm⁻³] (erfc) or implant dose [cm⁻²] (gaussian) |

### Example output

```
NanoDopant-Sim Results
-----------------------------------
  Dopant:          B
  Temperature:     1000 C
  Annealing time:  3600 s
  Profile:         erfc
  Solver:          analytic
  D_eff:           1.529e-14 cm2/s
  Junction depth:  0.4068 um

  -> output_B_1000C_3600s/profile.png
  -> output_B_1000C_3600s/heatmap.html
  -> output_B_1000C_3600s/animation.html
  -> output_B_1000C_3600s/animation.gif
```

---

## Architecture

NanoDopant-Sim is structured as three independent layers:

```
NanoDopant-Sim/
├── physics_engine/          # Layer 1 — Physics & numerics (pure Python/NumPy)
│   ├── models.py            #   DiffusionParams, DiffusionResult dataclasses
│   ├── dopants.py           #   Arrhenius parameters for B, P, As, Sb
│   ├── arrhenius.py         #   compute_diffusivity(dopant, T_K) -> D [cm²/s]
│   └── diffusion.py         #   solve_analytic(), solve_fdm() -> DiffusionResult
│
├── visualizer/              # Layer 2 — Visualization (Matplotlib + Plotly)
│   ├── static_plots.py      #   plot_profile() -> PNG
│   ├── heatmap.py           #   plot_heatmap() -> interactive HTML
│   └── animation.py         #   plot_animation_html() / plot_animation_gif()
│
├── cli/                     # Layer 3 — Interface (argparse CLI)
│   └── main.py              #   build_parser(), validate_args(), main()
│
├── notebooks/               # Case studies
│   └── finfet_2nm_case.ipynb
└── tests/                   # pytest suite (33 tests)
```

The layers have one-way dependencies: `cli` imports `physics_engine` and `visualizer`; `visualizer` imports `physics_engine`; `physics_engine` has no internal project dependencies.

---

## Relevance to FinFET and the 2nm Node

At the 2nm node (GAAFET/nanosheet architectures), source and drain extensions are separated from the channel by only 4–6 nm. Key requirements that connect directly to this simulator:

- **Junction depth control** — the erfc model predicts $x_j$ as a function of thermal budget; the 2nm target is $x_j < 10$ nm. The simulator quantitatively shows why spike RTP (< 1 s at 1050–1100 °C) is mandatory versus a conventional drive-in anneal.
- **Short-channel effect (SCE) suppression** — abrupt concentration gradients at the metallurgical junction reduce drain-induced barrier lowering (DIBL) and threshold voltage roll-off.
- **Thermal budget management** — the Arrhenius model reveals the sensitivity of $D$ to temperature; a 50 °C reduction at 1000 °C decreases $D_B$ by approximately 40%, directly constraining process integration choices.
- **Series resistance** — the Gaussian profile model applies to ultra-shallow junction formation after low-energy implantation, where preserving peak surface concentration minimizes contact resistance.

---

## Connection to Experimental Characterization

Simulation results are intended to be compared against, and validated by, physical characterization techniques:

| Technique | What it measures | Connection to model |
|-----------|-----------------|---------------------|
| **SIMS** (Secondary Ion Mass Spectrometry) | $C(x)$ concentration depth profile directly | Direct ground truth for erfc/Gaussian shape and junction depth |
| **XRD** (X-ray Diffraction) | Lattice strain from dopant-induced distortion | Verifies peak dopant concentration via Vegard's law |
| **TEM/STEM** | Physical junction abruptness, crystal quality | Validates absence of extended defects post-anneal |
| **4-point probe** | Sheet resistance $\rho_s$ | Integrates $C(x) \cdot \mu(x)$ over depth — corroborates $D_{\text{eff}}$ |

SIMS profiles extracted from test wafers are fitted against the erfc or Gaussian solution to extract an experimental $D_{\text{eff}}$, which is then compared to the Arrhenius prediction. Deviations indicate oxidation-enhanced diffusion (OED), dopant clustering, or non-equilibrium effects — motivating extensions toward full TCAD tools (Sentaurus, Silvaco).

---

## Running Tests

```bash
pytest tests/ -v
pytest tests/ --cov=physics_engine --cov=visualizer --cov-report=term-missing
```

The test suite covers analytic solver correctness, FDM stability and accuracy, Arrhenius diffusivity values, parameter validation, and CLI argument parsing — 33 tests total.

---

## Case Study Notebook

`notebooks/finfet_2nm_case.ipynb` — **FinFET 2nm Node: Boron Source/Drain Diffusion**

The notebook demonstrates:
1. Boron drive-in simulation at 1000 °C for a PMOS FinFET source/drain
2. Static concentration profile (PNG), interactive heatmap (HTML), and animated evolution (GIF)
3. Quantitative comparison of three anneal conditions (RTP spike 1 s, RTP 10 s, drive-in 3600 s) against the 2nm node junction depth target
4. Discussion of SIMS, XRD, TEM, and 4-point probe validation methods

To run:

```bash
cd notebooks
jupyter notebook finfet_2nm_case.ipynb
```

---

## Author

**Froylan González — Nanotechnology Engineering Graduate**  
fgonzalez63@alumnos.uaq.mx
