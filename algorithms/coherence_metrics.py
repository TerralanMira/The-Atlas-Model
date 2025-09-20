"""
algorithms/coherence_metrics.py

Coherence & resonance metrics for The Atlas Model.

Provides:
  - order parameter wrapper (R, psi)
  - phase dispersion and drift
  - cross-layer synchrony
  - energy variance (generic helper)
  - choice-preservation score (instrumentation hook)

Depends on algorithms.field_equations.order_parameter
"""

from __future__ import annotations
from typing import List, Tuple
import numpy as np

from .field_equations import order_parameter


def phase_coherence(theta: np.ndarray) -> Tuple[float, float]:
    """
    Returns Kuramoto order parameter (R, psi).
    R ∈ [0,1], psi in radians.
    """
    return order_parameter(theta)


def phase_dispersion(theta: np.ndarray) -> float:
    """
    Circular variance (1 - R). Lower is tighter phase locking.
    """
    R, _ = order_parameter(theta)
    return 1.0 - R


def phase_drift(theta_prev: np.ndarray, theta_curr: np.ndarray) -> float:
    """
    Mean absolute phase change (wrapped) between two time steps.
    """
    d = np.angle(np.exp(1j * (theta_curr - theta_prev)))
    return float(np.mean(np.abs(d)))


def cross_layer_sync(thetas: List[np.ndarray]) -> float:
    """
    Average pairwise mean-phase alignment across layers.
    Returns mean cos(Δψ) where Δψ are pairwise mean-phase differences.
    1.0 = fully aligned means; 0 ≈ orthogonal; -1 = anti-phase.
    """
    means = []
    for th in thetas:
        _, psi = order_parameter(th)
        means.append(psi)
    means = np.array(means)
    L = len(means)
    if L <= 1:
        return 1.0
    vals = []
    for i in range(L):
        for j in range(i + 1, L):
            vals.append(np.cos(means[i] - means[j]))
    return float(np.mean(vals)) if vals else 1.0


def energy_variance(signal: np.ndarray) -> float:
    """
    Variance of an arbitrary scalar signal (helper for LC grids etc.).
    """
    return float(np.var(signal))


def choice_preservation_score(
    offered_paths_count: int,
    irreversible_actions_count: int,
    consent_to_log: bool,
) -> float:
    """
    Lightweight metric for "choice before options":
      - rewards multiple reversible paths
      - penalizes irreversible actions
      - zeroes out if consent_to_log is False

    Score ∈ [0, 1].
    """
    if not consent_to_log:
        return 0.0
    path_term = min(max(offered_paths_count - 1, 0), 4) / 4.0  # 0..1
    penalty = min(irreversible_actions_count, 5) / 5.0         # 0..1
    score = max(path_term - 0.5 * penalty, 0.0)
    return float(min(score, 1.0))
