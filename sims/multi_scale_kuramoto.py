#!/usr/bin/env python3
"""
sims/multi_scale_kuramoto.py

A schema-driven Kuramoto runner that reads sims/presets.json, constructs
topologies (grid, circular, nested_spheres, flower_of_life), supports
multi-group and multi-layer presets, optional ouroboros feedback, and
emits dashboard-friendly metrics per step.

Designed to align with:
- sims/presets.json  (schema v1.0.0 with meta.defaults + presets)
- dashboard overlays expecting columns like:
  step,t,R_total,cross_sync,drift,C,Delta,Phi
- ethics flags for logging context: offer_two_paths, consent_to_log

If optional helpers are missing from algorithms/, local fallbacks are used.
"""

from __future__ import annotations
import argparse, json, math, os, csv
from dataclasses import dataclass
from typing import Dict, Any, Optional, Tuple, List

import numpy as np

# ──────────────────────────────────────────────────────────────────────────────
# Optional imports (fallbacks if not present)
# ──────────────────────────────────────────────────────────────────────────────
try:
    from algorithms.coherence_metrics import phase_coherence, local_coherence
except Exception:
    def phase_coherence(phases: np.ndarray) -> float:
        return float(np.abs(np.exp(1j * phases).mean()))

    def local_coherence(phases: np.ndarray, adjacency: np.ndarray) -> float:
        A = np.maximum(adjacency, adjacency.T)
        I, J = np.where(A > 0)
        if I.size == 0:
            return 0.0
        return float(np.cos(phases[J] - phases[I]).mean())

try:
    from algorithms.field_equations import wrap_phase
except Exception:
    def wrap_phase(theta: np.ndarray) -> np.ndarray:
        return np.mod(theta + np.pi, 2.0 * np.pi) - np.pi

TAU = 2.0 * math.pi

# ──────────────────────────────────────────────────────────────────────────────
# Utilities
# ──────────────────────────────────────────────────────────────────────────────

def ensure_dir(p: str) -> None:
    d = os.path.dirname(p)
    if d and not os.path.exists(d):
        os.makedirs(d, exist_ok=True)

def complex_mean_angle(ang: np.ndarray) -> float:
    z = np.exp(1j * ang).mean()
    return float(np.angle(z))

def cross_edge_sync(A: np.ndarray, theta: np.ndarray) -> float:
    A = np.maximum(A, A.T)
    I, J = np.where(A > 0)
    if I.size == 0:
        return 0.0
    d = theta[J] - theta[I]
    return float((np.cos(d).mean() + 1.0) * 0.5)

def phase_entropy_norm(theta: np.ndarray, bins: int = 36) -> float:
    h, _ = np.histogram(np.mod(theta, TAU), bins=bins, range=(0.0, TAU))
    p = h.astype(float)
    s = p.sum()
    if s == 0:
        return 0.0
    p /= s
    with np.errstate(divide="ignore", invalid="ignore"):
        ent = -(p * np.log(p + 1e-12)).sum()
    return float(ent / math.log(bins))

def lag1_smoothness(theta_now: np.ndarray, theta_prev: np.ndarray) -> float:
    dphi = np.angle(np.exp(1j * (theta_now - theta_prev)))
    return float((np.cos(dphi).mean() + 1.0) * 0.5)

def gaussian_omega(n: int, mean: float = 0.0, std: float = 0.1, seed: Optional[int] = None) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.normal(mean, std, size=n).astype(float)

def harmonic_scale_omega(n: int, scale: List[int] | List[float], seed: Optional[int] = None) -> np.ndarray:
    """Assign base frequencies from a small harmonic set (cycled)."""
    rng = np.random.default_rng(seed)
    base = np.array(scale, dtype=float)
    vals = np.tile(base, int(np.ceil(n / len(base))))[:n]
    # small jitter to avoid perfect degeneracy
    vals = vals + rng.normal(0.0, 0.01, size=n)
    return vals.astype(float)

def spiral_mapping_omega(n: int, turns: float = 2.0, std: float = 0.05, seed: Optional[int] = None) -> np.ndarray:
    """Map natural frequencies along a spiral in freq space."""
    rng = np.random.default_rng(seed)
    t = np.linspace(0.0, 1.0, n)
    base = turns * t
    return (base + rng.normal(0.0, std, size=n)).astype(float)

# ──────────────────────────────────────────────────────────────────────────────
# Geometries (adjacency & coordinates as needed)
# ──────────────────────────────────────────────────────────────────────────────

def adjacency_grid(rows: int, cols: int, diagonal: bool = False) -> np.ndarray:
    N = rows * cols
    A = np.zeros((N, N), float)
    def idx(r, c): return r * cols + c
    for r in range(rows):
        for c in range(cols):
            i = idx(r, c)
            for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
                rr, cc = r + dr, c + dc
                if 0 <= rr < rows and 0 <= cc < cols:
                    j = idx(rr, cc)
                    A[i, j] = A[j, i] = 1.0
            if diagonal:
                for dr, dc in [(1,1), (1,-1), (-1,1), (-1,-1)]:
                    rr, cc = r + dr, c + dc
                    if 0 <= rr < rows and 0 <= cc < cols:
                        j = idx(rr, cc)
                        A[i, j] = A[j, i] = 1.0
    return A

def adjacency_circular(nodes: int) -> np.ndarray:
    N = nodes
    A = np.zeros((N, N), float)
    for i in range(N):
        j1 = (i + 1) % N
        j2 = (i - 1 + N) % N
        A[i, j1] = A[j1, i] = 1.0
        A[i, j2] = A[j2, i] = 1.0
    return A

def adjacency_nested_spheres(layer_sizes: List[int], inter_strength: float = 0.2) -> np.ndarray:
    """Block adjacency: each layer ring-connected; inter-layer radial links."""
    n_total = sum(layer_sizes)
    A = np.zeros((n_total, n_total), float)
    offset = 0
    anchors = []
    for size in layer_sizes:
        # ring inside each layer
        for i in range(size):
            j1 = (i + 1) % size
            A[offset + i, offset + j1] = 1.0
            A[offset + j1, offset + i] = 1.0
        anchors.append(offset)     # pick node 0 of each layer as "radial" anchor
        offset += size
    # radial couplings between anchors
    for a, b in zip(anchors[:-1], anchors[1:]):
        A[a, b] = A[b, a] = inter_strength
    return A

def adjacency_flower_of_life(rings: int = 3) -> np.ndarray:
    """
    Approximate Flower-of-Life lattice:
    - One center + hexagonal rings (6, 12, 18, ...) up to 'rings'
    - Connect near neighbors within a distance threshold.
    """
    coords = []
    coords.append((0.0, 0.0))  # center
    # hex rings at integer radii; each ring has 6*k nodes
    for k in range(1, rings + 1):
        m = 6 * k
        for j in range(m):
            angle = 2.0 * math.pi * (j / m)
            x = k * math.cos(angle)
            y = k * math.sin(angle)
            coords.append((x, y))
    pts = np.array(coords, dtype=float)
    N = len(coords)
    A = np.zeros((N, N), float)
    # connect nodes within ~1.05 distance (hex-neighbor approx)
    for i in range(N):
        for j in range(i + 1, N):
            d = np.linalg.norm(pts[i] - pts[j])
            if d <= 1.05 + 1e-9:
                A[i, j] = A[j, i] = 1.0
    return A

def make_adjacency(geom: Dict[str, Any]) -> np.ndarray:
    name = geom.get("name", "grid")
    if name == "grid":
        return adjacency_grid(int(geom.get("rows", 8)), int(geom.get("cols", 8)), bool(geom.get("diagonal", False)))
    if name == "circular":
        return adjacency_circular(int(geom.get("nodes", 64)))
    if name == "nested_spheres":
        # layer sizes are implied by preset; we set a reasonable default
        # this will be overridden by multi-layer builder if provided
        return adjacency_nested_spheres([30, 60, 120, 240], inter_strength=0.2)
    if name == "flower_of_life":
        return adjacency_flower_of_life(int(geom.get("rings", 3)))
    raise ValueError(f"Unknown geometry: {name}")

# ──────────────────────────────────────────────────────────────────────────────
# Dynamics
# ──────────────────────────────────────────────────────────────────────────────

def step_kuramoto(theta: np.ndarray, omega: np.ndarray, K: float, A: np.ndarray,
                  dt: float, noise_std: float = 0.0, rng: Optional[np.random.Generator] = None,
                  feedback: Optional[Dict[str, Any]] = None) -> np.ndarray:
    if rng is None:
        rng = np.random.default_rng()
    A_sym = np.maximum(A, A.T)
    dtheta = omega.copy()
    # coupling term
    for i in range(len(theta)):
        dtheta[i] += K * np.sum(A_sym[i] * np.sin(theta - theta[i]))
    # optional feedback (ouroboros style)
    if feedback and feedback.get("type") == "ouroboros":
        gain = float(feedback.get("gain", 0.1))
        mean_ang = complex_mean_angle(theta)
        dtheta += gain * np.angle(np.exp(1j * (mean_ang - theta)))
    # noise
    if noise_std > 0.0:
        dtheta += rng.normal(0.0, noise_std, size=len(theta))
    theta_next = wrap_phase(theta + dt * dtheta)
    return theta_next

# ──────────────────────────────────────────────────────────────────────────────
# Preset loading and omega assignment
# ──────────────────────────────────────────────────────────────────────────────

def load_presets(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def pick_preset(blob: Dict[str, Any], name: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    meta = blob.get("meta", {})
    defaults = meta.get("defaults", {})
    presets = blob.get("presets", {})
    if name not in presets:
        raise KeyError(f"Preset '{name}' not found. Available: {list(presets.keys())}")
    return defaults, presets[name]

def build_omega(N: int, spec: Dict[str, Any], seed: Optional[int] = None) -> np.ndarray:
    dist = spec.get("distribution", "gaussian")
    if dist == "gaussian":
        return gaussian_omega(N, float(spec.get("mean", 0.0)), float(spec.get("std", 0.1)), seed)
    if dist == "harmonic_scale":
        return harmonic_scale_omega(N, spec.get("scale", [1,2,3,5,8]), seed)
    if dist == "spiral_mapping":
        return spiral_mapping_omega(N, float(spec.get("turns", 2.0)), float(spec.get("std", 0.05)), seed)
    raise ValueError(f"Unknown omega distribution: {dist}")

# ──────────────────────────────────────────────────────────────────────────────
# Builders for different preset styles
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class SimConfig:
    steps: int
    dt: float
    K: float
    noise_std: float
    seed: int
    output_csv: str
    offer_two_paths: bool
    consent_to_log: bool

def build_from_basic(preset: Dict[str, Any], defaults: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray, np.ndarray, SimConfig, Dict[str, Any]]:
    geom = preset.get("geometry", {"name": "grid"})
    A = make_adjacency(geom)
    N = int(preset.get("num_oscillators", A.shape[0]))
    # if A size doesn't match N, pad/truncate naively
    if A.shape[0] != N:
        # rebuild reasonable grid
        A = make_adjacency({"name": "grid", "rows": int(math.sqrt(N)) or 1, "cols": max(1, N // max(1, int(math.sqrt(N))))})
    omega = build_omega(N, preset.get("omega", {"distribution": "gaussian"}), seed=preset.get("seed", defaults.get("seed", 0)))
    theta0 = wrap_phase(np.random.default_rng(preset.get("seed", 0)).uniform(-math.pi, math.pi, size=N))
    cfg = SimConfig(
        steps=int(preset.get("steps", defaults.get("steps", 4000))),
        dt=float(preset.get("dt", defaults.get("dt", 0.01))),
        K=float(preset.get("coupling_strength", 0.5)),
        noise_std=float(preset.get("noise_std", defaults.get("noise_std", 0.0))),
        seed=int(preset.get("seed", defaults.get("seed", 0))),
        output_csv=str(preset.get("output_csv", defaults.get("output_csv", "logs/run.csv"))),
        offer_two_paths=bool(preset.get("offer_two_paths", defaults.get("offer_two_paths", True))),
        consent_to_log=bool(preset.get("consent_to_log", defaults.get("consent_to_log", True))),
    )
    return A, omega, theta0, cfg, {"feedback": preset.get("feedback")}

def build_from_groups(preset: Dict[str, Any], defaults: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray, np.ndarray, SimConfig, Dict[str, Any]]:
    groups: List[Dict[str, Any]] = preset.get("groups", [])
    if not groups:
        raise ValueError("Preset with groups requires 'groups' array.")

    sizes = [int(g.get("size", 0)) for g in groups]
    N = int(np.sum(sizes))
    # geometry: use provided or build grid with N close to rectangular
    geom = preset.get("geometry", {"name": "grid", "rows": int(math.sqrt(N)) or 1, "cols": max(1, N // max(1, int(math.sqrt(N))))})
    A = make_adjacency(geom)

    # per-group omega, concatenate
    rng_seed = preset.get("seed", defaults.get("seed", 0))
    parts = []
    for g in groups:
        parts.append(build_omega(int(g.get("size", 0)), g.get("omega", {"distribution": "gaussian"}), seed=rng_seed))
        rng_seed += 1
    omega = np.concatenate(parts)

    # effective K: blend group couplings using choice/mixing if provided
    Ks = [float(g.get("coupling_strength", 0.5)) for g in groups]
    choice = float(preset.get("choice_parameter", 0.5))
    if len(Ks) == 2:
        K_eff = Ks[0] * (1.0 - choice) + Ks[1] * choice
    else:
        K_eff = float(np.mean(Ks))

    # add weak inter-group edges depending on mixing prob
    mix = preset.get("mixing", {"type": "bipartite_edges", "prob": 0.2})
    if mix.get("type") == "bipartite_edges" and len(groups) == 2:
        prob = float(mix.get("prob", 0.2))
        rng = np.random.default_rng(rng_seed + 777)
        # map indices
        idxA = np.arange(0, sizes[0])
        idxB = np.arange(sizes[0], sizes[0] + sizes[1])
        for i in idxA:
            # connect with probability to random B
            if rng.random() < prob:
                j = int(rng.choice(idxB))
                A[i, j] = A[j, i] = 1.0

    theta0 = wrap_phase(np.random.default_rng(preset.get("seed", 0)).uniform(-math.pi, math.pi, size=N))
    cfg = SimConfig(
        steps=int(preset.get("steps", defaults.get("steps", 4000))),
        dt=float(preset.get("dt", defaults.get("dt", 0.01))),
        K=float(K_eff),
        noise_std=float(preset.get("noise_std", defaults.get("noise_std", 0.0))),
        seed=int(preset.get("seed", defaults.get("seed", 0))),
        output_csv=str(preset.get("output_csv", defaults.get("output_csv", "logs/run.csv"))),
        offer_two_paths=bool(preset.get("offer_two_paths", defaults.get("offer_two_paths", True))),
        consent_to_log=bool(preset.get("consent_to_log", defaults.get("consent_to_log", True))),
    )
    return A, omega, theta0, cfg, {"feedback": preset.get("feedback")}

def build_from_layers(preset: Dict[str, Any], defaults: Dict[str, Any]) -> Tuple[np.ndarray, np.ndarray, np.ndarray, SimConfig, Dict[str, Any]]:
    layers: List[Dict[str, Any]] = preset.get("layers", [])
    if not layers:
        raise ValueError("Preset with layers requires 'layers' array.")

    sizes = [int(L.get("size", 0)) for L in layers]
    N = int(np.sum(sizes))
    A = adjacency_nested_spheres(sizes, inter_strength=float(preset.get("interlayer_coupling", {}).get("strength", 0.2)))

    # compose omega per layer
    rng_seed = preset.get("seed", defaults.get("seed", 0))
    parts = []
    Ks = []
    for L in layers:
        parts.append(build_omega(int(L.get("size", 0)), L.get("omega", {"distribution": "gaussian"}), seed=rng_seed))
        Ks.append(float(L.get("K", 0.5)))
        rng_seed += 1
    omega = np.concatenate(parts)
    K_eff = float(np.mean(Ks)) if Ks else 0.5

    theta0 = wrap_phase(np.random.default_rng(preset.get("seed", 0)).uniform(-math.pi, math.pi, size=N))
    cfg = SimConfig(
        steps=int(preset.get("steps", defaults.get("steps", 4000))),
        dt=float(preset.get("dt", defaults.get("dt", 0.01))),
        K=float(K_eff),
        noise_std=float(preset.get("noise_std", defaults.get("noise_std", 0.0))),
        seed=int(preset.get("seed", defaults.get("seed", 0))),
        output_csv=str(preset.get("output_csv", defaults.get("output_csv", "logs/run.csv"))),
        offer_two_paths=bool(preset.get("offer_two_paths", defaults.get("offer_two_paths", True))),
        consent_to_log=bool(preset.get("consent_to_log", defaults.get("consent_to_log", True))),
    )
    return A, omega, theta0, cfg, {"feedback": preset.get("feedback")}

# ──────────────────────────────────────────────────────────────────────────────
# Runner
# ──────────────────────────────────────────────────────────────────────────────

def run_from_preset(preset_name: str, presets_path: str) -> None:
    blob = load_presets(presets_path)
    defaults, preset = pick_preset(blob, preset_name)

    engine = str(preset.get("engine", defaults.get("engine", "kuramoto")))

    # Build model state
    if "groups" in preset:
        A, omega, theta, cfg, extra = build_from_groups(preset, defaults)
    elif "layers" in preset and preset.get("geometry", {}).get("name") != "grid":
        # if explicit multi-layer semantic model
        A, omega, theta, cfg, extra = build_from_layers(preset, defaults)
    else:
        A, omega, theta, cfg, extra = build_from_basic(preset, defaults)

    feedback = extra.get("feedback")

    # Prepare writer
    ensure_dir(cfg.output_csv)
    header = [
        "preset","step","t",
        "R_total","cross_sync","drift","C","Delta","Phi",
        "offer_two_paths","consent_to_log"
    ]
    f = open(cfg.output_csv, "w", newline="")
    writer = csv.writer(f)
    writer.writerow(header)

    rng = np.random.default_rng(cfg.seed)
    theta_prev = theta.copy()

    # Integrate
    for k in range(cfg.steps):
        t = (k + 1) * cfg.dt
        theta_next = step_kuramoto(theta, omega, cfg.K, A, dt=cfg.dt, noise_std=cfg.noise_std, rng=rng, feedback=feedback)

        # Metrics
        R_total = phase_coherence(theta_next)
        cross   = cross_edge_sync(A, theta_next)
        drift   = float(np.mean(np.abs(np.angle(np.exp(1j * (theta_next - theta))))))
        C_raw   = local_coherence(theta_next, np.maximum(A, A.T))
        C_m01   = float((C_raw + 1.0) * 0.5)  # map [-1,1] → [0,1]
        Delta   = phase_entropy_norm(theta_next)
        Phi     = lag1_smoothness(theta_next, theta)

        writer.writerow([
            preset_name, k + 1, t,
            R_total, cross, drift, C_m01, Delta, Phi,
            int(cfg.offer_two_paths), int(cfg.consent_to_log)
        ])

        theta_prev = theta
        theta = theta_next

    f.close()

# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Multi-scale Kuramoto — schema-driven simulator")
    ap.add_argument("--preset", type=str, default="default", help="Preset name in presets.json")
    ap.add_argument("--presets-file", type=str, default="sims/presets.json", help="Path to presets JSON")
    return ap.parse_args()

def main():
    args = parse_args()
    run_from_preset(args.preset, args.presets_file)

if __name__ == "__main__":
    main()
