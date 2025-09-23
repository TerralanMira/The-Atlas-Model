import numpy as np
from typing import List

def coherence_matrix(threads: List[np.ndarray]) -> np.ndarray:
    """
    Compute pairwise coherence (correlation) between 'threads' (1D arrays).
    Returns an NxN matrix in [-1, 1].
    """
    N = len(threads)
    C = np.eye(N, dtype=float)
    zs = [(t - np.mean(t)) / (np.std(t) + 1e-9) for t in threads]
    for i in range(N):
        for j in range(i+1, N):
            n = min(len(zs[i]), len(zs[j]))
            r = float(np.dot(zs[i][:n], zs[j][:n]) / n)
            C[i, j] = C[j, i] = r
    return C

def weave_fabric(threads: List[np.ndarray], warp_index: int = 0) -> np.ndarray:
    """
    Interlace threads using one as 'warp' (reference) and others as 'weft'.
    Produces a 2D fabric by stacking lag-aligned signals.
    """
    ref = threads[warp_index]
    L = len(ref)
    fabric = [ref]
    for k, t in enumerate(threads):
        if k == warp_index: 
            continue
        # crude phase alignment via max cross-correlation lag
        n = min(len(ref), len(t))
        refz = (ref[:n] - ref[:n].mean()) / (ref[:n].std() + 1e-9)
        tz   = (t[:n]   - t[:n].mean())   / (t[:n].std() + 1e-9)
        xcorr = np.correlate(refz, tz, mode="full")
        lag = np.argmax(xcorr) - (n - 1)
        out = np.zeros(L)
        if lag >= 0:
            out[lag:lag+n] = t[:n]
        else:
            out[:n+lag] = t[-lag:n]
        fabric.append(out)
    return np.vstack(fabric)
