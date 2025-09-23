"""
Community resonance metrics: synchrony, entropy, phase gaps, and sensitivity.

Inputs:
- theta: np.ndarray shape (T, N) phases in radians
- groups: list[str] length N, group label per node (optional)
- adjacency: np.ndarray shape (N, N) weighted graph (optional)

Outputs:
- dict with time series of R_total, R_group, phase_entropy, inter_group_phase_gap
"""

import numpy as np
from collections import defaultdict
from typing import Dict, List, Optional, Tuple

def complex_order_parameter(theta_t: np.ndarray) -> Tuple[float, float]:
    """
    Single-timestep order parameter.
    Returns (R, psi) where R in [0,1], psi in [-pi, pi].
    """
    z = np.exp(1j * theta_t)
    mean = z.mean()
    R = np.abs(mean)
    psi = np.angle(mean)
    return float(R), float(psi)

def phase_entropy(theta_t: np.ndarray, bins: int = 36) -> float:
    """
    Shannon entropy of phase distribution.
    """
    hist, _ = np.histogram(theta_t % (2*np.pi), bins=bins, range=(0, 2*np.pi), density=True)
    hist = hist + 1e-12  # avoid log(0)
    return float(-np.sum(hist * np.log(hist)) / np.log(bins))

def group_indices(groups: Optional[List[str]]) -> Dict[str, np.ndarray]:
    if not groups:
        return {}
    idx = defaultdict(list)
    for i, g in enumerate(groups):
        idx[g].append(i)
    return {g: np.array(ix, dtype=int) for g, ix in idx.items()}

def time_series_metrics(theta: np.ndarray,
                        groups: Optional[List[str]] = None) -> Dict:
    """
    Compute time series of global and group metrics.
    theta: (T, N)
    """
    T, N = theta.shape
    out = {
        "R_total": np.zeros(T),
        "psi_total": np.zeros(T),
        "phase_entropy": np.zeros(T),
        "R_group": {},            # dict[group] -> (T,)
        "psi_group": {},          # dict[group] -> (T,)
        "inter_group_phase_gap": {}  # dict[(g1,g2)] -> (T,)
    }

    gidx = group_indices(groups)
    group_keys = list(gidx.keys())

    # allocate group arrays
    for g in group_keys:
        out["R_group"][g] = np.zeros(T)
        out["psi_group"][g] = np.zeros(T)

    # main loop
    for t in range(T):
        R, psi = complex_order_parameter(theta[t])
        out["R_total"][t] = R
        out["psi_total"][t] = psi
        out["phase_entropy"][t] = phase_entropy(theta[t])

        for g in group_keys:
            idx = gidx[g]
            Rg, psig = complex_order_parameter(theta[t, idx])
            out["R_group"][g][t] = Rg
            out["psi_group"][g][t] = psig

    # inter-group phase gaps
    for i in range(len(group_keys)):
        for j in range(i+1, len(group_keys)):
            g1, g2 = group_keys[i], group_keys[j]
            psi1 = out["psi_group"][g1]
            psi2 = out["psi_group"][g2]
            # wrap to [-pi, pi]
            dpsi = np.angle(np.exp(1j*(psi1 - psi2)))
            out["inter_group_phase_gap"][(g1, g2)] = dpsi

    return out

def sensitivity_to_node(theta: np.ndarray, node: int) -> float:
    """
    Simple sensitivity: how much does average R_total change
    if node phases are randomized (counterfactual)?
    """
    T, N = theta.shape
    R_base = np.mean([complex_order_parameter(theta[t])[0] for t in range(T)])

    rng = np.random.default_rng(42)
    theta_cf = theta.copy()
    theta_cf[:, node] = rng.uniform(0, 2*np.pi, size=T)
    R_cf = np.mean([complex_order_parameter(theta_cf[t])[0] for t in range(T)])
    return float(R_base - R_cf)

def summarize_metrics(metrics: Dict) -> Dict:
    """
    Compact summary for dashboards/logs.
    """
    summary = {
        "R_total_mean": float(np.mean(metrics["R_total"])),
        "R_total_std": float(np.std(metrics["R_total"])),
        "phase_entropy_mean": float(np.mean(metrics["phase_entropy"]))
    }
    for g, series in metrics["R_group"].items():
        summary[f"R_{g}_mean"] = float(np.mean(series))
    return summary
