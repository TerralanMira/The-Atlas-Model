import numpy as np
import math

from algorithms.resonance_dynamics import (
    wrap_phase, mean_phase, order_parameter,
    mirror_delta,
    collapse_signal, collapse_decision,
    HarmonicGate, gated_params,
    resonance_entropy_window,
    spiral_nudge,
    adjacency_circle6_center, adjacency_grid,
)

# ---------- basics ----------

def test_wrap_phase_bounds():
    x = np.array([-1.0, 0.0, 2*math.pi, 7*math.pi])
    y = wrap_phase(x)
    assert np.all(y >= 0.0) and np.all(y < 2*math.pi)

def test_mean_phase_and_order_parameter_simple():
    theta = np.linspace(0, 2*np.pi, 100, endpoint=False)
    R, psi = order_parameter(theta)
    assert 0.0 <= R <= 1.0
    assert -np.pi <= psi <= np.pi
    # perfectly aligned case
    theta2 = np.zeros(50)
    R2, psi2 = order_parameter(theta2)
    assert R2 == 1.0
    assert abs(psi2 - 0.0) < 1e-9

# ---------- mirror law ----------

def test_mirror_delta_small_nudge_toward_mean():
    theta = np.array([0.0, np.pi/2, np.pi])
    R, psi = order_parameter(theta)
    d = mirror_delta(theta, psi, gain=0.05)
    assert d.shape == theta.shape
    # nudge magnitudes should be small
    assert np.max(np.abs(d)) < 0.2

def test_mirror_delta_zero_gain_no_change():
    theta = np.random.rand(10) * 2*np.pi
    psi = mean_phase(theta)
    d = mirror_delta(theta, psi, gain=0.0)
    assert np.allclose(d, 0.0)

# ---------- collapse (choice) ----------

def test_collapse_signal_bounds_and_trends():
    # high R, high cross_sync, low drift -> high score
    s_hi = collapse_signal(R=0.95, cross_sync=0.9, drift=0.01)
    # low R, low cross_sync, high drift -> low score
    s_lo = collapse_signal(R=0.2, cross_sync=0.1, drift=0.8)
    assert 0.0 <= s_hi <= 1.0 and 0.0 <= s_lo <= 1.0
    assert s_hi > s_lo

def test_collapse_decision_threshold():
    assert collapse_decision(score=0.80, threshold=0.72) is True
    assert collapse_decision(score=0.65, threshold=0.72) is False

# ---------- harmonic infinity gate ----------

def test_harmonic_gate_scales_params():
    gate = HarmonicGate(integrity=0.8, stamina=0.9, humility=1.0, destabilizer=0.2, time_kernel=1.0)
    K_g, pi_g = gate.gate(K=0.5, pi=0.8)
    assert 0.0 <= K_g <= 2.0
    assert 0.0 <= pi_g <= 1.5
    # if ethics are zero, outputs should not inflate
    gate_zero = HarmonicGate(integrity=0.0, stamina=0.0, humility=0.0, destabilizer=0.0, time_kernel=1.0)
    K0, pi0 = gate_zero.gate(0.5, 0.8)
    assert K0 <= 0.5 and pi0 <= 0.8

def test_gated_params_wrapper():
    K_g, pi_g = gated_params(0.6, 0.9, integrity=1.0, stamina=1.0, humility=1.0, destabilizer=0.0, time_kernel=1.0)
    assert K_g >= 0.6 and pi_g >= 0.9

# ---------- resonance vs entropy ----------

def test_resonance_entropy_window_shapes_and_balance():
    R_series = np.concatenate([np.ones(50)*0.8, np.ones(50)*0.85])
    drift_series = np.concatenate([np.ones(50)*0.1, np.ones(50)*0.08])
    Rm, Em, bal = resonance_entropy_window(R_series, drift_series, window=80)
    assert 0.0 <= Rm <= 1.0
    assert 0.0 <= Em <= 1.0
    assert isinstance(bal, float)
    # higher coherence & lower drift should tilt balance positive
    assert bal > 0.0

# ---------- return spiral ----------

def test_spiral_nudge_converges_toward_target():
    current = 0.2
    target = 1.0
    for _ in range(100):
        current = spiral_nudge(current, target, rate=0.05, band=(0.0, 2.0))
    assert abs(current - target) < 1e-2

# ---------- geometry helpers ----------

def test_adjacency_circle6_center_properties():
    A = adjacency_circle6_center()
    assert A.shape == (7, 7)
    # symmetric and zero diagonal
    assert np.allclose(A, A.T)
    assert np.allclose(np.diag(A), 0.0)
    # center (0) connected to 6 others
    assert int(A[0].sum()) == 6

def test_adjacency_grid_properties():
    A = adjacency_grid(3, 3, diagonal=False)
    assert A.shape == (9, 9)
    assert np.allclose(A, A.T)
    # interior node (1,1) index 4 has 4 neighbors in 4-neigh grid
    assert int(A[4].sum()) == 4
