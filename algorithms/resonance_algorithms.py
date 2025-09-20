"""
algorithms/resonance_algorithms.py

Resonance algorithms for The Atlas Model:
  • Phase locking (PLV) — time-averaged phase synchronization
  • Pairwise phase consistency (PPC) — unbiased consistency estimator
  • Phase diffusion — stochastic drift estimate from wrapped increments
  • Entropy-based coherence — Shannon entropy on phase histograms
  • Mutual information (MI) — dependency strength between signals
  • Sliding-window helpers — time-resolved versions of the above

All functions are NumPy-based (no external deps) and vectorized where feasible.
Inputs:
  • Phases are in radians.
  • Time-major convention where applicable: shape (T, N) for T steps, N nodes.

License: MIT
"""
from __future__ import annotations
from typing import Tuple, Optional
import numpy as np


# ──────────────────────────────────────────────────────────────────────────────
# Utilities
# ──────────────────────────────────────────────────────────────────────────────

def _wrap_phase(x: np.ndarray) -> np.ndarray:
    """Wrap to [0, 2π)."""
    return np.mod(x, 2.0 * np.pi)

def _angle_diff(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Wrapped difference a - b into (-π, π]."""
    return np.angle(np.exp(1j * (a - b)))

def _to_2d_time_major(x: np.ndarray) -> np.ndarray:
    """
    Ensure array is 2D time-major: (T, N).
    If 1D → (T, 1). If already (T, N) → unchanged.
    If (N,) but intended as nodes over time, caller should reshape.
    """
    x = np.asarray(x)
    if x.ndim == 1:
        return x[:, None]
    if x.ndim == 2:
        return x
    raise ValueError("Expected 1D or 2D array (T,) or (T,N).")


# ──────────────────────────────────────────────────────────────────────────────
# Phase Locking Value (PLV)
# ──────────────────────────────────────────────────────────────────────────────

def plv_pair(phi1: np.ndarray, phi2: np.ndarray) -> float:
    """
    Phase Locking Value between two phase time series (same length).
      PLV = | mean_t exp( i(φ1 - φ2) ) |
    Returns ∈ [0, 1].
    """
    phi1 = np.asarray(phi1).ravel()
    phi2 = np.asarray(phi2).ravel()
    z = np.exp(1j * _angle_diff(phi1, phi2))
    return float(np.abs(np.mean(z)))

def plv_matrix(Theta: np.ndarray) -> np.ndarray:
    """
    PLV for all pairs from time-major phase matrix Theta (T, N).
    Returns (N, N) symmetric matrix with ones on the diagonal.
    """
    Theta = _to_2d_time_major(Theta)
    T, N = Theta.shape
    Z = np.exp(1j * Theta)                           # (T, N)
    M = np.zeros((N, N), dtype=float)
    for i in range(N):
        for j in range(i, N):
            # PLV between i and j via phase difference
            z = np.exp(1j * (Theta[:, i] - Theta[:, j]))
            val = np.abs(np.mean(z))
            M[i, j] = M[j, i] = float(val)
    np.fill_diagonal(M, 1.0)
    return M


# ──────────────────────────────────────────────────────────────────────────────
# Pairwise Phase Consistency (PPC) — unbiased
#   Vinck et al. 2010: PPC = (|Σ z|^2 - N) / (N (N - 1)), with z = e^{iΔφ_t}
# ──────────────────────────────────────────────────────────────────────────────

def ppc_pair(phi1: np.ndarray, phi2: np.ndarray) -> float:
    """
    Unbiased pairwise phase consistency between two series.
    PPC ∈ [-1/(N-1), 1], typically ≥0 for consistent phases.
    """
    phi1 = np.asarray(phi1).ravel()
    phi2 = np.asarray(phi2).ravel()
    z = np.exp(1j * _angle_diff(phi1, phi2))
    N = z.size
    if N < 2:
        return 0.0
    num = np.abs(np.sum(z)) ** 2 - N
    den = N * (N - 1)
    return float(num / den)

def ppc_matrix(Theta: np.ndarray) -> np.ndarray:
    """
    PPC for all pairs from time-major phase matrix Theta (T, N).
    Returns (N, N) symmetric matrix with ones on the diagonal (by convention).
    """
    Theta = _to_2d_time_major(Theta)
    T, N = Theta.shape
    M = np.zeros((N, N), dtype=float)
    for i in range(N):
        for j in range(i, N):
            val = ppc_pair(Theta[:, i], Theta[:, j]) if i != j else 1.0
            M[i, j] = M[j, i] = float(val)
    return M


# ──────────────────────────────────────────────────────────────────────────────
# Phase Diffusion
#   Estimate diffusion coefficient D from wrapped increments:
#     D ≈ Var(Δφ) / (2 Δt), for small Δt (per node)
# ──────────────────────────────────────────────────────────────────────────────

def phase_diffusion(theta: np.ndarray, dt: float) -> np.ndarray:
    """
    Estimate diffusion coefficient per node from phase series.
    Input:
      theta: time-major phases (T, N) or (T,)
      dt   : timestep
    Returns:
      D: (N,) diffusion estimates
    """
    X = _to_2d_time_major(theta)  # (T, N)
    dphi = _angle_diff(X[1:], X[:-1])  # (T-1, N)
    var = np.var(dphi, axis=0)         # per node
    D = var / (2.0 * max(dt, 1e-12))
    return D.astype(float)

def phase_diffusion_windowed(theta: np.ndarray, dt: float, win: int) -> np.ndarray:
    """
    Windowed diffusion estimates over time.
    Returns array shape (T-1, N) filled with NaN except where window is valid.
    """
    X = _to_2d_time_major(theta)
    T, N = X.shape
    dphi = _angle_diff(X[1:], X[:-1])  # (T-1, N)
    out = np.full_like(dphi, np.nan, dtype=float)
    W = max(2, int(win))
    for t in range(W, T-1):
        var = np.var(dphi[t-W:t], axis=0)
        out[t] = var / (2.0 * max(dt, 1e-12))
    return out


# ──────────────────────────────────────────────────────────────────────────────
# Entropy-based Coherence (phase histogram entropy)
#   Normalize Shannon entropy by log(bins); coherence = 1 - H_norm
# ──────────────────────────────────────────────────────────────────────────────

def phase_entropy(phases: np.ndarray, bins: int = 36, eps: float = 1e-12) -> float:
    """
    Normalized Shannon entropy of phase distribution (0..1).
      0 → delta-like (highly peaked); 1 → uniform.
    """
    x = _wrap_phase(np.asarray(phases).ravel())
    hist, _ = np.histogram(x, bins=bins, range=(0.0, 2.0*np.pi), density=False)
    p = hist.astype(float) / max(np.sum(hist), 1.0)
    H = -np.sum(p * np.log(p + eps))
    Hmax = np.log(max(bins, 2))
    return float(H / Hmax)

def entropy_coherence(phases: np.ndarray, bins: int = 36, eps: float = 1e-12) -> float:
    """
    Coherence from entropy (1 - normalized entropy) ∈ [0,1].
    """
    return float(1.0 - phase_entropy(phases, bins=bins, eps=eps))

def phase_entropy_windowed(theta: np.ndarray, bins: int = 36, win: int = 200) -> np.ndarray:
    """
    Sliding-window normalized phase entropy over time for (T,N) series.
    Returns (T, N) with NaN before the first full window.
    """
    X = _to_2d_time_major(theta)
    T, N = X.shape
    W = max(4, int(win))
    out = np.full((T, N), np.nan, dtype=float)
    for t in range(W, T):
        seg = X[t-W:t]  # (W, N)
        for n in range(N):
            out[t, n] = phase_entropy(seg[:, n], bins=bins)
    return out


# ──────────────────────────────────────────────────────────────────────────────
# Mutual Information (histogram estimator)
#   MI(X;Y) = Σ p(x,y) log( p(x,y) / (p(x)p(y)) )
#   Works for real-valued arrays (e.g., phase, amplitude); phases are wrapped.
# ──────────────────────────────────────────────────────────────────────────────

def mutual_information(x: np.ndarray, y: np.ndarray, bins: int = 32, normalized: bool = False) -> float:
    """
    Histogram-based MI (nats). If normalized=True, returns NMI ∈ [0,1] ≈ MI / min(Hx, Hy).
    """
    x = np.asarray(x).ravel()
    y = np.asarray(y).ravel()
    if x.size != y.size:
        raise ValueError("x and y must have same length")

    # For phases, keep them within [0,2π). For general signals this is harmless.
    xr = _wrap_phase(x)
    yr = _wrap_phase(y)

    H, xedges, yedges = np.histogram2d(xr, yr, bins=bins, range=((0, 2*np.pi), (0, 2*np.pi)))
    Pxy = H / max(np.sum(H), 1.0)
    Px = np.sum(Pxy, axis=1, keepdims=True)
    Py = np.sum(Pxy, axis=0, keepdims=True)

    eps = 1e-12
    MI = np.sum(Pxy * (np.log(Pxy + eps) - np.log(Px + eps) - np.log(Py + eps)))

    if not normalized:
        return float(max(MI, 0.0))

    # Normalized by the smaller marginal entropy (bounded-ish in [0,1])
    Hx = -np.sum(Px * np.log(Px + eps))
    Hy = -np.sum(Py * np.log(Py + eps))
    denom = max(min(Hx, Hy), eps)
    NMI = MI / denom
    # clip to [0,1] softly (estimator noise might push slightly above 1)
    return float(np.clip(NMI, 0.0, 1.0))

def mi_matrix(X: np.ndarray, bins: int = 32, normalized: bool = False) -> np.ndarray:
    """
    Pairwise MI for columns of time-major array X (T, N). Returns (N, N) symmetric matrix.
    """
    X = _to_2d_time_major(X)
    T, N = X.shape
    M = np.zeros((N, N), dtype=float)
    for i in range(N):
        for j in range(i, N):
            val = mutual_information(X[:, i], X[:, j], bins=bins, normalized=normalized)
            M[i, j] = M[j, i] = float(val if i != j else (1.0 if normalized else 0.0))
    return M


# ──────────────────────────────────────────────────────────────────────────────
# Sliding-window helpers for time-resolved analysis
# ──────────────────────────────────────────────────────────────────────────────

def sliding_plv(phi1: np.ndarray, phi2: np.ndarray, win: int, step: int = 1) -> np.ndarray:
    """
    Time-resolved PLV over sliding windows.
    Returns array length ≈ floor((T - win)/step) + 1
    """
    a = np.asarray(phi1).ravel()
    b = np.asarray(phi2).ravel()
    T = min(a.size, b.size)
    W = max(2, int(win))
    S = max(1, int(step))
    out = []
    for t in range(0, T - W + 1, S):
        out.append(plv_pair(a[t:t+W], b[t:t+W]))
    return np.array(out, dtype=float)

def sliding_entropy_coherence(theta: np.ndarray, win: int = 200, bins: int = 36, step: int = 1) -> np.ndarray:
    """
    Time-resolved entropy-based coherence for (T,N). Returns (K, N) sliding series.
    """
    X = _to_2d_time_major(theta)
    T, N = X.shape
    W = max(4, int(win))
    S = max(1, int(step))
    out = []
    for t in range(0, T - W + 1, S):
        seg = X[t:t+W]
        vals = [entropy_coherence(seg[:, n], bins=bins) for n in range(N)]
        out.append(vals)
    return np.array(out, dtype=float)


# ──────────────────────────────────────────────────────────────────────────────
# __all__
# ──────────────────────────────────────────────────────────────────────────────

__all__ = [
    # PLV
    "plv_pair", "plv_matrix",
    # PPC
    "ppc_pair", "ppc_matrix",
    # Diffusion
    "phase_diffusion", "phase_diffusion_windowed",
    # Entropy coherence
    "phase_entropy", "entropy_coherence", "phase_entropy_windowed",
    # Mutual information
    "mutual_information", "mi_matrix",
    # Sliding windows
    "sliding_plv", "sliding_entropy_coherence",
]
