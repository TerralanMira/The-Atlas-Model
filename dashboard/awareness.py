#!/usr/bin/env python3
"""
dashboard/awareness.py — Awareness Maps & Overlays
--------------------------------------------------
Lightweight awareness generators that modulate simulations
and render influence/attention as 2D maps.

Focus modes:
  • "flow"       → water bias (continuity / smoothing)
  • "spread"     → air bias (diffusion / propagation)
  • "threshold"  → plasma bias (ignition sensitivity)
  • "structure"  → crystal bias (geometric stabilization)

All functions are numpy + matplotlib only and cooperate
with dashboard.base / dashboard.overlays.
"""

from __future__ import annotations
from typing import Literal, Tuple, Optional
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

Focus = Literal["flow", "spread", "threshold", "structure"]


# ---------------------------
# Generators
# ---------------------------

def awareness_from_seed(H: int = 96, W: int = 96, seed: int = 7) -> np.ndarray:
    """
    Base awareness field in [0,1], smooth and gently structured.
    """
    rng = np.random.default_rng(seed)
    a = rng.random((H, W))
    for _ in range(3):
        a = 0.25 * (np.roll(a, 1, 0) + np.roll(a, -1, 0) + np.roll(a, 1, 1) + np.roll(a, -1, 1))
    a = (a - a.min()) / (a.max() - a.min() + 1e-12)
    return a


def modulate(map2d: np.ndarray, focus: Focus = "flow", intensity: float = 0.15) -> np.ndarray:
    """
    Awareness modulation of any 2D map (not in-place).
    """
    m = map2d.astype(float)
    if focus == "flow":          # smooth continuity
        k = 1 + intensity
        m = 0.25*(np.roll(m,1,0)+np.roll(m,-1,0)+np.roll(m,1,1)+np.roll(m,-1,1))*k
    elif focus == "spread":      # outward diffusion bias
        m = m + intensity * (np.roll(m,1,0)+np.roll(m,-1,0)+np.roll(m,1,1)+np.roll(m,-1,1)-4*m)
    elif focus == "threshold":   # lift highs (ignite), damp lows
        t = np.quantile(m, 0.6)
        m = np.where(m > t, m * (1 + intensity), m * (1 - 0.5*intensity))
    elif focus == "structure":   # snap to bands / geometry
        bands = np.linspace(m.min(), m.max()+1e-12, 8)
        idx = np.digitize(m, bands) / (len(bands))
        m = (1 - intensity) * m + intensity * idx
    # normalize
    m = (m - m.min()) / (m.max() - m.min() + 1e-12)
    return m


def awareness_cycle(base: np.ndarray,
                    sequence: Tuple[Focus, ...] = ("flow","spread","threshold","structure"),
                    gain: float = 0.12,
                    rounds: int = 2) -> np.ndarray:
    """
    Ouroboric awareness pass through a focus sequence, repeated.
    """
    m = base.copy()
    for r in range(rounds):
        for f in sequence:
            m = modulate(m, focus=f, intensity=gain * (1 + 0.25*r))
    return m


# ---------------------------
# Drawing
# ---------------------------

def draw_awareness(ax: plt.Axes,
                   A: np.ndarray,
                   title: Optional[str] = "Awareness — Influence Map"):
    im = ax.imshow(A, origin='lower', aspect='auto')
    ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    if title:
        ax.set_title(title, fontsize=11, pad=8)
    ax.set_xlabel("x"); ax.set_ylabel("y")
