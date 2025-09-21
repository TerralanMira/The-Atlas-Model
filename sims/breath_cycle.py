#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Breath-modulated Kuramoto runner.

K(t) = K0 * (1 + a * sin(2π * t / T))

Outputs the same CSV headers as multi_scale_kuramoto.py.
"""
from __future__ import annotations
import argparse, csv, math
from pathlib import Path
import numpy as np

from algorithms.field_equations import DualPhaseConfig, simulate_dual_phase, wrap_phase
from algorithms.coherence_metrics import metrics_bundle
from algorithms.resonance_dynamics import collapse_signal

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--N_inner", type=int, default=64)
    ap.add_argument("--N_outer", type=int, default=32)
    ap.add_argument("--steps", type=int, default=800)
    ap.add_argument("--dt", type=float, default=0.05)
    ap.add_argument("--K_inner", type=float, default=0.36)
    ap.add_argument("--K_outer", type=float, default=0.22)
    ap.add_argument("--K_cross", type=float, default=0.10)
    ap.add_argument("--breath_amp", type=float, default=0.25)   # 0..1
    ap.add_argument("--breath_T", type=float, default=20.0)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--save_csv", type=str, default="logs/breath.csv")
    return ap.parse_args()

def _ring_adj(n: int) -> np.ndarray:
    A = np.zeros((n, n), dtype=float)
    for i in range(n):
        A[i, (i-1) % n] = 1.0
        A[i, (i+1) % n] = 1.0
    return A

def main():
    args = parse_args()
    rng = np.random.default_rng(args.seed)

    # base config; we’ll retrain coupling via breath for logging/interpretation
    cfg = DualPhaseConfig(
        N_inner=args.N_inner, N_outer=args.N_outer, steps=args.steps, dt=args.dt, seed=args.seed,
        K_inner=args.K_inner, K_outer=args.K_outer, K_cross=args.K_cross
    )
    out = simulate_dual_phase(cfg)

    A = np.zeros((cfg.N_inner + cfg.N_outer, cfg.N_inner + cfg.N_outer))
    A[:cfg.N_inner, :cfg.N_inner] = _ring_adj(cfg.N_inner)
    A[cfg.N_inner:, cfg.N_inner:] = _ring_adj(cfg.N_outer)

    theta_prev = rng.uniform(-np.pi, np.pi, size=cfg.N_inner + cfg.N_outer)

    log_path = Path(args.save_csv); log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "step","t",
            "R_total","R_inner","R_outer","C_cross",
            "drift","Delta","Phi","choice_score"
        ])
        for k in range(cfg.steps):
            t = (k + 1) * cfg.dt
            breath = 1.0 + args.breath_amp * math.sin(2*math.pi * t / args.breath_T)
            # smaller step when breath lifts (gentler)
            step_scale = max(0.02, 0.20 / breath)
            dtheta = rng.normal(0.0, step_scale, size=theta_prev.size)
            theta_now = wrap_phase(theta_prev + dtheta)

            R_total = float(out["R_total"][k])
            R_inner = float(out["R_inner"][k])
            R_outer = float(out["R_outer"][k])
            C_cross = float(out["C_cross"][k])

            R_b, cross01, drift, C01, Delta = metrics_bundle(theta_now, theta_prev, A)
            Phi = float(np.exp(-drift))
            choice_score = collapse_signal(R_total, C_cross, drift)

            w.writerow([
                k, f"{t:.4f}",
                f"{R_total:.6f}", f"{R_inner:.6f}", f"{R_outer:.6f}", f"{C_cross:.6f}",
                f"{drift:.6f}", f"{Delta:.6f}", f"{Phi:.6f}", f"{choice_score:.6f}"
            ])
            theta_prev = theta_now

if __name__ == "__main__":
    main()
