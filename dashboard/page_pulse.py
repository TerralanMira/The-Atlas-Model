#!/usr/bin/env python3
"""
dashboard/page_pulse.py — Ouroboric Pulse Composer
--------------------------------------------------
Builds a page that visualizes the integrated loop:
  TL: Ouroboric pulse (atlas_coherence) line series
  TR: Layer contribution bars (normalized)
  BL: Threshold/ignition map (plasma)
  BR: Crystal stabilization snapshot

Consumes logs if present; otherwise uses synthetic fallbacks.
Outputs a single PNG to docs/assets.

Usage:
  python -m dashboard.page_pulse --out docs/assets/dashboard/pulse_page.png \
    --series logs/atlas_pulse/atlas_pulse_series.csv \
    --layers logs/atlas_pulse/atlas_pulse_layers.json
"""

from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np

from dashboard.base import Canvas, GridLayout, Panel, plots
from dashboard.overlays import stamp_resonant_overlay
from dashboard import fields


def _load_series(path: Path):
    if path.exists():
        # expects columns: step,atlas_coherence
        import pandas as pd
        df = pd.read_csv(path)
        return df["step"].values, df["atlas_coherence"].values
    # fallback synthetic
    xs = np.arange(60)
    ys = 0.6 + 0.2*np.sin(xs/6.0) + 0.05*np.sin(xs/2.5)
    return xs, ys


def _load_layer_means(path: Path):
    if not path.exists():
        labels = ["Water", "Air", "Plasma", "Crystal"]
        vals = np.array([0.45, 0.62, 0.53, 0.71])
        # normalize to [0,1]
        m, M = vals.min(), vals.max()
        vals = (vals - m) / (M - m + 1e-12)
        return labels, vals
    # expects JSON: {step: {layer: {metric: value, ...}, ...}, ...}
    J = json.loads(path.read_text())
    agg = {}
    for _step, layers in J.items():
        for lname, metrics in layers.items():
            nums = [float(v) for v in metrics.values() if isinstance(v, (int, float))]
            if not nums:
                continue
            agg.setdefault(lname, []).append(np.mean(nums))
    labels, vals = [], []
    for k, arr in agg.items():
        labels.append(k)
        vals.append(float(np.mean(arr)))
    vals = np.array(vals, dtype=float)
    # normalize
    m, M = np.nanmin(vals), np.nanmax(vals)
    vals = (vals - m) / (M - m + 1e-12)
    return labels, vals


def build_pulse_page(series_csv: Path | None = None,
                     layers_json: Path | None = None,
                     out_path: str | Path = "docs/assets/dashboard/pulse_page.png") -> str:
    series_csv = Path(series_csv) if series_csv else Path("logs/atlas_pulse/atlas_pulse_series.csv")
    layers_json = Path(layers_json) if layers_json else Path("logs/atlas_pulse/atlas_pulse_layers.json")

    xs, ys = _load_series(series_csv)
    labels, vals = _load_layer_means(layers_json)

    # plasma + crystal demo data (synthetic if no logs)
    charge = fields.synthetic_charge(96, 96)
    crystal = fields.synthetic_crystal(96, 96, p=0.55)

    cv = Canvas(width=1400, height=900, dpi=110, bgcolor="white")
    grid = GridLayout(rows=2, cols=2, pad=16)

    p1 = Panel(title="Ouroboric Pulse — Atlas Coherence")
    p2 = Panel(title="Layer Contribution (normalized)")
    p3 = Panel(title="Thresholds — Ignition Map")
    p4 = Panel(title="Stabilization — Crystal Snapshot")

    cv.attach(grid.place(p1, 0, 0))
    cv.attach(grid.place(p2, 0, 1))
    cv.attach(grid.place(p3, 1, 0))
    cv.attach(grid.place(p4, 1, 1))

    # TL: pulse
    plots.line(p1.ax, xs, ys, xlabel="Step", ylabel="Atlas Coherence")

    # TR: bars
    plots.bars(p2.ax, labels, vals, ylabel="Norm. Mean")

    # BL: plasma ignition (charge map + arcs)
    fields.draw_plasma_arcs(p3.ax, charge, threshold=0.72, rays=20)
    stamp_resonant_overlay(p3.ax, grid_spacing=0.14, grid_angle=22.5, fol_rings=1, fol_radius=0.22, rings_alpha=0.18)

    # BR: crystal lattice
    fields.draw_crystal_lattice(p4.ax, crystal)
    stamp_resonant_overlay(p4.ax, grid_spacing=0.12, grid_angle=30.0, fol_rings=2, fol_radius=0.25, rings_alpha=0.22)

    cv.save(out_path)
    return str(out_path)


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--series", type=str, default="logs/atlas_pulse/atlas_pulse_series.csv")
    ap.add_argument("--layers", type=str, default="logs/atlas_pulse/atlas_pulse_layers.json")
    ap.add_argument("--out", type=str, default="docs/assets/dashboard/pulse_page.png")
    return ap.parse_args()


if __name__ == "__main__":
    args = parse_args()
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    out = build_pulse_page(Path(args.series), Path(args.layers), args.out)
    print("Wrote", out)
