"""
Ritual window simulation:
- Groups with intra + cross coupling (from resonance_transfer)
- Cross-coupling (K_cross) and noise (σ) modulated periodically
- Captures how periodic "windows" (festivals, assemblies) amplify resonance transfer
"""

from __future__ import annotations
import numpy as np
from dataclasses import dataclass

@dataclass
class RitualConfig:
    steps: int = 3000
    dt: float = 0.05
    N_total: int = 100
    groups: tuple[int, ...] = (50, 50)
    K_intra: float = 1.0
    K_cross_base: float = 0.02
    K_cross_amp: float = 0.08
    period: int = 600        # steps per ritual cycle
    noise_base: float = 0.04
    noise_drop: float = 0.02
    omega_mu: float = 0.0
    omega_sigma: float = 0.2
    seed: int | None = 21

def _order_param(phases):
    return np.mean(np.exp(1j * phases))

def simulate(cfg: RitualConfig | dict) -> dict:
    if isinstance(cfg, dict):
        cfg = RitualConfig(**cfg)

    if cfg.seed is not None:
        np.random.seed(cfg.seed)

    assert sum(cfg.groups) == cfg.N_total
    omega = np.random.normal(cfg.omega_mu, cfg.omega_sigma, size=cfg.N_total)
    phases = np.random.uniform(0, 2*np.pi, size=cfg.N_total)

    group_slices = []
    start = 0
    for g in cfg.groups:
        group_slices.append(slice(start, start + g))
        start += g
    G = len(group_slices)

    R_global = np.zeros(cfg.steps)
    R_groups = np.zeros((cfg.steps, G))
    gap_series = np.zeros(cfg.steps)
    K_cross_t = np.zeros(cfg.steps)
    noise_t = np.zeros(cfg.steps)

    for t in range(cfg.steps):
        # modulate cross-coupling and noise in cycles
        cyc = np.sin(2*np.pi * t / cfg.period) * 0.5 + 0.5  # 0..1
        K_cross = cfg.K_cross_base + cfg.K_cross_amp * cyc
        noise = cfg.noise_base - cfg.noise_drop * cyc

        K_cross_t[t] = K_cross
        noise_t[t] = noise

        # group means
        means = []
        for g, sl in enumerate(group_slices):
            r = _order_param(phases[sl])
            R_groups[t, g] = np.abs(r)
            means.append(np.angle(r))
        R_global[t] = np.abs(_order_param(phases))

        if G == 2:
            gap = np.angle(np.exp(1j * (means[0] - means[1])))
            gap_series[t] = np.abs(gap)
        else:
            acc, pairs = 0.0, 0
            for i in range(G):
                for j in range(i+1, G):
                    d = np.angle(np.exp(1j * (means[i] - means[j])))
                    acc += np.abs(d); pairs += 1
            gap_series[t] = acc / max(1, pairs)

        # dynamics
        dphi = np.zeros_like(phases)
        for g, sl in enumerate(group_slices):
            phi_g = phases[sl]
            mean_g = means[g]
            dphi[sl] += cfg.K_intra * np.sin(mean_g - phi_g)
            for h, mean_h in enumerate(means):
                if h != g:
                    dphi[sl] += K_cross * np.sin(mean_h - phi_g)

        phases = phases + (omega + dphi) * cfg.dt + noise * np.sqrt(cfg.dt) * np.random.randn(cfg.N_total)
        phases = np.mod(phases, 2*np.pi)

    return {
        "cfg": cfg.__dict__,
        "R_global": R_global,
        "R_groups": R_groups,
        "gap": gap_series,
        "K_cross_t": K_cross_t,
        "noise_t": noise_t
    }

if __name__ == "__main__":
    res = simulate(RitualConfig())
    print({k: np.mean(v) if isinstance(v, np.ndarray) else v for k,v in res.items() if isinstance(v, (list, np.ndarray))})
