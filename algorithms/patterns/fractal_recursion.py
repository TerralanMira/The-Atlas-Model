import numpy as np
from typing import Callable, List, Tuple

def scale_recurse(seed: np.ndarray, scales: List[float], combine: Callable[[np.ndarray, np.ndarray], np.ndarray]) -> np.ndarray:
    """
    Recursively apply scaled versions of a seed pattern and combine them.
    - seed: 1D or 2D array
    - scales: list of scale factors (e.g., [1, 0.5, 0.25])
    - combine: function to combine accumulative pattern and new scaled pattern
    """
    acc = np.zeros_like(seed, dtype=float)
    for s in scales:
        # Resample by scale (nearest for simplicity; can swap for spline)
        if seed.ndim == 1:
            L = max(1, int(round(len(seed) * s)))
            idx = np.linspace(0, len(seed)-1, L).round().astype(int)
            scaled = seed[idx]
            # pad or crop to match acc
            out = np.zeros_like(acc)
            out[:min(len(out), len(scaled))] = scaled[:min(len(out), len(scaled))]
        else:
            H, W = seed.shape
            h = max(1, int(round(H * s)))
            w = max(1, int(round(W * s)))
            yi = np.linspace(0, H-1, h).round().astype(int)
            xi = np.linspace(0, W-1, w).round().astype(int)
            scaled = seed[np.ix_(yi, xi)]
            out = np.zeros_like(acc)
            out[:min(out.shape[0], h), :min(out.shape[1], w)] = scaled[:min(out.shape[0], h), :min(out.shape[1], w)]
        acc = combine(acc, out)
    return acc

def self_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """
    Scale-invariant similarity via normalized cross-correlation of envelopes.
    """
    a = (a - np.mean(a)) / (np.std(a) + 1e-9)
    b = (b - np.mean(b)) / (np.std(b) + 1e-9)
    if a.ndim == 1 and b.ndim == 1:
        n = min(len(a), len(b))
        return float(np.dot(a[:n], b[:n]) / n)
    else:
        # 2D: mean of element-wise product
        m, n = min(a.shape[0], b.shape[0]), min(a.shape[1], b.shape[1])
        return float(np.mean(a[:m, :n] * b[:m, :n]))
