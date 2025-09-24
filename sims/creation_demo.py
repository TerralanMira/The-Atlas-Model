"""
Minimal creation demo:
- Simulates N oscillators with sinusoid driver and noise
- Computes R(t), mean phase, gap(t)
- Evaluates Creation Gates (algorithms/creation_protocols.py)
- Emits JSON and CSV; optional plot

Run:
  python sims/creation_demo.py --steps 4000 --N 128 --K 0.8 --driver-amp 0.6 --plot
"""

from __future__ import annotations
import argparse
import csv
import math
import sys
from pathlib import Path

import numpy as np

# local imports
sys.path.append(str(Path(__file__).resolve().parents[1]))
from algorithms.creation_protocols import (
    order_parameter, phase_gap, evaluate_gates, GateConfig, tuning_recommendations, to_json
)

def simulate(
    steps=4000, N=128, K=0.8, driver_amp=0.6, driver_freq=0.006, noise_std=0.05, seed=7
):
    rng = np.random.default_rng(seed)
    # Initial phases, natural frequencies
    phases = rng.uniform(-np.pi, np.pi, size=N)
    omega = rng.normal(0.0, 0.05, size=N)

    # Ring topology coupling weights
    W = np.zeros((N, N), dtype=float)
    for i in range(N):
        W[i, (i - 1) % N] = 1.0
        W[i, (i + 1) % N] = 1.0
    W = W / W.sum(axis=1, keepdims=True)

    phases_hist = np.zeros((steps, N))
    R_series = np.zeros(steps)
    gap_series = np.zeros(steps)
    driver_phase = 0.0

    dt = 1.0
    for t in range(steps):
        # Driver signal
        driver_phase = (driver_phase + 2 * np.pi * driver_freq) % (2 * np.pi)
        drive = driver_amp * np.sin(driver_phase)

        # Kuramoto-like update with ring coupling and driver
        mean_sin = np.sin(phases)
        mean_cos = np.cos(phases)
        psi = math.atan2(mean_sin.mean(), mean_cos.mean())
        coupling_term = K * (W @ np.sin(psi - phases))

        dtheta = omega + coupling_term + drive + rng.normal(0.0, noise_std, size=N)
        phases = (phases + dt * dtheta + np.pi) % (2 * np.pi) - np.pi

        # Record
        R, psi_now = order_parameter(phases)
        gap = phase_gap(psi_now, driver_phase)
        phases_hist[t] = phases
        R_series[t] = R
        gap_series[t] = gap

    return phases_hist, R_series, gap_series

def write_csv(out_csv: Path, R_series, gap_series):
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t", "R", "gap"])
        for t, (R, g) in enumerate(zip(R_series, gap_series)):
            w.writerow([t, float(R), float(g)])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=4000)
    ap.add_argument("--N", type=int, default=128)
    ap.add_argument("--K", type=float, default=0.8)
    ap.add_argument("--driver-amp", type=float, default=0.6)
    ap.add_argument("--driver-freq", type=float, default=0.006)
    ap.add_argument("--noise-std", type=float, default=0.05)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--plot", action="store_true")
    args = ap.parse_args()

    phases_hist, R_series, gap_series = simulate(
        steps=args.steps, N=args.N, K=args.K,
        driver_amp=args.driver_amp, driver_freq=args.driver_freq,
        noise_std=args.noise_std, seed=args.seed
    )

    cfg = GateConfig()
    summary = evaluate_gates(R_series, gap_series, phases_hist, cfg=cfg, sovereignty_ok=True)

    # Emit JSON
    out_dir = Path("artifacts/creation_demo")
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "summary.json"
    json_path.write_text(to_json(summary))

    # Emit CSV
    write_csv(out_dir / "timeseries.csv", R_series, gap_series)

    # Optional plot
    if args.plot:
        try:
            import matplotlib.pyplot as plt
            fig1 = plt.figure()
            plt.plot(R_series)
            plt.title("R(t)")
            fig2 = plt.figure()
            plt.plot(np.abs(gap_series))
            plt.title("|gap(t)|")
            plt.show()
        except Exception as e:
            print(f"[plot] skipped: {e}")

    # Print concise console readout
    print("Hum: measuring emergence—no claims without gates.\n")
    print(to_json(summary))
    print("\nTuning:")
    for r in tuning_recommendations(summary):
        print(f"- {r}")

if __name__ == "__main__":
    main()
