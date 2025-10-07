from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from typing import Callable, Tuple, Optional

@dataclass
class KuramotoConfig:
    n_local: int = 64           # oscillators per local cluster
    n_clusters: int = 4
    k_local: float = 1.0        # intra-cluster coupling
    k_global: float = 0.15      # inter-cluster coupling (between cluster reps)
    dt: float = 0.01
    t_max: float = 20.0
    noise_sigma: float = 0.0
    seed: Optional[int] = 42

def _ring_adjacency(n: int) -> np.ndarray:
    A = np.zeros((n, n), float)
    for i in range(n):
        A[i, (i-1) % n] = 1.0
        A[i, (i+1) % n] = 1.0
    return A

def make_multiscale_graph(cfg: KuramotoConfig) -> np.ndarray:
    n = cfg.n_local * cfg.n_clusters
    A = np.zeros((n, n), float)
    # local rings
    for c in range(cfg.n_clusters):
        idx = slice(c * cfg.n_local, (c + 1) * cfg.n_local)
        A[idx, idx] = _ring_adjacency(cfg.n_local) * cfg.k_local
    # weak global ties between cluster “leaders”
    for c in range(cfg.n_clusters):
        for d in range(c + 1, cfg.n_clusters):
            i0 = c * cfg.n_local
            j0 = d * cfg.n_local
            A[i0, j0] = A[j0, i0] = cfg.k_global
    return A

def kuramoto_step(theta: np.ndarray, omega: np.ndarray, A: np.ndarray,
                  dt: float, noise: float, rng: np.random.Generator) -> np.ndarray:
    # dθ_i/dt = ω_i + Σ_j A_ij * sin(θ_j − θ_i) + ξ
    phase_diff = theta[None, :] - theta[:, None]
    coupling = np.sum(A * np.sin(phase_diff), axis=1)
    dtheta = omega + coupling
    if noise > 0:
        dtheta += rng.normal(0.0, noise, size=theta.shape)
    return (theta + dt * dtheta + np.pi) % (2 * np.pi) - np.pi

def order_parameter(theta: np.ndarray) -> Tuple[float, float]:
    z = np.exp(1j * theta).mean()
    return np.abs(z), np.angle(z)

def run(cfg: KuramotoConfig,
        omega_fn: Optional[Callable[[int], np.ndarray]] = None,
        callback: Optional[Callable[[int, np.ndarray, float, float], None]] = None):
    rng = np.random.default_rng(cfg.seed)
    n = cfg.n_local * cfg.n_clusters
    A = make_multiscale_graph(cfg)
    omega = omega_fn(n) if omega_fn else rng.normal(0.0, 0.1, size=n)
    theta = rng.uniform(-np.pi, np.pi, size=n)

    steps = int(cfg.t_max / cfg.dt)
    for t in range(steps):
        theta = kuramoto_step(theta, omega, A, cfg.dt, cfg.noise_sigma, rng)
        R, psi = order_parameter(theta)
        if callback:
            callback(t, theta, R, psi)

if __name__ == "__main__":
    cfg = KuramotoConfig()
    trace_R = []
    def cb(t, theta, R, psi):
        if t % 50 == 0:
            print(f"t={t:5d}  R={R:.3f}  psi={psi:.2f}")
        trace_R.append(R)
    run(cfg, callback=cb)
