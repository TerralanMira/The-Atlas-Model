#!/usr/bin/env python3
"""
dashboard/page_overlays_live.py — Live Overlay Composer (with Archetypes)
---------------------------------------------------------------------------
Composes:
  TL: Geometry (coherence → hex)
  TR: Plasma ripples (series → field)
  BL: Hybrid blend
  BR: Hybrid + resonant + archetype tint & symbols

Usage:
  python -m dashboard.page_overlays_live --archetype Seer \
      --coh logs/coherence_matrix.npy \
      --series logs/timeseries.csv \
      --out docs/assets/dashboard/overlays_live.png
"""

from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

from dashboard.base import Canvas, GridLayout, Panel
from dashboard.overlays import stamp_resonant_overlay
from algorithms.resonant_overlays import project_coherence_to_hex, ripple_from_timeseries
from algorithms.archetypes import ARCHETYPES, tint_image, stamp_symbols


def _load_coherence(path: Path | None, N: int = 24) -> np.ndarray:
    if path and path.exists():
        return np.load(path)
    rng = np.random.default_rng(5)
    A = rng.random((N, N)); C = 0.5*(A + A.T); np.fill_diagonal(C, 1.0)
    return C

def _load_series(path: Path | None, L: int = 120) -> np.ndarray:
    if path and path.exists():
        if path.suffix.lower() == ".npy":
            return np.load(path)
        import csv
        vals = []
        with open(path, "r", newline="") as f:
            for row in csv.reader(f):
                try: vals.append(float(row[0]))
                except: pass
        if vals: return np.array(vals, dtype=float)
    t = np.linspace(0, 2*np.pi, L, endpoint=False)
    return 0.6 + 0.25*np.sin(2.1*t) + 0.15*np.sin(5.3*t + 0.7)

def build_overlays_live(coh_path: str | None = None,
                        series_path: str | None = None,
                        archetype: str = "Seer",
                        out_path: str | Path = "docs/assets/dashboard/overlays_live.png") -> str:
    C = _load_coherence(Path(coh_path) if coh_path else None)
    s = _load_series(Path(series_path) if series_path else None)

    geo = project_coherence_to_hex(C, rings=3, canvas=(320, 320))
    rip = ripple_from_timeseries(s, canvas=(320, 320), waves=3, dispersion=0.22)
    hybrid = (0.55*geo + 0.45*rip)

    # compose
    cv = Canvas(width=1400, height=900, dpi=110, bgcolor="white")
    grid = GridLayout(2, 2, pad=16)

    p1 = Panel(title="Geometry from Coherence (Hex Projection)")
    p2 = Panel(title="Plasma Ripples from Time-Series")
    p3 = Panel(title="Hybrid Blend (Geometry × Plasma)")
    p4 = Panel(title=f"Hybrid + Resonant + Archetype — {archetype}")

    cv.attach(grid.place(p1, 0, 0))
    cv.attach(grid.place(p2, 0, 1))
    cv.attach(grid.place(p3, 1, 0))
    cv.attach(grid.place(p4, 1, 1))

    # TL/TR/BL
    for ax, img, title in [(p1.ax, geo, p1.title),
                           (p2.ax, rip, p2.title),
                           (p3.ax, hybrid, p3.title)]:
        im = ax.imshow(img, origin="lower", aspect="equal")
        ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        ax.set_title(title, fontsize=11, pad=8); ax.set_xlabel("x"); ax.set_ylabel("y")

    # BR: archetype tint + resonant overlay + symbols
    spec = ARCHETYPES.get(archetype, ARCHETYPES["Seer"])
    tinted = tint_image(hybrid, spec["palette"])
    ax4 = p4.ax
    ax4.imshow(tinted[..., :3], origin="lower", aspect="equal")
    # resonance stamp
    stamp_resonant_overlay(ax4, grid_spacing=0.12, grid_angle=30.0,
                           fol_rings=2, fol_radius=0.26, rings_alpha=0.22)
    # symbol stamps at peaks (use underlying hybrid magnitude)
    stamp_symbols(ax4, hybrid, archetype, k=5)
    ax4.set_title(p4.title, fontsize=11, pad=8); ax4.set_xlabel("x"); ax4.set_ylabel("y")

    cv.save(out_path)
    return str(out_path)


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("--coh", type=str, default=None)
    ap.add_argument("--series", type=str, default=None)
    ap.add_argument("--archetype", type=str, default="Seer",
                    choices=list(ARCHETYPES.keys()))
    ap.add_argument("--out", type=str, default="docs/assets/dashboard/overlays_live.png")
    return ap.parse_args()


if __name__ == "__main__":
    args = parse_args()
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    out = build_overlays_live(args.coh, args.series, args.archetype, args.out)
    print("Wrote", out)
