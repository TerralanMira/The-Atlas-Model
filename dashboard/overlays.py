#!/usr/bin/env python3
"""
dashboard/overlays.py — Resonant Overlays
-----------------------------------------

Geometric overlays to make the hum visible:
  • Flower of Life (FoL)
  • Harmonic Grid (rotated lattice)
  • Resonance Rings (concentric frequency bands)

All functions draw directly onto a provided matplotlib Axes.
No heavy deps beyond numpy/matplotlib.

Usage (with dashboard/base.py):
    from dashboard.base import Canvas, GridLayout, Panel
    from dashboard.overlays import draw_flower_of_life, draw_harmonic_grid, draw_resonance_rings

    cv = Canvas(width=1200, height=800)
    grid = GridLayout(2, 2, pad=16)
    p = Panel(title="Resonant Overlay")
    cv.attach(grid.place(p, 0, 0))
    cv.render()

    # Draw overlays on p.ax
    draw_harmonic_grid(p.ax, spacing=0.2, angle_deg=30, count=20, alpha=0.15)
    draw_flower_of_life(p.ax, cx=0.5, cy=0.5, base_r=0.25, rings=2, line_alpha=0.6)
    draw_resonance_rings(p.ax, cx=0.5, cy=0.5, radii=[0.12, 0.2, 0.32, 0.5], alpha=0.25)

    cv.save("docs/assets/dashboard/overlay_demo.png")
"""

from __future__ import annotations
import math
from typing import Iterable, Tuple, Optional, List

import numpy as np
import matplotlib
matplotlib.use("Agg")  # safe for headless
import matplotlib.pyplot as plt


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def _as_display(ax: plt.Axes):
    """
    Configure axis for overlay drawing on unit square [0,1]x[0,1].
    If current limits look like data bounds, we don't override them.
    """
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    # Heuristic: if limits are equal or default, set to [0,1]
    if not np.isfinite([x0, x1, y0, y1]).all() or (x0 == x1) or (y0 == y1):
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
    ax.set_aspect("equal", adjustable="box")


def _circle(ax: plt.Axes, cx: float, cy: float, r: float, lw: float = 1.0, alpha: float = 0.8, color: Optional[str] = None):
    theta = np.linspace(0, 2 * np.pi, 360)
    x = cx + r * np.cos(theta)
    y = cy + r * np.sin(theta)
    ax.plot(x, y, linewidth=lw, alpha=alpha, color=color)


def _line(ax: plt.Axes, x0: float, y0: float, x1: float, y1: float, lw: float = 1.0, alpha: float = 0.5, color: Optional[str] = None):
    ax.plot([x0, x1], [y0, y1], linewidth=lw, alpha=alpha, color=color)


# ------------------------------------------------------------
# Flower of Life
# ------------------------------------------------------------

def _fol_centers(cx: float, cy: float, r: float, rings: int) -> List[Tuple[float, float]]:
    """
    Generate centers in a hexagonal packing up to 'rings' around center.
    """
    centers = [(cx, cy)]
    # Hex lattice basis
    dx = r
    dy = r * math.sqrt(3) / 2.0
    # spiral rings
    for k in range(1, rings + 1):
        # start at top
        x = cx
        y = cy + k * (2 * dy / math.sqrt(3)) * math.sqrt(3) / 2.0  # simplifies to k*dy? keep robust
        y = cy + k * dy * 2 / 1.7320508075688772 * 0  # we'll place by axial steps below instead
        # Better: axial coords approach
        # Directions for hex axial steps (q,r) mapped to cartesian:
        # six directions around the ring
        dirs = [(1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1), (1, -1)]
        # start at "north" position in axial coords
        q, r_ax = 0, -k
        # convert axial -> cart
        def to_xy(q_, r_):
            # cube/axial to 2D hex (pointy-top) spacing: dx=r, dy=r*sqrt(3)/2
            return (cx + r * (q_ + r_/2.0), cy + r * (math.sqrt(3)/2.0) * r_)
        x, y = to_xy(q, r_ax)
        for d in range(6):
            dq, dr = dirs[d]
            steps = k
            for _ in range(steps):
                centers.append((x, y))
                q += dq
                r_ax += dr
                x, y = to_xy(q, r_ax)
    # de-duplicate near-equals
    uniq = []
    seen = set()
    for (x, y) in centers:
        key = (round(x, 6), round(y, 6))
        if key not in seen:
            seen.add(key)
            uniq.append((x, y))
    return uniq


def draw_flower_of_life(ax: plt.Axes,
                        cx: float = 0.5,
                        cy: float = 0.5,
                        base_r: float = 0.25,
                        rings: int = 2,
                        line_alpha: float = 0.7,
                        lw: float = 0.8,
                        color: Optional[str] = None):
    """
    Draw a Flower-of-Life pattern centered at (cx,cy) with given base radius and ring count.
    - rings = number of hex rings around center (0 = single circle)
    """
    _as_display(ax)

    centers = _fol_centers(cx, cy, base_r, rings)
    # anchor circle
    _circle(ax, cx, cy, base_r, lw=lw, alpha=line_alpha, color=color)
    # neighbors
    for (x, y) in centers:
        _circle(ax, x, y, base_r, lw=lw, alpha=line_alpha, color=color)

    # subtle bounding ring (optional aesthetic)
    _circle(ax, cx, cy, base_r * (2 + rings * 0.35), lw=lw * 0.8, alpha=line_alpha * 0.4, color=color)


# ------------------------------------------------------------
# Harmonic Grid (rotated lattice)
# ------------------------------------------------------------

def draw_harmonic_grid(ax: plt.Axes,
                       spacing: float = 0.1,
                       angle_deg: float = 0.0,
                       count: int = 16,
                       alpha: float = 0.15,
                       lw: float = 1.0,
                       color: Optional[str] = None):
    """
    Draw a rotated line lattice over [0,1]^2.
    - spacing: distance between lines in normalized units
    - angle_deg: rotation angle
    - count: number of lines on each family (two families → total ~2*count)
    """
    _as_display(ax)
    angle = math.radians(angle_deg)
    ca, sa = math.cos(angle), math.sin(angle)

    # Define lines in rotated coordinates u,v such that lines are u = k*spacing and v = k*spacing
    ks = np.arange(-count, count + 1)

    def rot(x, y):
        # rotate point by +angle about center (0.5,0.5)
        x0, y0 = x - 0.5, y - 0.5
        xr = x0 * ca - y0 * sa + 0.5
        yr = x0 * sa + y0 * ca + 0.5
        return xr, yr

    # Draw family 1: vertical in rotated frame (u const)
    for k in ks:
        u = k * spacing + 0.5  # center at 0.5
        # two endpoints in rotated frame → map back
        x0, y0 = rot(u, 0.0)
        x1, y1 = rot(u, 1.0)
        _line(ax, x0, y0, x1, y1, lw=lw, alpha=alpha, color=color)

    # Family 2: horizontal in rotated frame (v const)
    for k in ks:
        v = k * spacing + 0.5
        x0, y0 = rot(0.0, v)
        x1, y1 = rot(1.0, v)
        _line(ax, x0, y0, x1, y1, lw=lw, alpha=alpha, color=color)


# ------------------------------------------------------------
# Resonance Rings
# ------------------------------------------------------------

def draw_resonance_rings(ax: plt.Axes,
                         cx: float = 0.5,
                         cy: float = 0.5,
                         radii: Iterable[float] = (0.1, 0.2, 0.33, 0.5),
                         alpha: float = 0.25,
                         lw: float = 1.5,
                         color: Optional[str] = None):
    """
    Draw concentric rings (e.g., frequency bands). Radii in normalized [0, ~0.7].
    """
    _as_display(ax)
    for r in radii:
        _circle(ax, cx, cy, r, lw=lw, alpha=alpha, color=color)


# ------------------------------------------------------------
# Composite convenience
# ------------------------------------------------------------

def stamp_resonant_overlay(ax: plt.Axes,
                           *,
                           grid_spacing: float = 0.12,
                           grid_angle: float = 30.0,
                           grid_alpha: float = 0.12,
                           fol_rings: int = 2,
                           fol_radius: float = 0.25,
                           fol_alpha: float = 0.6,
                           rings: Iterable[float] = (0.12, 0.2, 0.32, 0.5),
                           rings_alpha: float = 0.25):
    """
    Stamp a tasteful, layered overlay: harmonic grid + FoL + resonance rings.
    """
    draw_harmonic_grid(ax, spacing=grid_spacing, angle_deg=grid_angle, count=24, alpha=grid_alpha)
    draw_flower_of_life(ax, cx=0.5, cy=0.5, base_r=fol_radius, rings=fol_rings, line_alpha=fol_alpha)
    draw_resonance_rings(ax, cx=0.5, cy=0.5, radii=rings, alpha=rings_alpha)


# ------------------------------------------------------------
# Minimal self-test
# ------------------------------------------------------------

if __name__ == "__main__":
    # Quick visual check
    fig, ax = plt.subplots(figsize=(6, 6), dpi=120)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_aspect("equal", adjustable="box")
    ax.axis("off")

    draw_harmonic_grid(ax, spacing=0.1, angle_deg=30, count=18, alpha=0.12)
    draw_flower_of_life(ax, base_r=0.23, rings=2, line_alpha=0.65)
    draw_resonance_rings(ax, radii=[0.12, 0.2, 0.32, 0.5], alpha=0.25)

    out = "docs/assets/dashboard/overlay_selftest.png"
    import os, pathlib
    pathlib.Path(out).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print("Wrote", out)
