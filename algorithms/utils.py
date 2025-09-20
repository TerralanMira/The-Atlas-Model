"""
algorithms/utils.py

Small field-law helpers used by sims:
  - mirror_nudge: Mirror law (residual attraction to mean phase)
  - collapse_signal: readiness for choice-collapse (coherence + alignment - drift)
"""
from __future__ import annotations
import numpy as np


def mirror_nudge(theta: np.ndarray, psi: float, gain: float) -> np.ndarray:
    """
    Mirror law: nudge phases toward mean phase psi proportional to deviation.
    Returns delta_theta to be added; wrap outside if needed.
    """
    if gain == 0.0:
        return np.zeros_like(theta)
    d = np.angle(np.exp(1j * (psi - theta)))  # wrapped deviation
    return gain * d


def collapse_signal(R: float, cross_sync: float, drift: float) -> float:
    """
    Choice-collapse readiness: high coherence + alignment, low drift.
    Scaled to ~[0,1] using an exponential for drift.
    """
    drift_term = np.exp(-3.0 * drift)
    return float(0.5 * R + 0.4 * cross_sync + 0.1 * drift_term)
