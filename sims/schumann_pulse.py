"""
Schumann-like baseline hum driving a Kuramoto field.

- External driver: sum of sinusoidal components (e.g., 7.83, 14.3, 20.8 ... units).
- Agents: phases with natural frequencies and noise.
- Coupling: intra-field K plus external forcing strength K_env.
- Outputs: global coherence R(t), driver envelope, component traces, phase offset to driver.

Time units are arbitrary "steps" with dt; frequencies are in cycles per second-like units,
so phase = 2π f (t*dt). Use relative magnitudes; we don't claim biophysical fidelity.

Author: Atlas (hum-led)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any
import numpy as np

@dataclass
class Driver:
    freq: float          # e.g., 7.83
    amplitude: float     # driver amplitude weight
    phase: float = 0.0   # initial phase offset (radians)

@dataclass
class SchumannConfig:
    steps: int = 3000
    dt: float = 0.01
    N: int = 256
    K: float = 1.1                 # intra-field coupling
    K_env: float = 0.3             # coupling to external driver
    noise_std: float = 0.03
    omega_mu: float = 0.0          # mean intrinsic frequency
    omega_sigma: float = 0.25      # diversity of intrinsic frequency
    seed: int | None = 11
    drivers: List[Driver] = field(default_factory=lambda: [
        Driver(freq=7.83, amplitude=1.0, phase=0.0),
        Driver(freq=14.3, amplitude=0.6, phase=0.0),
        Driver(freq=20.8, amplitude=0.4, phase=0.0)
    ])

def _order_param(phases: np.ndarray) -> complex:
    """Kuramoto order parameter for a 1D phase array."""
    return np.mean(np.exp(1j * phases))

def _driver_series(cfg: SchumannConfig) -> Dict[str, np.ndarray]:
    """Compute composite driver and component traces."""
    t = np.arange(cfg.steps) * cfg.dt
    comps = []
    for d in cfg.drivers:
        comps.append(d.amplitude * np.sin(2*np.pi*d.freq*t + d.phase))
    comps = np.array(comps)                       # shape: (C, T)
    env = comps.sum(axis=0)                       # composite
    return {"t": t, "components": comps, "env": env}

def simulate(cfg: SchumannConfig | Dict[str, Any]) -> Dict[str, Any]:
    """Run Schumann-driven Kuramoto and return metrics + timeseries."""
    if isinstance(cfg, dict):
        # allow dict drivers as {"freq":..,"amplitude":..}
        drivers = cfg.get("drivers", None)
        if drivers and len(drivers) and not isinstance(drivers[0], Driver):
            cfg["drivers"] = [Driver(**d) for d in drivers]
        cfg = SchumannConfig(**cfg)

    if cfg.seed is not None:
        np.random.seed(cfg.seed)

    # initialize
    omega = np.random.normal(cfg.omega_mu, cfg.omega_sigma, size=cfg.N)
    phases = np.random.uniform(0, 2*np.pi, size=cfg.N)

    drv = _driver_series(cfg)
    env = drv["env"]                                  # (T,)
    t = drv["t"]

    R = np.zeros(cfg.steps)
    phi_env = np.zeros(cfg.steps)                     # envelope phase (analytic angle proxy)
    # simple phase proxy: use instantaneous arctangent of derivative vs value
    env_d = np.gradient(env, cfg.dt)
    phi_env = np.arctan2(env_d, env)                  # not Hilbert; good enough for phase relation

    phase_gap_to_env = np.zeros(cfg.steps)            # |mean_phase - env_phase|

    for k in range(cfg.steps):
        mean = np.angle(_order_param(phases))
        R[k] = np.abs(_order_param(phases))
        phase_gap_to_env[k] = np.abs(np.angle(np.exp(1j*(mean - phi_env[k]))))

        # dynamics: intra-field + external forcing
        dphi = cfg.K * np.sin(mean - phases) + cfg.K_env * np.sin(phi_env[k] - phases)
        noise = cfg.noise_std * np.sqrt(cfg.dt) * np.random.randn(cfg.N)
        phases = phases + (omega + dphi) * cfg.dt + noise
        phases = np.mod(phases, 2*np.pi)

    # summaries (use second half to avoid warm-up bias)
    tail = slice(cfg.steps // 2, cfg.steps)
    summary = {
        "R_mean_tail": float(np.mean(R[tail])),
        "gap_mean_tail": float(np.mean(phase_gap_to_env[tail])),
        "R_std_tail": float(np.std(R[tail])),
    }

    return {
        "cfg": {
            **{k: getattr(cfg, k) for k in vars(cfg) if k != "drivers"},
            "drivers": [vars(d) for d in cfg.drivers],
        },
        "t": t,
        "R": R,
        "env": env,
        "env_components": drv["components"],  # shape (C, T)
        "phi_env": phi_env,
        "phase_gap_to_env": phase_gap_to_env,
        "summary": summary,
    }

if __name__ == "__main__":
    res = simulate(SchumannConfig())
    print(res["summary"])
