#!/usr/bin/env python3
"""
Harmonic Observation — observation lowers effective noise and stabilizes coherence.

Model: Kuramoto with stochastic noise σ and observation parameter ρ in [0,1].
Effective noise: σ_eff = σ * exp(-ρ). Optional coherence potential λ.

Outputs:
- sims/figures/harmonic_observation_R.png
- sims/out/harmonic_observation_metrics.csv
"""
from __future__ import annotations
import argparse, os, math, csv
from dataclasses import dataclass
import numpy as np
import matplotlib.pyplot as plt

@dataclass
class Params:
    n: int = 256
    K: float = 1.2
    sigma: float = 0.5
    rho: float = 0.6     # observation strength in [0,1]
    lam: float = 0.0     # ethics-as-coherence (stabilizer)
    dt: float = 0.02
    steps: int = 5000
    seed: int = 42
    topology: str = "all"  # all | ring

def adjacency(n: int, mode: str) -> np.ndarray:
    if mode == "ring":
        A = np.zeros((n, n))
        for i in range(n):
            A[i, (i-1) % n] = A[i, (i+1) % n] = 1.0
        return A
    # fully-connected (no self)
    A = np.ones((n, n)) - np.eye(n)
    return A

def order_parameter(theta: np.ndarray) -> tuple[float,float]:
    z = np.exp(1j * theta).mean()
    return np.abs(z), np.angle(z)

def simulate(p: Params):
    rng = np.random.default_rng(p.seed)
    theta = rng.uniform(0, 2*np.pi, size=p.n)
    omega = rng.normal(0.0, 1.0, size=p.n)  # natural frequencies
    A = adjacency(p.n, p.topology)
    deg = A.sum(axis=1, keepdims=True)
    deg[deg == 0] = 1.0

    sigma_eff = p.sigma * math.exp(-p.rho)

    R_hist = []
    for t in range(p.steps):
        R, psi = order_parameter(theta)
        # pairwise coupling term
        dtheta = theta[:, None] - theta[None, :]
        coupl = (A * np.sin(-dtheta)).sum(axis=1, keepdims=False) / deg[:,0]
        # ethics-as-coherence: mild pull to mean phase (acts like viscosity)
        pull = p.lam * np.sin(psi - theta)

        noise = sigma_eff * np.sqrt(p.dt) * rng.normal(0.0, 1.0, size=p.n)
        theta = (theta + p.dt * (omega + p.K * coupl + pull) + noise) % (2*np.pi)
        R_hist.append(R)

    return np.array(R_hist), theta

def save_metrics(R_hist: np.ndarray, out_csv: str):
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["step", "R"])
        for i, r in enumerate(R_hist):
            w.writerow([i, float(r)])

def plot_R(R_hist: np.ndarray, out_png: str, title: str):
    os.makedirs(os.path.dirname(out_png), exist_ok=True)
    plt.figure(figsize=(7,4))
    plt.plot(R_hist)
    plt.xlabel("step")
    plt.ylabel("coherence R(t)")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(out_png, dpi=150)
    plt.close()

def main(argv=None):
    ap = argparse.ArgumentParser(description="Harmonic Observation simulation")
    ap.add_argument("--n", type=int, default=Params.n)
    ap.add_argument("--K", type=float, default=Params.K)
    ap.add_argument("--sigma", type=float, default=Params.sigma)
    ap.add_argument("--rho", type=float, default=Params.rho)
    ap.add_argument("--lam", type=float, default=Params.lam)
    ap.add_argument("--dt", type=float, default=Params.dt)
    ap.add_argument("--steps", type=int, default=Params.steps)
    ap.add_argument("--seed", type=int, default=Params.seed)
    ap.add_argument("--topology", choices=["all","ring"], default=Params.topology)
    ns = ap.parse_args(argv)

    p = Params(n=ns.n, K=ns.K, sigma=ns.sigma, rho=ns.rho, lam=ns.lam,
               dt=ns.dt, steps=ns.steps, seed=ns.seed, topology=ns.topology)
    R_hist, _ = simulate(p)
    plot_R(R_hist, "sims/figures/harmonic_observation_R.png",
           f"Harmonic Observation (K={p.K}, ρ={p.rho}, λ={p.lam})")
    save_metrics(R_hist, "sims/out/harmonic_observation_metrics.csv")

if __name__ == "__main__":
    raise SystemExit(main())
