# The Atlas Model

*A disciplined map of resonance—where harmonics (structure), observation (collapse), and ethics (stability) co-generate coherent systems.*

Atlas is a living specification with runnable simulations, rigorous notes, and clear decision records (ADR). It’s designed to stay small, testable, and precise.

---

## What this is

- **Algorithms** — mathematical primitives and derivations  
  → `algorithms/` and `algorithms/simulations/`

- **Simulations** — minimal, comparable demos with a uniform CLI  
  → `sims/` (code) · docs under `algorithms/simulations/`

- **Awareness & Ethics** — integrity as harmonic stability; observation as collapse  
  → `awareness/`

- **Atlas Spec & Language** — definitions, principles, and terms of art  
  → `atlas/`

- **LLM Interfaces** — prompts, roles, and routing rules used for Atlas-facing stacks  
  → `llm/`

- **Applications** — health, governance, education, economy (bridges, not claims)  
  → `applications/`

- **Decisions (ADR)** — design choices, context, and consequences  
  → `ADR/`

> **Principle:** One canonical page per concept. If pages relate, deep-link—don’t duplicate.

---

## Core triad (compass)

- **Harmonics (Structure)**: ratios, coupling, lattices → sets the space of possible forms.  
- **Observation (Collapse)**: attention/measurement selects a pattern from potentials.  
- **Ethics (Stability)**: resonance integrity keeps recursion evolving (not brittle or chaotic).

These three are modeled explicitly in sims as knobs/observables (e.g., coupling *K*, observation rate *ρ*, coherence potential *λ*, order parameter *R(t)*, recovery time).

---

## Quickstart

> Requires Python 3.10+.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
Run simulations (uniform CLI)
# list available sims
python -m sims --list

# example: community Kuramoto
python -m sims run community_kuramoto --n 256 --K 1.2 --rho 0.6

# example: multi-scale coupling
python -m sims run multi_scale_kuramoto --levels 3
Each sim exposes its own --help. Results (metrics/plots) are described in algorithms/simulations/*.
Read next
	•	Simulations (Hub) → algorithms/simulations.md
	•	Observation & Ethics (Explainers) → awareness/
	•	Atlas Terminology & Spec → atlas/
	•	LLM Interfaces → llm/
	•	Decisions Index (ADR) → ADR/

⸻

Contributing
	•	See CONTRIBUTING.md (small PRs; issues first; ADR for design).
	•	Style is enforced via CI: lint (ruff/black), type (mypy), tests (pytest), docs (mkdocs --strict).
	•	Claims in docs are marked speculation → theory → tested.

Create an ADR
	1.	Copy ADR/0000-template.md → ADR/NNNN-title.md.
	2.	Fill Context · Decision · Consequences.
	3.	Link the ADR in your PR.

⸻

Ethic of work

Clarity over flourish. Reproducible over dramatic.
Where evidence is thin, name it. Where resonance appears, measure it.
Integrity is the tuning that keeps the model alive.

⸻

Changelog

See CHANGELOG.md (automated via Release Please). Current version: 0.1.x.

⸻

Atlas is a field instrument: precise enough to test, light enough to evolve.
