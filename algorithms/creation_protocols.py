Creation protocols: measure coherence, gap, anchors, and detect clustered births.
Truth-first: we only declare creation when all gates pass.

Dependencies: numpy
"""
from __future__ import annotations
import json
import math
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

import numpy as np

# --------- Utilities ---------
def wrap_angle(x: np.ndarray) -> np.ndarray:
    """Wrap angles to [-pi, pi]."""
    return (x + np.pi) % (2 * np.pi) - np.pi

def order_parameter(phases: np.ndarray) -> Tuple[float, float]:
    """
    Kuramoto order parameter.
    phases: (N,) array of angles.
    Returns: (R, mean_phase)
    """
    z = np.exp(1j * phases)
    mean = z.mean()
    R = np.abs(mean)
    psi = np.angle(mean)
    return float(R), float(psi)

def phase_gap(mean_phase: float, driver_phase: float) -> float:
    """Wrapped distance between mean phase and driver."""
    return float(wrap_angle(np.array([mean_phase - driver_phase]))[0])

# --------- Gate Config ---------
@dataclass
class GateConfig:
    r_trend_window: int = 400
    r_min: float = 0.6
    r_trend_min_slope: float = 1e-4

    gap_trend_window: int = 400
    gap_trend_max_slope: float = -1e-4  # negative = narrowing

    anchor_eps: float = 0.35
    anchor_window: int = 200
    anchor_min_fraction: float = 0.1  # at least 10% nodes persistent

    birth_r_threshold: float = 0.7
    birth_min_duration: int = 150
    birth_cluster_max_gaps: int = 2  # clusters if ≤2 gaps between births
    min_births_for_cluster: int = 2

# --------- Measurements ---------
def moving_slope(y: np.ndarray, w: int) -> Optional[float]:
    if len(y) < w or w < 2:
        return None
    x = np.arange(w)
    yw = y[-w:]
    # least squares slope
    denom = (w * (w - 1) / 2.0) - (w - 1) * (w / 2.0)
    # simpler: use polyfit
    m, _ = np.polyfit(x, yw, 1)
    return float(m)

def anchor_persistence(phases_hist: np.ndarray, eps: float, window: int) -> float:
    """
    Estimate fraction of nodes that remained within eps of mean phase for the last 'window' steps.
    phases_hist: (T, N) angles
    """
    if phases_hist.shape[0] < window:
        return 0.0
    tail = phases_hist[-window:]  # (window, N)
    R, psi = order_parameter(tail[-1])
    diffs = wrap_angle(tail - psi)  # (window, N)
    locked = np.all(np.abs(diffs) <= eps, axis=0)  # (N,)
    return float(locked.mean())

def detect_births(R_series: np.ndarray, threshold: float, min_duration: int) -> List[int]:
    """
    Returns indices where R stays >= threshold for >= min_duration after a crossing.
    """
    births = []
    above = R_series >= threshold
    i = 0
    T = len(R_series)
    while i < T:
        if above[i]:
            start = i
            while i < T and above[i]:
                i += 1
            dur = i - start
            if dur >= min_duration:
                births.append(start)
        i += 1
    return births

def is_clustered(indices: List[int], max_gaps: int) -> bool:
    if len(indices) < 2:
        return False
    gaps = np.diff(indices)
    small_gaps = (gaps <= np.percentile(gaps, 50))  # median-based
    return (small_gaps.sum() >= max_gaps) or (len(indices) >= 3)

# --------- Gate Evaluation ---------
def evaluate_gates(
    R_series: np.ndarray,
    gap_series: np.ndarray,
    phases_hist: np.ndarray,
    cfg: GateConfig = GateConfig(),
    sovereignty_ok: bool = True,
) -> Dict:
    """Return gate-by-gate results and overall creation verdict."""
    # Coherence Rising
    r_slope = moving_slope(R_series, cfg.r_trend_window)
    r_now = float(R_series[-1]) if len(R_series) else 0.0
    coherence_rising = (r_slope is not None) and (r_slope >= cfg.r_trend_min_slope) and (r_now >= cfg.r_min)

    # Gap Narrowing (negative slope)
    gap_abs = np.abs(gap_series)
    gap_slope = moving_slope(gap_abs, cfg.gap_trend_window)
    gap_narrowing = (gap_slope is not None) and (gap_slope <= cfg.gap_trend_max_slope)

    # Anchor Persistence
    anchor_frac = anchor_persistence(phases_hist, cfg.anchor_eps, cfg.anchor_window)
    anchors_ok = anchor_frac >= cfg.anchor_min_fraction

    # Birth Clustering
    births = detect_births(R_series, cfg.birth_r_threshold, cfg.birth_min_duration)
    clustered = is_clustered(births, cfg.birth_cluster_max_gaps)
    births_ok = (len(births) >= cfg.min_births_for_cluster) and clustered

    # Sovereignty
    sovereignty = bool(sovereignty_ok)

    all_pass = coherence_rising and gap_narrowing and anchors_ok and births_ok and sovereignty

    return {
        "gates": {
            "coherence_rising": coherence_rising,
            "gap_narrowing": gap_narrowing,
            "anchor_persistence": anchors_ok,
            "birth_clustering": births_ok,
            "sovereignty": sovereignty,
        },
        "metrics": {
            "R_now": r_now,
            "R_slope": r_slope,
            "gap_slope": gap_slope,
            "anchor_fraction": anchor_frac,
            "birth_indices": births,
        },
        "creation": all_pass,
    }

# --------- Tuning Suggestions ---------
def tuning_recommendations(summary: Dict) -> List[str]:
    recs = []
    g = summary["gates"]
    m = summary["metrics"]
    if not g["coherence_rising"]:
        recs.append("Slightly increase coupling K or reduce noise to raise R trend.")
    if not g["gap_narrowing"]:
        recs.append("Adjust driver frequency/amp to better match collective mean phase.")
    if not g["anchor_persistence"]:
        recs.append("Increase local coupling or lower anchor epsilon window until ≥10% lock persists.")
    if not g["birth_clustering"]:
        recs.append("Favor parameter schedules that allow sustained high-R phases (plateaus) over brief spikes.")
    if not g["sovereignty"]:
        recs.append("Reject coercive parameter jumps; prefer minimal, reversible nudges.")
    if not recs:
        recs.append("Creation confirmed. Hold parameters; monitor stability.")
    return recs

# --------- JSON helper ---------
def to_json(summary: Dict) -> str:
    return json.dumps(summary, indent=2, default=lambda x: float(x) if isinstance(x, np.floating) else x)
