"""
Atlas Orchestrator — weave layers into one pulse.

This module coordinates multiple elemental subsystems and emits a single
coherence pulse for the whole. It DOES NOT replace individual sims; it
calls them in sequence (or parallel later) and aggregates metrics.

It gracefully degrades: if a layer's module is missing, it skips it.

Outputs (from run_once / run_steps):
- dict with per-layer metrics and a global 'atlas_coherence' key.

Dependencies: numpy (matplotlib not required here)
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
import numpy as np

# ---------- Optional imports (graceful if absent) ----------
def _try_import():
    mods = {}

    # Earth
    try:
        from algorithms.earth_structures import (
            lattice_adjacency, row_normalize, ThresholdField, MultiWellPotential,
            EarthStepConfig, earth_step, variance_coherence, phase_locking_value
        )
        mods["earth"] = {
            "lattice_adjacency": lattice_adjacency,
            "row_normalize": row_normalize,
            "ThresholdField": ThresholdField,
            "MultiWellPotential": MultiWellPotential,
            "EarthStepConfig": EarthStepConfig,
            "earth_step": earth_step,
            "variance_coherence": variance_coherence,
            "phase_locking_value": phase_locking_value,
        }
    except Exception:
        mods["earth"] = None

    # Self-learning network (Water/Air coupling surrogate)
    try:
        from algorithms.self_learning_networks import SelfLearningNetwork
        mods["selflearn"] = {"SelfLearningNetwork": SelfLearningNetwork}
    except Exception:
        mods["selflearn"] = None

    # Crystal
    try:
        from algorithms.crystal_growth import CrystalConfig, grow_crystal
        mods["crystal"] = {"CrystalConfig": CrystalConfig, "grow_crystal": grow_crystal}
    except Exception:
        mods["crystal"] = None

    return mods

MODS = _try_import()

# ---------- Config ----------
@dataclass
class AtlasConfig:
    seed: Optional[int] = 42
    steps: int = 200  # total macro steps for orchestrator loop

    # Earth
    earth_rows: int = 20
    earth_cols: int = 20

    # Self-learning network
    sln_nodes: int = 150
    sln_lr: float = 0.06

    # Crystal
    crystal_steps: int = 400

# ---------- Helpers ----------
def _earth_pulse(cfg: AtlasConfig, rng: np.random.Generator) -> Optional[Dict[str, float]]:
    if MODS["earth"] is None:
        return None
    m = MODS["earth"]

    n_rows, n_cols = cfg.earth_rows, cfg.earth_cols
    N = n_rows * n_cols

    A = m["lattice_adjacency"](n_rows, n_cols, periodic=True)
    A_norm = m["row_normalize"](A)
    thresholds = m["ThresholdField"].gradient(n_rows, n_cols, low=0.05, high=0.25)
    potential = m["MultiWellPotential"].triwell(centers=(-0.8, 0.0, 0.8),
                                                weights=(1.0, 0.5, 1.0), stiffness=0.8)
    state = rng.normal(0.0, 0.4, size=N).astype(float)
    phases = rng.uniform(0, 2*np.pi, size=N).astype(float)
    omega  = rng.normal(0.0, 0.05, size=N).astype(float)

    cfg_e = m["EarthStepConfig"]()
    # a short burst to get a stable pulse
    for _ in range(120):
        state, phases = m["earth_step"](state, phases, omega, A, A_norm, thresholds, potential, cfg_e)

    amp = m["variance_coherence"](state)
    phs = m["phase_locking_value"](phases)
    return {"earth_amp": float(amp), "earth_phase": float(phs)}

def _selflearn_pulse(cfg: AtlasConfig, rng: np.random.Generator) -> Optional[Dict[str, float]]:
    if MODS["selflearn"] is None:
        return None
    SLN = MODS["selflearn"]["SelfLearningNetwork"]
    net = SLN(num_nodes=cfg.sln_nodes, learning_rate=cfg.sln_lr)
    coh = 0.0
    for _ in range(200):
        net.step()
        coh = net.coherence_metric()
    return {"selflearn_coherence": float(coh)}

def _crystal_pulse(cfg: AtlasConfig, rng: np.random.Generator) -> Optional[Dict[str, float]]:
    if MODS["crystal"] is None:
        return None
    CrystalConfig = MODS["crystal"]["CrystalConfig"]
    grow_crystal  = MODS["crystal"]["grow_crystal"]

    ccfg = CrystalConfig(steps=cfg.crystal_steps)
    L, Tm, Fm, E, I = grow_crystal(ccfg, rng)
    # simple structural signal
    area = float(L.sum())
    occupied_ratio = area / (L.size + 1e-8)
    # temporal smoothness (earlier accretion more uniform -> lower std)
    tvals = Tm[L > 0].astype(float)
    if tvals.size > 0:
        tvals_std = float(np.nanstd(tvals))
    else:
        tvals_std = float("nan")
    return {"crystal_occupied": occupied_ratio, "crystal_time_std": tvals_std}

def _aggregate(pulses: Dict[str, Dict[str, float]]) -> float:
    """
    Combine available layer metrics into a single atlas_coherence in [0,1]-ish.
    The mapping is simple and monotone; refine as the forest grows.
    """
    vals = []

    e = pulses.get("earth")
    if e:
        # average of amplitude & phase
        vals.append(0.5 * (e["earth_amp"] + e["earth_phase"]))

    s = pulses.get("selflearn")
    if s:
        vals.append(s["selflearn_coherence"])  # already ~[0,1]

    c = pulses.get("crystal")
    if c:
        # Higher occupied ratio good; lower time_std good → map via sigmoid-ish
        occ = c["crystal_occupied"]
        tstd = c["crystal_time_std"]
        tterm = 1.0 / (1.0 + (tstd / 50.0 if np.isfinite(tstd) else 5.0))
        vals.append(0.5 * occ + 0.5 * tterm)

    if not vals:
        return 0.0
    # squash to [0,1) softly
    v = float(np.clip(np.mean(vals), 0.0, 1.0))
    return v

# ---------- Public API ----------
def run_once(cfg: AtlasConfig = AtlasConfig()) -> Dict[str, Any]:
    rng = np.random.default_rng(cfg.seed)

    pulses = {}
    pulses["earth"] = _earth_pulse(cfg, rng)
    pulses["selflearn"] = _selflearn_pulse(cfg, rng)
    pulses["crystal"] = _crystal_pulse(cfg, rng)

    # remove Nones
    pulses = {k: v for k, v in pulses.items() if v is not None}
    atlas_coh = _aggregate(pulses)
    return {"layers": pulses, "atlas_coherence": atlas_coh}

def run_steps(cfg: AtlasConfig = AtlasConfig(), steps: int = 5) -> Dict[str, Any]:
    """
    Repeat run_once() to get a short series; useful for dashboards.
    """
    series = []
    for _ in range(steps):
        out = run_once(cfg)
        series.append(out["atlas_coherence"])
    return {"series": series, "mean": float(np.mean(series)), "std": float(np.std(series))}
