# -*- coding: utf-8 -*-
import numpy as np
from algorithms.coherence_metrics import (
    phase_coherence,
    local_coherence,
    cross_edge_sync,
    phase_entropy_norm,
    lag1_smoothness,
    mean_drift,
    metrics_bundle,
    wrap_phase,
)

def line_adjacency(n: int) -> np.ndarray:
    A = np.zeros((n, n), dtype=float)
    for i in range(n - 1):
        A[i, i + 1] = 1.0
        A[i + 1, i] = 1.0
    return A

def test_basic_coherence_values():
    n = 8
    theta_sync = np.zeros(n)
    theta_split = np.linspace(0, 2*np.pi, n, endpoint=False)
    A = line_adjacency(n)

    R_sync = phase_coherence(theta_sync)
    R_split = phase_coherence(theta_split)
    assert 0.0 <= R_sync <= 1.0 and 0.0 <= R_split <= 1.0
    assert R_sync > R_split, "perfect sync should have higher R"

    C_raw = local_coherence(theta_sync, A)
    C01 = (C_raw + 1.0) * 0.5
    X = cross_edge_sync(A, theta_sync)
    assert 0.0 <= C01 <= 1.0
    assert 0.0 <= X <= 1.0
    assert X >= 0.9, "cross-edge sync should be near 1.0 for aligned phases"

def test_entropy_and_flow():
    n = 64
    theta_uniform = np.linspace(0, 2*np.pi, n, endpoint=False)
    theta_cluster = np.concatenate([np.zeros(n//2), np.pi*np.ones(n//2)])
    ent_uniform = phase_entropy_norm(theta_uniform, bins=32)
    ent_cluster = phase_entropy_norm(theta_cluster, bins=32)
    assert ent_uniform > ent_cluster, "uniform phases have higher entropy"

    theta_prev = theta_uniform.copy()
    theta_now = wrap_phase(theta_prev + 0.1)  # tiny shift
    phi = lag1_smoothness(theta_now, theta_prev)
    drift = mean_drift(theta_now, theta_prev)
    assert 0.0 <= phi <= 1.0
    assert 0.0 <= drift <= np.pi

def test_metrics_bundle_contract():
    n = 12
    A = line_adjacency(n)
    t0 = np.zeros(n)
    t1 = wrap_phase(t0 + 0.05)
    R, cross01, drift, C01, Delta = metrics_bundle(t1, t0, A)
    for v in [R, cross01, C01, Delta]:
        assert 0.0 <= v <= 1.0
    assert 0.0 <= drift <= np.pi
