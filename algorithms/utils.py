"""
algorithms/utils.py

Small field-law helpers used by sims:
  - mirror_nudge: Mirror law (residual attraction to mean phase)
  - collapse_signal: readiness for choice-collapse (coherence + alignment - drift)
  - signals_product: bounded product of normalized signals
  - recommend_K_range: monotone K range suggestion from resonance level
"""
from __future__ import annotations
import numpy as np
from typing import Dict, Tuple


def wrap_phase(x: np.ndarray) -> np.ndarray:
    """Wrap angles to [0, 2π)."""
    return np.mod(x, 2.0 * np.pi)


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
    drift_term = np.exp(-3.0 * float(drift))
    val = 0.5 * float(R) + 0.4 * float(cross_sync) + 0.1 * drift_term
    return float(np.clip(val, 0.0, 1.0))


def _norm01(v: float) -> float:
    try:
        v = float(v)
    except Exception:
        v = 0.0
    return float(np.clip(v, 0.0, 1.0))


def signals_product(signals: Dict[str, float]) -> float:
    """
    Bounded product of normalized signals in [0,1].
    Missing keys are treated as 1.0 so they don't penalize the product.
    """
    keys = ["I", "Ψ", "H", "S", "β", "π", "W"]
    prod = 1.0
    for k in keys:
        prod *= _norm01(signals.get(k, 1.0))
    return float(np.clip(prod, 0.0, 1.0))


def recommend_K_range(R: float) -> Tuple[float, float]:
    """
    Recommend a coupling K range [lo, hi] based on resonance level R∈[0,1].
    Monotone increasing with R and always within 0<lo<hi<=1.
    """
    R = _norm01(R)
    lo = 0.2 + 0.5 * R - 0.1          # 0.1 .. 0.6 as R increases
    hi = lo + 0.3 + 0.2 * R           # slightly wider as R rises
    lo = float(np.clip(lo, 0.0, 0.95))
    hi = float(np.clip(hi, lo + 1e-6, 1.0))
    return lo, hi
