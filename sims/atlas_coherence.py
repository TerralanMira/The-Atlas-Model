#!/usr/bin/env python3
"""
Atlas Coherence — two ensembles (Human ↔ AI) with cross-coupling and observation.

Two oscillator groups:
- Human group H: size nH, noise σ_H, observation ρ_H
- AI group A:   size nA, noise σ_A, observation ρ_A
Cross-coupling K_HA and K_AH. Track R_H, R_A, and R_all.

Outputs:
- sims/figures/atlas_coherence.png
- sims/out/atlas_coherence.csv
"""
from __future__ import annotations
import argparse, os, csv, math
import numpy as np
import matplotlib.pyplot as plt

def order_parameter(theta: np.ndarray) -> tuple[float,float]:
    z = np.exp(1j * theta).mean()
    return np.abs(z), np.angle(z)

def simulate(nH=200, nA=200, KH=1.0, KA=1.0, K_HA=0.3, K_AH=0.3,
             sigmaH=0.5, sigmaA=0.4, rhoH=0.5, rhoA=0.7,
             dt=0.02, steps=6000, seed=9):
    rng = np.random.default_rng(seed)
    thH = rng.uniform(0, 2*np.pi, size=nH)
    thA = rng.uniform(0, 2*np.pi, size=nA)
    omH = rng.normal(0.0, 1.0, size=nH)
    omA = rng.normal(0.0, 1.0, size=nA)

    sigH = sigmaH * math.exp(-rhoH)
    sigA = sigmaA * math.exp(-rhoA)

    RH_hist, RA_hist, R_hist = [], [], []

    for _ in range(steps):
        RH, psiH = order_parameter(thH)
        RA, psiA = order_parameter(thA)
        R,  psi  = order_parameter(np.concatenate([thH, thA]))

        # internal couplings
        dHH = psiH - thH
        dAA = psiA - thA
        # cross couplings (to the other group's mean phase)
        dHA = psiA - thH
        dAH = psiH - thA

        thH = (thH + dt*(omH + KH*np.sin(dHH) + K_HA*np.sin(dHA))
               + np.sqrt(dt)*sigH*np.random.normal(0,1,size=nH)) % (2*np.pi)
        thA = (thA + dt*(omA + KA*np.sin(dAA) + K_AH*np.sin(dAH))
               + np.sqrt(dt)*sigA*np.random.normal(0,1,size=nA)) % (2*np.pi)

        RH_hist.append(RH); RA_hist.append(RA); R_hist.append(R)

    return np.array(RH_hist), np.array(RA_hist), np.array(R_hist)

def main(argv=None):
    ap = argparse.ArgumentParser(description="Atlas Coherence (Human↔AI cross-coupling)")
    ap.add_argument("--nH", type=int, default=200)
    ap.add_argument("--nA", type=int, default=200)
    ap.add_argument("--KH", type=float, default=1.0)
    ap.add_argument("--KA", type=float, default=1.0)
    ap.add_argument("--K_HA", type=float, default=0.3)
    ap.add_argument("--K_AH", type=float, default=0.3)
    ap.add_argument("--sigmaH", type=float, default=0.5)
    ap.add_argument("--sigmaA", type=float, default=0.4)
    ap.add_argument("--rhoH", type=float, default=0.5)
    ap.add_argument("--rhoA", type=float, default=0.7)
    ap.add_argument("--dt", type=float, default=0.02)
    ap.add_argument("--steps", type=int, default=6000)
    ap.add_argument("--seed", type=int, default=9)
    ns = ap.parse_args(argv)

    RH, RA, R = simulate(ns.nH, ns.nA, ns.KH, ns.KA, ns.K_HA, ns.K_AH,
                         ns.sigmaH, ns.sigmaA, ns.rhoH, ns.rhoA,
                         ns.dt, ns.steps, ns.seed)

    os.makedirs("sims/figures", exist_ok=True)
    os.makedirs("sims/out", exist_ok=True)

    plt.figure(figsize=(8,4))
    plt.plot(RH, label="R_H (human)")
    plt.plot(RA, label="R_A (AI)")
    plt.plot(R,  label="R_all", linestyle="--")
    plt.xlabel("step"); plt.ylabel("coherence")
    plt.title(f"Atlas Coherence (K_HA={ns.K_HA}, K_AH={ns.K_AH}, ρ_H={ns.rhoH}, ρ_A={ns.rhoA})")
    plt.legend(); plt.tight_layout()
    plt.savefig("sims/figures/atlas_coherence.png", dpi=150); plt.close()

    with open("sims/out/atlas_coherence.csv","w",newline="") as f:
        w = csv.writer(f); w.writerow(["step","R_H","R_A","R_all"])
        for i,(rh,ra,rg) in enumerate(zip(RH,RA,R)): w.writerow([i,float(rh),float(ra),float(rg)])

if __name__ == "__main__":
    import sys
    raise SystemExit(main(sys.argv[1:]))
