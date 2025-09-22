#!/usr/bin/env python3
"""
dashboard/page_awareness.py — Awareness Page Composer
-----------------------------------------------------
Renders a single page showing:
  TL: Base awareness seed
  TR: Ouroboric awareness (cycled sequence)
  BL: Modulation on a flow (water/air) potential map
  BR: Modulation on a charge (plasma) map + overlay

Usage:
  python -m dashboard.page_awareness --out docs/assets/dashboard/awareness_page.png
"""

from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np

from dashboard.base import Canvas, GridLayout, Panel
from dashboard.overlays import stamp_resonant_overlay
from dashboard import fields
from dashboard import awareness as A


def build_awareness_page(out_path: str | Path = "docs/assets/dashboard/awareness_page.png") -> str:
    H = W = 96
    base = A.awareness_from_seed(H, W, seed=11)
    cyc  = A.awareness_cycle(base, rounds=3)

    # targets to modulate
    height = fields.synthetic_height(H, W, freq=8.0)
    charge = fields.synthetic_charge(H, W)

    flow_mod    = A.modulate(height, focus="flow", intensity=0.18)
    plasma_mod  = A.modulate(charge,  focus="threshold", intensity=0.22)

    cv = Canvas(width=1400, height=900, dpi=110, bgcolor="white")
    grid = GridLayout(rows=2, cols=2, pad=16)

    p1 = Panel(title="Awareness — Base Seed")
    p2 = Panel(title="Awareness — Ouroboric Cycle")
    p3 = Panel(title="Water/Air — Flow Potential (modulated)")
    p4 = Panel(title="Plasma — Charge (modulated) + Resonant Overlay")

    cv.attach(grid.place(p1, 0, 0))
    cv.attach(grid.place(p2, 0, 1))
    cv.attach(grid.place(p3, 1, 0))
    cv.attach(grid.place(p4, 1, 1))

    # draw
    from dashboard.awareness import draw_awareness as drawA
    drawA(p1.ax, base, title=p1.title)
    drawA(p2.ax, cyc,  title=p2.title)

    # show flow/crystal compatible views by reusing field renderers
    fields.draw_awareness_heat(p3.ax, flow_mod, title=p3.title)
    fields.draw_awareness_heat(p4.ax, plasma_mod, title=None)
    stamp_resonant_overlay(p4.ax, grid_spacing=0.12, grid_angle=30.0, fol_rings=2, fol_radius=0.27)

    cv.save(out_path)
    return str(out_path)


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=str, default="docs/assets/dashboard/awareness_page.png")
    return ap.parse_args()


if __name__ == "__main__":
    args = parse_args()
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    out = build_awareness_page(args.out)
    print("Wrote", out)
