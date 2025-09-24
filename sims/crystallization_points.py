"""
Crystallization points:
- Agents on a graph evolve Kuramoto-style.
- Nodes with sustained high local coherence + resource surplus "crystallize".
- Crystallized nodes act as anchors: reduced noise, stronger coupling, slow decay if underfed.

This models how coherence becomes persistent structure between pulses.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any
import numpy as np

@dataclass
class CrystalConfig:
    steps: int = 3000
    dt: float = 0.05
    N: int = 150
    k_ring: int = 6
    p_rewire: float = 0.05           # Watts–Strogatz small-world
    K: float = 1.0                   # base coupling
    noise_std: float = 0.035
    omega_mu: float = 0.0
    omega_sigma: float = 0.25
    # crystallization conditions
    window: int = 80                 # samples to evaluate local coherence
    thresh_R_local: float = 0.85     # required local coherence
    thresh_resource: float = 0.55    # required resource level
    # anchor effects
    K_anchor_boost: float = 0.6      # added to K for edges touching anchor
    noise_anchor_drop: float = 0.02  # subtracted from noise for anchor nodes
    # resource dynamics (simple logistic-ish tank per node)
    resource_gain: float = 0.35
    resource_leak: float = 0.22
    resource_noise: float = 0.02
    r_init: float = 0.6
    # anchor decay if starved
    anchor_half_life: int = 600      # steps to lose anchoring when r low
    starve_threshold: float = 0.35
    seed: Optional[int] = 13

def _watts_strogatz(N: int, k: int, p: float, rng: np.random.Generator) -> np.ndarray:
    """Adjacency list as index arrays for each node."""
    # ring lattice
    neighbors = [set() for _ in range(N)]
    for i in range(N):
        for j in range(1, k//2 + 1):
            a = (i - j) % N; b = (i + j) % N
            neighbors[i].add(a); neighbors[i].add(b)
    # rewire
    for i in range(N):
        for j in list(neighbors[i]):
            if j > i:  # undirected; handle once
                if rng.random() < p:
                    # pick new target not self or existing
                    choices = [x for x in range(N) if x != i and x not in neighbors[i]]
                    if choices:
                        new = int(rng.choice(choices))
                        neighbors[i].remove(j); neighbors[j].remove(i)
                        neighbors[i].add(new); neighbors[new].add(i)
    # convert to arrays
    return [np.array(sorted(list(s)), dtype=int) for s in neighbors]

def _order_param(phases: np.ndarray) -> complex:
    return np.mean(np.exp(1j * phases))

def simulate(cfg: CrystalConfig | Dict[str, Any]) -> Dict[str, Any]:
    if isinstance(cfg, dict):
        cfg = CrystalConfig(**cfg)
    rng = np.random.default_rng(cfg.seed)

    omega = rng.normal(cfg.omega_mu, cfg.omega_sigma, size=cfg.N)
    phases = rng.uniform(0, 2*np.pi, size=cfg.N)
    r = np.clip(cfg.r_init + 0.05*rng.standard_normal(cfg.N), 0.0, 1.0)

    nbrs = _watts_strogatz(cfg.N, cfg.k_ring, cfg.p_rewire, rng)

    # state for anchors
    is_anchor = np.zeros(cfg.N, dtype=bool)
    anchor_age = np.zeros(cfg.N, dtype=int)

    # buffers
    R_global = np.zeros(cfg.steps)
    R_local = np.zeros((cfg.steps, cfg.N))
    anchors_count = np.zeros(cfg.steps, dtype=int)
    r_hist = np.zeros((cfg.steps, cfg.N))

    # simple circular-mean helper
    def local_R(i: int, phi: np.ndarray) -> float:
        group = np.concatenate(([i], nbrs[i]))
        return np.abs(np.mean(np.exp(1j * phi[group])))

    # sliding window storage for local R
    Rbuf = np.zeros((cfg.window, cfg.N))
    wptr = 0
    warm = 0

    for t in range(cfg.steps):
        # compute local coherence
        for i in range(cfg.N):
            Rloc = local_R(i, phases)
            R_local[t, i] = Rloc
            Rbuf[wptr, i] = Rloc
        wptr = (wptr + 1) % cfg.window
        warm = min(warm + 1, cfg.window)

        # detect crystallization
        if warm == cfg.window:
            Rmean_local = Rbuf.mean(axis=0)
            to_anchor = (~is_anchor) & (Rmean_local >= cfg.thresh_R_local) & (r >= cfg.thresh_resource)
            is_anchor[to_anchor] = True
            anchor_age[to_anchor] = 0

        # anchor decay if starved
        starving = is_anchor & (r < cfg.starve_threshold)
        anchor_age[is_anchor] += 1
        decay_prob = np.zeros(cfg.N)
        hl = max(1, cfg.anchor_half_life)
        decay_prob[starving] = 1.0 - 0.5 ** (anchor_age[starving] / hl)
        drop = rng.random(cfg.N) < decay_prob
        is_anchor[drop] = False
        anchor_age[drop] = 0

        # global order
        R_global[t] = np.abs(_order_param(phases))
        anchors_count[t] = int(is_anchor.sum())
        r_hist[t] = r

        # dynamics
        mean_phase = np.angle(_order_param(phases))
        dphi = np.zeros(cfg.N)

        # base Kuramoto on graph (neighbor mean)
        for i in range(cfg.N):
            if len(nbrs[i]) == 0:
                continue
            neighbor_mean = np.angle(np.mean(np.exp(1j * phases[nbrs[i]])))
            dphi[i] += cfg.K * np.sin(neighbor_mean - phases[i])

        # anchor effects: edges touching anchors strengthen coupling; anchors get lower noise
        effective_K = np.full(cfg.N, cfg.K)
        for i in range(cfg.N):
            if np.any(is_anchor[nbrs[i]]) or is_anchor[i]:
                effective_K[i] += cfg.K_anchor_boost

        # integrate
        noise_node = cfg.noise_std * np.ones(cfg.N)
        noise_node[is_anchor] = np.maximum(0.0, noise_node[is_anchor] - cfg.noise_anchor_drop)

        phases = phases + (omega + dphi * (effective_K / cfg.K)) * cfg.dt \
                 + noise_node * np.sqrt(cfg.dt) * rng.standard_normal(cfg.N)
        phases = np.mod(phases, 2*np.pi)

        # resource dynamics: gain from coherence, leak otherwise
        gain = cfg.resource_gain * (R_local[t] - 0.5)  # centered so low coherence still possible
        r = r + (gain - cfg.resource_leak*(r-0.5)) * cfg.dt \
              + cfg.resource_noise * np.sqrt(cfg.dt) * rng.standard_normal(cfg.N)
        r = np.clip(r, 0.0, 1.0)

    tail = slice(cfg.steps//2, cfg.steps)
    summary = {
        "R_mean_tail": float(np.mean(R_global[tail])),
        "anchors_tail_mean": float(np.mean(anchors_count[tail])),
        "r_tail_mean": float(np.mean(r_hist[tail])),
    }

    return {
        "cfg": vars(cfg),
        "R": R_global,
        "R_local": R_local,
        "anchors": is_anchor,
        "anchors_count": anchors_count,
        "r_hist": r_hist,
        "summary": summary
    }

if __name__ == "__main__":
    out = simulate(CrystalConfig())
    print(out["summary"])
