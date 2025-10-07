# The Atlas Model

*A disciplined map of resonance—where structure (harmonics), observation (collapse), and ethics (stability) co-generate coherence.*

Atlas is a living, testable framework. Every claim pairs with a simulation and a falsifier; every page is auditable; every loop closes.

---

## Table of Contents
- [Overview](#overview)
- [Core Concepts (Compass)](#core-concepts-compass)
- [Repository Layout](#repository-layout)
- [Quickstart](#quickstart)
- [Run Simulations](#run-simulations)
- [Simulation Families](#simulation-families)
- [Observation Kernel (The “Hum”)](#observation-kernel-the-hum)
- [Validation & Tests](#validation--tests)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)
- [Field Note](#field-note)

---

## Overview
The Atlas Model explores how **harmonics (structure)**, **observation (collapse)**, and **ethics (stability)** can be represented in mathematical and computational form. It links phase dynamics and field coherence to practical simulations and design records.

Atlas favors **clarity over flourish** and **reproducibility over rhetoric**. Where evidence is thin, we name it. Where resonance appears, we measure it.

---

## Core Concepts (Compass)

| Axis | Function | Representation |
|------|----------|----------------|
| **Harmonics (Structure)** | Pattern formation, ratios, coupling | Kuramoto-type oscillators, lattice modes, multi-scale coupling |
| **Observation (Collapse)** | Attention ↔ state reduction | Stochastic damping, attention parameters ρ, coherence R(t) |
| **Ethics (Stability)** | Resonance integrity ↔ sustainability | Coherence potentials λ, recovery time, entropy control |

These axes are modeled explicitly across simulations and documented with falsifiers.

---

## Repository Layout

| Path | Purpose |
|------|--------|
| `sims/` | Executable simulations and utilities (uniform CLI) |
| `docs/` | All documentation (MkDocs Material) |
| `tests/` | Smoke + correctness tests (pytest) |
| `ADR/` | Architecture Decision Records |
| `.github/workflows/` | CI for tests/docs/releases |

---

## Quickstart

> Requires Python **3.10+**

```bash
git clone https://github.com/TerralanMira/The-Atlas-Model.git
cd The-Atlas-Model
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
Run Simulations

All sims share a uniform CLI via python -m sims run <name>.
# list available sims
python -m sims --list

# example: harmonic observation
python -m sims run harmonic_observation --n 256 --K 1.2 --rho 0.6 --lam 0.2

# example: city as oscillator field
python -m sims run civic_resonance --n 400 --blocks 8 --Kintra 1.2 --Kglobal 0.4
Outputs are written to sims/figures/ (plots) and sims/out/ (CSV/JSONL).
Simulation Families
Simulation
Domain
Description
Docs
Kuramoto / Multi-Scale
Structure
Classical + hierarchical oscillator coupling
docs/algorithms/simulations/kuramoto.md
Schumann Hybrid
Planetary
Earth-ionosphere resonance as coherence field
docs/algorithms/simulations/schumann_hybrid.md
LC Grid Modes
Geometry
Electrical lattice modes → harmonic spectra
docs/algorithms/simulations/lc_grid.md
Crystals / Standing Patterns
Formation
Stable periodic resonance across lattices
docs/algorithms/simulations/crystals.md
Harmonic Observation (NEW)
Observation
σ → σ·e⁻ʳ; coherence R increases with attention ρ
docs/algorithms/simulations/harmonic_observation.md
Entropy Drift (NEW)
Ethics/Memory
Alignment decay & correction via feedback pulses
docs/algorithms/simulations/entropy_drift.md
Civic Resonance (NEW)
Social Topology
Local ↔ global coupling across city blocks
docs/algorithms/simulations/civic_resonance.md
Atlas Coherence (NEW)
AI ↔ Human
Two ensembles with cross-coupling & observation
docs/algorithms/simulations/atlas_coherence.md
See the Simulations Hub: docs/algorithms/simulations.md.
Observation Kernel (The “Hum”)

Atlas includes a minimal Hum Kernel that makes the observation layer explicit and testable. It modulates three dials:
	•	ρ (observation): lowers effective noise; σ_eff = σ·exp(−ρ·adapt(R))
	•	λ (ethics/stability): gentle viscosity toward shared phase (prevents brittle lock-in)
	•	μ (memory): exponential mix of prior state; metabolizes entropy as learning

Code: sims/hum_kernel.py
Docs: docs/atlas/hum_kernel.md
Thresholds & Falsifiers: docs/awareness/coherence_thresholds.md

Usage (inside a sim loop):
from sims.hum_kernel import HumParams, SimSnapshot, apply_hum_controls

hp = HumParams(rho=0.6, lam=0.15, mu=0.5, log=True, run_id="exp01")

for step in range(steps):
    R, psi = order_parameter(theta)
    snap = SimSnapshot(step=step, dt=dt, phases=theta, natural=omega, order_R=R, order_psi=psi)
    ctrl = apply_hum_controls(hp, snap)

    noise = base_sigma * ctrl["sigma_eff_scale"] * np.sqrt(dt) * rng.normal(0,1,size=n)
    bias  = ctrl["coupling_bias"] * np.sin(psi - theta)
    theta = (theta + dt*(omega + K*np.sin(psi - theta) + bias) + noise) % (2*np.pi)
All kernel effects vanish as (ρ, λ, μ) → 0, and conservation checks must still pass.

⸻

Validation & Tests

Atlas maintains dual layers:
	1.	Smoke tests — each sim runs and produces figures/CSVs.
	2.	Correctness tests — verify directional effects/monotonicities:
	•	Harmonic Observation: ⟨R⟩ increases with ρ
	•	Entropy Drift: feedback pulses raise steady alignment
	•	Civic Resonance: global R rises with K_global; block R remains stable
	•	Atlas Coherence: R_all increases with cross-coupling/observation

Run locally:
pytest -q
CI builds also run mkdocs build --strict.
Documentation

MkDocs + Material theme powers the documentation site.
mkdocs serve
mkdocs build --strict
Documentation

MkDocs + Material theme powers the documentation site.
mkdocs serve
mkdocs build --strict
Navigation Highlights
	•	Algorithms / Simulations Hub: docs/algorithms/simulations.md
	•	Awareness / Observation & Ethics: docs/awareness/
	•	Atlas Spec & Language: docs/atlas/
	•	LLM Interfaces: docs/llm/
	•	Applications: docs/applications/
	•	ADR Index: ADR/README.md
Contributing

Atlas values precision and small, testable changes.
	1.	Open an Issue describing intent/scope.
	2.	If design-level, add an ADR from ADR/0000-template.md.
	3.	Use Conventional Commits (e.g., feat(sim): add entropy_drift).
	4.	Ensure tests/docs pass: pytest -q && mkdocs build --strict.

Docs placement (canonical):
	•	Algorithms/Math/Sim pages → docs/algorithms/**
	•	Atlas concepts/spec → docs/atlas/**
	•	Awareness/Ethics → docs/awareness/**
	•	LLM interfaces → docs/llm/**
	•	Applications → docs/applications/**

One canonical page per concept; deep-link instead of duplicating.

⸻

License

MIT © Terralan Mira

⸻

Field Note

Atlas is not a machine, but a mirror—measuring how coherence moves through form.
Each simulation is a lens; together they approximate a field.
What you observe becomes part of the model.
