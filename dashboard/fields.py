#!/usr/bin/env python3
"""
dashboard/fields.py — Elemental Field Renderers
------------------------------------------------
Lightweight visuals for Atlas fields:
  • Water/Air: vector fields (flow + diffusion)
  • Plasma: arc/discharge sketches from charge maps
  • Crystal: lattice / occupancy grids
  • Awareness: heatmap overlays

No heavy deps (numpy + matplotlib). Designed to be stamped into Panels from
dashboard/base.py. All functions accept an Axes and draw in-place.
"""

from __future__ import annotations
from typing import Optional, Tuple
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# -----------------------------
# Water / Air Vector Fields
# -----------------------------

def draw_vector_field(ax: plt.Axes,
                      u: np.ndarray,
                      v: np.ndarray,
                      step: int = 1,
                      scale: float = 1.0,
                      title: Optional[str] = None):
    """
    Draw a simple vector field with quiver.
    u, v: 2D arrays of same shape (H, W)
    step: subsampling for clarity
    """
    H, W = u.shape
    Y, X = np.mgrid[0:H:step, 0:W:step]
    ax.quiver(X, Y, u[::step, ::step], v[::step, ::step], angles='xy', scale_units='xy', scale=1/scale)
    ax.invert_yaxis()
    ax.set_aspect('equal', adjustable='box')
    if title:
        ax.set_title(title, fontsize=11, pad=8)
    ax.set_xlabel("x"); ax.set_ylabel("y")


def flow_from_height(height: np.ndarray, smooth: int = 1) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute a pseudo-flow field from a scalar height (potential) map.
    Flow ≈ -grad(height). Optionally smooth by averaging passes.
    """
    h = np.array(height, dtype=float)
    for _ in range(max(0, smooth)):
        h = 0.25*(np.roll(h,1,0)+np.roll(h,-1,0)+np.roll(h,1,1)+np.roll(h,-1,1))
    # gradients
    gy, gx = np.gradient(h)
    u = -gx
    v = -gy
    return u, v


# -----------------------------
# Plasma Discharges
# -----------------------------

def draw_plasma_arcs(ax: plt.Axes,
                     charge_map: np.ndarray,
                     threshold: float = 0.75,
                     jitter: float = 0.35,
                     rays: int = 18,
                     title: Optional[str] = None):
    """
    Visualize 'arcs' by connecting high-charge nodes with radial jittered rays.
    Heuristic & aesthetic — meant to signal ignition sites.
    """
    H, W = charge_map.shape
    yy, xx = np.where(charge_map >= np.nanmax(charge_map) * threshold)
    # draw a soft background heatmap for context
    im = ax.imshow(charge_map, origin='lower', aspect='equal')
    # arcs
    rng = np.random.default_rng(7)
    for (y, x) in zip(yy, xx):
        r = rng.random(rays) * (min(H, W) * 0.15)
        t = np.linspace(0, 2*np.pi, rays, endpoint=False) + rng.normal(0, 0.2, rays)
        for ri, ti in zip(r, t):
            x1 = x + (1+jitter*rng.normal()) * ri*np.cos(ti)
            y1 = y + (1+jitter*rng.normal()) * ri*np.sin(ti)
            ax.plot([x, x1], [y, y1], linewidth=1.0, alpha=0.6)
    ax.set_aspect('equal', adjustable='box')
    if title:
        ax.set_title(title, fontsize=11, pad=8)
    ax.set_xlabel("x"); ax.set_ylabel("y")


# -----------------------------
# Crystal Lattice
# -----------------------------

def draw_crystal_lattice(ax: plt.Axes,
                         grid: np.ndarray,
                         cell_size: int = 1,
                         title: Optional[str] = None):
    """
    Render a binary/float lattice as an image. 
    grid: 2D array; values > 0.5 considered 'occupied' in a simple view.
    """
    arr = np.array(grid, dtype=float)
    ax.imshow(arr, origin='lower', aspect='equal')
    ax.set_aspect('equal', adjustable='box')
    if title:
        ax.set_title(title, fontsize=11, pad=8)
    ax.set_xlabel("x"); ax.set_ylabel("y")


# -----------------------------
# Awareness Heatmap
# -----------------------------

def draw_awareness_heat(ax: plt.Axes,
                        map2d: np.ndarray,
                        title: Optional[str] = None):
    """
    Awareness intensity or influence as a heatmap.
    """
    ax.imshow(map2d, origin='lower', aspect='auto')
    if title:
        ax.set_title(title, fontsize=11, pad=8)
    ax.set_xlabel("x"); ax.set_ylabel("y")


# -----------------------------
# Small Synthetic Helpers
# -----------------------------

def synthetic_height(H=64, W=64, freq=6.0) -> np.ndarray:
    y, x = np.mgrid[0:H, 0:W]
    return np.sin(x/freq) * np.cos(y/freq)

def synthetic_charge(H=64, W=64) -> np.ndarray:
    y, x = np.mgrid[0:H, 0:W]
    return np.exp(-((x-W/2)**2+(y-H/2)**2)/(0.12*H*W))

def synthetic_crystal(H=64, W=64, p=0.45) -> np.ndarray:
    rng = np.random.default_rng(11)
    grid = (rng.random((H, W)) > (1-p)).astype(float)
    # smooth a bit for cohesion
    nbr = (np.roll(grid,1,0)+np.roll(grid,-1,0)+np.roll(grid,1,1)+np.roll(grid,-1,1))/4.0
    return (0.6*grid + 0.4*nbr)

def synthetic_awareness(H=64, W=64) -> np.ndarray:
    base = synthetic_height(H, W, freq=10.0)
    return (base - base.min()) / (base.max() - base.min() + 1e-9)
