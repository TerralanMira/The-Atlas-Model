#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dual-Phase Field dynamics + Soul-in-Field signature.

Implements two families referenced across the Field Applications docs:

1) Dual-Phase Field (inner/outer Kuramoto with optional outer driver)
   - Inner (Φ_I): within (e.g., a group of humans)
   - Outer (Φ_O): without (e.g., place/planetary/civic anchor)
   - Coherence emerges when inner alignment and tuned outer coupling interact.

2) Soul-in-Field signature
   - Person-level resonance from origin magnitude (MΩ), memory echo (β),
     permeability (π), wonder (W), and awareness signals:
     Integrity (I), Stamina/Presence (Ψ), Humility (H), Surrender (S).

Exports (used by tests):
- DualPhaseConfig
- simulate_dual_phase(cfg)
- SoulSignature
- soul_resonance(sig, R_between=0.0)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Tuple, Optional
import math
import numpy as np

TAU = 2.0 * math.pi


# ──────────────────────────────────────────────────────────────────────────────
# Utilities
# ──────────────────────────────────────────────────────────────────────────────

def wrap_phase(theta: np.ndarray) -> np.ndarray:
    """Map angles to (-pi, pi]."""
    return (theta + math.pi) % (2.0 * math.pi) - math.pi

def kuramoto_order_parameter(theta: np.ndarray) -> Tuple[float, float]:
    """
    Return (R, psi): R ∈ [0,1], psi mean phase angle.
    """
    z = np.exp(1j * theta).mean()
    return float(np.abs(z)), float(np.angle(z))


# ──────────────────────────────────────────────────────────────────────────────
# Dual-Phase Field
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class DualPhaseConfig:
    # sizes
    N_inner: int = 64
    N_outer: int = 32
    # timing
    steps: int = 1000
    dt: float = 0.05
    seed: Optional[int] = 0
    # couplings
    K_inner: float = 0.4
    K_outer: float = 0.25
    K_cross: float = 0.15  # inner↔outer coupling
    # natural frequencies
    omega_inner_std: float = 0.10
    omega_outer_std: float = 0.05
    # optional Schumann-like outer driver: dΦ_O/dt += A * sin(Ω t + φ)
    driver_amp: float = 0.0
    driver_omega: float = 7.83  # Hz metaphorically; unitless here
    driver_phase: float = 0.0
    # noise
    noise_std: float = 0.0


def _ring_adjacency(n: int) -> np.ndarray:
    A = np.zeros((n, n), dtype=float)
    for i in range(n):
        A[i, (i - 1) % n] = 1.0
        A[i, (i + 1) % n] = 1.0
    return A


def simulate_dual_phase(cfg: DualPhaseConfig) -> Dict[str, np.ndarray]:
    """
    Minimal two-layer Kuramoto integrator with inner/outer rings and cross-coupling.
    Returns time series arrays keyed by: R_total, R_inner, R_outer, C_cross (proxy).
    """
    rng = np.random.default_rng(cfg.seed)

    # states
    theta_I = rng.uniform(-math.pi, math.pi, size=cfg.N_inner)
    theta_O = rng.uniform(-math.pi, math.pi, size=cfg.N_outer)

    # natural frequencies
    omega_I = rng.normal(0.0, cfg.omega_inner_std, size=cfg.N_inner)
    omega_O = rng.normal(0.0, cfg.omega_outer_std, size=cfg.N_outer)

    # adjacency (simple rings)
    A_I = _ring_adjacency(cfg.N_inner)
    A_O = _ring_adjacency(cfg.N_outer)

    out = {
        "R_total": np.zeros(cfg.steps),
        "R_inner": np.zeros(cfg.steps),
        "R_outer": np.zeros(cfg.steps),
        "C_cross": np.zeros(cfg.steps),  # crude inner↔outer sync proxy
    }

    # helper for cross term: use mean phases
    def cross_term(inner: np.ndarray, outer: np.ndarray, K: float) -> Tuple[np.ndarray, np.ndarray]:
        _, psi_I = kuramoto_order_parameter(inner)
        _, psi_O = kuramoto_order_parameter(outer)
        # pull each layer slightly toward the other's mean
        return K * np.sin(psi_O - inner), K * np.sin(psi_I - outer)

    for k in range(cfg.steps):
        t = (k + 1) * cfg.dt

        # coupling on rings
        dI = omega_I.copy()
        for i in range(cfg.N_inner):
            dI[i] += cfg.K_inner * np.sum(A_I[i] * np.sin(theta_I - theta_I[i]))

        dO = omega_O.copy()
        for j in range(cfg.N_outer):
            dO[j] += cfg.K_outer * np.sum(A_O[j] * np.sin(theta_O - theta_O[j]))

        # cross-coupling (mean-angle attraction)
        cI, cO = cross_term(theta_I, theta_O, cfg.K_cross)
        dI += cI
        dO += cO

        # optional outer driver
        if cfg.driver_amp != 0.0:
            dO += cfg.driver_amp * np.sin(cfg.driver_omega * t + cfg.driver_phase)

        # noise
        if cfg.noise_std > 0.0:
            dI += rng.normal(0.0, cfg.noise_std, size=cfg.N_inner)
            dO += rng.normal(0.0, cfg.noise_std, size=cfg.N_outer)

        # integrate
        theta_I = wrap_phase(theta_I + cfg.dt * dI)
        theta_O = wrap_phase(theta_O + cfg.dt * dO)

        # metrics
        R_i, _ = kuramoto_order_parameter(theta_I)
        R_o, _ = kuramoto_order_parameter(theta_O)
        R_t, _ = kuramoto_order_parameter(np.concatenate([theta_I, theta_O]))
        # cross proxy: alignment of layer means
        cross = math.cos(_angle_diff_of_means(theta_I, theta_O))
        out["R_inner"][k] = R_i
        out["R_outer"][k] = R_o
        out["R_total"][k] = R_t
        out["C_cross"][k] = (cross + 1.0) * 0.5  # map to [0,1]

    return out


def _angle_diff_of_means(inner: np.ndarray, outer: np.ndarray) -> float:
    _, psi_I = kuramoto_order_parameter(inner)
    _, psi_O = kuramoto_order_parameter(outer)
    return float(np.angle(np.exp(1j * (psi_I - psi_O))))


# ──────────────────────────────────────────────────────────────────────────────
# Soul-in-Field
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class SoulSignature:
    MOmega: float = 1.0  # origin magnitude
    beta_echo: float = 0.7  # memory echo
    pi: float = 0.7      # permeability
    W: float = 0.7       # wonder
    I: float = 0.7       # integrity
    Psi: float = 0.7     # stamina / presence
    H: float = 0.7       # humility
    S: float = 0.7       # surrender


def soul_resonance(sig: SoulSignature, R_between: float = 0.0) -> float:
    """
    Simple positive-valued resonance score ∈ (0, +∞), typically ~[0,1.5].
    In practice we interpret a soft-normalized version in [0,1].
    """
    # core product of awareness terms
    core = (sig.I * sig.Psi * sig.H * sig.S)
    # permeability + memory echo amplify but penalize extremes
    perm = sig.pi * (1.0 - 0.3 * abs(sig.pi - 0.7))
    echo = sig.beta_echo * (1.0 - 0.2 * abs(sig.beta_echo - 0.7))
    # wonder as curvature opener
    curv = 0.7 + 0.6 * (sig.W - 0.5)
    # origin magnitude and between-group coherence as gates
    gate = 0.5 + 0.5 * (math.tanh(sig.MOmega - 0.6))
    between = 0.7 + 0.3 * R_between
    raw = gate * between * core * perm * echo * curv
    # soft clip into [0,1]
    return float(1.0 - math.exp(-raw))
