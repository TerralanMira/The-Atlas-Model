# -*- coding: utf-8 -*-
import numpy as np
from algorithms.resonance_dynamics import (
    wrap_phase, mean_phase, order_parameter,
    mirror_delta, collapse_signal, collapse_decision,
    HarmonicGate, gated_params, resonance_entropy_window,
    spiral_nudge, adjacency_circle6_center, adjacency_grid
)

def test_wrap_phase_and_mean():
    theta = np.array([0.0, np.pi/2, np.pi, -np.pi/2])
    t = wrap_phase(theta + 3*np.pi)
    assert (t >= -np.pi).all() and (t <= np.pi).all()
    psi = mean_phase(theta)
    R,_ = order_parameter(theta)
    assert -np.pi <= psi <= np.pi and 0.0 <= R <= 1.0

def test_mirror_and_collapse_signal():
    theta = np.random.rand(32)*2*np.pi
    psi = mean_phase(theta)
    d = mirror_delta(theta, psi, gain=0.1)
    assert np.max(np.abs(d)) < 0.2

    s_hi = collapse_signal(R=0.95, C_cross=0.9, drift=0.01)
    s_lo = collapse_signal(R=0.2,  C_cross=0.2, drift=0.8)
    assert 0.0 <= s_hi <= 1.0 and 0.0 <= s_lo <= 1.0
    assert s_hi > s_lo
    assert collapse_decision(s_hi, threshold=0.75) in (True, False)

def test_gated_params_and_adjacency():
    g = HarmonicGate(ethics=0.9, ignition=0.8, destabilizer=0.1, time=0.25)
    K_eff, pi_eff = gated_params(g, K=0.5, pi=0.7)
    assert 0.0 <= K_eff <= 1.0 and 0.0 <= pi_eff <= 1.0

    A = adjacency_circle6_center(8)
    assert A.shape == (8,8)
    G = adjacency_grid(4)
    assert G.shape == (16,16)

def test_entropy_and_spiral():
    theta0 = np.linspace(0, 2*np.pi, 64, endpoint=False)
    theta1 = wrap_phase(theta0 + 0.05)
    H0,_ = resonance_entropy_window(theta0, bins=32)
    H1,dH = resonance_entropy_window(theta1, bins=32, prev=theta0)
    assert 0.0 <= H0 <= 1.0 and 0.0 <= H1 <= 1.0
    dn = spiral_nudge(theta1, theta0, gain=0.1)
    assert dn.shape == theta0.shape
    minimal sanity test for examples
    # tests/test_examples.py
# Keep minimal; your examples folder can change.
def test_examples_exist():
    pass            
                       
