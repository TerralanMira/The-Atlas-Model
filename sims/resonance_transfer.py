"""
Resonance transfer between sub-communities.

Two (or more) groups with internal Kuramoto-like coupling and weak cross-coupling.
Tracks within-group coherence, between-group phase gap, and global coherence.

This is a minimal, readable instrument — not overfit — so it can be extended.
"""

from __future__ import annotations
from dataclasses import dataclass
import numpy as np

@dataclass
class TransferConfig:
    steps: int = 2000
    dt: float = 0.05
    N_total: int = 100          # total agents
    groups: tuple[int, ...] = (50, 50)  # sizes per group (sum must equal N_total)
    K_intra: float = 1.0        # within-group coupling
    K_cross: float = 0.05       # cross-group (leakage) coupling
    noise_std: float = 0.03
    omega_mu: float = 0.0
    omega_sigma: float = 0.2
    seed: int | None = 7

def _order_param(phases: np.ndarray) -> complex:
    """Kuramoto order parameter for a 1D phase array."""
    return np.mean(np.exp(1j * phases))

def _group_indices(groups: tuple[int, ...]) -> list[slice]:
    idx = []
    start = 0
    for g in groups:
        idx.append(slice(start, start + g))
        start += g
    return idx

def simulate(cfg: TransferConfig | dict) -> dict:
    """Run resonance transfer simulation and return metrics + timeseries."""
    if isinstance(cfg, dict):
        cfg = TransferConfig(**cfg)

    if cfg.seed is not None:
        np.random.seed(cfg.seed)

    assert sum(cfg.groups) == cfg.N_total, "sum(groups) must equal N_total"

    # natural frequencies and initial phases
    omega = np.random.normal(cfg.omega_mu, cfg.omega_sigma, size=cfg.N_total)
    phases = np.random.uniform(0, 2*np.pi, size=cfg.N_total)

    groups_idx = _group_indices(cfg.groups)
    G = len(groups_idx)

    # outputs
    R_global = np.zeros(cfg.steps)
    R_groups = np.zeros((cfg.steps, G))
    phase_means = np.zeros((cfg.steps, G))
    gap_series = np.zeros(cfg.steps)  # pairwise mean phase gap (for G=2) or mean of all gaps

    for t in range(cfg.steps):
        # compute group means
        means = []
        for g, sl in enumerate(groups_idx):
            r = _order_param(phases[sl])
            R_groups[t, g] = np.abs(r)
            means.append(np.angle(r))
            phase_means[t, g] = means[-1]

        # compute global order
        R_global[t] = np.abs(_order_param(phases))

        # mean phase gaps (for G>2, average pairwise gaps on circle)
        if G == 2:
            diff = np.angle(np.exp(1j * (means[0] - means[1])))
            gap_series[t] = np.abs(diff)
        else:
            # average pairwise circular distance
            acc = 0.0
            pairs = 0
            for i in range(G):
                for j in range(i+1, G):
                    d = np.angle(np.exp(1j * (means[i] - means[j])))
                    acc += np.abs(d)
                    pairs += 1
            gap_series[t] = acc / max(1, pairs)

        # dynamics update (Euler–Maruyama)
        dphi = np.zeros_like(phases)
        for g, sl in enumerate(groups_idx):
            phi_g = phases[sl]
            mean_g = means[g]

            # intra-group pull
            dphi[sl] += cfg.K_intra * np.sin(mean_g - phi_g)

            # cross-group leakage: attract toward other groups' means
            for h, mean_h in enumerate(means):
                if h == g:
                    continue
                dphi[sl] += cfg.K_cross * np.sin(mean_h - phi_g)

        # integrate with natural frequency and noise
        phases = phases + (omega + dphi) * cfg.dt + cfg.noise_std * np.sqrt(cfg.dt) * np.random.randn(cfg.N_total)
        phases = np.mod(phases, 2*np.pi)

    summary = {
        "R_global_mean": float(np.mean(R_global[int(0.5*cfg.steps):])),
        "gap_mean": float(np.mean(gap_series[int(0.5*cfg.steps):])),
        "R_groups_mean": [float(np.mean(R_groups[int(0.5*cfg.steps):, g])) for g in range(G)]
    }

    return {
        "cfg": cfg.__dict__,
        "R_global": R_global,
        "R_groups": R_groups,
        "phase_means": phase_means,
        "gap": gap_series,
        "summary": summary
    }

if __name__ == "__main__":
    res = simulate(TransferConfig())
    print(res["summary"])
