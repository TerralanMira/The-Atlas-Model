# sims/creation.py
"""
Synchronization-Led Emergence (Toy Kuramoto Model)
==================================================

This module simulates a *phase-coupled oscillator system* in which
collective synchronization can trigger an abrupt, stable structure we
label a “creation event” (emergence). It is a **toy** computational model,
not a cosmological or biological claim.

Governing equations
-------------------
Oscillator phases (i = 1..N), Kuramoto-like dynamics:

    dθ_i/dt = ω_i
              + (K(t)/N) * Σ_j sin(θ_j − θ_i)
              + A_drive * sin(2π f_drive t + φ)

Order parameter:

    R(t) e^{iψ(t)} = (1/N) * Σ_j e^{i θ_j(t)}
    with R ∈ [0,1], ψ ∈ [−π, π].

Coupling growth (bounded logistic-like with relaxation):

    dK/dt = α * max(0, R(t) − R_thresh) * (K_max − K)
            − β * (K − K_min)

Event logic (delegated to algorithms/creation_protocols.py):
- Detects upward crossings of R(t) beyond R_event, with minimal hold time T_hold.
- Additional guardrails can include minimum K and minimum anchors (locally phase-locked nodes).

**Claims & Limits**
- Scope: toy Kuramoto system (dimensionless or arbitrary units).
- Demonstrates: how coherence + growth rules can yield abrupt structure (an “event”).
- NOT claiming: cosmological creation or biological genesis.

Outputs
-------
The simulate() function returns arrays for R(t), K(t), gap_to_env(t), and an
array of creation events. Companion demo saves CSV + PNG.

"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Tuple
import numpy as np

# ----------------- utilities ----------------- #

def wrap_angle(x: np.ndarray) -> np.ndarray:
    """Wrap angles to [-pi, pi] elementwise."""
    return (x + np.pi) % (2 * np.pi) - np.pi

def order_parameter(phases: np.ndarray) -> Tuple[float, float]:
    """
    Kuramoto order parameter for a 1D phase vector.
    Returns (R, psi) where R ∈ [0,1], psi ∈ [-pi, pi].
    """
    z = np.exp(1j * phases)
    z_mean = np.mean(z)
    R = np.abs(z_mean)
    psi = np.angle(z_mean)
    return float(R), float(psi)

# ----------------- config ----------------- #

@dataclass(frozen=True)
class CreationConfig:
    N: int = 120                 # number of oscillators
    steps: int = 6000            # time steps
    dt: float = 0.002            # time step (s or a.u.)
    seed: int = 7

    # intrinsic
    omega_mean: float = 2.0 * np.pi * 1.0   # mean natural freq (rad/s)
    omega_spread: float = 0.3               # gaussian std (rad/s)

    # coupling K(t)
    K_init: float = 0.1
    K_min: float = 0.0
    K_max: float = 4.0
    alpha: float = 1.2                       # growth rate when R>R_thresh
    beta: float = 0.3                        # relaxation toward K_min
    R_thresh: float = 0.55                   # coherence threshold for growth

    # external drive
    A_drive: float = 0.0                     # amplitude (rad/s)
    f_drive: float = 0.5                     # Hz
    phi_drive: float = 0.0                   # rad

    # event detection thresholds (delegated)
    R_event: float = 0.8
    T_hold: float = 0.5                      # seconds (steps*dt to cross)

    # misc
    record_every: int = 1                    # record at every step

# ----------------- simulation core ----------------- #

def simulate(cfg: CreationConfig) -> Dict[str, np.ndarray | Dict[str, float]]:
    """
    Run the toy Kuramoto system with bounded coupling growth.
    Returns arrays and a summary dict. Event detection is performed via
    algorithms.creation_protocols.detect_events.
    """
    rng = np.random.default_rng(cfg.seed)

    # natural frequencies ω_i
    omega = rng.normal(loc=cfg.omega_mean, scale=cfg.omega_spread, size=cfg.N)
    # phases θ_i
    theta = rng.uniform(low=-np.pi, high=np.pi, size=cfg.N)
    # coupling K
    K = cfg.K_init

    # outputs
    T = cfg.steps
    R_tr = np.zeros(T, dtype=float)
    psi_tr = np.zeros(T, dtype=float)
    K_tr = np.zeros(T, dtype=float)
    gap_env_tr = np.zeros(T, dtype=float)   # |ω_i − ω_mean| averaged (a proxy)
    anchors_tr = np.zeros(T, dtype=float)   # fraction locally phase-locked

    # drive angular frequency
    w_drive = 2.0 * np.pi * cfg.f_drive

    # helper: local anchor fraction (simple nearest-neighbor lock proxy)
    def local_anchor_fraction(phases: np.ndarray, tol: float = 0.25) -> float:
        # fraction of nodes whose nearest neighbor phase difference < tol
        phases_sorted = np.sort(wrap_angle(phases.copy()))
        diffs = np.abs(np.diff(np.concatenate([phases_sorted, phases_sorted[:1] + 2*np.pi])))
        return float(np.mean(diffs < tol))

    for t_idx in range(T):
        t = t_idx * cfg.dt

        # compute order parameter
        R, psi = order_parameter(theta)
        R_tr[t_idx] = R
        psi_tr[t_idx] = psi

        # proxy environment gap: mean absolute deviation from ω_mean
        gap_env_tr[t_idx] = float(np.mean(np.abs(omega - np.mean(omega))))
        anchors_tr[t_idx] = local_anchor_fraction(theta)

        K_tr[t_idx] = K

        # external drive term (same added to all oscillators)
        drive = cfg.A_drive * np.sin(w_drive * t + cfg.phi_drive)

        # Kuramoto update (Euler)
        # dθ_i = ω_i + (K/N)*Σ_j sin(θ_j − θ_i) + drive
        sines = np.sin(theta[None, :] - theta[:, None])  # NxN
        coupling_term = (K / cfg.N) * np.sum(sines, axis=1)
        dtheta = omega + coupling_term + drive
        theta = wrap_angle(theta + cfg.dt * dtheta)

        # K growth dynamics
        # dK/dt = α * max(0, R − R_thresh) * (K_max − K) − β*(K − K_min)
        grow = max(0.0, R - cfg.R_thresh)
        dK = cfg.alpha * grow * (cfg.K_max - K) - cfg.beta * (K - cfg.K_min)
        K = float(np.clip(K + cfg.dt * dK, cfg.K_min, cfg.K_max))

    # event detection (upward R crossing + hold)
    from algorithms.creation_protocols import detect_events
    events = detect_events(
        R_tr,
        K_tr,
        anchors_tr,
        dt=cfg.dt,
        R_event=cfg.R_event,
        T_hold=cfg.T_hold,
        K_min=cfg.K_min + 0.05  # small guard
    )

    # summary (tail averages)
    tail = slice(int(0.8 * T), T)
    summary = {
        "seed": cfg.seed,
        "R_mean_tail": float(np.mean(R_tr[tail])),
        "K_mean_tail": float(np.mean(K_tr[tail])),
        "anchors_mean_tail": float(np.mean(anchors_tr[tail])),
        "events_count": int(events.shape[0]),
    }

    return {
        "R": R_tr,
        "psi": psi_tr,
        "K": K_tr,
        "gap_to_env": gap_env_tr,
        "anchors_frac": anchors_tr,
        "creation_events": events,  # shape (E, 3): [t_sec, R_at, K_at]
        "summary": summary,
    }
