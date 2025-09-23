import numpy as np
from typing import Tuple

# Simplified XY-like lattice alignment (phase on each site)
def crystal_step(theta: np.ndarray, J: float = 1.0, noise: float = 0.0) -> np.ndarray:
    """
    One update step on a 2D lattice of phases theta (radians).
    Each cell aligns to the mean angle of its 4-neighborhood (Von Neumann).
    """
    H, W = theta.shape
    out = theta.copy()
    for i in range(H):
        for j in range(W):
            nbrs = []
            for di, dj in ((1,0),(-1,0),(0,1),(0,-1)):
                ii, jj = (i+di) % H, (j+dj) % W
                nbrs.append(theta[ii, jj])
            # mean direction using vector sum
            vx = np.mean(np.cos(nbrs))
            vy = np.mean(np.sin(nbrs))
            mean_angle = np.arctan2(vy, vx)
            out[i, j] = (1 - J) * theta[i, j] + J * mean_angle + (np.random.randn() * noise if noise > 0 else 0.0)
    return out

def order_parameter(theta: np.ndarray) -> float:
    """
    Global alignment 0..1: magnitude of average unit vector.
    """
    vx = np.mean(np.cos(theta))
    vy = np.mean(np.sin(theta))
    return float(np.sqrt(vx*vx + vy*vy))

def lattice_sim(H: int = 40, W: int = 40, steps: int = 200, J: float = 0.5, noise: float = 0.1, seed: int = 42) -> Tuple[np.ndarray, float]:
    """
    Run a crystalline alignment simulation and return final lattice and order parameter.
    """
    rng = np.random.RandomState(seed)
    theta = rng.uniform(-np.pi, np.pi, size=(H, W))
    for _ in range(steps):
        theta = crystal_step(theta, J=J, noise=noise)
    return theta, order_parameter(theta)
