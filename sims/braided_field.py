"""
Braided Field:
Schumann baseline (external driver) + Ritual windows (time-varying openness)
+ Crystallization points (persistent anchors) on a small-world graph.

This file is self-contained to avoid import tangles. It mirrors the intent of:
- sims/schumann_pulse.py
- sims/ritual_window.py
- sims/crystallization_points.py

Outputs key traces so docs/dashboard can plot the braid on one canvas.

Author: Atlas (hum-led)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import numpy as np


# ---------- Baseline driver (Schumann-like) ----------

@dataclass
class Driver:
    freq: float
    amplitude: float
    phase: float = 0.0

def driver_series(steps: int, dt: float, drivers: List[Driver]) -> Dict[str, np.ndarray]:
    t = np.arange(steps) * dt
    comps = np.array([d.amplitude * np.sin(2*np.pi*d.freq*t + d.phase) for d in drivers])  # (C,T)
    env = comps.sum(axis=0)
    # crude phase proxy: arctan of derivative vs value
    env_d = np.gradient(env, dt)
    phi_env = np.arctan2(env_d, env)
    return {"t": t, "components": comps, "env": env, "phi_env": phi_env}


# ---------- Config ----------

@dataclass
class BraidedConfig:
    # time
    steps: int = 3000
    dt: float = 0.02
    seed: Optional[int] = 42
    # population/graph
    N: int = 160
    k_ring: int = 6
    p_rewire: float = 0.06
    # agent frequencies & noise
    omega_mu: float = 0.0
    omega_sigma: float = 0.25
    noise_std: float = 0.035
    # base coupling (neighbor Kuramoto)
    K_base: float = 1.0
    # ritual window (time-varying openness)
    period: int = 600
    K_cross_base: float = 0.02      # global openness baseline
    K_cross_amp: float = 0.08       # ritual lift
    noise_drop: float = 0.02        # noise decreases in ritual windows
    # Schumann driver
    K_env: float = 0.28
    drivers: List[Driver] = field(default_factory=lambda: [
        Driver(7.83, 1.0, 0.0),
        Driver(14.3, 0.6, 0.0),
        Driver(20.8, 0.4, 0.0),
    ])
    # crystallization
    window: int = 80
    thresh_R_local: float = 0.85
    thresh_resource: float = 0.55
    K_anchor_boost: float = 0.6
    noise_anchor_drop: float = 0.02
    anchor_half_life: int = 600
    starve_threshold: float = 0.35
    # resource tank
    r_init: float = 0.6
    resource_gain: float = 0.35
    resource_leak: float = 0.22
    resource_noise: float = 0.02


# ---------- Graph ----------

def watts_strogatz(N: int, k: int, p: float, rng: np.random.Generator):
    nbrs = [set() for _ in range(N)]
    for i in range(N):
        for j in range(1, k//2 + 1):
            a = (i - j) % N; b = (i + j) % N
            nbrs[i].add(a); nbrs[i].add(b)
    for i in range(N):
        for j in list(nbrs[i]):
            if j > i and rng.random() < p:
                choices = [x for x in range(N) if x != i and x not in nbrs[i]]
                if choices:
                    new = int(rng.choice(choices))
                    nbrs[i].remove(j); nbrs[j].remove(i)
                    nbrs[i].add(new); nbrs[new].add(i)
    return [np.array(sorted(list(s)), dtype=int) for s in nbrs]


# ---------- Helpers ----------

def order_param(phases: np.ndarray) -> complex:
    return np.mean(np.exp(1j * phases))

def local_R(i: int, phases: np.ndarray, nbrs) -> float:
    if len(nbrs[i]) == 0:
        return 0.0
    group = np.concatenate(([i], nbrs[i]))
    return float(np.abs(np.mean(np.exp(1j * phases[group]))))


# ---------- Simulation ----------

def simulate(cfg: BraidedConfig | Dict[str, Any]) -> Dict[str, Any]:
    if isinstance(cfg, dict):
        # allow drivers listed as dicts
        d = cfg.get("drivers", None)
        if d and len(d) and not isinstance(d[0], Driver):
            cfg["drivers"] = [Driver(**x) for x in d]
        cfg = BraidedConfig(**cfg)

    rng = np.random.default_rng(cfg.seed)
    omega = rng.normal(cfg.omega_mu, cfg.omega_sigma, size=cfg.N)
    phases = rng.uniform(0, 2*np.pi, size=cfg.N)
    nbrs = watts_strogatz(cfg.N, cfg.k_ring, cfg.p_rewire, rng)

    # resources + anchors
    r = np.clip(cfg.r_init + 0.05*rng.standard_normal(cfg.N), 0.0, 1.0)
    is_anchor = np.zeros(cfg.N, dtype=bool)
    anchor_age = np.zeros(cfg.N, dtype=int)

    drv = driver_series(cfg.steps, cfg.dt, cfg.drivers)

    # buffers
    R_global = np.zeros(cfg.steps)
    R_local = np.zeros((cfg.steps, cfg.N))
    anchors_count = np.zeros(cfg.steps, dtype=int)
    r_hist = np.zeros((cfg.steps, cfg.N))
    K_cross_t = np.zeros(cfg.steps)
    noise_t = np.zeros(cfg.steps)
    gap_to_env = np.zeros(cfg.steps)

    # sliding window for local coherence
    Rbuf = np.zeros((cfg.window, cfg.N)); wptr = 0; warm = 0

    for t in range(cfg.steps):
        # ritual modulation
        cyc = np.sin(2*np.pi * t / cfg.period) * 0.5 + 0.5  # 0..1
        K_cross = cfg.K_cross_base + cfg.K_cross_amp * cyc
        noise_mod = cfg.noise_std - cfg.noise_drop * cyc
        K_cross_t[t] = K_cross
        noise_t[t] = noise_mod

        # local coherence
        for i in range(cfg.N):
            Ri = local_R(i, phases, nbrs)
            R_local[t, i] = Ri
            Rbuf[wptr, i] = Ri
        wptr = (wptr + 1) % cfg.window
        warm = min(warm + 1, cfg.window)

        # crystallize
        if warm == cfg.window:
            Rmean_local = Rbuf.mean(axis=0)
            to_anchor = (~is_anchor) & (Rmean_local >= cfg.thresh_R_local) & (r >= cfg.thresh_resource)
            is_anchor[to_anchor] = True
            anchor_age[to_anchor] = 0

        # starve → decay
        starving = is_anchor & (r < cfg.starve_threshold)
        anchor_age[is_anchor] += 1
        hl = max(1, cfg.anchor_half_life)
        decay_prob = np.zeros(cfg.N)
        decay_prob[starving] = 1.0 - 0.5 ** (anchor_age[starving] / hl)
        drop = rng.random(cfg.N) < decay_prob
        is_anchor[drop] = False
        anchor_age[drop] = 0

        # global stats
        mean_phase_c = order_param(phases)
        R_global[t] = np.abs(mean_phase_c)
        anchors_count[t] = int(is_anchor.sum())
        r_hist[t] = r

        # phase gap to environment driver
        mean_phase = np.angle(mean_phase_c)
        gap_to_env[t] = np.abs(np.angle(np.exp(1j * (mean_phase - drv["phi_env"][t]))))

        # dynamics
        dphi = np.zeros(cfg.N)

        # neighbor alignment (base)
        for i in range(cfg.N):
            if len(nbrs[i]) == 0:
                continue
            neighbor_mean = np.angle(np.mean(np.exp(1j * phases[nbrs[i]])))
            dphi[i] += cfg.K_base * np.sin(neighbor_mean - phases[i])

        # cross openness (ritual): pull toward global mean
        dphi += K_cross * np.sin(mean_phase - phases)

        # Schumann driver
        dphi += cfg.K_env * np.sin(drv["phi_env"][t] - phases)

        # anchor effect → stronger effective K near anchors; anchors get lower noise
        K_eff_scale = np.ones(cfg.N)
        for i in range(cfg.N):
            if is_anchor[i] or (len(nbrs[i]) and np.any(is_anchor[nbrs[i]])):
                K_eff_scale[i] += cfg.K_anchor_boost / max(cfg.K_base, 1e-6)

        noise_node = np.full(cfg.N, noise_mod)
        noise_node[is_anchor] = np.maximum(0.0, noise_node[is_anchor] - cfg.noise_anchor_drop)

        # integrate
        phases = phases + (omega + dphi * K_eff_scale) * cfg.dt \
                 + noise_node * np.sqrt(cfg.dt) * rng.standard_normal(cfg.N)
        phases = np.mod(phases, 2*np.pi)

        # resources (coherence-coupled)
        gain = cfg.resource_gain * (R_local[t] - 0.5)
        r = r + (gain - cfg.resource_leak * (r - 0.5)) * cfg.dt \
              + cfg.resource_noise * np.sqrt(cfg.dt) * rng.standard_normal(cfg.N)
        r = np.clip(r, 0.0, 1.0)

    # summaries (tail window)
    tail = slice(cfg.steps // 2, cfg.steps)
    summary = {
        "R_mean_tail": float(np.mean(R_global[tail])),
        "gap_env_tail": float(np.mean(gap_to_env[tail])),
        "anchors_tail_mean": float(np.mean(anchors_count[tail])),
        "r_tail_mean": float(np.mean(r_hist[tail])),
    }

    return {
        "cfg": {
            **{k: getattr(cfg, k) for k in vars(cfg) if k != "drivers"},
            "drivers": [vars(d) for d in cfg.drivers],
        },
        "t": drv["t"],
        "R": R_global,
        "gap_to_env": gap_to_env,
        "K_cross_t": K_cross_t,
        "noise_t": noise_t,
        "anchors_count": anchors_count,
        "R_local": R_local,
        "r_hist": r_hist,
        "env": drv["env"],
        "env_components": drv["components"],
        "phi_env": drv["phi_env"],
        "summary": summary,
    }

if __name__ == "__main__":
    out = simulate(BraidedConfig())
    print(out["summary"])
