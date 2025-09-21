#!/usr/bin/env python3
"""
sims/breath_cycle.py

The Breath of Atlas — a cyclic expansion/contraction driver that modulates
coupling (K) and permeability (pi) over an inhale/exhale and logs the field's
response. Designed to complement multi_scale_kuramoto.py and the dashboard
overlays (Individual/Relational/Collective/Planetary/Cosmic).

If core helpers (algorithms.field_equations / algorithms.resonance_dynamics)
aren't present, we fall back to local implementations so this file remains
drop-in.

Outputs: CSV with columns aligned to the dashboard + ingest scripts:
  step,t,R_total,cross_sync,drift,C,Delta,Phi,ready,choice_score,
  phase,phase_pos,K_eff,pi_eff

Usage (example):
  python sims/breath_cycle.py --geometry circle6_center --period 20.0 --steps 4000 \
      --csv logs/breath_circle.csv
"""

from __future__ import annotations
import argparse, csv, math, os
from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np

# ──────────────────────────────────────────────────────────────────────────────
# Optional imports from the broader repo; fall back to local definitions
# ──────────────────────────────────────────────────────────────────────────────

try:
    from algorithms.coherence_metrics import phase_coherence, local_coherence
except Exception:
    def phase_coherence(phases: np.ndarray) -> float:
        return float(np.abs(np.exp(1j * phases).mean()))

    def local_coherence(phases: np.ndarray, adjacency: np.ndarray) -> float:
        A = np.maximum(adjacency, adjacency.T)
        I, J = np.where(A > 0)
        if I.size == 0:
            return 0.0
        return float(np.cos(phases[J] - phases[I]).mean())

try:
    from algorithms.field_equations import (
        adjacency_circle6_center, adjacency_grid, wrap_phase
    )
except Exception:
    def adjacency_circle6_center() -> np.ndarray:
        # 7 nodes: one center (0), six around it (1..6), ring & spokes
        N = 7
        A = np.zeros((N, N), float)
        # spokes
        for j in range(1, 7):
            A[0, j] = A[j, 0] = 1.0
        # ring
        for j in range(1, 7):
            A[j, 1 + (j - 2) % 6] = 1.0
            A[j, 1 + (j % 6)] = 1.0
        return A

    def adjacency_grid(rows: int, cols: int, diagonal: bool = False) -> np.ndarray:
        N = rows * cols
        A = np.zeros((N, N), float)
        def idx(r, c): return r * cols + c
        for r in range(rows):
            for c in range(cols):
                i = idx(r, c)
                for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
                    rr, cc = r + dr, c + dc
                    if 0 <= rr < rows and 0 <= cc < cols:
                        j = idx(rr, cc)
                        A[i, j] = A[j, i] = 1.0
                if diagonal:
                    for dr, dc in [(1,1), (1,-1), (-1,1), (-1,-1)]:
                        rr, cc = r + dr, c + dc
                        if 0 <= rr < rows and 0 <= cc < cols:
                            j = idx(rr, cc)
                            A[i, j] = A[j, i] = 1.0
        return A

    def wrap_phase(theta: np.ndarray) -> np.ndarray:
        return np.mod(theta + np.pi, 2.0 * np.pi) - np.pi

try:
    from algorithms.resonance_dynamics import (
        collapse_signal, collapse_decision, HarmonicGate, gated_params
    )
except Exception:
    def collapse_signal(R_total: float, cross_sync: float, drift: float) -> float:
        # Heuristic readiness: coherence high, drift not clamped, bridges decent
        r = 0.5 * R_total + 0.3 * cross_sync + 0.2 * max(0.0, 1.0 - min(1.0, drift * 10.0))
        return float(max(0.0, min(1.0, r)))

    def collapse_decision(ready: float, consent: bool, offer_two_paths: bool, thresh: float = 0.7) -> bool:
        if not consent or not offer_two_paths:
            return False
        return ready >= thresh

    class HarmonicGate:
        def __init__(self, ethics: float = 1.0, ignition: float = 1.0, destabilizer: float = 0.0, time_gate: float = 1.0):
            self.ethics = float(ethics)
            self.ignition = float(ignition)
            self.destabilizer = float(destabilizer)
            self.time_gate = float(time_gate)

    def gated_params(K: float, pi: float, gate: HarmonicGate, t_step: int) -> Tuple[float, float]:
        # Simple passthrough; real implementation may adapt over time
        return float(K), float(pi)

TAU = 2.0 * math.pi


# ──────────────────────────────────────────────────────────────────────────────
# Geometry / Omega
# ──────────────────────────────────────────────────────────────────────────────

def make_adjacency(geometry: str, rows: int, cols: int) -> np.ndarray:
    if geometry == "circle6_center":
        return adjacency_circle6_center()
    if geometry == "grid":
        if rows <= 0 or cols <= 0:
            raise ValueError("grid geometry requires positive --rows and --cols")
        return adjacency_grid(rows, cols, diagonal=False)
    raise ValueError(f"unknown geometry: {geometry}")

def make_omega(N: int, mean: float = 0.0, std: float = 0.1, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.normal(mean, std, size=N).astype(float)

def cross_edge_sync(A: np.ndarray, theta: np.ndarray) -> float:
    A = np.maximum(A, A.T)
    I, J = np.where(A > 0)
    if I.size == 0:
        return 0.0
    d = theta[J] - theta[I]
    return float((np.cos(d).mean() + 1.0) * 0.5)

def phase_entropy_norm(theta: np.ndarray, bins: int = 36) -> float:
    h, _ = np.histogram(np.mod(theta, TAU), bins=bins, range=(0.0, TAU))
    p = h.astype(float)
    if p.sum() == 0:
        return 0.0
    p /= p.sum()
    with np.errstate(divide="ignore", invalid="ignore"):
        ent = -(p * np.log(p + 1e-12)).sum()
    return float(ent / math.log(bins))

def lag1_smoothness(theta_now: np.ndarray, theta_prev: np.ndarray) -> float:
    dphi = np.angle(np.exp(1j * (theta_now - theta_prev)))
    return float((np.cos(dphi).mean() + 1.0) * 0.5)


# ──────────────────────────────────────────────────────────────────────────────
# Kuramoto integrator (local, simple)
# dθ_i = ω_i + K_eff * Σ_j A_ij * sin(θ_j - θ_i) + noise
# ──────────────────────────────────────────────────────────────────────────────

def step_kuramoto(theta: np.ndarray, omega: np.ndarray, K_eff: float, A: np.ndarray,
                  dt: float, noise_std: float = 0.0, rng: Optional[np.random.Generator] = None) -> np.ndarray:
    if rng is None:
        rng = np.random.default_rng()
    dtheta = omega.copy()
    # coupling
    A_sym = np.maximum(A, A.T)
    for i in range(len(theta)):
        dtheta[i] += K_eff * np.sum(A_sym[i] * np.sin(theta - theta[i]))
    # noise
    if noise_std > 0.0:
        dtheta += rng.normal(0.0, noise_std, size=len(theta))
    theta_next = wrap_phase(theta + dt * dtheta)
    return theta_next


# ──────────────────────────────────────────────────────────────────────────────
# Breath cycle driver
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class BreathConfig:
    period: float = 20.0          # seconds per full breath (inhale+exhale)
    inhale_ratio: float = 0.5     # fraction of period spent inhaling
    K_min: float = 0.4
    K_max: float = 1.0
    pi_min: float = 0.4
    pi_max: float = 1.0
    phase_offset: float = 0.0     # radians in [0, 2π)

def breath_phase(t: float, cfg: BreathConfig) -> Tuple[str, float]:
    """
    Returns ('inhale'|'exhale', phase_pos in [0,1]) for time t given period & ratio.
    phase_pos counts 0→1 within the current half-cycle.
    """
    T = max(1e-6, cfg.period)
    pos = (t % T) / T
    cut = cfg.inhale_ratio
    if pos < cut:
        # inhale half
        seg = pos / cut
        return "inhale", float(seg)
    else:
        # exhale half
        seg = (pos - cut) / max(1e-6, (1.0 - cut))
        return "exhale", float(seg)

def modulate_params(phase_name: str, phase_pos: float, cfg: BreathConfig) -> Tuple[float, float]:
    """
    Smoothly modulate K, pi across inhale/exhale with a cosine easing.
    Inhale: ramp from min → max; Exhale: ramp max → min.
    """
    def ease(x):  # cosine ease (0..1)
        return 0.5 * (1.0 - math.cos(math.pi * max(0.0, min(1.0, x))))
    w = ease(phase_pos)
    if phase_name == "inhale":
        K = cfg.K_min + (cfg.K_max - cfg.K_min) * w
        pi = cfg.pi_min + (cfg.pi_max - cfg.pi_min) * w
    else:
        K = cfg.K_max - (cfg.K_max - cfg.K_min) * w
        pi = cfg.pi_max - (cfg.pi_max - cfg.pi_min) * w
    return float(K), float(pi)


# ──────────────────────────────────────────────────────────────────────────────
# Runner
# ──────────────────────────────────────────────────────────────────────────────

def run_breath(geometry: str = "circle6_center",
               rows: int = 8, cols: int = 8,
               steps: int = 4000, dt: float = 0.01,
               period: float = 20.0, inhale_ratio: float = 0.5,
               noise_std: float = 0.0,
               csv_path: Optional[str] = "logs/breath.csv",
               seed: int = 0,
               offer_two_paths: bool = True,
               consent_to_log: bool = True) -> None:

    A = make_adjacency(geometry, rows, cols)
    N = A.shape[0]
    rng = np.random.default_rng(seed)
    theta = wrap_phase(rng.uniform(-math.pi, math.pi, size=N))
    theta_prev = theta.copy()
    omega = make_omega(N, std=0.1, seed=seed)

    cfg = BreathConfig(period=float(period), inhale_ratio=float(inhale_ratio),
                       K_min=0.4, K_max=1.0, pi_min=0.4, pi_max=1.0)

    header = [
        "step","t",
        "R_total","cross_sync","drift","C","Delta","Phi",
        "ready","choice_score",
        "phase","phase_pos","K_eff","pi_eff",
        "offer_two_paths","consent_to_log"
    ]
    writer = None
    f = None
    if csv_path:
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        f = open(csv_path, "w", newline="")
        writer = csv.writer(f)
        writer.writerow(header)

    gate = HarmonicGate(ethics=1.0, ignition=1.0, destabilizer=noise_std, time_gate=1.0)

    for k in range(steps):
        t = (k + 1) * dt
        phase_name, phase_pos = breath_phase(t, cfg)
        K_target, pi_target = modulate_params(phase_name, phase_pos, cfg)
        K_eff, pi_eff = gated_params(K_target, pi_target, gate=gate, t_step=k)

        theta_next = step_kuramoto(theta, omega, K_eff, A, dt=dt, noise_std=noise_std, rng=rng)

        # Metrics
        R_total = phase_coherence(theta_next)
        cross   = cross_edge_sync(A, theta_next)
        drift   = float(np.mean(np.abs(np.angle(np.exp(1j * (theta_next - theta))))))
        C_raw   = local_coherence(theta_next, np.maximum(A, A.T))
        C_m01   = float((C_raw + 1.0) * 0.5)  # map [-1,1] → [0,1]
        Delta   = phase_entropy_norm(theta_next)
        Phi     = lag1_smoothness(theta_next, theta)

        ready = collapse_signal(R_total, cross, drift)
        choice_ok = collapse_decision(
            ready=ready,
            consent=bool(consent_to_log),
            offer_two_paths=bool(offer_two_paths),
            thresh=0.70
        )
        choice_score = 1.0 if choice_ok else 0.0

        if writer:
            writer.writerow([
                k + 1, t,
                R_total, cross, drift, C_m01, Delta, Phi,
                ready, choice_score,
                phase_name, phase_pos, K_eff, pi_eff,
                int(offer_two_paths), int(consent_to_log)
            ])

        theta_prev = theta
        theta = theta_next

    if f:
        f.close()


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Atlas Breath Cycle — cyclic K,π modulation with resonance logging")
    ap.add_argument("--geometry", type=str, default="circle6_center", choices=["circle6_center","grid"],
                    help="Topology of adjacency")
    ap.add_argument("--rows", type=int, default=8, help="Grid rows (if geometry=grid)")
    ap.add_argument("--cols", type=int, default=8, help="Grid cols (if geometry=grid)")
    ap.add_argument("--steps", type=int, default=4000, help="Number of integration steps")
    ap.add_argument("--dt", type=float, default=0.01, help="Time step")
    ap.add_argument("--period", type=float, default=20.0, help="Breath period (seconds)")
    ap.add_argument("--inhale_ratio", type=float, default=0.5, help="Fraction of period spent inhaling (0..1)")
    ap.add_argument("--noise_std", type=float, default=0.0, help="Additive noise std to dynamics")
    ap.add_argument("--csv", type=str, default="logs/breath.csv", help="Output CSV path")
    ap.add_argument("--seed", type=int, default=0, help="Random seed")
    ap.add_argument("--no-two-paths", action="store_true", help="Disable reversible options")
    ap.add_argument("--no-consent", action="store_true", help="Disable consent flag")
    return ap.parse_args()

def main():
    args = parse_args()
    run_breath(
        geometry=args.geometry,
        rows=int(args.rows), cols=int(args.cols),
        steps=int(args.steps), dt=float(args.dt),
        period=float(args.period), inhale_ratio=float(args.inhale_ratio),
        noise_std=float(args.noise_std),
        csv_path=args.csv,
        seed=int(args.seed),
        offer_two_paths=(not args.no_two_paths),
        consent_to_log=(not args.no_consent)
    )

if __name__ == "__main__":
    main()
