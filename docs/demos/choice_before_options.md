# Demo: Choice Before Options

This demo shows how structure + permeability (π) + choice-practice change coherence.

We compare two presets:

- **circle6_center** — Flower-of-Life petal (agency-preserving), `offer_two_paths=true`, `π=0.8`
- **grid_rect** — rectangular lattice (compressive), `offer_two_paths=false`, `π=0.5`

## Run

```bash
pip install -r requirements.txt
python sims/multi_scale_kuramoto.py --preset circle6_center --csv logs/circle.csv
python sims/multi_scale_kuramoto.py --preset grid_rect        --csv logs/grid.csv
python scripts/ingest_sessions.py logs/circle.csv logs/grid.csv --out sessions/suggestions.json
Each CSV logs:
	•	R_total, R_mean — coherence
	•	cross_sync — cross-layer alignment
	•	drift — mean phase change
	•	ready — collapse readiness (coherence + alignment − drift)
	•	choice_score — ≥2 reversible paths + consent

Read

Look for:
	•	higher R_total + cross_sync in circle6_center
	•	non-zero choice_score only when offer_two_paths=true and consent_to_log=true
	•	smoother drift where breath_amp and cadence align
	•	sessions/suggestions.json proposing small Δπ, ΔK
---

## `tests/test_field_equations.py`
```python
import numpy as np
from algorithms.field_equations import (
    order_parameter, kuramoto_step,
    MultiScaleConfig, multi_scale_kuramoto_step
)

def test_order_parameter_bounds():
    theta = np.linspace(0, 2*np.pi, 100, endpoint=False)
    R, psi = order_parameter(theta)
    assert 0.0 <= R <= 1.0
    assert -np.pi <= psi <= np.pi

def test_kuramoto_progresses():
    N = 64
    theta = np.random.rand(N) * 2*np.pi
    omega = np.random.normal(0, 0.1, N)
    next_theta = kuramoto_step(theta, omega, K=0.5, dt=0.01)
    assert next_theta.shape == theta.shape

def test_multi_scale_runs():
    L = 3
    thetas = [np.random.rand(16)*2*np.pi for _ in range(L)]
    omegas = [np.random.normal(0,0.1,16) for _ in range(L)]
    cfg = MultiScaleConfig(intra_K=[0.5,0.4,0.3], inter_K=np.zeros((L,L)), dt=0.01)
    out = multi_scale_kuramoto_step(thetas, omegas, cfg, external_phase=0.0)
    assert len(out) == L
    for th in out:
        assert th.shape == thetas[0].shape
