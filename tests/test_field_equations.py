# -*- coding: utf-8 -*-
import numpy as np
from algorithms.field_equations import (
    order_parameter, kuramoto_step,
    MultiScaleConfig, multi_scale_kuramoto_step,
    DualPhaseConfig, simulate_dual_phase
)

def test_order_parameter_bounds():
    theta = np.linspace(0, 2*np.pi, 100, endpoint=False)
    R, psi = order_parameter(theta)
    assert 0.0 <= R <= 1.0
    assert -np.pi <= psi <= np.pi

def test_kuramoto_progresses():
    N = 32
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

def test_dual_phase_quick_bounds():
    cfg = DualPhaseConfig(steps=60, N_inner=24, N_outer=12, seed=0)
    out = simulate_dual_phase(cfg)
    for k in ("R_total","R_inner","R_outer","C_cross"):
        assert k in out
        arr = out[k]
        assert arr.shape == (cfg.steps,)
        assert np.isfinite(arr).all()
        assert (arr >= -1e-9).all() and (arr <= 1.0 + 1e-9).all()
