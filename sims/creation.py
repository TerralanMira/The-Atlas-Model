"""
Creation (Genesis) Simulation

From near-silence to living structure:
- Start cold (low coupling, higher noise).
- Slowly ramp ritual openness and lower noise (an annealing schedule).
- Baseline hum nudges orientation.
- When local coherence + resources are ample, "creation events" add long-range edges.
- Crystallization points lock in as anchors that persist between pulses.

Self-contained (numpy only).

Author: Atlas
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
import numpy as np


# ---------- Driver (Schumann-like) ----------

@dataclass
class Driver:
    freq: float
    amplitude: float
    phase: float = 0.0

def driver_series(steps: int, dt: float, drivers: List[Driver]) -> Dict[str, np.ndarray]:
    t = np.arange(steps) * dt
    comps = np.array([d.amplitude * np.sin(2*np.pi*d.freq*t + d.phase) for d in drivers])  # (C,T)
    env = comps.sum(axis=0)
    env_d = np.gradient(env, dt)
    phi_env = np.arctan2(env_d, env)  # crude phase proxy
    return {"t": t, "components": comps, "env": env, "phi_env": phi_env}


# ---------- Config ----------

@dataclass
class CreationConfig:
    # time
    steps: int = 4000
    dt: float = 0.02
    seed: Optional[int] = 108
    # population
    N: int = 180
    k_ring: int = 4           # very low initial lattice degree
    p_rewire: float = 0.02
    # base coupling + noise (start cold)
    K_base_start: float = 0.6
    K_base_end: float = 1.0
    noise_start: float = 0.06
    noise_end: float = 0.03
    # ritual windows (ramped openness)
    period: int = 600
    K_cross_base_start: float = 0.0
    K_cross_base_end: float = 0.02
    K_cross_amp_start: float = 0.0
    K_cross_amp_end: float = 0.08
    # driver
    K_env: float = 0.28
    drivers: List[Driver] = field(default_factory=lambda: [
        Driver(7.83, 1.0, 0.0),
        Driver(14.3, 0.6, 0.0),
        Driver(20.8, 0.4, 0.0),
    ])
    # resources
    r_init: float = 0.55
    resource_gain: float = 0.33
    resource_leak: float = 0.20
    resource_noise: float = 0.02
    # crystallization
    window: int = 80
    thresh_R_local: float = 0.84
    thresh_resource: float = 0.55
    K_anchor_boost: float = 0.6
    noise_anchor_drop: float = 0.02
    anchor_half_life: int = 700
    starve_threshold: float = 0.35
    # creation events (edge births)
    grow_every: int = 200             # steps between growth checks
    grow_budget: int = 80             # total edges that can be birthed
    grow_batch_min: int = 3
    grow_batch_max: int = 8
    grow_require_R_local: float = 0.80
    grow_require_r: float = 0.55
    # summary tail
    tail_frac: float = 0.5


# ---------- Graph helpers ----------

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

def add_edge(u: int, v: int, nbrs: List[np.ndarray]) -> None:
    # mutate neighbor lists in place
    su = set(nbrs[u].tolist()); sv = set(nbrs[v].tolist())
    if v not in su and u != v:
        su.add(v); sv.add(u)
        nbrs[u] = np.array(sorted(list(su)), dtype=int)
        nbrs[v] = np.array(sorted(list(sv)), dtype=int)


# ---------- Utilities ----------

def lerp(a: float, b: float, x: float) -> float:
    return (1.0 - x) * a + x * b

def order_param(phases: np.ndarray) -> complex:
    return np.mean(np.exp(1j * phases))

def local_R(i: int, phases: np.ndarray, nbrs: List[np.ndarray]) -> float:
    if len(nbrs[i]) == 0:
        return 0.0
    group = np.concatenate(([i], nbrs[i]))
    return float(np.abs(np.mean(np.exp(1j * phases[group]))))


# ---------- Simulation ----------

def simulate(cfg: CreationConfig | Dict[str, Any]) -> Dict[str, Any]:
    if isinstance(cfg, dict):
        d = cfg.get("drivers", None)
        if d and len(d) and not isinstance(d[0], Driver):
            cfg["drivers"] = [Driver(**x) for x in d]
        cfg = CreationConfig(**cfg)

    rng = np.random.default_rng(cfg.seed)

    # state
    phases = rng.uniform(0, 2*np.pi, size=cfg.N)
    omega = rng.normal(0.0, 0.25, size=cfg.N)
    r = np.clip(cfg.r_init + 0.05 * rng.standard_normal(cfg.N), 0.0, 1.0)
    nbrs = watts_strogatz(cfg.N, cfg.k_ring, cfg.p_rewire, rng)

    # anchors
    is_anchor = np.zeros(cfg.N, dtype=bool)
    anchor_age = np.zeros(cfg.N, dtype=int)

    # driver
    drv = driver_series(cfg.steps, cfg.dt, cfg.drivers)

    # logs
    R_global = np.zeros(cfg.steps)
    gap_env = np.zeros(cfg.steps)
    K_cross_t = np.zeros(cfg.steps)
    noise_t = np.zeros(cfg.steps)
    R_local = np.zeros((cfg.steps, cfg.N))
    r_hist = np.zeros((cfg.steps, cfg.N))
    anchors_count = np.zeros(cfg.steps, dtype=int)
    # creation events as tuples: (t, u, v)
    creation_events: List[Tuple[int,int,int]] = []

    # sliding window for local coherence
    Rbuf = np.zeros((cfg.window, cfg.N)); wptr = 0; warm = 0

    # growth budget tracker
    edges_left = cfg.grow_budget

    for t in range(cfg.steps):
        # annealing (0..1 ramp)
        x = t / max(1, cfg.steps-1)
        K_base = lerp(cfg.K_base_start, cfg.K_base_end, x)
        noise_base = lerp(cfg.noise_start, cfg.noise_end, x)
        K_cross_base = lerp(cfg.K_cross_base_start, cfg.K_cross_base_end, x)
        K_cross_amp  = lerp(cfg.K_cross_amp_start,  cfg.K_cross_amp_end,  x)

        # ritual modulation
        cyc = np.sin(2*np.pi * t / cfg.period) * 0.5 + 0.5   # 0..1
        K_cross = K_cross_base + K_cross_amp * cyc
        noise_mod = noise_base - 0.02 * cyc
        K_cross_t[t] = K_cross
        noise_t[t] = noise_mod

        # local coherence
        for i in range(cfg.N):
            Ri = local_R(i, phases, nbrs)
            R_local[t, i] = Ri
            Rbuf[wptr, i] = Ri
        wptr = (wptr + 1) % cfg.window
        warm = min(warm + 1, cfg.window)

        # crystallization
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
        mean_c = order_param(phases)
        R_global[t] = np.abs(mean_c)
        anchors_count[t] = int(is_anchor.sum())
        mean_phase = np.angle(mean_c)
        gap_env[t] = np.abs(np.angle(np.exp(1j * (mean_phase - drv["phi_env"][t]))))
        r_hist[t] = r

        # dynamics
        dphi = np.zeros(cfg.N)

        # neighbor mean (base)
        for i in range(cfg.N):
            if len(nbrs[i]) == 0:
                continue
            neighbor_mean = np.angle(np.mean(np.exp(1j * phases[nbrs[i]])))
            dphi[i] += K_base * np.sin(neighbor_mean - phases[i])

        # cross openness (ritual)
        dphi += K_cross * np.sin(mean_phase - phases)

        # Schumann driver
        dphi += cfg.K_env * np.sin(drv["phi_env"][t] - phases)

        # anchor effect
        K_eff_scale = np.ones(cfg.N)
        for i in range(cfg.N):
            if is_anchor[i] or (len(nbrs[i]) and np.any(is_anchor[nbrs[i]])):
                K_eff_scale[i] += cfg.K_anchor_boost / max(K_base, 1e-6)

        # noise shaping
        noise_node = np.full(cfg.N, noise_mod)
        noise_node[is_anchor] = np.maximum(0.0, noise_node[is_anchor] - cfg.noise_anchor_drop)

        # integrate
        phases = phases + (omega + dphi * K_eff_scale) * cfg.dt \
                 + noise_node * np.sqrt(cfg.dt) * rng.standard_normal(cfg.N)
        phases = np.mod(phases, 2*np.pi)

        # resources
        gain = cfg.resource_gain * (R_local[t] - 0.5)
        r = r + (gain - cfg.resource_leak * (r - 0.5)) * cfg.dt \
              + cfg.resource_noise * np.sqrt(cfg.dt) * rng.standard_normal(cfg.N)
        r = np.clip(r, 0.0, 1.0)

        # -------- creation events: birth long-range edges --------
        if edges_left > 0 and (t % cfg.grow_every == 0) and warm == cfg.window:
            # eligible nodes: coherent & resourced
            eligible = np.where((Rbuf.mean(axis=0) >= cfg.grow_require_R_local) & (r >= cfg.grow_require_r))[0]
            if eligible.size >= 2:
                batch = int(rng.integers(cfg.grow_batch_min, cfg.grow_batch_max+1))
                batch = min(batch, edges_left)
                for _ in range(batch):
                    u = int(rng.choice(eligible))
                    # connect u to a far node that's not already a neighbor
                    pool = [v for v in range(cfg.N) if v != u and v not in nbrs[u]]
                    if not pool:
                        continue
                    # prefer distant by ring-distance
                    v = int(rng.choice(pool))
                    add_edge(u, v, nbrs)
                    creation_events.append((t, u, v))
                    edges_left -= 1
                    if edges_left == 0:
                        break

    # summaries
    tail_start = int(cfg.steps * (1.0 - cfg.tail_frac))
    tail = slice(tail_start, cfg.steps)
    summary = {
        "R_mean_tail": float(np.mean(R_global[tail])),
        "gap_env_tail": float(np.mean(gap_env[tail])),
        "anchors_tail_mean": float(np.mean(anchors_count[tail])),
        "r_tail_mean": float(np.mean(r_hist[tail])),
        "edges_birthed": int(len(creation_events)),
    }

    return {
        "cfg": {
            **{k: getattr(cfg, k) for k in vars(cfg) if k != "drivers"},
            "drivers": [vars(d) for d in cfg.drivers],
        },
        "t": drv["t"],
        "R": R_global,
        "gap_to_env": gap_env,
        "K_cross_t": K_cross_t,
        "noise_t": noise_t,
        "anchors_count": anchors_count,
        "R_local": R_local,
        "r_hist": r_hist,
        "env": drv["env"],
        "env_components": drv["components"],
        "phi_env": drv["phi_env"],
        "creation_events": np.array(creation_events, dtype=int) if creation_events else np.zeros((0,3), dtype=int),
        "summary": summary,
    }

if __name__ == "__main__":
    out = simulate(CreationConfig())
    print(out["summary"])
