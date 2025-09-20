"""
algorithms/field_equations.py

Core field dynamics for The Atlas Model.

Provides:
  • Kuramoto oscillator dynamics (with optional external driver)
  • LC grid resonance via graph Laplacian coupling
  • Multi-scale Kuramoto coupling across layers
  • Order-parameter utility

Pure NumPy; no plotting; designed for sims to import.

License: MIT
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple, List
import numpy as np


# ─────────── Utilities ───────────

def order_parameter(theta: np.ndarray) -> Tuple[float, float]:
    """
    Kuramoto order parameter.
      R ∈ [0,1] measures coherence, psi is mean phase (radians).
    """
    z = np.exp(1j * theta)
    mean = np.mean(z)
    R = np.abs(mean)
    psi = np.angle(mean)
    return float(R), float(psi)


def graph_laplacian(adj: np.ndarray, normalized: bool = False) -> np.ndarray:
    """
    Compute (optionally normalized) graph Laplacian from adjacency.
    - adj: symmetric NxN, nonnegative.
    """
    deg = np.sum(adj, axis=1)
    L = np.diag(deg) - adj
    if not normalized:
        return L
    with np.errstate(divide="ignore"):
        d_inv_sqrt = np.where(deg > 0, 1.0 / np.sqrt(deg), 0.0)
    D_inv_sqrt = np.diag(d_inv_sqrt)
    I = np.eye(adj.shape[0])
    return I - D_inv_sqrt @ adj @ D_inv_sqrt


# ─────────── Kuramoto ───────────

@dataclass
class KuramotoConfig:
    K: float = 0.5
    dt: float = 0.01
    gamma_ext: float = 0.0                 # coupling to external phase
    adjacency: Optional[np.ndarray] = None # None => all-to-all


def kuramoto_step(
    theta: np.ndarray,
    omega: np.ndarray,
    K: float,
    dt: float,
    adjacency: Optional[np.ndarray] = None,
    external_phase: Optional[float] = None,
    gamma_ext: float = 0.0,
) -> np.ndarray:
    """
    One Euler step for Kuramoto oscillators.

    All-to-all:
      dθ_i = ω_i + (K * R) sin(ψ - θ_i) + γ sin(φ_ext - θ_i)

    Network:
      dθ_i = ω_i + K * sum_j A_ij sin(θ_j - θ_i)/deg_i + γ sin(φ_ext - θ_i)
    """
    theta = np.asarray(theta, dtype=float)
    omega = np.asarray(omega, dtype=float)

    if adjacency is None:
        R, psi = order_parameter(theta)
        coupling = K * R * np.sin(psi - theta)
    else:
        deg = np.sum(adjacency, axis=1)
        d = theta[None, :] - theta[:, None]
        S = np.sin(d)
        num = np.sum(adjacency * S, axis=1)
        denom = np.maximum(deg, 1.0)
        coupling = K * (num / denom)

    ext_term = 0.0
    if external_phase is not None and gamma_ext != 0.0:
        ext_term = gamma_ext * np.sin(external_phase - theta)

    dtheta = omega + coupling + ext_term
    return (theta + dt * dtheta) % (2 * np.pi)


# ─────────── LC grid (graph-coupled) ───────────

@dataclass
class LCGridConfig:
    dt: float = 0.005
    L: float | np.ndarray = 1.0
    C: float | np.ndarray = 1.0
    G: float = 1.0
    normalized_laplacian: bool = True


def lc_grid_step(
    v: np.ndarray,
    i: np.ndarray,
    adj: np.ndarray,
    cfg: LCGridConfig,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Discrete-time LC grid with graph Laplacian coupling.

    C dv/dt = i
    L di/dt = -v - G * (Laplacian @ v)

    Semi-implicit:
      i_{t+dt} = i_t + dt/L * (-v_t - G Lg v_t)
      v_{t+dt} = v_t + dt/C * i_{t+dt}
    """
    Lg = graph_laplacian(adj, normalized=cfg.normalized_laplacian)
    L = np.asarray(cfg.L if np.ndim(cfg.L) else np.full_like(v, cfg.L), dtype=float)
    C = np.asarray(cfg.C if np.ndim(cfg.C) else np.full_like(v, cfg.C), dtype=float)

    Ls = np.where(L == 0, 1e-9, L)
    Cs = np.where(C == 0, 1e-9, C)

    force = -v - cfg.G * (Lg @ v)
    i_next = i + (cfg.dt / Ls) * force
    v_next = v + (cfg.dt / Cs) * i_next
    return v_next, i_next


# ─────────── Multi-scale Kuramoto ───────────

@dataclass
class MultiScaleConfig:
    intra_K: List[float]
    inter_K: np.ndarray
    dt: float = 0.01
    gamma_ext: float = 0.0  # applied equally to layers


def multi_scale_kuramoto_step(
    thetas: List[np.ndarray],
    omegas: List[np.ndarray],
    cfg: MultiScaleConfig,
    external_phase: Optional[float] = None,
) -> List[np.ndarray]:
    """
    Advance L Kuramoto layers with intra- and inter-layer coupling.
    For layer k:
      dθ_i = ω_i + K_intra_k R_k sin(ψ_k - θ_i)
             + Σ_m inter_K[k,m] sin(ψ_m - θ_i)
             + γ sin(φ_ext - θ_i)
    """
    L = len(thetas)
    out: List[np.ndarray] = []

    layer_means = [order_parameter(th) for th in thetas]  # (R, psi)

    for k in range(L):
        th, om = thetas[k], omegas[k]
        Rk, psik = layer_means[k]

        coupling = cfg.intra_K[k] * Rk * np.sin(psik - th)

        inter_term = np.zeros_like(th)
        for m in range(L):
            if m == k:
                continue
            Rm, psik_m = layer_means[m]
            inter_term += cfg.inter_K[k, m] * np.sin(psik_m - th)

        ext_term = 0.0
        if external_phase is not None and cfg.gamma_ext != 0.0:
            ext_term = cfg.gamma_ext * np.sin(external_phase - th)

        dth = om + coupling + inter_term + ext_term
        th_next = (th + cfg.dt * dth) % (2 * np.pi)
        out.append(th_next)

    return out


__all__ = [
    "order_parameter", "graph_laplacian",
    "KuramotoConfig", "kuramoto_step",
    "LCGridConfig", "lc_grid_step",
    "MultiScaleConfig", "multi_scale_kuramoto_step",
]
