"""
Multilayer Community Resonance Simulator (extended)

Adds:
- r_history[t, i]: per-node resource over time
- env_phase_history[t]: environment driver phase over time
- before/after comparison helpers (returned in result['windows'])

Run:
    python sims/multilayer_resonance.py --preset multilayer_demo
"""

import argparse
import json
import numpy as np
from pathlib import Path

# flexible local imports
try:
    from algorithms.community_metrics import time_series_metrics, summarize_metrics
    from algorithms.environment_drivers import CompositeDriver, SineDriver
except Exception:
    import sys
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from algorithms.community_metrics import time_series_metrics, summarize_metrics
    from algorithms.environment_drivers import CompositeDriver, SineDriver

TWOPI = 2 * np.pi

def make_default_layers(N: int, L: int, k_ring: int, p_rewire: float, rng: np.random.Generator):
    layers = []
    for _ in range(L):
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
                    r = rng.integers(0, N)
                    while r == i:
                        r = rng.integers(0, N)
                    A[i, r] = A[r, i] = 1
        layers.append(A)
    return layers

def euler_step_multilayer(theta, omega, K_node, layers, gamma, noise_std, dt):
    L, N = theta.shape
    dtheta = np.zeros((L, N))
    for l in range(L):
        A = layers[l]
        deg = np.clip(A.sum(axis=1), 1e-9, None)
        for i in range(N):
            coupling = np.sum(A[i] * np.sin(theta[l] - theta[l, i])) / deg[i]
            dtheta[l, i] = omega[i] + K_node[i] * coupling
    # interlayer diagonal align
    for i in range(N):
        mean_i = np.angle(np.mean(np.exp(1j * theta[:, i])))
        for l in range(L):
            dtheta[l, i] += gamma * np.sin(mean_i - theta[l, i])
    if noise_std > 0:
        dtheta += np.random.normal(0, noise_std, size=(L, N))
    return (theta + dt * dtheta) % TWOPI

def adaptive_frequency_update(omega, theta_layer, alpha, dt):
    psi_local = np.angle(np.mean(np.exp(1j * theta_layer)))
    err = np.angle(np.exp(1j * (psi_local - theta_layer)))
    return omega + alpha * err * dt

def resource_update(r, R_local, params, dt):
    a = float(params.get("gain", 0.5))
    b = float(params.get("leak", 0.3))
    dr = a * R_local * (1.0 - r) - b * (1.0 - R_local) * r
    r_new = np.clip(r + dt * dr, 0.0, 1.0)
    return r_new

def apply_environment(theta, env_phase, K_env, layer_index):
    return (theta[layer_index] + K_env * np.sin(env_phase - theta[layer_index])) % TWOPI

def simulate(preset: dict, seed: int = 11):
    rng = np.random.default_rng(seed)

    # core params
    N = int(preset.get("N", 80))
    L = int(preset.get("L", 2))
    steps = int(preset.get("steps", 2000))
    dt = float(preset.get("dt", 0.05))
    noise_std = float(preset.get("noise_std", 0.03))
    gamma = float(preset.get("gamma", 0.4))
    alpha = float(preset.get("alpha", 0.02))
    resource_params = preset.get("resource", {"gain": 0.5, "leak": 0.3})
    K_base = float(preset.get("K", 1.2))
    K_env = float(preset.get("K_env", 0.2))
    env_layer = int(preset.get("env_layer", 0))

    # groups (optional)
    groups = preset.get("groups", None)
    if groups is not None and len(groups) != N:
        raise ValueError("Length of 'groups' must match N")

    # layers
    if "layers" in preset and isinstance(preset["layers"], list):
        layers = [np.array(A, dtype=float) for A in preset["layers"]]
        L = len(layers)
        for A in layers:
            if A.shape[0] != N or A.shape[1] != N:
                raise ValueError("All layer adjacency matrices must be NxN")
    else:
        k_ring = int(preset.get("k_ring", 6))
        p_rewire = float(preset.get("p_rewire", 0.08))
        layers = make_default_layers(N, L, k_ring, p_rewire, rng)

    # natural frequencies and initial phases
    omega_mu = float(preset.get("omega_mu", 0.0))
    omega_sigma = float(preset.get("omega_sigma", 0.25))
    omega = rng.normal(omega_mu, omega_sigma, size=N)
    theta = rng.uniform(0, TWOPI, size=(L, N))

    # resources K_of_r
    r = np.clip(np.array(preset.get("r0", rng.uniform(0.3, 0.7, size=N)), dtype=float), 0.0, 1.0)
    def K_of_r(rvals):  # coupling scales with resource
        return K_base * (0.2 + 0.8 * rvals)

    # environment driver
    if "env_drivers" in preset:
        drivers = [SineDriver(**d) for d in preset["env_drivers"]]
    else:
        drivers = [SineDriver(freq_hz=7.83, amplitude=1.0)]
    env = CompositeDriver(drivers, dt=dt, time_scale=float(preset.get("time_scale", 1.0)))

    # interventions
    interventions = preset.get("interventions", [])

    # storage
    TH = np.zeros((steps, N))          # phases on metrics layer
    TH_comm = np.zeros((steps, N))     # phases on community layer
    r_history = np.zeros((steps, N))   # resources over time
    env_phase_history = np.zeros(steps)

    L_metrics_layer = int(preset.get("metrics_layer", 0))
    comm_layer = int(preset.get("community_layer", min(1, L-1)))

    # helper for local coherence proxy R_local
    def local_R(layer_idx):
        A = layers[layer_idx]
        deg = np.clip(A.sum(axis=1), 1e-9, None)
        nbr_mean = np.zeros(N, dtype=complex)
        for i in range(N):
            if deg[i] > 0:
                nbr_mean[i] = np.sum(A[i] * np.exp(1j * theta[layer_idx])) / deg[i]
        return np.abs(nbr_mean)

    for t in range(steps):
        # scheduled interventions
        for iv in interventions:
            t0, t1 = iv.get("t_start", 0), iv.get("t_end", 0)
            active = t0 <= t < t1
            if active and iv.get("type") == "increase_coupling":
                K_base = float(iv.get("new_K", K_base))
            if active and iv.get("type") == "reduce_noise":
                noise_std = float(iv.get("new_noise", noise_std))
            if active and iv.get("type") == "add_bridge":
                l = int(iv.get("layer", 0))
                i, j = int(iv["i"]), int(iv["j"])
                w = float(iv.get("weight", 1.0))
                layers[l][i, j] = layers[l][j, i] = w

        # env
        phi_env = env.phase_at(t)
        env_phase_history[t] = phi_env
        theta[env_layer] = apply_environment(theta, phi_env, K_env, env_layer)

        # step
        K_node = K_of_r(r)
        theta = euler_step_multilayer(theta, omega, K_node, layers, gamma, noise_std, dt)
        omega = adaptive_frequency_update(omega, theta[comm_layer], alpha, dt)

        # resources
        R_local = local_R(comm_layer)
        r = resource_update(r, R_local, resource_params, dt)

        # record
        TH[t] = theta[L_metrics_layer]
        TH_comm[t] = theta[comm_layer]
        r_history[t] = r

    # metrics
    m = time_series_metrics(TH, groups=groups)
    summary = summarize_metrics(m)

    # optional before/after windows around first intervention (if present)
    windows = None
    if len(interventions) > 0 and "t_start" in interventions[0] and "t_end" in interventions[0]:
        t0 = int(interventions[0]["t_start"])
        t1 = int(interventions[0]["t_end"])
        pre = slice(max(0, t0 - 200), max(1, t0))
        post = slice(min(TH.shape[0], t1), min(TH.shape[0], t1 + 200))
        windows = {"pre": (pre.start, pre.stop), "post": (post.start, post.stop)}

    return {
        "summary": summary,
        "metrics_layer": m,
        "community_layer_phases": TH_comm,
        "r_history": r_history,
        "env_phase": env_phase_history,
        "final_resources_mean": float(np.mean(r)),
        "final_omega_mean": float(np.mean(omega)),
        "windows": windows,
        "interventions": interventions,
        "groups": groups
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preset", type=str, default="multilayer_demo")
    parser.add_argument("--presets_path", type=str, default=str(Path(__file__).with_name("presets.json")))
    args = parser.parse_args()

    with open(args.presets_path, "r") as f:
        presets = json.load(f)
    if args.preset not in presets:
        raise KeyError(f"Preset '{args.preset}' not found.")
    result = simulate(presets[args.preset])
    print("=== Multilayer Resonance Summary ===")
    for k, v in result["summary"].items():
        print(f"{k}: {v:.4f}")
    print(f"final_resources_mean: {result['final_resources_mean']:.4f}")
    print(f"final_omega_mean: {result['final_omega_mean']:.4f}")

if __name__ == "__main__":
    main()
