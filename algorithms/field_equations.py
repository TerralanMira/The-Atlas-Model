#!/usr/bin/env python3
"""
algorithms/field_equations.py

Shared math primitives for sims:
- phase wrapping
- breath envelope + K(t)
- gentle ouroboros feedback term
"""

from __future__ import annotations
import math
import numpy as np

TAU = 2.0 * math.pi

# ──────────────────────────────────────────────────────────────────────────────

def wrap_phase(theta: np.ndarray) -> np.ndarray:
    return np.mod(theta + np.pi, 2.0 * np.pi) - np.pi

# ──────────────────────────────────────────────────────────────────────────────
# Breath modulation
# ──────────────────────────────────────────────────────────────────────────────

def cosine_ease_01(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return 0.5 - 0.5 * math.cos(math.pi * x)

def breath_envelope(t: float, period: float, inhale_ratio: float) -> float:
    T = max(1e-9, period)
    Ti = max(1e-9, inhale_ratio) * T
    tm = t % T
    if tm <= Ti:
        return cosine_ease_01(tm / Ti)      # inhale ramp
    return 1.0 - cosine_ease_01((tm - Ti) / max(1e-9, T - Ti))  # exhale ramp

def K_over_time(K_min: float, K_max: float, t: float, period: float, inhale_ratio: float) -> float:
    e = breath_envelope(t, period, inhale_ratio)
    return (1.0 - e) * K_min + e * K_max

# ──────────────────────────────────────────────────────────────────────────────
# Ouroboros feedback
# ──────────────────────────────────────────────────────────────────────────────

def ouroboros_feedback(theta: np.ndarray, gain: float) -> np.ndarray:
    """
    Small nudge toward mean angle; keep gain modest (e.g., 0.05–0.2).
    Returns an additive term for dtheta.
    """
    z = np.exp(1j * theta).mean()
    mean_ang = float(np.angle(z))
    return gain * np.angle(np.exp(1j * (mean_ang - theta)))
