"""The Atlas Model — Resonance Dynamics
NumPy utilities that encode small, testable field laws.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Optional
import numpy as np

TAU = 2.0 * np.pi

# ── Basics ─────────────────────────────────────────────────────────────────────

def wrap_phase(x: np.ndarray) -> np.ndarray:
    """Wrap angles to [0, 2π)."""
    return np.mod(x, TAU)

def mean_phase(theta: np.ndarray) -> float:
    """Circular mean angle of a 1D array of phases."""
    z = np.exp(1j * theta)
    mean = np.mean(z)
    return float(np.angle(mean))

def order_parameter(theta: np.ndarray) -> Tuple[float, float]:
    """Return Kuramoto order parameter magnitude R and mean phase ψ."""
    z = np.exp(1j * theta)
    mean = np.mean(z)
    R = np.abs(mean)
    psi = float(np.angle(mean))
    return float(R), psi

# ── Mirror law ─────────────────────────────────────────────────────────────────

def mirror_delta(theta: np.ndarray, gain: float = 0.05) -> np.ndarray:
    """Delta to nudge each phase toward the circular mean."""
    if gain == 0.0:
        return np.zeros_like(theta)
    _, psi = order_parameter(theta)
    d = np.angle(np.exp(1j * (psi - theta)))
    return gain * d

# ── Choice collapse ────────────────────────────────────────────────────────────

def collapse_signal(R: float, cross_sync: float, drift: float) -> float:
    drift_term = np.exp(-3.0 * float(drift))
    val = 0.5 * float(R) + 0.4 * float(cross_sync) + 0.1 * drift_term
    return float(np.clip(val, 0.0, 1.0))

def collapse_decision(ready: float, consent: bool = True, offer_two_paths: bool = True, thresh: float = 0.7) -> bool:
    """True only when readiness exceeds threshold AND consent AND reversible options exist."""
    return bool((ready >= thresh) and consent and offer_two_paths)

# ── Harmonic Infinity Gate ─────────────────────────────────────────────────────

@dataclass
class HarmonicGate:
    ethics: float = 1.0        # [0..1] diminish params if below 1
    ignition: float = 1.0      # multiplier for activation
    destabilizer: float = 0.0  # small noise proportion
    time_gate: float = 1.0     # optional time scaling

def gated_params(K: float, pi: float, gate: Optional[HarmonicGate] = None, t_step: Optional[int] = None) -> Tuple[float, float]:
    """Apply simple gating to K and π (permissive, bounded)."""
    if gate is None:
        return float(np.clip(K, 0.0, 1.0)), float(np.clip(pi, 0.0, 1.0))
    K2 = K * gate.ignition * gate.ethics
    pi2 = pi * gate.ignition * gate.ethics
    if gate.destabilizer > 0.0:
        rng = np.random.default_rng(t_step or 0)
        K2 += gate.destabilizer * rng.normal(0.0, 0.01)
        pi2 += gate.destabilizer * rng.normal(0.0, 0.01)
    K2 = float(np.clip(K2, 0.0, 1.0))
    pi2 = float(np.clip(pi2, 0.0, 1.0))
    return K2, pi2

# ── Resonance vs Entropy window ────────────────────────────────────────────────

def _hist_entropy(ph: np.ndarray, bins: int = 36) -> float:
    h, _ = np.histogram(np.mod(ph, TAU), bins=bins, range=(0.0, TAU), density=False)
    p = h.astype(float)
    if p.sum() == 0:
        return 0.0
    p = p / p.sum()
    with np.errstate(divide='ignore', invalid='ignore'):
        ent = -(p * np.log(p + 1e-12)).sum()
    return float(ent / np.log(bins))  # normalized

def resonance_entropy_window(theta: np.ndarray, win: int = 128, bins: int = 36) -> np.ndarray:
    """Return 1 - normalized entropy over a sliding window (higher = more resonant)."""
    T = theta.shape[0]
    out = np.full(T, np.nan, dtype=float)
    if win <= 1 or T < win:
        return out
    for t in range(win - 1, T):
        ent = _hist_entropy(theta[t - win + 1 : t + 1], bins=bins)
        out[t] = 1.0 - ent  # coherence proxy
    return out

# ── Return Spiral ──────────────────────────────────────────────────────────────

def spiral_nudge(x: float, target: float, rate: float = 0.05) -> float:
    """Gentle exponential approach to target without overshoot."""
    x = float(x); target = float(target)
    dx = (target - x) * rate
    return float(x + dx)

# ── Geometry helpers ──────────────────────────────────────────────────────────

def adjacency_circle6_center() -> np.ndarray:
    """Adjacency for 7 nodes: node 0 center connected to 1..6; symmetric, zero diag."""
    A = np.zeros((7,7), dtype=float)
    for i in range(1,7):
        A[0,i] = 1.0
        A[i,0] = 1.0
    return A

def adjacency_grid(rows: int, cols: int, diagonal: bool = False) -> np.ndarray:
    """Rect grid adjacency (4-neigh if diagonal=False, else 8-neigh)."""
    N = rows * cols
    A = np.zeros((N,N), dtype=float)
    def idx(r,c): return r*cols + c
    for r in range(rows):
        for c in range(cols):
            i = idx(r,c)
            for dr in (-1,0,1):
                for dc in (-1,0,1):
                    if dr == 0 and dc == 0:
                        continue
                    if not diagonal and abs(dr)+abs(dc) != 1:
                        continue
                    rr, cc = r+dr, c+dc
                    if 0 <= rr < rows and 0 <= cc < cols:
                        j = idx(rr,cc)
                        A[i,j] = 1.0
    A = np.maximum(A, A.T)
    np.fill_diagonal(A, 0.0)
    return A
