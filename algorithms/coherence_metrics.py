Signal- and session-level coherence helpers used across the repo.

Includes:
- HRV metrics (RMSSD, SDNN, pNN50)
- Circular statistics for phase data (circular mean/variance)
- Kuramoto order parameter R from phases
- R-from-events: compute R using timestamped events (e.g., claps / turn starts)
- Simple composite coherence index for sessions

Notes
-----
All functions are lightweight, numpy-only, and safe to import in notebooks or scripts.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Tuple, Optional, Dict
import numpy as np


# ---------------------------------------------------------------------
# HRV (Heart Rate Variability) metrics
# ---------------------------------------------------------------------

def _nn_intervals(rr_ms: Iterable[float]) -> np.ndarray:
    """
    Convert RR intervals (ms) to array and drop non-positive values.
    """
    rr = np.asarray(list(rr_ms), dtype=float)
    rr = rr[np.isfinite(rr) & (rr > 0.0)]
    return rr


def hrv_rmssd(rr_ms: Iterable[float]) -> float:
    """
    Root Mean Square of Successive Differences (RMSSD).
    Input: RR intervals in milliseconds.
    """
    rr = _nn_intervals(rr_ms)
    if rr.size < 2:
        return np.nan
    diff = np.diff(rr)
    return float(np.sqrt(np.mean(diff * diff)))


def hrv_sdnn(rr_ms: Iterable[float]) -> float:
    """
    SDNN: standard deviation of NN intervals (ms).
    """
    rr = _nn_intervals(rr_ms)
    if rr.size < 2:
        return np.nan
    return float(np.std(rr, ddof=1))


def hrv_pnn50(rr_ms: Iterable[float]) -> float:
    """
    pNN50: percentage of successive differences greater than 50 ms.
    """
    rr = _nn_intervals(rr_ms)
    if rr.size < 2:
        return np.nan
    diff = np.abs(np.diff(rr))
    return float(100.0 * np.mean(diff > 50.0))


# ---------------------------------------------------------------------
# Circular / phase metrics
# ---------------------------------------------------------------------

def circular_mean(theta: Iterable[float]) -> float:
    """
    Circular mean of phases (radians).
    """
    th = np.asarray(list(theta), dtype=float)
    if th.size == 0:
        return np.nan
    z = np.exp(1j * th).mean()
    return float(np.angle(z))


def circular_variance(theta: Iterable[float]) -> float:
    """
    Circular variance ∈ [0, 1] (0 = tightly clustered, 1 = uniform).
    Defined as 1 - R, with R the mean resultant length.
    """
    th = np.asarray(list(theta), dtype=float)
    if th.size == 0:
        return np.nan
    R = np.abs(np.exp(1j * th).mean())
    return float(1.0 - R)


def order_parameter_from_phases(theta: Iterable[float]) -> Tuple[float, float]:
    """
    Kuramoto order parameter from phases.

    Returns
    -------
    (R, psi) : (float, float)
        R ∈ [0,1] coherence magnitude; psi mean phase (radians).
    """
    th = np.asarray(list(theta), dtype=float)
    if th.size == 0:
        return (np.nan, np.nan)
    z = np.exp(1j * th).mean()
    return (float(np.abs(z)), float(np.angle(z)))


# ---------------------------------------------------------------------
# R from event times (e.g., claps / turn starts)
# ---------------------------------------------------------------------

def phases_from_events(event_times: Iterable[float],
                       period: float) -> np.ndarray:
    """
    Map event timestamps onto a phase circle using a hypothesized period.

    Parameters
    ----------
    event_times : iterable of float (seconds)
    period : float
        Assumed base period (seconds). Example: 5.0 s breath cycle.

    Returns
    -------
    np.ndarray
        Phases in radians corresponding to events.
    """
    t = np.asarray(list(event_times), dtype=float)
    if t.size == 0 or not np.isfinite(period) or period <= 0:
        return np.array([], dtype=float)

    phases = (2.0 * np.pi * (t % period) / period).astype(float)
    return phases


def R_from_events(event_times: Iterable[float],
                  period: float) -> float:
    """
    Compute Kuramoto R from timestamps by mapping them to phases.

    Example
    -------
    >>> R = R_from_events([0.0, 4.9, 10.1, 15.0], period=5.0)
    """
    th = phases_from_events(event_times, period=period)
    if th.size == 0:
        return np.nan
    R, _ = order_parameter_from_phases(th)
    return R


# ---------------------------------------------------------------------
# Composite coherence index
# ---------------------------------------------------------------------

@dataclass
class CoherenceInputs:
    """
    Inputs for composite coherence index.

    Either supply physiological RR intervals (pre/post) and / or
    provide phase-derived R values (pre/post).
    """
    # physiological (RR intervals in ms)
    rr_pre: Optional[np.ndarray] = None
    rr_post: Optional[np.ndarray] = None

    # phase-based (Kuramoto order parameter)
    R_pre: Optional[float] = None
    R_post: Optional[float] = None


def coherence_index(inputs: CoherenceInputs,
                    alpha: float = 0.5) -> Dict[str, float]:
    """
    Compute a simple session coherence index combining HRV and R.

    Parameters
    ----------
    inputs : CoherenceInputs
        Provide RR intervals arrays and/or R values.
    alpha : float
        Blend weight for phase vs. physiology.
        0.0 → only HRV; 1.0 → only R. Default 0.5.

    Returns
    -------
    dict
        {
          "R_gain": ΔR,
          "RMSSD_gain": ΔRMSSD,
          "index": composite ∈ [0, 1] (heuristic),
          "rmssd_pre": ...,
          "rmssd_post": ...,
          "R_pre": ...,
          "R_post": ...
        }
    """
    # --- phase-based ---
    R_pre = inputs.R_pre if inputs.R_pre is not None else np.nan
    R_post = inputs.R_post if inputs.R_post is not None else np.nan
    dR = (R_post - R_pre) if (np.isfinite(R_pre) and np.isfinite(R_post)) else np.nan

    # --- HRV-based ---
    rmssd_pre = hrv_rmssd(inputs.rr_pre) if inputs.rr_pre is not None else np.nan
    rmssd_post = hrv_rmssd(inputs.rr_post) if inputs.rr_post is not None else np.nan
    dRMSSD = (rmssd_post - rmssd_pre) if (np.isfinite(rmssd_pre) and np.isfinite(rmssd_post)) else np.nan

    # Normalize deltas to [0,1] heuristically for composite
    def _norm_delta(x: float, scale: float) -> float:
        if not np.isfinite(x):
            return np.nan
        return float(np.clip(0.5 + 0.5 * (x / scale), 0.0, 1.0))

    # Heuristic scales (tune per cohort)
    nR = _norm_delta(dR, scale=0.30)         # ΔR of +0.30 → full credit
    nRM = _norm_delta(dRMSSD, scale=15.0)    # +15 ms RMSSD → full credit

    # Blend to single index
    if np.isnan(nR) and np.isnan(nRM):
        idx = np.nan
    elif np.isnan(nR):
        idx = nRM
    elif np.isnan(nRM):
        idx = nR
    else:
        idx = float((alpha * nR) + ((1.0 - alpha) * nRM))

    return {
        "R_gain": float(dR) if np.isfinite(dR) else np.nan,
        "RMSSD_gain": float(dRMSSD) if np.isfinite(dRMSSD) else np.nan,
        "index": idx,
        "rmssd_pre": float(rmssd_pre) if np.isfinite(rmssd_pre) else np.nan,
        "rmssd_post": float(rmssd_post) if np.isfinite(rmssd_post) else np.nan,
        "R_pre": float(R_pre) if np.isfinite(R_pre) else np.nan,
        "R_post": float(R_post) if np.isfinite(R_post) else np.nan,
    }


# ---------------------------------------------------------------------
# Tiny self-test
# ---------------------------------------------------------------------

if __name__ == "__main__":
    # Fake RR intervals (ms)
    rr_pre = np.array([820, 840, 810, 835, 825, 845, 830], dtype=float)
    rr_post = np.array([860, 870, 855, 875, 865, 880, 870], dtype=float)

    # Fake event times (s) for a 5s period
    evt_pre = [0.0, 5.1, 10.2, 15.0, 20.3]
    evt_post = [0.0, 5.02, 10.01, 14.98, 20.00]

    Rpre = R_from_events(evt_pre, period=5.0)
    Rpost = R_from_events(evt_post, period=5.0)

    out = coherence_index(
        CoherenceInputs(rr_pre=rr_pre, rr_post=rr_post, R_pre=Rpre, R_post=Rpost),
        alpha=0.5
    )
    print("[coherence_index]", out)
