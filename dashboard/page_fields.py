#!/usr/bin/env python3
"""
dashboard/page_fields.py — Elemental Fields Page Composer
---------------------------------------------------------
Composes a ready-to-save dashboard image that shows:
  TL: Water/Air vector field (from scalar height → flow)
  TR: Plasma arcs (from charge map)
  BL: Crystal lattice
  BR: Awareness heatmap + optional resonant overlay

Consumes either provided arrays or falls back to synthetic examples.
Outputs a single PNG you can link from docs or MkDocs.

Usage (from repo root):
  python -m dashboard.page_fields --out docs/assets/dashboard/fields_page.png
"""

from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np

from dashboard.base import Canvas, GridLayout, Panel, plots
from dashboard.overlays import stamp_resonant_overlay
from dashboard import fields


def build_fields_page(height_map: np.ndarray | None = None,
                      charge_map: np.ndarray | None = None,
                      crystal_grid: np.ndarray | None = None,
                      awareness_map: np.ndarray | None = None,
                      out_path: str | Path = "docs/assets/dashboard/fields_page.png") -> str:
    # fallbacks
    H = W = 96
    if height_map is None:
        height_map = fields.synthetic_height(H, W, freq=7.0)
    if charge_map is None:
        charge_map = fields.synthetic_charge(H, W)
    if crystal_grid is None:
        crystal_grid = fields.synthetic_crystal(H, W, p=0.55)
    if awareness_map is None:
        awareness_map = fields.synthetic_awareness(H, W)

    # compute flow from height (water/air)
    u, v = fields.flow_from_height(height_map, smooth=1)

    # canvas + grid
    cv = Canvas(width=1400, height=900, dpi=110, bgcolor="white")
    grid = GridLayout(rows=2, cols=2, pad=16)

    p1 = Panel(title="Water/Air — Flow Field")
    p2 = Panel(title="Plasma — Discharge Arcs")
    p3 = Panel(title="Crystal — Lattice")
    p4 = Panel(title="Awareness — Heatmap + Resonant Overlay")

    cv.attach(grid.place(p1, 0, 0))
    cv.attach(grid.place(p2, 0, 1))
    cv.attach(grid.place(p3, 1, 0))
    cv.attach(grid.place(p4, 1, 1))

    # draw
    fields.draw_vector_field(p1.ax, u, v, step=2, scale=0.15)
    fields.draw_plasma_arcs(p2.ax, charge_map, threshold=0.70, jitter=0.35, rays=22)
    fields.draw_crystal_lattice(p3.ax, crystal_grid)
    fields.draw_awareness_heat(p4.ax, awareness_map)

    # stamp resonant overlay on awareness panel for beauty + alignment
    stamp_resonant_overlay(p4.ax, grid_spacing=0.12, grid_angle=30.0, fol_rings=2, fol_radius=0.28)

    cv.save(out_path)
    return str(out_path)


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=str, default="docs/assets/dashboard/fields_page.png")
    return ap.parse_args()


if __name__ == "__main__":
    args = parse_args()
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    out = build_fields_page(out_path=args.out)
    print("Wrote", out)
