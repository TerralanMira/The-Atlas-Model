import numpy as np
from typing import Tuple

def propagate_coherence(x: np.ndarray, coupling: np.ndarray, steps: int = 50, alpha: float = 0.2) -> np.ndarray:
    """
    Propagate coherence from source vector x across a coupling matrix (graph Laplacian-like diffusion).
    x: (N,) initial coherence
    coupling: (N,N) row-stochastic or normalized adjacency
    alpha: diffusion strength in (0,1)
    """
    y = x.astype(float).copy()
    for _ in range(steps):
        y = (1 - alpha) * y + alpha * coupling.dot(y)
    return y

def multiplex_diffusion(xs: Tuple[np.ndarray, ...], Cs: Tuple[np.ndarray, ...], beta: float = 0.1, steps: int = 50) -> Tuple[np.ndarray, ...]:
    """
    Diffusion across multiple coupled layers (multiplex).
    xs: tuple of state vectors for each layer
    Cs: tuple of coupling matrices (one per layer)
    beta: inter-layer coupling (averaging toward the mean across layers)
    """
    L = len(xs)
    ys = tuple(x.copy().astype(float) for x in xs)
    for _ in range(steps):
        # intra-layer diffusion
        ys = tuple((1 - 0.2) * y + 0.2 * C.dot(y) for y, C in zip(ys, Cs))
        # inter-layer mixing
        mean_state = sum(ys) / L
        ys = tuple((1 - beta) * y + beta * mean_state for y in ys)
    return ys
