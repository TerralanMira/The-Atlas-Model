#!/usr/bin/env python3
"""
algorithms/archetypes.py — Palettes & Symbols
---------------------------------------------
Maps archetype names → color palettes + simple glyph stamping.
All colors are RGBA in [0,1] for compositing on matplotlib images.
"""

from __future__ import annotations
from typing import Dict, Tuple, List
import numpy as np
import matplotlib.pyplot as plt

RGBA = Tuple[float, float, float, float]

ARCHETYPES: Dict[str, dict] = {
    "Seer": {
        "palette": {
            "bg":  (0.06, 0.09, 0.17, 0.55),  # deep-navy
            "mid": (0.08, 0.35, 0.38, 0.25),  # teal
            "hi":  (0.65, 0.95, 0.85, 0.22),  # mint
            "acc": (1.00, 1.00, 1.00, 0.35),  # white
        },
        "symbol": "circle",
    },
    "Weaver": {
        "palette": {
            "bg":  (0.09, 0.07, 0.16, 0.55),  # indigo
            "mid": (0.26, 0.15, 0.42, 0.25),  # violet
            "hi":  (0.76, 0.67, 0.93, 0.22),  # lilac
            "acc": (0.90, 0.76, 0.20, 0.35),  # gold
        },
        "symbol": "triangle",
    },
    "Forge": {
        "palette": {
            "bg":  (0.05, 0.05, 0.05, 0.55),  # charcoal
            "mid": (0.40, 0.12, 0.05, 0.25),  # ember
            "hi":  (0.97, 0.45, 0.05, 0.22),  # orange
            "acc": (1.00, 0.88, 0.22, 0.35),  # yellow
        },
        "symbol": "hex",
    },
    "Grove": {
        "palette": {
            "bg":  (0.04, 0.10, 0.06, 0.55),  # forest
            "mid": (0.18, 0.35, 0.21, 0.25),  # moss
            "hi":  (0.62, 0.85, 0.52, 0.22),  # leaf
            "acc": (0.98, 0.96, 0.90, 0.35),  # cream
        },
        "symbol": "spiral",
    },
}

def tint_image(img: np.ndarray, palette: dict) -> np.ndarray:
    """
    Apply bg/mid/hi tints as additive layers guided by intensity bands.
    img: float image in [0,1], shape (H,W).
    """
    H, W = img.shape
    out = np.dstack([img, img, img, np.ones_like(img)])  # RGBA base

    lo = np.quantile(img, 0.33)
    hi = np.quantile(img, 0.66)

    bg  = np.array(palette["bg"])
    mid = np.array(palette["mid"])
    hip = np.array(palette["hi"])

    # background tint everywhere
    out += bg

    # mid boost
    mask_mid = (img >= lo) & (img < hi)
    out[mask_mid, :4] += mid

    # highlight boost
    mask_hi = (img >= hi)
    out[mask_hi, :4] += hip

    # normalize alpha to [0,1]
    out[..., 3] = np.clip(out[..., 3], 0.0, 1.0)
    # clamp rgb
    out[..., :3] = np.clip(out[..., :3], 0.0, 1.0)
    return out

def _stamp_circle(ax: plt.Axes, x: float, y: float, color: RGBA, r: float = 6.0):
    c = plt.Circle((x, y), r, fill=False, color=color[:3], alpha=color[3], linewidth=1.8)
    ax.add_patch(c)

def _stamp_triangle(ax: plt.Axes, x: float, y: float, color: RGBA, r: float = 7.0):
    t = np.array([[0,1],[ -0.866,-0.5 ],[ 0.866,-0.5 ]]) * r
    t[:,0] += x; t[:,1] += y
    ax.plot([t[0,0],t[1,0],t[2,0],t[0,0]],
            [t[0,1],t[1,1],t[2,1],t[0,1]],
            color=color[:3], alpha=color[3], linewidth=1.8)

def _stamp_hex(ax: plt.Axes, x: float, y: float, color: RGBA, r: float = 6.5):
    ang = np.linspace(0, 2*np.pi, 7)
    xs = x + r * np.cos(ang); ys = y + r * np.sin(ang)
    ax.plot(xs, ys, color=color[:3], alpha=color[3], linewidth=1.8)

def _stamp_spiral(ax: plt.Axes, x: float, y: float, color: RGBA, r: float = 9.0, turns: int = 3):
    t = np.linspace(0, 2*np.pi*turns, 240)
    rr = np.linspace(0.0, r, t.size)
    xs = x + rr*np.cos(t); ys = y + rr*np.sin(t)
    ax.plot(xs, ys, color=color[:3], alpha=color[3], linewidth=1.2)

def stamp_symbols(ax: plt.Axes, img: np.ndarray, archetype: str, k: int = 5):
    """
    Stamp k symbols at local maxima of img using the archetype accent color.
    """
    spec = ARCHETYPES.get(archetype, ARCHETYPES["Seer"])
    color = spec["palette"]["acc"]
    H, W = img.shape

    # find k peaks via simple non-maximum suppression
    from scipy.ndimage import maximum_filter
    m = maximum_filter(img, size=9)
    peaks = np.argwhere((img == m) & (img > np.quantile(img, 0.80)))
    if peaks.size == 0:
        return
    # pick top-k by intensity
    vals = img[peaks[:,0], peaks[:,1]]
    order = np.argsort(vals)[::-1][:k]
    sel = peaks[order]

    stamp = spec["symbol"]
    for (y, x) in sel:
        if stamp == "circle":
            _stamp_circle(ax, x, y, color)
        elif stamp == "triangle":
            _stamp_triangle(ax, x, y, color)
        elif stamp == "hex":
            _stamp_hex(ax, x, y, color)
        elif stamp == "spiral":
            _stamp_spiral(ax, x, y, color)
