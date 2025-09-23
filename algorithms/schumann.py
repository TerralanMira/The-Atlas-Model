"""
algorithms/schumann.py

Minimal, dependency-light routines to:
- Load a time-series (1D)
- Extract a low-frequency 'pulse' via simple bandpass-ish smoothing
- Compute phase (via analytic signal) and a simple phase-locking metric (PLV-style)
- Produce entrainment per-channel from CSV of flows

Notes:
- This is a simple, interpretable seed. For production, swap in SciPy/NumPy advanced filters,
  Hilbert transforms, or STFTs.
"""

import numpy as np
import csv
import os
import math
from typing import Dict, List

def load_series(path: str) -> np.ndarray:
    arr = np.load(path) if path.endswith('.npy') else np.loadtxt(path, delimiter=',')
    # ensure 1D
    return np.asarray(arr).reshape(-1)

def simple_smooth(x: np.ndarray, window: int = 11) -> np.ndarray:
    if window < 3:
        return x
    kernel = np.ones(window) / window
    return np.convolve(x, kernel, mode='same')

def analytic_phase(x: np.ndarray) -> np.ndarray:
    """
    Lightweight analytic phase: approximate via quadrature using Hilbert-like envelope.
    If SciPy is available, replace with scipy.signal.hilbert for precision.
    """
    # crude approach: compute derivative as quadrature surrogate
    dx = np.gradient(x)
    phase = np.arctan2(dx, x + 1e-12)
    return np.unwrap(phase)

def phase_locking_value(phase1: np.ndarray, phase2: np.ndarray) -> float:
    """Compute PLV-like measure between two phase series (0..1)."""
    d = phase1 - phase2
    return np.abs(np.mean(np.exp(1j * d)))

def compute_entrainment(pulse: np.ndarray, flows: Dict[str, np.ndarray]) -> Dict[str, float]:
    p_phase = analytic_phase(pulse)
    scores = {}
    for name, arr in flows.items():
        a = simple_smooth(arr, window=9)
        ph = analytic_phase(a)
        plv = phase_locking_value(p_phase, ph)
        amp_corr = np.corrcoef(np.abs(pulse), np.abs(a))[0,1]
        # combine metrics with simple weighting
        plv = float(np.nan_to_num(plv))
        amp_corr = float(np.nan_to_num(amp_corr))
        score = 0.6 * plv + 0.4 * max(0.0, min(1.0, (amp_corr+1)/2))  # normalize corr(-1..1)->(0..1)
        scores[name] = score
    return scores

def read_flows_from_csv(path: str) -> Dict[str, np.ndarray]:
    """
    Expect CSV with header: timestamp,event,field,value
    Returns dict keyed by field name of 1D arrays (aligned by read order)
    """
    fields: Dict[str, List[float]] = {}
    with open(path, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            field = row.get('field') or row.get('element') or 'unknown'
            try:
                val = float(row.get('value', 0.0))
            except:
                val = 0.0
            fields.setdefault(field, []).append(val)
    return {k: np.asarray(v) for k, v in fields.items()}

def save_entrainment(scores: Dict[str, float], out_csv: str):
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    with open(out_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['field','entrainment_score'])
        for k,v in scores.items():
            writer.writerow([k, f"{v:.4f}"])

# CLI convenience
if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--pulse', required=True, help="path to pulse .npy or CSV")
    p.add_argument('--flows', required=True, help="path to flows csv (timestamp,event,field,value)")
    p.add_argument('--out', required=True, help="out csv for entrainment")
    args = p.parse_args()

    pulse = load_series(args.pulse)
    flows = read_flows_from_csv(args.flows)
    scores = compute_entrainment(pulse, flows)
    save_entrainment(scores, args.out)
    print(f"Saved entrainment to {args.out}")
