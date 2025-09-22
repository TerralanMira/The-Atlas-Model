#!/usr/bin/env python3
"""
algorithms/resonant_overlays.py — Living Resonant Overlays
-----------------------------------------------------------
Life first: computational overlays you can feed with real data.

Includes:
  • project_coherence_to_hex()  → map an NxN coherence matrix to a hexagonal lattice
  • ripple_from_timeseries()    → plasma-like ripple field from a 1D signal
  • normalize(), to_uint8()     → small utilities

All outputs are numpy arrays you can draw with matplotlib or stamp into dashboard panels.
No heavy dependencies.
"""

from __future__ import annotations
import math
from typing import Tuple
import numpy as np


# ------------------------------------------------------------
# Utilities
# ------------------------------------------------------------

def normalize(x: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    x = x.astype(float)
    mn, mx = np.nanmin(x), np.nanmax(x)
    if mx - mn < eps:
        return np.zeros_like(x)
    return (x - mn) / (mx - mn + eps)

def to_uint8(x: np.ndarray) -> np.ndarray:
    x = normalize(x)
    return (255.0 * x).clip(0, 255).astype(np.uint8)


# ------------------------------------------------------------
# 1) Geometry from Coherence (hex lattice / Flower-of-Life vibe)
# ------------------------------------------------------------

def _hex_coords(rings: int) -> np.ndarray:
    """
    Return axial hex coords (q,r) for a hexagon of given radius (rings).
    rings=0 → center only.
    """
    coords = [(0, 0)]
    if rings <= 0:
        return np.array(coords, dtype=int)

    dirs = [(1,0),(0,1),(-1,1),(-1,0),(0,-1),(1,-1)]
    for k in range(1, rings+1):
        q, r = 0, -k  # start at "north"
        for d in range(6):
            dq, dr = dirs[d]
            for _ in range(k):
                coords.append((q, r))
                q += dq
                r += dr
    return np.array(coords, dtype=int)

def _axial_to_xy(q: int, r: int, a: float = 1.0) -> Tuple[float, float]:
    """
    Convert axial hex (q,r) to 2D coords for pointy-top hexes.
    'a' is the lattice spacing in pixels (or arbitrary).
    """
    x = a * (q + r/2.0)
    y = a * (math.sqrt(3)/2.0) * r
    return x, y

def project_coherence_to_hex(C: np.ndarray, rings: int = 3, canvas: Tuple[int,int]=(256,256)) -> np.ndarray:
    """
    Map an NxN coherence matrix C to a hexagonal lattice field.
    Strategy:
      1) Compute principal energy per dimension (row mean).
      2) Sort dims by energy; assign to hex coords (center outward).
      3) Render as a soft field by splatting gaussian bumps on a canvas.

    Returns a 2D float array in [0,1].
    """
    C = np.array(C, dtype=float)
    if C.ndim != 2 or C.shape[0] != C.shape[1]:
        raise ValueError("C must be square NxN")

    N = C.shape[0]
    energy = normalize(np.nanmean(np.abs(C), axis=1))  # per-dimension energy
    order = np.argsort(energy)[::-1]                   # high → low

    coords = _hex_coords(rings)
    if len(coords) < N:
        # increase rings to fit all dims
        need = N
        k = rings
        while len(_hex_coords(k)) < need:
            k += 1
        coords = _hex_coords(k)

    # build coordinate list sorted center-out by ring index
    # current coords already spiral; good enough for aesthetic packing
    a = min(canvas)/ (2.5 * (rings+1))  # spacing heuristic
    pts = [ _axial_to_xy(int(q), int(r), a=a) for (q,r) in coords[:N] ]

    H, W = canvas
    field = np.zeros((H, W), dtype=float)

    # gaussian splat per dim
    yy, xx = np.mgrid[0:H, 0:W]
    for rank, dim in enumerate(order):
        x, y = pts[rank]
        # center canvas
        cx = W/2 + x
        cy = H/2 - y
        val = 0.35 + 0.65 * energy[dim]  # base + weighted
        sigma = max(4.0, 14.0 * (1.0 - energy[dim]))  # high energy → tighter
        g = np.exp(-(((xx-cx)**2 + (yy-cy)**2)/(2*sigma**2)))
        field += val * g

    return normalize(field)


# ------------------------------------------------------------
# 2) Plasma Ripples from Time-Series
# ------------------------------------------------------------

def ripple_from_timeseries(s: np.ndarray,
                           canvas: Tuple[int,int]=(256,256),
                           waves: int = 3,
                           dispersion: float = 0.25,
                           seed: int = 7) -> np.ndarray:
    """
    Create a plasma-like ripple field from a 1D signal s.
    Steps:
      1) normalize s → [0,1]
      2) place a few radial sources whose radii evolve from s (and harmonics)
      3) sum cosinusoidal wavefronts with mild dispersion & noise

    Returns a 2D float array in [0,1].
    """
    rng = np.random.default_rng(seed)
    s = normalize(np.array(s, dtype=float))
    H, W = canvas
    yy, xx = np.mgrid[0:H, 0:W]
    cx, cy = W/2, H/2

    # source positions (near center with slight jitter)
    sources = []
    for k in range(waves):
        dx = rng.normal(0, 0.12*W)
        dy = rng.normal(0, 0.12*H)
        sources.append((cx+dx, cy+dy))

    # build radius evolutions for each source using harmonics of s
    t = np.linspace(0, 2*np.pi, len(s), endpoint=False)
    # harmonic envelopes
    envs = [ s,
             normalize(s * (0.6 + 0.4*np.sin(2*t))),
             normalize(s * (0.5 + 0.5*np.cos(3*t))) ]

    field = np.zeros((H, W), dtype=float)
    # pick a few time slices across s
    steps = min(24, len(s))
    idxs = np.linspace(0, len(s)-1, steps).astype(int)

    for k, (sx, sy) in enumerate(sources):
        for i in idxs:
            # wave radius from combined envelopes
            r = 8 + 42*envs[k % len(envs)][i]
            d = np.sqrt((xx - sx)**2 + (yy - sy)**2)
            # cosine ripple with mild dispersion
            phase = 2*np.pi * (d / (r+1e-6))
            damp  = np.exp(-dispersion * (d / (0.6*max(H,W))))
            field += (0.5 + 0.5*np.cos(phase)) * damp

    # add faint noise for plasma texture
    noise = rng.normal(0, 0.05, size=(H, W))
    field = normalize(field + noise)
    return field
