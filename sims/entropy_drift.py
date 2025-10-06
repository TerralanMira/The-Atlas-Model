#!/usr/bin/env python3
"""
Entropy Drift — alignment decays without feedback; periodic corrections restore coherence.

Scalar alignment a(t) ∈ [0,1] with decay rate γ. Optional feedback pulses every T steps with gain g.

Outputs:
- sims/figures/entropy_drift.png
- sims/out/entropy_drift.csv
"""
from __future__ import annotations
import argparse, os, csv
import numpy as np
import matplotlib.pyplot as plt

def simulate(a0=0.9, gamma=0.0015, steps=10000, pulse_T=1000, gain=0.25, noise=0.0, seed=7):
    rng = np.random.default_rng(seed)
    a = a0
    hist = []
    for t in range(steps):
        # decay
        a = a - gamma * a
        # optional noisy drift
        a = a + noise * rng.normal(0.0, 0.01)
        # feedback pulse
        if pulse_T > 0 and (t % pulse_T == 0) and t > 0:
            a = a + gain * (1.0 - a)
        # clamp
        a = float(max(0.0, min(1.0, a)))
        hist.append(a)
    return np.array(hist)

def main(argv=None):
    ap = argparse.ArgumentParser(description="Entropy Drift (alignment decay & correction)")
    ap.add_argument("--a0", type=float, default=0.9)
    ap.add_argument("--gamma", type=float, default=0.0015)
    ap.add_argument("--steps", type=int, default=10000)
    ap.add_argument("--pulse_T", type=int, default=1000)
    ap.add_argument("--gain", type=float, default=0.25)
    ap.add_argument("--noise", type=float, default=0.0)
    ap.add_argument("--seed", type=int, default=7)
    ns = ap.parse_args(argv)

    y = simulate(ns.a0, ns.gamma, ns.steps, ns.pulse_T, ns.gain, ns.noise, ns.seed)

    os.makedirs("sims/figures", exist_ok=True)
    os.makedirs("sims/out", exist_ok=True)

    plt.figure(figsize=(7,4))
    plt.plot(y)
    plt.xlabel("step")
    plt.ylabel("alignment a(t)")
    plt.title(f"Entropy Drift (γ={ns.gamma}, T={ns.pulse_T}, gain={ns.gain})")
    plt.tight_layout()
    plt.savefig("sims/figures/entropy_drift.png", dpi=150)
    plt.close()

    with open("sims/out/entropy_drift.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["step","a"])
        for i, v in enumerate(y): w.writerow([i, float(v)])

if __name__ == "__main__":
    import sys
    raise SystemExit(main(sys.argv[1:]))
