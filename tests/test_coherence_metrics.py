# -*- coding: utf-8 -*-
import numpy as np
from algorithms.coherence_metrics import (
    wrap_phase, order_parameter, phase_coherence,
    local_coherence, cross_edge_sync, phase_entropy_norm,
    lag1_smoothness, mean_drift, metrics_bundle
)

def line_adj(n):
    A = np.zeros((n,n))
    for i in range(n-1):
        A[i,i+1]=A[i+1,i]=1.0
    return A

def test_basic_values():
    n = 16
    theta = np.zeros(n)
    R, _ = order_parameter(theta)
    assert 0.99 <= R <= 1.0
    A = line_adj(n)
    C01 = (local_coherence(theta, A) + 1.0)*0.5
    X = cross_edge_sync(A, theta)
    assert 0.9 <= C01 <= 1.0 and 0.9 <= X <= 1.0

def test_entropy_and_flow():
    n = 64
    theta_uniform = np.linspace(0, 2*np.pi, n, endpoint=False)
    theta_cluster = np.concatenate([np.zeros(n//2), np.pi*np.ones(n//2)])
    e_u = phase_entropy_norm(theta_uniform)
    e_c = phase_entropy_norm(theta_cluster)
    assert e_u > e_c

    t0 = theta_uniform
    t1 = wrap_phase(t0 + 0.1)
    phi = lag1_smoothness(t1, t0)
    drift = mean_drift(t1, t0)
    assert 0.0 <= phi <= 1.0 and 0.0 <= drift <= np.pi

def test_bundle_contract():
    n = 12
    A = line_adj(n)
    t0 = np.zeros(n)
    t1 = wrap_phase(t0 + 0.05)
    R, cross01, drift, C01, Delta = metrics_bundle(t1, t0, A)
    for v in (R, cross01, C01, Delta):
        assert 0.0 <= v <= 1.0
