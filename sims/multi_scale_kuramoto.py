#!/usr/bin/env python3
"""
sims/multi_scale_kuramoto.py

Multi-scale Kuramoto runner with relational awareness signals:
  - C   : coherence (cross-edge synchrony)                ∈ [0,1]
  - Delta: difference kept alive (phase-entropy diversity) ∈ [0,1]
  - Phi : flow (lag-1 circular smoothness)                ∈ [0,1]

Also logs:
  R_total, R_mean, cross_sync, drift, ready, choice_score,
  offer_two_paths, consent_to_log

Presets are read from sims/presets.json (optional); built-ins provided.

MIT License.
"""
from __future__ import annotations
import argparse
import csv
import json
import math
import os
from dataclasses import dataclass
from typing import Optional, Tuple

import numpy as np

from algorithms.field_equations import (
    kuramoto_step, order_parameter, wrap_phase,
    adjacency_circle6_center, adjacency_grid
)
from algorithms.resonance_dynamics import (
    collapse_signal, collapse_decision, HarmonicGate, gated_params
)

TAU = 2.0 * math.pi


# ──────────────────────────────────────────────────────────────────────────────
# Utility metrics (pure NumPy)
# ──────────────────────────────────────────────────────────────────────────────

def cross_edge_sync(A: np.ndarray, theta: np.ndarray) -> float:
    """Mean cos(θ_j - θ_i) over edges, mapped to [0,1]."""
    A = np.maximum(A, A.T)
    I, J = np.where(A > 0)
    if I.size == 0:
        return 0.0
    d = theta[J] - theta[I]
    return float((np.cos(d).mean() + 1.0) * 0.5)

def phase_entropy_norm(theta: np.ndarray, bins: int = 36) -> float:
    """Normalized histogram entropy of phases in [0,1]; 1=diverse, 0=clamped."""
    h, _ = np.histogram(np.mod(theta, TAU), bins=bins, range=(0.0, TAU))
    p = h.astype(float)
    if p.sum() == 0:
        return 0.0
    p /= p.sum()
    with np.errstate(divide="ignore", invalid="ignore"):
        ent = -(p * np.log(p + 1e-12)).sum()
    return float(ent / math.log(bins))

def lag1_circular_smoothness(theta_now: np.ndarray, theta_prev: np.ndarray) -> float:
    """
    Φ proxy: average cos(Δθ) across nodes (Δθ wrapped), mapped to [0,1].
    1.0 means very smooth evolution (small, coherent step), ~0 means jittery.
    """
    dphi = np.angle(np.exp(1j * (theta_now - theta_prev)))
    return float((np.cos(dphi).mean() + 1.0) * 0.5)


# ──────────────────────────────────────────────────────────────────────────────
# Presets
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class Preset:
    name: str
    geometry: str = "circle6_center"   # "circle6_center" | "grid"
    rows: int = 0
    cols: int = 0
    K: float = 0.85
    pi: float = 0.75
    offer_two_paths: bool = True
    consent_to_log: bool = True

def default_preset(name: str = "circle6_center") -> Preset:
    if name == "grid_rect":
        return Preset(name="grid_rect", geometry="grid", rows=8, cols=8, K=0.8, pi=0.7)
    return Preset(name="circle6_center", geometry="circle6_center", K=0.85, pi=0.75)

def load_preset(path: Optional[str], name: Optional[str]) -> Preset:
    if path and os.path.isfile(path):
        with open(path, "r") as f:
            data = json.load(f)
        # if presets.json contains an array of presets, find by name
        if isinstance(data, list):
            if not name:
                raise ValueError("When presets.json is a list, --preset <name> is required.")
            for p in data:
                if p.get("name") == name:
                    return Preset(**{
                        "name": p.get("name", name),
                        "geometry": p.get("geometry", "grid"),
                        "rows": p.get("rows", 0),
                        "cols": p.get("cols", 0),
                        "K": float(p.get("K", 0.8)),
                        "pi": float(p.get("pi", 0.7)),
                        "offer_two_paths": bool(p.get("offer_two_paths", True)),
                        "consent_to_log": bool(p.get("consent_to_log", True)),
                    })
            raise ValueError(f"Preset '{name}' not found in {path}")
        # otherwise accept a single dict preset
        return Preset(**{
            "name": data.get("name", name or "preset"),
            "geometry": data.get("geometry", "grid"),
            "rows": data.get("rows", 0),
            "cols": data.get("cols", 0),
            "K": float(data.get("K", 0.8)),
            "pi": float(data.get("pi", 0.7)),
            "offer_two_paths": bool(data.get("offer_two_paths", True)),
            "consent_to_log": bool(data.get("consent_to_log", True)),
        })
    # fall back to built-in
    return default_preset(name or "circle6_center")


# ──────────────────────────────────────────────────────────────────────────────
# Geometry & natural frequencies
# ──────────────────────────────────────────────────────────────────────────────

def make_adjacency(p: Preset) -> np.ndarray:
    if p.geometry == "circle6_center":
        return adjacency_circle6_center()
    if p.geometry == "grid":
        if p.rows <= 0 or p.cols <= 0:
            raise ValueError("grid geometry requires positive rows and cols")
        return adjacency_grid(p.rows, p.cols, diagonal=False)
    raise ValueError(f"Unknown geometry: {p.geometry}")

def make_omega(N: int, mean: float = 0.0, std: float = 0.1, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.normal(loc=mean, scale=std, size=N).astype(float)


# ──────────────────────────────────────────────────────────────────────────────
# Runner
# ──────────────────────────────────────────────────────────────────────────────

def run_sim(p: Preset, steps: int = 2000, dt: float = 0.01,
            csv_path: Optional[str] = None,
            seed: int = 0,
            gate: Optional[HarmonicGate] = None) -> None:
    A = make_adjacency(p)
    N = A.shape[0]

    rng = np.random.default_rng(seed)
    theta = np.mod(rng.uniform(0, TAU, size=N), TAU)
    omega = make_omega(N, std=0.1, seed=seed)

    # header
    header = [
        "step", "t",
        "R_total", "R_mean", "cross_sync", "drift",
        "C", "Delta", "Phi",
        "ready", "choice_score",
        "offer_two_paths", "consent_to_log"
    ]

    writer = None
    f = None
    if csv_path:
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        f = open(csv_path, "w", newline="")
        writer = csv.writer(f)
        writer.writerow(header)

    # initial previous state (for Φ)
    theta_prev = np.array(theta, copy=True)

    # optional gate
    gate = gate or HarmonicGate(ethics=1.0, ignition=1.0, destabilizer=0.0, time_gate=1.0)

    for k in range(steps):
        t = (k + 1) * dt

        # gate-adjusted params
        K_eff, pi_eff = gated_params(p.K, p.pi, gate=gate, t_step=k)

        # one step
        theta_next, metrics = kuramoto_step(theta, omega, K_eff, A, dt=dt)

        # primary metrics
        R_total = float(metrics["R_total"])
        cross   = float(metrics["cross_sync"])
        drift   = float(metrics["drift"])

        # relational measures
        C_val     = cross  # coherence across edges
        Delta_val = phase_entropy_norm(theta_next, bins=36)     # diversity
        Phi_val   = lag1_circular_smoothness(theta_next, theta) # flow

        # readiness & ethical collapse
        ready = collapse_signal(R_total, cross, drift)
        choice_ok = collapse_decision(
            ready=ready,
            consent=bool(p.consent_to_log),           # reusing consent flag here as example
            offer_two_paths=bool(p.offer_two_paths),
            thresh=0.70
        )
        choice_score = 1.0 if choice_ok else 0.0

        # write row
        if writer:
            writer.writerow([
                k + 1, t,
                R_total, R_total, cross, drift,
                C_val, Delta_val, Phi_val,
                ready, choice_score,
                int(p.offer_two_paths), int(p.consent_to_log)
            ])

        # advance
        theta_prev[:] = theta
        theta = theta_next

    if f:
        f.close()


# ──────────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Multi-scale Kuramoto with relational signals (C, Δ, Φ)")
    ap.add_argument("--presets", type=str, default="sims/presets.json",
                    help="Path to presets.json (optional).")
    ap.add_argument("--preset", type=str, default="circle6_center",
                    help="Preset name (e.g., circle6_center, grid_rect).")
    ap.add_argument("--steps", type=int, default=2000, help="Simulation steps.")
    ap.add_argument("--dt", type=float, default=0.01, help="Time step.")
    ap.add_argument("--K", type=float, default=None, help="Override coupling K ∈ [0,1].")
    ap.add_argument("--pi", type=float, default=None, help="Override permeability π ∈ [0,1].")
    ap.add_argument("--csv", type=str, default="logs/run.csv", help="Output CSV path.")
    ap.add_argument("--seed", type=int, default=0, help="Random seed.")
    ap.add_argument("--no-two-paths", action="store_true", help="Disable reversible options.")
    ap.add_argument("--no-consent", action="store_true", help="Disable consent flag.")
    ap.add_argument("--destabilizer", type=float, default=0.0, help="Gate noise proportion (small).")
    return ap.parse_args()

def main():
    args = parse_args()
    p = load_preset(args.presets, args.preset)

    # CLI overrides
    if args.K is not None:
        p.K = float(args.K)
    if args.pi is not None:
        p.pi = float(args.pi)
    if args.no_two_paths:
        p.offer_two_paths = False
    if args.no_consent:
        p.consent_to_log = False

    gate = HarmonicGate(
        ethics=1.0,
        ignition=1.0,
        destabilizer=max(0.0, float(args.destabilizer)),
        time_gate=1.0
    )

    run_sim(
        p=p,
        steps=int(args.steps),
        dt=float(args.dt),
        csv_path=args.csv,
        seed=int(args.seed),
        gate=gate
    )

if __name__ == "__main__":
    main()
