"""
lc_grid_modes.py
----------------

Compute low-order eigenmodes of a 2D Laplacian on a rectangular grid.
Treats modes as LC-grid resonances (ω ~ sqrt(λ)).

Dependencies: numpy, (optional) matplotlib

Run:
    python sims/lc_grid_modes.py
"""

import numpy as np

try:
    import matplotlib.pyplot as plt
except Exception:
    plt = None


def laplacian_2d(ny: int, nx: int) -> np.ndarray:
    """
    5-point finite-difference Laplacian with Dirichlet edges.
    Returns (ny*nx, ny*nx) dense matrix for small grids.
    """
    N = ny * nx
    L = np.zeros((N, N), dtype=float)

    def idx(y, x): return y * nx + x

    for y in range(ny):
        for x in range(nx):
            i = idx(y, x)
            L[i, i] = 4.0
            if y > 0:      L[i, idx(y-1, x)] = -1.0
            if y < ny-1:   L[i, idx(y+1, x)] = -1.0
            if x > 0:      L[i, idx(y, x-1)] = -1.0
            if x < nx-1:   L[i, idx(y, x+1)] = -1.0
    return L


def modes(ny=20, nx=20, k=6):
    L = laplacian_2d(ny, nx)
    # Dense eigendecomposition (fine for small grids)
    evals, evecs = np.linalg.eigh(L)
    # Sort ascending
    idx = np.argsort(evals)
    evals = evals[idx]
    evecs = evecs[:, idx]
    # Skip the smallest (often near-0 if Neumann; Dirichlet keeps >0)
    return evals[:k], evecs[:, :k]


def reshape_mode(vec, ny, nx):
    return vec.reshape(ny, nx)


def main():
    ny, nx, k = 24, 24, 6
    evals, evecs = modes(ny, nx, k)
    freqs = np.sqrt(np.clip(evals, 0, None))

    print("λ (first 6):", np.round(evals, 5))
    print("ω ~ sqrt(λ):", np.round(freqs, 5))

    if plt is None:
        return

    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(2, 3, figsize=(9, 6))
    axs = axs.ravel()
    for i in range(k):
        m = reshape_mode(evecs[:, i], ny, nx)
        axs[i].imshow(m, origin="lower")
        axs[i].set_title(f"Mode {i+1}\nλ={evals[i]:.4f}")
        axs[i].axis("off")
    fig.suptitle("LC Grid Modes (Dirichlet)")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
