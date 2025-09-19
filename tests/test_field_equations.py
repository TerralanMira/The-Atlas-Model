import numpy as np
from algorithms.field_equations import DualPhaseConfig, simulate_dual_phase, soul_resonance, SoulSignature

def test_dual_phase_runs():
    cfg = DualPhaseConfig(N_inner=32, N_outer=16, steps=200, dt=0.05, seed=1)
    out = simulate_dual_phase(cfg)
    assert "R_total" in out and len(out["R_total"]) == cfg.steps
    assert 0.0 <= out["R_total"][-1] <= 1.0

def test_soul_resonance_positive():
    sig = SoulSignature(MOmega=1.2, beta_echo=0.7, pi=0.8, W=0.75, I=0.8, Psi=0.7, H=0.7, S=0.85)
    r = soul_resonance(sig, R_between=0.6)
    assert r > 0.0
 Run:
pip install pytest numpy
pytest -q
 
