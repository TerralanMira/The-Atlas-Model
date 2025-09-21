#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-scale (inner↔outer) Kuramoto runner.

Outputs CSV with headers:
step, t, R_total, R_inner, R_outer, C_cross, drift, Delta, Phi, choice_score
"""
from __future__ import annotations
import argparse
import csv
from pathlib import Path
import numpy as np

from algorithms.field_equations import DualPhaseConfig, simulate_dual_phase, wrap_phase  # wrap_phase re-export ok
from algorithms.coherence_metrics import (
    metrics_bundle,  # -> (R, cross01, drift, C01, Delta)
)
from algorithms.resonance_dynamics import collapse_signal

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--N_inner", type=int, default=64)
    ap.add_argument("--N_outer", type=int, default=32)
    ap.add_argument("--steps", type=int, default=800)
    ap.add_argument("--dt", type=float, default=0.05)
    ap.add_argument("--K_inner", type=float, default=0.40)
    ap.add_argument("--K_outer", type=float, default=0.25)
    ap.add_argument("--K_cross", type=float, default=0.15)
    ap.add_argument("--omega_inner_std", type=float, default=0.10)
    ap.add_argument("--omega_outer_std", type=float, default=0.05)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--save_csv", type=str, default="logs/multi_scale.csv")
    ap.add_argument("--plot", action="store_true")
    return ap.parse_args()

def _ring_adj(n: int) -> np.ndarray:
    A = np.zeros((n, n), dtype=float)
    for i in range(n):
        A[i, (i-1) % n] = 1.0
        A[i, (i+1) % n] = 1.0
    return A

def main():
    args = parse_args()

    cfg = DualPhaseConfig(
        N_inner=args.N_inner, N_outer=args.N_outer,
        steps=args.steps, dt=args.dt, seed=args.seed,
        K_inner=args.K_inner, K_outer=args.K_outer, K_cross=args.K_cross,
        omega_inner_std=args.omega_inner_std, omega_outer_std=args.omega_outer_std
    )

    out = simulate_dual_phase(cfg)

    # Build a simple adjacency that matches the concatenated state length
    A_inner = _ring_adj(cfg.N_inner)
    A_outer = _ring_adj(cfg.N_outer)
    # block-diagonal ring for bundle calc (cross info comes from C_cross & collapse_signal)
    A = np.zeros((cfg.N_inner + cfg.N_outer, cfg.N_inner + cfg.N_outer))
    A[:cfg.N_inner, :cfg.N_inner] = A_inner
    A[cfg.N_inner:, cfg.N_inner:] = A_outer

    # For drift & Phi we need lag values; synthesize a tiny phase trajectory
    # consistent with R_inner/R_outer trends (purely for smoothness/entropy proxies here)
    rng = np.random.default_rng(cfg.seed)
    theta_prev = rng.uniform(-np.pi, np.pi, size=cfg.N_inner + cfg.N_outer)

    log_path = Path(args.save_csv)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "step", "t",
            "R_total", "R_inner", "R_outer", "C_cross",
            "drift", "Delta", "Phi", "choice_score"
        ])

        for k in range(cfg.steps):
            t = (k + 1) * cfg.dt

            # synthesize a gentle step using coherence to scale movement
            # higher R_total -> smaller random step (gentler)
            R_total = float(out["R_total"][k])
            step_scale = max(0.02, 0.20 * (1.0 - R_total))
            dtheta = rng.normal(0.0, step_scale, size=theta_prev.size)
            theta_now = wrap_phase(theta_prev + dtheta)

            # bundle over concatenated state (gives R, cross01, drift, C01, Delta)
            R_b, cross01, drift, C01, Delta = metrics_bundle(theta_now, theta_prev, A)
            # prefer reported R_total/R_inner/R_outer + C_cross from simulate_dual_phase
            R_inner = float(out["R_inner"][k])
            R_outer = float(out["R_outer"][k])
            C_cross = float(out["C_cross"][k])

            # lag-1 smoothness proxy Phi from bundle: invert normalized drift gently
            Phi = float(np.exp(-drift))  # [0,1], small drift => Phi≈1

            # choice / collapse signal (higher with high order & cross, low drift)
            choice_score = collapse_signal(R_total, C_cross, drift)

            w.writerow([
                k, f"{t:.4f}",
                f"{R_total:.6f}", f"{R_inner:.6f}", f"{R_outer:.6f}", f"{C_cross:.6f}",
                f"{drift:.6f}", f"{Delta:.6f}", f"{Phi:.6f}", f"{choice_score:.6f}"
            ])

            theta_prev = theta_now

    if args.plot:
        try:
            import matplotlib.pyplot as plt
            import pandas as pd
            df = pd.read_csv(log_path)
            plt.figure()
            plt.plot(df["t"], df["R_total"], label="R_total")
            plt.plot(df["t"], df["R_inner"], label="R_inner")
            plt.plot(df["t"], df["R_outer"], label="R_outer")
            plt.plot(df["t"], df["C_cross"], label="C_cross")
            plt.legend(); plt.xlabel("t"); plt.ylabel("coherence"); plt.title("Multi-Scale")
            plt.show()
        except Exception:
            pass

if __name__ == "__main__":
    main()
