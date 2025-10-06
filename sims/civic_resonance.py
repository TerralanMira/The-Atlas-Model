#!/usr/bin/env python3
"""
Civic Resonance — multi-node city field with local and global coupling.

N community nodes; each has a phase θ_i. Intra-neighborhood coupling Kintra,
global coupling Kglobal to the city mean phase ψ. Tracks global R(t) and per-block R_k(t).

Outputs:
- sims/figures/civic_resonance_R.png
- sims/out/civic_resonance.csv
"""
from __future__ import annotations
import argparse, os, csv
import numpy as np
import matplotlib.pyplot as plt

def order_parameter(theta: np.ndarray) -> tuple[float,float]:
    z = np.exp(1j * theta).mean()
    return np.abs(z), np.angle(z)

def block_indices(n: int, blocks: int):
    # partition n into contiguous blocks
    base = n // blocks
    rem = n % blocks
    idxs = []
    start = 0
    for b in range(blocks):
        size = base + (1 if b < rem else 0)
        idxs.append(slice(start, start+size))
        start += size
    return idxs

def simulate(n=400, blocks=8, Kintra=1.2, Kglobal=0.4, sigma=0.2, dt=0.02, steps=6000, seed=123):
    rng = np.random.default_rng(seed)
    theta = rng.uniform(0, 2*np.pi, size=n)
    omega = rng.normal(0.0, 1.0, size=n)
    idxs = block_indices(n, blocks)

    Rg_hist = []
    Rb_hist = []  # store mean of block coherences

    for t in range(steps):
        Rg, psi = order_parameter(theta)
        # intra-block coupling
        coupl = np.zeros_like(theta)
        for s in idxs:
            th = theta[s]
            Rb, psib = order_parameter(th)
            coupl[s] += Kintra * np.sin(psib - th)
        # global coupling
        coupl += Kglobal * np.sin(psi - theta)
        # noise
        theta = (theta + dt * (omega + coupl) + np.sqrt(dt)*sigma*rng.normal(0,1,size=n)) % (2*np.pi)

        # record
        Rg_hist.append(Rg)
        blk_Rs = [order_parameter(theta[s])[0] for s in idxs]
        Rb_hist.append(float(np.mean(blk_Rs)))
    return np.array(Rg_hist), np.array(Rb_hist)

def main(argv=None):
    ap = argparse.ArgumentParser(description="Civic Resonance (city as oscillator field)")
    ap.add_argument("--n", type=int, default=400)
    ap.add_argument("--blocks", type=int, default=8)
    ap.add_argument("--Kintra", type=float, default=1.2)
    ap.add_argument("--Kglobal", type=float, default=0.4)
    ap.add_argument("--sigma", type=float, default=0.2)
    ap.add_argument("--dt", type=float, default=0.02)
    ap.add_argument("--steps", type=int, default=6000)
    ap.add_argument("--seed", type=int, default=123)
    ns = ap.parse_args(argv)

    Rg, Rb = simulate(ns.n, ns.blocks, ns.Kintra, ns.Kglobal, ns.sigma, ns.dt, ns.steps, ns.seed)

    os.makedirs("sims/figures", exist_ok=True)
    os.makedirs("sims/out", exist_ok=True)

    plt.figure(figsize=(8,4))
    plt.plot(Rg, label="global R")
    plt.plot(Rb, label="mean block R", linestyle="--")
    plt.xlabel("step"); plt.ylabel("coherence")
    plt.title(f"Civic Resonance (Kintra={ns.Kintra}, Kglobal={ns.Kglobal})")
    plt.legend(); plt.tight_layout()
    plt.savefig("sims/figures/civic_resonance_R.png", dpi=150); plt.close()

    with open("sims/out/civic_resonance.csv","w",newline="") as f:
        w = csv.writer(f); w.writerow(["step","R_global","R_blocks_mean"])
        for i,(rg,rb) in enumerate(zip(Rg,Rb)): w.writerow([i,float(rg),float(rb)])

if __name__ == "__main__":
    import sys
    raise SystemExit(main(sys.argv[1:]))
