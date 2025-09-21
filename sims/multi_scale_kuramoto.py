#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Two-layer Kuramoto runner that calls algorithms.field_equations.DualPhaseConfig / simulate_dual_phase.

Usage:
    python sims/multi_scale_kuramoto.py
    python sims/multi_scale_kuramoto.py --steps 1000 --K_inner 0.5 --K_outer 0.3 --K_cross 0.12
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

import numpy as np
try:
    import matplotlib.pyplot as plt
except Exception:
    plt = None

from algorithms.field_equations import DualPhaseConfig, simulate_dual_phase

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
    ap.add_argument("--driver_amp", type=float, default=0.00)
    ap.add_argument("--driver_omega", type=float, default=7.83)
    ap.add_argument("--driver_phase", type=float, default=0.0)
    ap.add_argument("--noise_std", type=float, default=0.00)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--plot", action="store_true")
    ap.add_argument("--save_csv", type=str, default="logs/multi_scale.csv")
    return ap.parse_args()

def main():
    args = parse_args()
    cfg = DualPhaseConfig(
        N_inner=args.N_inner, N_outer=args.N_outer,
        steps=args.steps, dt=args.dt, seed=args.seed,
        K_inner=args.K_inner, K_outer=args.K_outer, K_cross=args.K_cross,
        omega_inner_std=args.omega_inner_std, omega_outer_std=args.omega_outer_std,
        driver_amp=args.driver_amp, driver_omega=args.driver_omega,
        driver_phase=args.driver_phase, noise_std=args.noise_std
    )

    out = simulate_dual_phase(cfg)

    # ensure logs dir
    log_path = Path(args.save_csv)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    # write CSV
    import csv
    with open(log_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["step", "R_total", "R_inner", "R_outer", "C_cross"])
        for k in range(cfg.steps):
            w.writerow([k, out["R_total"][k], out["R_inner"][k], out["R_outer"][k], out["C_cross"][k]])

    if args.plot and plt is not None:
        t = np.arange(cfg.steps) * cfg.dt
        plt.figure()
        plt.plot(t, out["R_total"], label="R_total")
        plt.plot(t, out["R_inner"], label="R_inner")
        plt.plot(t, out["R_outer"], label="R_outer")
        plt.plot(t, out["C_cross"], label="C_cross")
        plt.xlabel("time")
        plt.ylabel("coherence")
        plt.legend()
        plt.title("Multi-Scale Kuramoto")
        plt.show()

if __name__ == "__main__":
    main()
