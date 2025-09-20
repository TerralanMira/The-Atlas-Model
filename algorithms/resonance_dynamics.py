"""
algorithms/resonance_dynamics.py

The Atlas Model — Resonance Dynamics (core laws as callable utilities)

This module turns field laws into small, testable functions that other parts
(algorithms, sims, LLM conductor) can compose. It is NumPy-only.

Implements:
  • Mirror Law: residual attraction to mean phase
  • Choice Collapse Readiness: collapse signal & decision
  • Harmonic Infinity Gate: ethics/ignition/destabilizer/time gating for K and π
  • Resonance vs Entropy: windowed metrics for coherence vs disorder
  • Return Spiral: gentle nudge back toward prior coherent attractor
  • Geometry Helpers: circle-6-center and grid adjacencies (for graph sims)

Intended use:
  - Sims call these to *shape* dynamics (not replace physics).
  - Conductor can reference collapse readiness for decision timing.
  - Learning scripts can compute R↔E and spiral back toward better presets.

License: MIT
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, Optional
import numpy as np


# ──────────────────────────────────────────────────────────────────────────────
# Basics (shared helpers)
# ──────────────────────────────────────────────────────────────────────────────

def wrap_phase(x: np.ndarray) -> np.ndarray:
    """Wrap real values to [0, 2π)."""
    return np.mod(x, 2.0 * np.pi)


def mean_phase(theta: np.ndarray) -> float:
    """Mean phase angle ψ (radians)."""
    z = np.exp(1j * theta)
    return float(np.angle(np.mean(z)))


def order_parameter(theta: np.ndarray) -> Tuple[float, float]:
    """Kuramoto order parameter (R, ψ)."""
    z = np.exp(1j * theta)
    mean = np.mean(z)
    return float(np.abs(mean)), float(np.angle(mean))


# ──────────────────────────────────────────────────────────────────────────────
# Mirror Law
# ──────────────────────────────────────────────────────────────────────────────

def mirror_delta(theta: np.ndarray, psi: float, gain: float = 0.02) -> np.ndarray:
    """
    Residual attraction to mean phase ψ.
    Returns Δθ to add to theta (wrap outside if needed).

    - gain is small (e.g., 0.01–0.05) so this remains a nudge, not a clamp.
    """
    if gain == 0.0:
        return np.zeros_like(theta)
    dev = np.angle(np.exp(1j * (psi - theta)))  # wrapped deviation
    return gain * dev


# ──────────────────────────────────────────────────────────────────────────────
# Choice Collapse (readiness + decision)
# ──────────────────────────────────────────────────────────────────────────────

def collapse_signal(R: float, cross_sync: float, drift: float) -> float:
    """
    Readiness for choice-collapse: high coherence + cross-layer alignment, low drift.

    Returns a score ~[0,1]: larger means more ready to collapse a superposition.
    """
    drift_term = np.exp(-3.0 * drift)         # low drift → large term
    score = 0.5 * R + 0.4 * cross_sync + 0.1 * drift_term
    return float(np.clip(score, 0.0, 1.0))


def collapse_decision(score: float, threshold: float = 0.72) -> bool:
    """
    Decide whether to collapse. Keep a slight hysteresis margin by choosing a
    threshold >= 0.7 in practice.
    """
    return bool(score >= threshold)


# ──────────────────────────────────────────────────────────────────────────────
# Harmonic Infinity Gate (ethics × ignition × destabilizer ÷ time kernel)
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class HarmonicGate:
    """
    Parameters for gating coupling (K) and permeability (π).

    integrity, stamina, humility ∈ [0,1]      → ethical/energetic scalars
    destabilizer ∈ [0,1]                      → chaos pressure (0 calm … 1 high)
    time_kernel > 0                           → longer horizon = smoother gating
    """
    integrity: float = 1.0
    stamina: float = 1.0
    humility: float = 1.0
    destabilizer: float = 0.0
    time_kernel: float = 1.0  # >0

    def gate(self, K: float, pi: float) -> Tuple[float, float]:
        """
        Gate K (coupling) and π (inter-layer permeability).
        - Ethics/ignition raise the ceiling.
        - Destabilizer reduces them.
        - Time kernel smooths the effect (acts as denominator).
        """
        base = self.integrity * self.stamina * self.humility
        damp = (1.0 - 0.6 * self.destabilizer)  # retain some agency under stress
        denom = max(self.time_kernel, 1e-6)
        factor = np.clip((base * damp) / denom, 0.0, 1.5)  # allow mild >1 boost

        K_g = float(np.clip(K * factor, 0.0, 2.0))
        pi_g = float(np.clip(pi * factor, 0.0, 1.5))
        return K_g, pi_g


# ──────────────────────────────────────────────────────────────────────────────
# Resonance vs Entropy (windowed metrics)
# ──────────────────────────────────────────────────────────────────────────────

def resonance_entropy_window(
    R_series: np.ndarray,
    drift_series: np.ndarray,
    window: int = 100,
) -> Tuple[float, float, float]:
    """
    Compute windowed resonance/entropy metrics.

    Inputs:
      R_series      : coherence per step (0..1)
      drift_series  : mean absolute wrapped phase change per step
      window        : tail length to compute statistics

    Returns:
      (R_mean, E_mean, balance) where
        R_mean = mean(R) over window
        E_mean = normalized entropy proxy = mean(sigmoid(drift))
        balance = R_mean - E_mean  (positive → resonance leading)
    """
    w = max(1, int(window))
    Rw = R_series[-w:]
    Dw = drift_series[-w:]

    R_mean = float(np.mean(Rw)) if Rw.size else 0.0
    # map drift to [0,1] via logistic to get an "entropy-ish" proxy
    E_mean = float(np.mean(1.0 / (1.0 + np.exp(-6.0 * (Dw - 0.2))))) if Dw.size else 0.0
    balance = R_mean - E_mean
    return R_mean, E_mean, float(balance)


# ──────────────────────────────────────────────────────────────────────────────
# Return Spiral (nudge toward known coherent attractor)
# ──────────────────────────────────────────────────────────────────────────────

def spiral_nudge(
    current: float,
    target: float,
    rate: float = 0.02,
    band: Tuple[float, float] = (0.0, 1.5),
) -> float:
    """
    Gentle exponential nudge of a scalar parameter (e.g., π or K) toward a
    prior known coherent target. Returns the updated value, clamped to band.
    """
    new = current + rate * (target - current)
    return float(np.clip(new, band[0], band[1]))


# ──────────────────────────────────────────────────────────────────────────────
# Geometry helpers (adjacency builders)
# ──────────────────────────────────────────────────────────────────────────────

def adjacency_circle6_center() -> np.ndarray:
    """
    Build adjacency for 7-node flower: 6 around 1 center (index 0 = center).
    Connect center to all petals; ring neighbors to each other (hexagon).
    """
    n = 7
    A = np.zeros((n, n), dtype=float)
    # center connections
    for i in range(1, n):
        A[0, i] = A[i, 0] = 1.0
    # ring connections (1..6 in a loop)
    for i in range(1, n):
        j = 1 + (i % 6)
        A[i, j] = A[j, i] = 1.0
    return A


def adjacency_grid(rows: int, cols: int, diagonal: bool = False) -> np.ndarray:
    """
    2D rectangular grid adjacency (rows×cols). 4-neighbor by default; set
    diagonal=True for 8-neighbor.
    """
    N = rows * cols
    A = np.zeros((N, N), dtype=float)

    def idx(r, c): return r * cols + c

    for r in range(rows):
        for c in range(cols):
            i = idx(r, c)
            # 4-neighbors
            for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                rr, cc = r + dr, c + dc
                if 0 <= rr < rows and 0 <= cc < cols:
                    j = idx(rr, cc)
                    A[i, j] = A[j, i] = 1.0
            if diagonal:
                for dr, dc in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
                    rr, cc = r + dr, c + dc
                    if 0 <= rr < rows and 0 <= cc < cols:
                        j = idx(rr, cc)
                        A[i, j] = A[j, i] = 1.0
    return A


# ──────────────────────────────────────────────────────────────────────────────
# Example “apply-gates” helper (optional convenience for sims)
# ──────────────────────────────────────────────────────────────────────────────

def gated_params(
    K: float,
    pi: float,
    integrity: float = 1.0,
    stamina: float = 1.0,
    humility: float = 1.0,
    destabilizer: float = 0.0,
    time_kernel: float = 1.0,
) -> Tuple[float, float]:
    """
    Convenience wrapper around HarmonicGate().gate for one-off calls.
    """
    return HarmonicGate(
        integrity=integrity,
        stamina=stamina,
        humility=humility,
        destabilizer=destabilizer,
        time_kernel=time_kernel,
    ).gate(K, pi)


# ──────────────────────────────────────────────────────────────────────────────
# __all__
# ──────────────────────────────────────────────────────────────────────────────

__all__ = [
    # basics
    "wrap_phase", "mean_phase", "order_parameter",
    # mirror
    "mirror_delta",
    # choice collapse
    "collapse_signal", "collapse_decision",
    # harmonic gate
    "HarmonicGate", "gated_params",
    # resonance vs entropy
    "resonance_entropy_window",
    # return spiral
    "spiral_nudge",
    # geometry
    "adjacency_circle6_center", "adjacency_grid",
]
