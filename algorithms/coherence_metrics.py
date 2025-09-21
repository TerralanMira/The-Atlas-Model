# -*- coding: utf-8 -*-
"""
Coherence & resonance metrics for The Atlas Model.

Exports:
- wrap_phase(theta)
- order_parameter(theta) -> (R, psi)
- phase_coherence(theta) -> (R, psi)
- local_coherence(theta, A) -> raw mean cos difference ([-1,1])
- cross_edge_sync(A, theta) -> [0,1]
- phase_entropy_norm(theta, bins=32) -> [0,1]
- lag1_smoothness(theta_now, theta_prev) -> [0,1]
- mean_drift(theta_now, theta_prev) -> [0, pi]
- metrics_bundle(theta_now, theta_prev, A) -> (R, cross01, drift, C01, Delta)
"""
from __future__ import annotations
import numpy as np

TAU = 2*np.pi

def wrap_phase(theta: np.ndarray) -> np.ndarray:
    return (theta + np.pi) % TAU - np.pi

def order_parameter(theta: np.ndarray) -> tuple[float, float]:
    z = np.exp(1j*theta).mean()
    return float(np.abs(z)), float(np.angle(z))

def phase_coherence(theta: np.ndarray) -> tuple[float, float]:
    return order_parameter(theta)

def local_coherence(theta: np.ndarray, A: np.ndarray) -> float:
    # raw mean cosine of differences on edges (in [-1,1])
    if A.size == 0 or A.sum() == 0:
        return 0.0
    num = 0.0
    den = 0.0
    for i in range(A.shape[0]):
        nbrs = np.where(A[i] > 0)[0]
        if nbrs.size == 0: 
            continue
        d = wrap_phase(theta[nbrs] - theta[i])
        num += np.cos(d).sum()
        den += nbrs.size
    return float(num/den) if den else 0.0

def cross_edge_sync(A: np.ndarray, theta: np.ndarray) -> float:
    # map local_coherence to [0,1]
    C = local_coherence(theta, A)
    return float((C + 1.0)*0.5)

def phase_entropy_norm(theta: np.ndarray, bins: int = 32) -> float:
    # circular histogram on [-pi,pi)
    t = wrap_phase(theta)
    hist, _ = np.histogram(t, bins=bins, range=(-np.pi, np.pi), density=False)
    p = hist / np.maximum(hist.sum(), 1e-9)
    with np.errstate(divide='ignore', invalid='ignore'):
        H = -(p * np.log(p + 1e-12)).sum()
    Hmax = np.log(bins)
    return float(H / Hmax) if Hmax > 0 else 0.0  # [0,1]

def lag1_smoothness(theta_now: np.ndarray, theta_prev: np.ndarray) -> float:
    d = wrap_phase(theta_now - theta_prev)
    # map small steps to ~1, large to ~0
    return float(np.exp(-np.mean(np.abs(d))))

def mean_drift(theta_now: np.ndarray, theta_prev: np.ndarray) -> float:
    d = wrap_phase(theta_now - theta_prev)
    return float(np.mean(np.abs(d)))

def metrics_bundle(theta_now: np.ndarray, theta_prev: np.ndarray, A: np.ndarray):
    R, _ = order_parameter(theta_now)
    cross01 = cross_edge_sync(A, theta_now)
    drift = mean_drift(theta_now, theta_prev)
    C_raw = local_coherence(theta_now, A)
    C01 = float((C_raw + 1.0)*0.5)
    Delta = phase_entropy_norm(theta_now)
    return float(R), float(cross01), float(drift), float(C01), float(Delta)
