"""
algorithms/field_equations.py

Core field equations for The Atlas Model.

Implements two minimal, robust engines that other layers can compose:

1) Kuramoto oscillator field (phase-only)
   - dθ_i/dt = ω_i + (K/deg_i) * Σ_j A_ij * sin(θ_j - θ_i)
   - step function returns next phases plus basic resonance metrics

2) LC grid (position/velocity on a lattice; simple mass-spring analog)
   - x''_i + γ x'_i + ω0^2 x_i = c * Σ_j A_ij * (x_j - x_i)
   - step function integrates with semi-implicit (symplectic) Euler

Also includes:
- order parameter (R, ψ)
- cross_sync over edges
- drift estimate (avg |Δθ|/dt)
- small utilities to normalize adjacency and ensure numerical stability

NumPy-only. MIT License.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Optional
import numpy as np

TAU = 2.0 * np.pi


# ──────────────────────────────────────────────────────────────────────────────
# Utilities
# ──────────────────────────────────────────────────────────────────────────────

def wrap_phase(theta: np.ndarray) -> np.ndarray:
    """Wrap angles to [0, 2π)."""
    return np.mod(theta, TAU)

def order_parameter(theta: np.ndarray) -> Tuple[float, float]:
    """
    Kuramoto order parameter.
    Returns:
      R ∈ [0,1], psi ∈ (-π, π]
    """
    z = np.exp(1j * theta)
    mean = np.mean(z)
    R = float(np.abs(mean))
    psi = float(np.angle(mean))
    return R, psi

def normalize_adjacency(A: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    """
    Row-normalize adjacency so each node's incoming weight sums to 1 (where degree>0).
    Keeps zeros where degree==0.
    """
    A = np.asarray(A, dtype=float)
    deg = A.sum(axis=1, keepdims=True)
    out = np.zeros_like(A)
    mask = deg > eps
    out[mask[:, 0]] = A[mask[:, 0]] / deg[mask]
    return out

def mean_edge_cos(A: np.ndarray, theta: np.ndarray) -> float:
    """
    Cross-edge synchrony: average cos(θ_j - θ_i) over edges (i,j) with A_ij > 0.
    Returns ∈ [-1, 1]. Uses symmetric edges (max(A, A^T)).
    """
    A = np.maximum(A, A.T)
    idx = np.where(A > 0)
    if idx[0].size == 0:
        return 0.0
    dphi = theta[idx[1]] - theta[idx[0]]
    val = float(np.mean(np.cos(dphi)))
    # map from [-1,1] to [0,1] because we treat "alignment" as non-negative
    return (val + 1.0) * 0.5

def drift_rate(theta_next: np.ndarray, theta_now: np.ndarray, dt: float, eps: float = 1e-12) -> float:
    """
    Mean wrapped angular speed per node: E[ |wrap(Δθ)| ] / dt.
    """
    dphi = np.angle(np.exp(1j * (theta_next - theta_now)))
    return float(np.mean(np.abs(dphi)) / max(dt, eps))


# ──────────────────────────────────────────────────────────────────────────────
# Kuramoto field
# ──────────────────────────────────────────────────────────────────────────────

def kuramoto_dtheta(theta: np.ndarray,
                    omega: np.ndarray,
                    K: float,
                    A: np.ndarray) -> np.ndarray:
    """
    Compute dθ/dt for Kuramoto with adjacency A (not necessarily normalized).
    We normalize by degree to keep K interpretable across topologies.
    """
    theta = np.asarray(theta, dtype=float).ravel()
    omega = np.asarray(omega, dtype=float).ravel()
    A = np.asarray(A, dtype=float)
    if theta.size != omega.size:
        raise ValueError("theta and omega must have same length")
    if A.shape != (theta.size, theta.size):
        raise ValueError("A must be square with size matching len(theta)")

    # coupling term
    diff = theta[None, :] - theta[:, None]             # (N,N) θ_i - θ_j
    S = np.sin(-diff)                                  # sin(θ_j - θ_i)
    deg = np.sum(A, axis=1, keepdims=True)            # degree
    deg_safe = np.where(deg > 0, deg, 1.0)
    coupling = (K / deg_safe) * np.sum(A * S, axis=1, keepdims=True)  # (N,1)
    dtheta = omega[:, None] + coupling
    return dtheta.ravel()

def kuramoto_step(theta: np.ndarray,
                  omega: np.ndarray,
                  K: float,
                  A: np.ndarray,
                  dt: float = 0.01) -> Tuple[np.ndarray, dict]:
    """
    One explicit Euler step for Kuramoto; returns (theta_next, metrics).
    Metrics keys: R_total, R_mean(=R_total), cross_sync, drift
    """
    theta = np.asarray(theta, dtype=float).ravel()
    dtheta = kuramoto_dtheta(theta, omega, K, A)
    theta_next = wrap_phase(theta + dt * dtheta)

    R_total, _psi = order_parameter(theta_next)
    cross = mean_edge_cos(A, theta_next)
    drift = drift_rate(theta_next, theta, dt)

    metrics = {
        "R_total": float(R_total),
        "R_mean": float(R_total),
        "cross_sync": float(cross),
        "drift": float(drift),
    }
    return theta_next, metrics


# ──────────────────────────────────────────────────────────────────────────────
# LC grid (mass–spring analog on adjacency A)
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class LCParams:
    omega0: float = 1.0   # natural frequency
    gamma: float = 0.05   # damping
    coupling: float = 0.2 # neighbor coupling strength
    dt: float = 0.01

@dataclass
class LCState:
    x: np.ndarray   # positions (N,)
    v: np.ndarray   # velocities (N,)

def lc_grid_accel(state: LCState, A: np.ndarray, p: LCParams) -> np.ndarray:
    """
    Acceleration: a = -ω0^2 x - γ v + c * Σ_j A_ij (x_j - x_i)
    """
    x = state.x
    v = state.v
    # Laplacian-like term: Σ A_ij (x_j - x_i) = (A x) - (deg * x)
    Ax = A @ x
    deg = A.sum(axis=1)
    lap = Ax - deg * x
    a = - (p.omega0 ** 2) * x - p.gamma * v + p.coupling * lap
    return a

def lc_grid_step(state: LCState, A: np.ndarray, p: LCParams) -> LCState:
    """
    Semi-implicit (symplectic) Euler:
      v_{t+Δ} = v_t + Δ a(x_t, v_t)
      x_{t+Δ} = x_t + Δ v_{t+Δ}
    """
    a = lc_grid_accel(state, A, p)
    v_next = state.v + p.dt * a
    x_next = state.x + p.dt * v_next
    return LCState(x=x_next, v=v_next)


# ──────────────────────────────────────────────────────────────────────────────
# Convenience builders
# ──────────────────────────────────────────────────────────────────────────────

def adjacency_circle6_center() -> np.ndarray:
    """
    7-node star: node 0 connected to nodes 1..6, symmetric.
    """
    A = np.zeros((7, 7), dtype=float)
    for i in range(1, 7):
        A[0, i] = 1.0
        A[i, 0] = 1.0
    return A

def adjacency_grid(rows: int, cols: int, diagonal: bool = False) -> np.ndarray:
    """
    Rectangular grid adjacency; 4-neighbor or 8-neighbor if diagonal=True.
    """
    N = rows * cols
    A = np.zeros((N, N), dtype=float)

    def idx(r, c): return r * cols + c
    for r in range(rows):
        for c in range(cols):
            i = idx(r, c)
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    if not diagonal and abs(dr) + abs(dc) != 1:
                        continue
                    rr, cc = r + dr, c + dc
                    if 0 <= rr < rows and 0 <= cc < cols:
                        j = idx(rr, cc)
                        A[i, j] = 1.0
    A = np.maximum(A, A.T)
    np.fill_diagonal(A, 0.0)
    return A


# ──────────────────────────────────────────────────────────────────────────────
# Batch helpers (useful for sims/tests)
# ──────────────────────────────────────────────────────────────────────────────

def kuramoto_run(theta0: np.ndarray,
                 omega: np.ndarray,
                 K: float,
                 A: np.ndarray,
                 steps: int,
                 dt: float = 0.01) -> Tuple[np.ndarray, np.ndarray]:
    """
    Run multiple Kuramoto steps.
    Returns:
      Theta: (T, N) phases over time
      Metrics: (T,) array of R_total
    """
    theta = np.asarray(theta0, dtype=float).ravel()
    N = theta.size
    T = int(max(1, steps))
    out = np.zeros((T, N), dtype=float)
    Rs = np.zeros(T, dtype=float)
    for t in range(T):
        theta, m = kuramoto_step(theta, omega, K, A, dt=dt)
        out[t] = theta
        Rs[t] = m["R_total"]
    return out, Rs


# ──────────────────────────────────────────────────────────────────────────────
# __all__
# ──────────────────────────────────────────────────────────────────────────────

__all__ = [
    # utils
    "wrap_phase", "order_parameter", "normalize_adjacency",
    "mean_edge_cos", "drift_rate",
    # kuramoto
    "kuramoto_dtheta", "kuramoto_step", "kuramoto_run",
    # lc grid
    "LCParams", "LCState", "lc_grid_accel", "lc_grid_step",
    # adjacencies
    "adjacency_circle6_center", "adjacency_grid",
]
