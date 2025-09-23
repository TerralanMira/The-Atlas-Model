"""
Community Kuramoto Simulator

- Loads a preset from sims/presets.json (graph, K, dt, steps, noise, groups)
- Simulates phases on a network with Euler integration
- Computes community resonance metrics and prints a compact summary

Usage:
    python sims/community_kuramoto.py --preset community_demo
"""

import argparse
import json
import numpy as np
from pathlib import Path

try:
    # Local import; ensure algorithms is a package or adjust sys.path as needed
    from algorithms.community_metrics import time_series_metrics, summarize_metrics
except Exception:
    # Fallback: allow running as script when project root isn't in PYTHONPATH
    import sys
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from algorithms.community_metrics import time_series_metrics, summarize_metrics

def euler_step(theta, omega, K, A, noise_std, dt):
    """
    One Euler step for graph-coupled Kuramoto.
    theta: (N,)
    omega: (N,)
    A: (N,N)
    """
    N = theta.shape[0]
    deg = np.clip(A.sum(axis=1), 1e-9, None)
    sin_terms = np.zeros(N)
    # interaction term
    for i in range(N):
        sin_terms[i] = np.sum(A[i] * np.sin(theta - theta[i])) / deg[i]
    dtheta = omega + K * sin_terms
    if noise_std > 0:
        dtheta += np.random.normal(0, noise_std, size=N)
    return (theta + dt * dtheta) % (2*np.pi)

def simulate(preset: dict, seed: int = 7):
    rng = np.random.default_rng(seed)

    N = int(preset.get("N", 50))
    steps = int(preset.get("steps", 2000))
    dt = float(preset.get("dt", 0.05))
    K = float(preset.get("K", 1.0))
    noise_std = float(preset.get("noise_std", 0.0))

    # Graph
    if "adjacency" in preset:
        A = np.array(preset["adjacency"], dtype=float)
        N = A.shape[0]
    else:
        # default: ring + small-world rewirings
        p_rewire = float(preset.get("p_rewire", 0.05))
        k_ring = int(preset.get("k_ring", 4))
        A = np.zeros((N, N))
        for i in range(N):
            for k in range(1, k_ring//2 + 1):
                j = (i + k) % N
                A[i, j] = 1
                A[j, i] = 1
        # rewire
        for i in range(N):
            for j in range(i+1, N):
                if A[i, j] == 1 and rng.random() < p_rewire:
                    A[i, j] = A[j, i] = 0
                    # new random connection
                    r = rng.integers(0, N)
                    while r == i:
                        r = rng.integers(0, N)
                    A[i, r] = A[r, i] = 1

    # Groups (labels)
    groups = preset.get("groups", None)
    if groups is not None and len(groups) != N:
        raise ValueError("Length of 'groups' must match N")

    # Natural frequencies
    if "omega" in preset:
        omega = np.array(preset["omega"], dtype=float)
        if omega.shape[0] != N:
            raise ValueError("omega length must equal N")
    else:
        omega_mu = float(preset.get("omega_mu", 0.0))
        omega_sigma = float(preset.get("omega_sigma", 0.3))
        omega = rng.normal(omega_mu, omega_sigma, size=N)

    # Initial phases
    if "theta0" in preset:
        theta = np.array(preset["theta0"], dtype=float) % (2*np.pi)
        if theta.shape[0] != N:
            raise ValueError("theta0 length must equal N")
    else:
        theta = rng.uniform(0, 2*np.pi, size=N)

    # Optional intervention schedule
    interventions = preset.get("interventions", [])  # list of {t_start,t_end, type, params}

    # Sim loop
    T = steps
    TH = np.zeros((T, N))
    K_t = K

    for t in range(T):
        # apply interventions if any
        for iv in interventions:
            t0, t1 = iv.get("t_start", 0), iv.get("t_end", 0)
            if t0 <= t < t1:
                if iv.get("type") == "increase_coupling":
                    K_t = K * float(iv.get("factor", 2.0))
                elif iv.get("type") == "reduce_noise":
                    noise_std = float(iv.get("new_noise", 0.0))
                elif iv.get("type") == "add_bridge":
                    i, j, w = iv["i"], iv["j"], float(iv.get("weight", 1.0))
                    A[i, j] = A[j, i] = w
            else:
                # reset to defaults after window
                K_t = K

        theta = euler_step(theta, omega, K_t, A, noise_std, dt)
        TH[t] = theta

    # Metrics
    m = time_series_metrics(TH, groups=groups)
    summary = summarize_metrics(m)
    return {"summary": summary, "metrics": m}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preset", type=str, default="community_demo")
    parser.add_argument("--presets_path", type=str, default=str(Path(__file__).with_name("presets.json")))
    args = parser.parse_args()

    with open(args.presets_path, "r") as f:
        presets = json.load(f)
    if args.preset not in presets:
        raise KeyError(f"Preset '{args.preset}' not found.")
    result = simulate(presets[args.preset])
    print("=== Community Resonance Summary ===")
    for k, v in result["summary"].items():
        print(f"{k}: {v:.4f}")

if __name__ == "__main__":
    main()
