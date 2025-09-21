#!/usr/bin/env python3
"""
algorithms/coherence_metrics.py

Coherence + flow metrics used across sims and dashboards.
Independent, numpy-only. Safe fallbacks for all consumers.
"""

from __future__ import annotations
import math
from typing import Tuple
import numpy as np

TAU = 2.0 * math.pi

# ──────────────────────────────────────────────────────────────────────────────
# Core helpers
# ──────────────────────────────────────────────────────────────────────────────

def wrap_phase(theta: np.ndarray) -> np.ndarray:
    """Map angles to (-pi, pi]."""
    return np.mod(theta + np.pi, 2.0 * np.pi) - np.pi

def complex_mean_angle(theta: np.ndarray) -> float:
    """Angle of the mean complex phasor."""
    z = np.exp(1j * theta).mean()
    return float(np.angle(z))

# ──────────────────────────────────────────────────────────────────────────────
# Global / local coherence
# ──────────────────────────────────────────────────────────────────────────────

def phase_coherence(theta: np.ndarray) -> float:
    """
    Kuramoto order parameter magnitude in [0,1].
    0 = incoherent, 1 = fully phase-locked.
    """
    return float(np.abs(np.exp(1j * theta).mean()))

def local_coherence(theta: np.ndarray, adjacency: np.ndarray) -> float:
    """
    Mean cosine agreement across edges.
    Returns raw mean in [-1,1]. Map to [0,1] by (x+1)/2 if desired.
    """
    A = np.maximum(adjacency, adjacency.T)
    I, J = np.where(A > 0)
    if I.size == 0:
        return 0.0
    d = theta[J] - theta[I]
    return float(np.cos(d).mean())

def cross_edge_sync(adjacency: np.ndarray, theta: np.ndarray) -> float:
    """
    Local agreement remapped to [0,1] for dashboards.
    """
    A = np.maximum(adjacency, adjacency.T)
    I, J = np.where(A > 0)
    if I.size == 0:
        return 0.0
    d = theta[J] - theta[I]
    return float((np.cos(d).mean() + 1.0) * 0.5)

# ──────────────────────────────────────────────────────────────────────────────
# Diversity / flow / drift
# ──────────────────────────────────────────────────────────────────────────────

def phase_entropy_norm(theta: np.ndarray, bins: int = 36) -> float:
    """
    Normalized entropy of the phase histogram in [0,1].
    0 ~ concentrated / clamped. 1 ~ maximally spread.
    """
    h, _ = np.histogram(np.mod(theta, TAU), bins=bins, range=(0.0, TAU))
    p = h.astype(float)
    s = p.sum()
    if s <= 0:
        return 0.0
    p /= s
    with np.errstate(divide="ignore", invalid="ignore"):
        ent = -(p * np.log(p + 1e-12)).sum()
    return float(ent / math.log(bins))

def lag1_smoothness(theta_now: np.ndarray, theta_prev: np.ndarray) -> float:
    """
    Flow gentleness in [0,1]; higher = smoother changes.
    """
    dphi = np.angle(np.exp(1j * (theta_now - theta_prev)))
    return float((np.cos(dphi).mean() + 1.0) * 0.5)

def mean_drift(theta_now: np.ndarray, theta_prev: np.ndarray) -> float:
    """
    Mean absolute phase change per step (0..pi).
    Useful as 'drift' indicator.
    """
    return float(np.mean(np.abs(np.angle(np.exp(1j * (theta_now - theta_prev))))))

# ──────────────────────────────────────────────────────────────────────────────
# Natural frequency samplers
# ──────────────────────────────────────────────────────────────────────────────

def omega_gaussian(n: int, mean: float = 0.0, std: float = 0.1, seed: int | None = None) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.normal(mean, std, size=n).astype(float)

def omega_harmonic_scale(n: int, scale: list[int | float], seed: int | None = None) -> np.ndarray:
    rng = np.random.default_rng(seed)
    base = np.array(scale, dtype=float)
    vals = np.tile(base, int(np.ceil(n / len(base))))[:n]
    vals = vals + rng.normal(0.0, 0.01, size=n)
    return vals.astype(float)

def omega_spiral(n: int, turns: float = 2.0, std: float = 0.05, seed: int | None = None) -> np.ndarray:
    rng = np.random.default_rng(seed)
    t = np.linspace(0.0, 1.0, n)
    base = turns * t
    return (base + rng.normal(0.0, std, size=n)).astype(float)

# ──────────────────────────────────────────────────────────────────────────────
# Convenience bundle (one call → all metrics)
# ──────────────────────────────────────────────────────────────────────────────

def metrics_bundle(theta_now: np.ndarray,
                   theta_prev: np.ndarray,
                   adjacency: np.ndarray) -> Tuple[float, float, float, float, float]:
    """
    Returns (R_total, cross_sync01, drift, C01, Delta).
    Phi (smoothness) is easily computed from lag1_smoothness if needed.
    """
    R_total = phase_coherence(theta_now)
    cross01 = cross_edge_sync(adjacency, theta_now)
    drift   = mean_drift(theta_now, theta_prev)
    C_raw   = local_coherence(theta_now, adjacency)
    C01     = (C_raw + 1.0) * 0.5
    Delta   = phase_entropy_norm(theta_now)
    return float(R_total), float(cross01), float(drift), float(C01), float(Delta)
