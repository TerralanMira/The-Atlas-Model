# -*- coding: utf-8 -*-
"""
Field dynamics & utilities used by sims and tests.

Exports (simple Kuramoto + multi-scale + dual-phase):
- order_parameter(theta) -> (R, psi)
- kuramoto_step(theta, omega, K=0.0, dt=0.01, A=None) -> next_theta
- class MultiScaleConfig(intra_K, inter_K, dt=0.01, gamma_ext=0.0)
- multi_scale_kuramoto_step(thetas, omegas, cfg, external_phase=0.0) -> list[theta_next]
- class DualPhaseConfig(...)
- simulate_dual_phase(cfg) -> dict[str, np.ndarray]
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List
import numpy as np
import math

TAU = 2*np.pi

# ---------- basics ----------
def wrap_phase(theta: np.ndarray) -> np.ndarray:
    return (theta + np.pi) % TAU - np.pi

def order_parameter(theta: np.ndarray) -> tuple[float, float]:
    z = np.exp(1j*theta).mean()
    return float(np.abs(z)), float(np.angle(z))

# ---------- single-layer Kuramoto ----------
def kuramoto_step(theta: np.ndarray, omega: np.ndarray, K: float = 0.0, dt: float = 0.01, A: np.ndarray | None = None) -> np.ndarray:
    """
    theta, omega ∈ R^N, optional adjacency A (0/1) uses sin coupling along edges; if None, use mean-field.
    """
    N = theta.shape[0]
    if A is None:
        R, psi = order_parameter(theta)
        dtheta = omega + K*R*np.sin(psi - theta)
    else:
        dtheta = omega.copy()
        for i in range(N):
            nbrs = np.where(A[i] > 0)[0]
            if nbrs.size:
                dtheta[i] += (K / max(1, nbrs.size)) * np.sum(np.sin(theta[nbrs] - theta[i]))
    return wrap_phase(theta + dt*dtheta)

# ---------- multi-scale (L coupled layers) ----------
@dataclass
class MultiScaleConfig:
    intra_K: List[float]
    inter_K: np.ndarray  # LxL gains (diagonal ignored)
    dt: float = 0.01
    gamma_ext: float = 0.0  # global external pull (to external_phase)

def _mean_phase(theta: np.ndarray) -> float:
    return float(np.angle(np.exp(1j*theta).mean()))

def multi_scale_kuramoto_step(thetas: List[np.ndarray], omegas: List[np.ndarray], cfg: MultiScaleConfig, external_phase: float = 0.0) -> List[np.ndarray]:
    L = len(thetas)
    next_thetas = []
    means = [ _mean_phase(th) for th in thetas ]
    for ℓ in range(L):
        th = thetas[ℓ]; om = omegas[ℓ]
        # intra-layer mean-field
        R, psi = order_parameter(th)
        d = om + cfg.intra_K[ℓ]*R*np.sin(psi - th)
        # inter-layer gentle mean-phase attraction
        for m in range(L):
            if m == ℓ: 
                continue
            Kxm = cfg.inter_K[ℓ, m]
            if Kxm != 0.0:
                d += Kxm * np.sin(means[m] - th)
        # optional external driver
        if cfg.gamma_ext != 0.0:
            d += cfg.gamma_ext * np.sin(external_phase - th)
        next_thetas.append(wrap_phase(th + cfg.dt*d))
    return next_thetas

# ---------- dual-phase convenience (for tests & examples) ----------
@dataclass
class DualPhaseConfig:
    N_inner: int = 32
    N_outer: int = 16
    steps: int = 200
    dt: float = 0.02
    K_inner: float = 0.4
    K_outer: float = 0.25
    K_cross: float = 0.12
    omega_inner_std: float = 0.1
    omega_outer_std: float = 0.05
    seed: int = 0

def simulate_dual_phase(cfg: DualPhaseConfig) -> dict[str, np.ndarray]:
    rng = np.random.default_rng(cfg.seed)
    thI = rng.uniform(-np.pi, np.pi, size=cfg.N_inner)
    thO = rng.uniform(-np.pi, np.pi, size=cfg.N_outer)
    omI = rng.normal(0.0, cfg.omega_inner_std, size=cfg.N_inner)
    omO = rng.normal(0.0, cfg.omega_outer_std, size=cfg.N_outer)

    R_total = np.zeros(cfg.steps)
    R_inner = np.zeros(cfg.steps)
    R_outer = np.zeros(cfg.steps)
    C_cross = np.zeros(cfg.steps)

    def mean_phase(x): return float(np.angle(np.exp(1j*x).mean()))
    for k in range(cfg.steps):
        # intra mean-field
        RI, psiI = order_parameter(thI)
        RO, psiO = order_parameter(thO)
        dI = omI + cfg.K_inner*RI*np.sin(psiI - thI)
        dO = omO + cfg.K_outer*RO*np.sin(psiO - thO)
        # cross via mean phases
        dI += cfg.K_cross*np.sin(psiO - thI)
        dO += cfg.K_cross*np.sin(psiI - thO)
        # integrate
        thI = wrap_phase(thI + cfg.dt*dI)
        thO = wrap_phase(thO + cfg.dt*dO)
        # metrics
        RT, _ = order_parameter(np.concatenate([thI, thO]))
        R_total[k], R_inner[k], R_outer[k] = RT, RI, RO
        C_cross[k] = (math.cos(mean_phase(thI) - mean_phase(thO)) + 1.0)*0.5

    return {"R_total": R_total, "R_inner": R_inner, "R_outer": R_outer, "C_cross": C_cross}
