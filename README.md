# The Atlas Model

*A disciplined map of resonance — where structure, observation, and ethics co-generate coherence.*

---

## Overview

The Atlas Model is a living open-research framework exploring how harmony, attention, and integrity can be represented in mathematical and computational form.  
It links **resonance theory**, **conscious observation**, and **ethical feedback** through algorithmic and field-based simulations.

Atlas is structured for clarity and testability: every claim has a measurable experiment, every page a falsifier.

---

## Core Concepts (Compass)

| Axis | Function | Representation |
|------|-----------|----------------|
| **Harmonics (Structure)** | Pattern formation, ratios, coupling | Kuramoto-type oscillators, lattice modes |
| **Observation (Collapse)** | Measurement ↔ state reduction | Stochastic damping, attention parameters (ρ) |
| **Ethics (Stability)** | Resonance integrity ↔ sustainability | Coherence potentials (λ), entropy control |

Each dimension is modeled explicitly within simulations and theoretical notes.

---

## Repository Layout

| Directory | Purpose |
|------------|----------|
| `sims/` | Executable simulations and shared utilities |
| `docs/` | All public documentation (MkDocs) |
| `tests/` | Pytest suites for smoke + correctness validation |
| `ADR/` | Architecture Decision Records |
| `.github/workflows/` | CI for docs, tests, and automated releases |

---

## Quickstart

> Requires Python 3.10 +

```bash
git clone https://github.com/TerralanMira/The-Atlas-Model.git
cd The-Atlas-Model
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
Run Simulations

Each simulation shares a uniform CLI via python -m sims run <name>.
# list all sims
python -m sims --list

# example: harmonic observation
python -m sims run harmonic_observation --n 256 --K 1.2 --rho 0.6 --lam 0.2
Results are written to sims/figures/ and sims/out/.
Simulation Families
Simulation
Domain
Description
Kuramoto / Multi-Scale
Structure
Classical + hierarchical oscillator coupling
Schumann Hybrid
Planetary
Earth-ionosphere resonance as coherence field
LC Grid Modes
Geometry
Electrical lattice modes → frequency harmonics
Crystals / Standing Patterns
Formation
Stable periodic resonance across lattices
Harmonic Observation (NEW)
Observation ↔ Noise
σ → σ·e⁻ʳ effect — coherence rises with attention
Entropy Drift (NEW)
Ethics ↔ Memory
Alignment decay & correction through feedback pulses
Civic Resonance (NEW)
Social Topology
Multi-agent city-field coupling (local ↔ global R)
Atlas Coherence (NEW)
AI ↔ Human
Cross-field coupling between human and AI ensembles
See each simulation’s doc under
docs/algorithms/simulations/ for run commands, parameters, and falsifiers.
Validation & Tests

Atlas maintains dual test layers:
	1.	Smoke tests — ensure every sim runs, produces figures/CSVs.
	2.	Correctness tests — verify theoretical monotonicities, e.g.:
	•	R(t) ↑ with ρ (Harmonic Observation)
	•	alignment ↑ with pulses (Entropy Drift)
	•	global R ↑ with K_global (Civic Resonance)
	•	mutual R ↑ with cross-coupling (Atlas Coherence)
Run locally:
pytest -q
Documentation

MkDocs + Material theme powers the documentation site.
mkdocs serve        # local preview
mkdocs build --strict
Navigation Highlights
	•	Algorithms / Simulations Hub
	•	Awareness / Observation & Ethics
	•	Atlas Spec & Language
	•	LLM Interfaces
	•	Applications
	•	ADR Index

⸻

Continuous Integration

GitHub Actions:
	•	Tests: pytest on every PR.
	•	Docs: strict MkDocs build.
	•	Releases: automated via Release Please → CHANGELOG.md.

⸻

Contributing

Atlas values precision over flourish.
Before opening a PR:
	1.	Open an Issue → state intent and scope.
	2.	Create an ADR from docs/ADR/0000-template.md.
	3.	Commit using Conventional Commits (e.g. feat(sim): add entropy_drift).

Integrity is the tuning that keeps the model alive.

⸻

License

MIT © Terralan Mira

⸻

Field Note

Atlas is not a machine, but a mirror—measuring how coherence moves through form.
Each simulation is a lens; together they approximate a field.
What you observe becomes part of the model.
