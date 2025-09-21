#!/usr/bin/env python3
"""
sims/breath_cycle.py

Breath-modulated resonance runner.
- Modulates coupling K(t) (and optional permeability π(t)) over an inhale/exhale cycle
  using cosine easing (smooth start/stop).
- Emits dashboard-aligned metrics per step:
  R_total, cross_sync, drift, C, Delta, Phi, plus ethics flags.
- Geometry adapters: grid, circular, nested_spheres, flower_of_life.

Matches schema keys used in sims/presets.json (e.g., 'breath_flower' preset).
If algorithms/ helpers are absent, safe fallbacks are used.

Usage:
  python sims/breath_cycle.py --preset breath_flower --presets-file sims/presets.json
"""

from __future__ import annotations
import argparse, json, math, os, csv
from typing import Dict, Any, Optional, List, Tuple
import numpy as np

# ──────────────────────────────────────────────────────────────────────────────
# Optional imports (fallbacks if repo-local modules missing)
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
# Small utilities
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

# ──────────────────────────────────────────────────────────────────────────────
# Geometries
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
    n_total = sum(layer_sizes)
    A = np.zeros((n_total, n_total), float)
    offset = 0
    anchors = []
    for size in layer_sizes:
        for i in range(size):
            j1 = (i + 1) % size
            A[offset + i, offset + j1] = 1.0
            A[offset + j1, offset + i] = 1.0
        anchors.append(offset)
        offset += size
    for a, b in zip(anchors[:-1], anchors[1:]):
        A[a, b] = A[b, a] = inter_strength
    return A

def adjacency_flower_of_life(rings: int = 3) -> np.ndarray:
    coords = [(0.0, 0.0)]
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
    for i in range(N):
        for j in range(i + 1, N):
            d = np.linalg.norm(pts[i] - pts[j])
            if d <= 1.05 + 1e-9:
                A[i, j] = A[j, i] = 1.0
    return A

def make_adjacency(geom: Dict[str, Any], fallback_n: int | None = None) -> np.ndarray:
    name = geom.get("name", "grid")
    if name == "grid":
        return adjacency_grid(int(geom.get("rows", 8)), int(geom.get("cols", 8)), bool(geom.get("diagonal", False)))
    if name == "circular":
        return adjacency_circular(int(geom.get("nodes", fallback_n or 64)))
    if name == "nested_spheres":
        return adjacency_nested_spheres([30, 60, 120, 240], inter_strength=0.2)
    if name == "flower_of_life":
        return adjacency_flower_of_life(int(geom.get("rings", 3)))
    raise ValueError(f"Unknown geometry: {name}")

# ──────────────────────────────────────────────────────────────────────────────
# Breath profile
# ──────────────────────────────────────────────────────────────────────────────
def cosine_ease_01(x: float) -> float:
    """0..1 → 0..1 with smooth start/end (cosine)."""
    return 0.5 - 0.5 * math.cos(math.pi * max(0.0, min(1.0, x)))

def breath_envelope(t: float, period: float, inhale_ratio: float) -> float:
    """
    Returns e(t) in [0,1].
    0..T*inhale_ratio → inhale ramp up
    T*inhale_ratio..T → exhale ramp down
    """
    T = period
    Ti = max(1e-9, inhale_ratio) * T
    t_mod = t % T
    if t_mod <= Ti:  # inhale
        return cosine_ease_01(t_mod / Ti)
    # exhale
    return 1.0 - cosine_ease_01((t_mod - Ti) / max(1e-9, T - Ti))

def K_over_time(K_min: float, K_max: float, t: float, period: float, inhale_ratio: float) -> float:
    e = breath_envelope(t, period, inhale_ratio)
    return (1.0 - e) * K_min + e * K_max

# ──────────────────────────────────────────────────────────────────────────────
# Preset loading
# ──────────────────────────────────────────────────────────────────────────────
def load_presets(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def pick_preset(blob: Dict[str, Any], name: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    # supports both schema’d (meta/defaults/presets) and simple (top-level dict) files
    if "presets" in blob:
        meta = blob.get("meta", {})
        defaults = meta.get("defaults", {})
        presets = blob["presets"]
        if name not in presets:
            raise KeyError(f"Preset '{name}' not found. Available: {list(presets.keys())}")
        return defaults, presets[name]
    else:
        if name not in blob:
            raise KeyError(f"Preset '{name}' not found. Available: {list(blob.keys())}")
        return {}, blob[name]

# ──────────────────────────────────────────────────────────────────────────────
# Runner
# ──────────────────────────────────────────────────────────────────────────────
def run_breath_preset(preset_name: str, presets_path: str) -> None:
    blob = load_presets(presets_path)
    defaults, preset = pick_preset(blob, preset_name)

    # geometry
    geom = preset.get("geometry", {"name": "grid", "rows": 10, "cols": 10})
    N_hint = int(preset.get("num_oscillators", 64))
    A = make_adjacency(geom, fallback_n=N_hint)
    if A.shape[0] != N_hint:
        # if mismatch, rebuild simple grid close to N_hint
        side = int(max(1, round(math.sqrt(N_hint))))
        A = adjacency_grid(side, max(1, N_hint // max(1, side)))

    N = A.shape[0]

    # frequencies & initial phases
    omega_spec = preset.get("omega", {"distribution": "gaussian", "mean": 0.0, "std": 0.08})
    seed = int(preset.get("seed", defaults.get("seed", 0)))
    rng = np.random.default_rng(seed)
    omega = gaussian_omega(N, float(omega_spec.get("mean", 0.0)), float(omega_spec.get("std", 0.08)), seed)
    theta = wrap_phase(rng.uniform(-math.pi, math.pi, size=N))
    theta_prev = theta.copy()

    # breath params
    period = float(preset.get("period", defaults.get("period", 20.0)))
    inhale_ratio = float(preset.get("inhale_ratio", defaults.get("inhale_ratio", 0.5)))

    # K min/max (if only one provided, use ±20% band)
    K_base = float(preset.get("coupling_strength", 0.6))
    K_min = float(preset.get("K_min", K_base * 0.8))
    K_max = float(preset.get("K_max", K_base * 1.2))

    # numerics / IO
    steps = int(preset.get("steps", defaults.get("steps", 6000)))
    dt = float(preset.get("dt", defaults.get("dt", 0.01)))
    noise_std = float(preset.get("noise_std", defaults.get("noise_std", 0.002)))
    output_csv = str(preset.get("output_csv", defaults.get("output_csv", "logs/breath.csv")))

    # ethics context flags
    offer_two_paths = bool(preset.get("offer_two_paths", defaults.get("offer_two_paths", True)))
    consent_to_log  = bool(preset.get("consent_to_log",  defaults.get("consent_to_log",  True)))

    # writer
    ensure_dir(output_csv)
    header = ["preset","step","t","K_eff",
              "R_total","cross_sync","drift","C","Delta","Phi",
              "offer_two_paths","consent_to_log"]
    f = open(output_csv, "w", newline="")
    writer = csv.writer(f)
    writer.writerow(header)

    A_sym = np.maximum(A, A.T)

    for k in range(steps):
        t = (k + 1) * dt
        # breath-modulated K(t)
        K_t = K_over_time(K_min, K_max, t, period, inhale_ratio)

        # Kuramoto update with K(t)
        dtheta = omega.copy()
        # coupling term
        for i in range(N):
            dtheta[i] += K_t * np.sum(A_sym[i] * np.sin(theta - theta[i]))
        # noise
        if noise_std > 0.0:
            dtheta += rng.normal(0.0, noise_std, size=N)
        theta_next = wrap_phase(theta + dt * dtheta)

        # metrics
        R_total = phase_coherence(theta_next)
        cross   = cross_edge_sync(A_sym, theta_next)
        drift   = float(np.mean(np.abs(np.angle(np.exp(1j * (theta_next - theta))))))
        C_raw   = local_coherence(theta_next, A_sym)
        C_m01   = float((C_raw + 1.0) * 0.5)  # [-1,1] → [0,1]
        Delta   = phase_entropy_norm(theta_next)
        Phi     = lag1_smoothness(theta_next, theta)

        writer.writerow([preset_name, k + 1, t, K_t,
                         R_total, cross, drift, C_m01, Delta, Phi,
                         int(offer_two_paths), int(consent_to_log)])

        theta_prev = theta
        theta = theta_next

    f.close()

# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────
def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Breath-modulated resonance runner")
    ap.add_argument("--preset", type=str, default="breath_flower", help="Preset name in presets.json")
    ap.add_argument("--presets-file", type=str, default="sims/presets.json", help="Path to presets JSON")
    return ap.parse_args()

def main():
    args = parse_args()
    run_breath_preset(args.preset, args.presets_file)

if __name__ == "__main__":
    main()
