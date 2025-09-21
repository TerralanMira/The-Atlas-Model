#!/usr/bin/env python3
"""
algorithms/flow_dynamics.py

Flow dynamics for Atlas:
- Encodes the Awareness→Coherence→Field→Apply→Ground→Return (A-C-F-A-G-R) cycle
  as a time-varying modulation of coupling and permeability (the "hum").
- Bundles composite flow indicators that combine coherence (C), diversity (Δ),
  gentleness (Φ), and drift to suggest safe, reversible moves.

Use cases
---------
1) As a light "conductor" above Kuramoto updates in sims/*.
2) To score runs post-hoc (reading CSVs) and compute hum indices.
3) To prototype higher-level controllers (e.g., adaptive K schedules).

Design notes
------------
- Minimal dependencies (NumPy only). Optional imports from:
    algorithms.coherence_metrics
    algorithms.field_equations
  have clean fallbacks so the file is self-contained.
- All angles are in radians; phases mapped to (-π, π].

Author: Atlas
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Tuple, Optional
import math
import numpy as np

# ── Optional imports with fallbacks ───────────────────────────────────────────
try:
    from algorithms.coherence_metrics import (
        wrap_phase as _wrap_phase,        # may not exist there; we fall back
        phase_coherence,
        local_coherence,
        cross_edge_sync,
        phase_entropy_norm,
        lag1_smoothness,
        mean_drift,
        metrics_bundle,
    )
except Exception:
    def _wrap_phase(theta: np.ndarray) -> np.ndarray:
        return np.mod(theta + np.pi, 2.0 * np.pi) - np.pi

    def phase_coherence(theta: np.ndarray) -> float:
        return float(np.abs(np.exp(1j * theta).mean()))

    def local_coherence(theta: np.ndarray, A: np.ndarray) -> float:
        A = np.maximum(A, A.T)
        I, J = np.where(A > 0)
        if I.size == 0:
            return 0.0
        return float(np.cos(theta[J] - theta[I]).mean())

    def cross_edge_sync(A: np.ndarray, theta: np.ndarray) -> float:
        A = np.maximum(A, A.T)
        I, J = np.where(A > 0)
        if I.size == 0:
            return 0.0
        return float((np.cos(theta[J] - theta[I]).mean() + 1.0) * 0.5)

    def phase_entropy_norm(theta: np.ndarray, bins: int = 36) -> float:
        h, _ = np.histogram(np.mod(theta, 2.0 * np.pi), bins=bins, range=(0.0, 2.0 * np.pi))
        p = h.astype(float); s = p.sum()
        if s <= 0: return 0.0
        p /= s
        with np.errstate(divide="ignore", invalid="ignore"):
            ent = -(p * np.log(p + 1e-12)).sum()
        return float(ent / math.log(bins))

    def lag1_smoothness(theta_now: np.ndarray, theta_prev: np.ndarray) -> float:
        dphi = np.angle(np.exp(1j * (theta_now - theta_prev)))
        return float((np.cos(dphi).mean() + 1.0) * 0.5)

    def mean_drift(theta_now: np.ndarray, theta_prev: np.ndarray) -> float:
        return float(np.mean(np.abs(np.angle(np.exp(1j * (theta_now - theta_prev))))))

    def metrics_bundle(theta_now: np.ndarray,
                       theta_prev: np.ndarray,
                       A: np.ndarray) -> Tuple[float, float, float, float, float]:
        R_total = phase_coherence(theta_now)
        cross01 = cross_edge_sync(A, theta_now)
        drift   = mean_drift(theta_now, theta_prev)
        C_raw   = local_coherence(theta_now, A)
        C01     = (C_raw + 1.0) * 0.5
        Delta   = phase_entropy_norm(theta_now)
        return float(R_total), float(cross01), float(drift), float(C01), float(Delta)

try:
    from algorithms.field_equations import (
        wrap_phase as wrap_phase,
        breath_envelope,
        K_over_time,
        ouroboros_feedback,
    )
except Exception:
    wrap_phase = _wrap_phase

    def _cosine_ease_01(x: float) -> float:
        x = max(0.0, min(1.0, x))
        return 0.5 - 0.5 * math.cos(math.pi * x)

    def breath_envelope(t: float, period: float, inhale_ratio: float) -> float:
        T = max(1e-9, period)
        Ti = max(1e-9, inhale_ratio) * T
        tm = t % T
        if tm <= Ti:
            return _cosine_ease_01(tm / Ti)      # inhale ramp
        return 1.0 - _cosine_ease_01((tm - Ti) / max(1e-9, T - Ti))  # exhale ramp

    def K_over_time(K_min: float, K_max: float, t: float, period: float, inhale_ratio: float) -> float:
        e = breath_envelope(t, period, inhale_ratio)
        return (1.0 - e) * K_min + e * K_max

    def ouroboros_feedback(theta: np.ndarray, gain: float) -> np.ndarray:
        z = np.exp(1j * theta).mean()
        mean_ang = float(np.angle(z))
        return gain * np.angle(np.exp(1j * (mean_ang - theta)))

# ── Data classes ──────────────────────────────────────────────────────────────

@dataclass
class HumSchedule:
    """
    Breath-like schedule that maps the A-C-F-A-G-R cycle over one 'period'.
    Each phase can modulate effective coupling (K), optional permeability π,
    or any scalar control you pass downstream.
    """
    period: float = 20.0          # seconds
    inhale_ratio: float = 0.5     # fraction of period spent "ascending"
    K_min: float = 0.4
    K_max: float = 0.8
    pi_min: float = 0.2           # optional permeability (0..1)
    pi_max: float = 0.9
    feedback_gain: float = 0.0    # optional ouroboros nudge

    def snapshot(self, t: float) -> Dict[str, float]:
        e = breath_envelope(t, self.period, self.inhale_ratio)   # 0..1
        K_eff = (1.0 - e) * self.K_min + e * self.K_max
        pi_eff = (1.0 - e) * self.pi_min + e * self.pi_max
        return {"e": e, "K": K_eff, "pi": pi_eff, "gain": self.feedback_gain}

# ── Flow indices (composite signals) ─────────────────────────────────────────

def hum_index(C01: float, Delta: float, Phi: float) -> float:
    """
    Core 'hum' score combining coherence (C01), diversity (Delta), and gentleness (Phi).
    Balanced, not maxed: penalize clamp (low Delta) and turbulence (low Phi).
    """
    # geometric-like blend with soft floors to avoid collapse
    eps = 1e-6
    return float(((C01 + eps) * (Delta + eps) * (Phi + eps)) ** (1.0 / 3.0))

def clamp_risk(R_total: float, Delta: float, drift: float) -> float:
    """
    High when global order is high AND diversity/drift are low.
    """
    R = max(0.0, min(1.0, R_total))
    D = max(0.0, min(1.0, Delta))
    d = max(0.0, min(math.pi, drift)) / math.pi  # normalize 0..1
    return float(R * (1.0 - D) * (1.0 - d))

def turbulence(r: float, phi: float) -> float:
    """
    Simple turbulence proxy: low smoothness with mid/high drift or low order.
    """
    r = max(0.0, min(1.0, r))
    phi = max(0.0, min(1.0, phi))
    return float((1.0 - phi) * (1.0 - r))

# ── Flow step helper (plug into sims) ────────────────────────────────────────

def flow_step(theta: np.ndarray,
              omega: np.ndarray,
              A: np.ndarray,
              t: float,
              dt: float,
              schedule: HumSchedule,
              noise_std: float = 0.0,
              rng: Optional[np.random.Generator] = None) -> Tuple[np.ndarray, Dict[str, float]]:
    """
    One integration step that:
    - samples the current hum schedule (K, π, gain)
    - applies Kuramoto coupling with optional ouroboros feedback
    - returns next theta and an info dict of metrics + controls
    """
    if rng is None:
        rng = np.random.default_rng()

    snap = schedule.snapshot(t)
    K = float(snap["K"])
    gain = float(snap["gain"])

    # Kuramoto update with optional feedback
    A_sym = np.maximum(A, A.T)
    dtheta = omega.copy()
    # coupling
    for i in range(len(theta)):
        dtheta[i] += K * np.sum(A_sym[i] * np.sin(theta - theta[i]))
    # gentle self-reference (ouroboros)
    if gain > 0.0:
        dtheta += ouroboros_feedback(theta, gain)
    # stochasticity
    if noise_std > 0.0:
        dtheta += rng.normal(0.0, noise_std, size=len(theta))

    theta_next = wrap_phase(theta + dt * dtheta)

    # Metrics (use previous theta for drift/Phi)
    R_total, cross01, drift, C01, Delta = metrics_bundle(theta_next, theta, A_sym)
    Phi = lag1_smoothness(theta_next, theta)
    H  = hum_index(C01, Delta, Phi)
    clamp = clamp_risk(R_total, Delta, drift)
    turb  = turbulence(R_total, Phi)

    info = {
        "K_eff": K,
        "pi_eff": float(snap["pi"]),
        "e": float(snap["e"]),
        "gain": gain,
        "R_total": R_total,
        "cross_sync": cross01,
        "drift": drift,
        "C": C01,
        "Delta": Delta,
        "Phi": Phi,
        "hum_index": H,
        "clamp_risk": clamp,
        "turbulence": turb,
    }
    return theta_next, info

# ── Controller suggestion (small, reversible moves) ──────────────────────────

def controller_suggestion(info: Dict[str, float]) -> Dict[str, Any]:
    """
    Given the latest flow metrics, suggest gentle parameter nudges.
    This is advisory (no side effects); sims can consume as they wish.
    """
    K = info.get("K_eff", 0.6)
    Phi = info.get("Phi", 0.5)
    Delta = info.get("Delta", 0.5)
    clamp = info.get("clamp_risk", 0.0)
    turb  = info.get("turbulence", 0.0)

    suggestions = []

    # If clamp risk high → back off K a little, or widen ω
    if clamp > 0.35:
        suggestions.append({"param": "K", "delta": -0.05, "why": "reduce over-lock; preserve Δ"})
        suggestions.append({"param": "omega_std", "delta": +0.01, "why": "reintroduce plurality"})

    # If turbulence high → keep K but raise smoothness (e.g., reduce dt or add breath)
    if turb > 0.35:
        suggestions.append({"param": "use_breath", "value": True, "why": "cosine easing to increase Φ"})
        suggestions.append({"param": "dt", "scale": 0.9, "why": "smaller steps to reduce jitter"})

    # If both Δ and Φ healthy but C stagnant → small K+ nudges
    if Delta > 0.4 and Phi > 0.6 and info.get("C", 0.0) < 0.55:
        suggestions.append({"param": "K", "delta": +0.03, "why": "lift local coherence without collapsing Δ"})

    return {
        "score": info.get("hum_index", 0.0),
        "clamp_risk": clamp,
        "turbulence": turb,
        "suggestions": suggestions
    }

# ── Convenience: run a tiny flow loop (engine-agnostic) ──────────────────────

def run_flow(theta0: np.ndarray,
             omega: np.ndarray,
             A: np.ndarray,
             steps: int,
             dt: float,
             schedule: HumSchedule,
             noise_std: float = 0.0,
             seed: Optional[int] = None) -> Dict[str, np.ndarray]:
    """
    Minimal integrator for quick tests (not a replacement for sims/* runners).
    Returns trajectories for inspection or unit tests.
    """
    rng = np.random.default_rng(seed)
    N = theta0.shape[0]
    theta = theta0.copy()
    out = {
        "K_eff": np.zeros(steps),
        "R_total": np.zeros(steps),
        "C": np.zeros(steps),
        "Delta": np.zeros(steps),
        "Phi": np.zeros(steps),
        "drift": np.zeros(steps),
        "hum_index": np.zeros(steps),
        "clamp_risk": np.zeros(steps),
        "turbulence": np.zeros(steps),
    }
    for k in range(steps):
        t = (k + 1) * dt
        theta_next, info = flow_step(theta, omega, A, t, dt, schedule, noise_std, rng)
        for key in out:
            out[key][k] = info[key]
        theta = theta_next
    return out
