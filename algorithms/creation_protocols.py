# algorithms/creation_protocols.py
"""
Creation Event Protocols (Detection Logic)
==========================================

Defines **testable criteria** for flagging an emergence (“creation”) event
in a Kuramoto-like toy system.

Primary criterion
-----------------
1) **Upward crossing** of order parameter R(t) through `R_event`.
2) **Hold time**: R(t) remains ≥ R_event for at least `T_hold` seconds.
3) **Guards**: coupling K(t) ≥ K_min_guard and optional anchor fraction
   exceeds a minimal level if provided.

Inputs
------
- R: np.ndarray, shape (T,)           # order parameter trace
- K: np.ndarray, shape (T,)           # coupling trace
- anchors: np.ndarray, shape (T,)     # fraction locally phase-locked (0..1)
- dt: float                           # step size
- R_event: float (default 0.8)
- T_hold: float (seconds)
- K_min: float (guard threshold)

Returns
-------
np.ndarray of shape (E, 3) with rows:
    [t_event_sec, R_at_event, K_at_event]

**Note**: This file asserts only what the traces show. It does not claim
cosmology/biology; it’s a computational detection of abrupt coherence.

"""

from __future__ import annotations
import numpy as np

def detect_events(
    R: np.ndarray,
    K: np.ndarray,
    anchors: np.ndarray,
    dt: float,
    R_event: float = 0.8,
    T_hold: float = 0.5,
    K_min: float = 0.0,
    anchors_min: float = 0.0,
) -> np.ndarray:
    assert R.ndim == 1 and K.ndim == 1 and anchors.ndim == 1
    assert len(R) == len(K) == len(anchors)
    T = len(R)
    hold_steps = int(max(1, round(T_hold / dt)))
    events = []

    above = R >= R_event
    i = 1
    while i < T:
        # rising edge (upward crossing)
        if (not above[i-1]) and above[i]:
            start = i
            end = min(T, i + hold_steps)
            if np.all(above[start:end]) and (K[i] >= K_min) and (anchors[i] >= anchors_min):
                t_sec = i * dt
                events.append([float(t_sec), float(R[i]), float(K[i])])
                # skip ahead to avoid double-counting continuous plateau
                i = end
                continue
        i += 1

    if not events:
        return np.zeros((0, 3), dtype=float)
    return np.array(events, dtype=float)
