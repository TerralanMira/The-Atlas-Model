"""
Earth Structures — Lattices, Thresholds, and Attractor Basins
-------------------------------------------------------------

The Earth layer provides structure and stability for the Atlas Model.
This module implements:
  • Lattice generators (grid graphs) with optional periodic boundaries
  • Discrete Laplacian and helper ops for diffusion on lattices
  • Threshold fields (inertia / friction) that resist incoherent motion
  • Simple attractor basin dynamics (multi-well potentials)
  • Kuramoto-on-lattice stepper (synchronization over structure)
  • Coherence metrics (variance-based + phase-locking value estimate)

Dependencies: numpy (matplotlib only used in optional demo)
"""

from dataclasses import dataclass
import numpy as np


# -------------------------------
# LATTICE / STRUCTURE GENERATORS
# -------------------------------

def grid_indices(n_rows: int, n_cols: int):
    """Return array of (i,j) pairs for an n_rows x n_cols grid."""
    idx = np.indices((n_rows, n_cols)).reshape(2, -1).T
    return idx  # shape (N, 2)


def to_linear(i: int, j: int, n_cols: int) -> int:
    """2D -> 1D index."""
    return i * n_cols + j


def neighbors_4(i: int, j: int, n_rows: int, n_cols: int, periodic: bool):
    """Return 4-neighborhood of (i,j)."""
    up    = ((i - 1) % n_rows if periodic else i - 1, j)
    down  = ((i + 1) % n_rows if periodic else i + 1, j)
    left  = (i, (j - 1) % n_cols if periodic else j - 1)
    right = (i, (j + 1) % n_cols if periodic else j + 1)

    neigh = []
    for (r, c) in (up, down, left, right):
        if 0 <= r < n_rows and 0 <= c < n_cols:
            neigh.append((r, c))
    return neigh


def lattice_adjacency(n_rows: int, n_cols: int, periodic: bool = False) -> np.ndarray:
    """
    Build adjacency matrix A for an n_rows x n_cols 4-neighbor grid.
    If periodic=True, wrap edges (torus); else clip at borders.
    """
    N = n_rows * n_cols
    A = np.zeros((N, N), dtype=float)
    for i in range(n_rows):
        for j in range(n_cols):
            u = to_linear(i, j, n_cols)
            for (r, c) in neighbors_4(i, j, n_rows, n_cols, periodic):
                v = to_linear(r, c, n_cols)
                A[u, v] = 1.0
    return A


def row_normalize(mat: np.ndarray) -> np.ndarray:
    """Row-normalize a matrix (safe for zero rows)."""
    M = mat.copy()
    s = M.sum(axis=1, keepdims=True)
    s[s == 0] = 1.0
    return M / s


def lattice_laplacian(A: np.ndarray) -> np.ndarray:
    """
    Graph Laplacian L = D - A (combinatorial).
    Useful for diffusion-like dynamics on the Earth layer.
    """
    D = np.diag(A.sum(axis=1))
    return D - A


# -------------------------------
# THRESHOLD / INERTIA FIELDS
# -------------------------------

@dataclass
class ThresholdField:
    """
    Represents a spatial field of thresholds (inertia/friction).
    Higher threshold => more resistance to change.
    """
    values: np.ndarray  # shape (N,)

    @classmethod
    def constant(cls, N: int, value: float = 0.2):
        return cls(values=np.full(N, float(value)))

    @classmethod
    def gradient(cls, n_rows: int, n_cols: int, low: float = 0.1, high: float = 0.4):
        """
        Vertical gradient from top (low) to bottom (high).
        """
        g = np.linspace(low, high, n_rows).reshape(-1, 1)
        field = np.tile(g, (1, n_cols)).reshape(-1)
        return cls(values=field)

    def apply(self, delta: np.ndarray) -> np.ndarray:
        """
        Damp changes that are below local threshold.
        delta: proposed state change (N,)
        """
        mask = np.abs(delta) < self.values
        out = delta.copy()
        out[mask] = 0.0  # insufficient force to overcome inertia
        return out


# -------------------------------
# ATTRACTOR BASINS (MULTI-WELL)
# -------------------------------

@dataclass
class MultiWellPotential:
    """
    1D multi-well potential applied element-wise to a state vector.
    V(x) = sum_k a_k * (x - m_k)^2 * (x - m_k)^2  (quartic wells around means m_k)
    """
    wells: np.ndarray  # centers m_k, shape (K,)
    weights: np.ndarray  # a_k >= 0, shape (K,)
    stiffness: float = 1.0

    @classmethod
    def symmetric_biwell(cls, m1=-0.5, m2=0.5, weight=1.0, stiffness=1.0):
        return cls(wells=np.array([m1, m2]), weights=np.array([weight, weight]), stiffness=stiffness)

    @classmethod
    def triwell(cls, centers=(-0.8, 0.0, 0.8), weights=(1.0, 0.6, 1.0), stiffness=1.0):
        return cls(wells=np.array(centers, dtype=float),
                   weights=np.array(weights, dtype=float),
                   stiffness=stiffness)

    def grad(self, x: np.ndarray) -> np.ndarray:
        """
        Gradient dV/dx at each x_i.
        For quartic wells: sum_k a_k * 2*(x - m_k) * ( (x - m_k)^2 )
        """
        g = np.zeros_like(x)
        for ak, mk in zip(self.weights, self.wells):
            d = (x - mk)
            g += ak * 2.0 * d * (d ** 2)
        return self.stiffness * g


# -------------------------------
# DYNAMICS ON THE EARTH LAYER
# -------------------------------

def diffuse_on_lattice(state: np.ndarray, A_norm: np.ndarray, alpha: float = 0.15) -> np.ndarray:
    """
    Simple diffusion step on a lattice using row-normalized adjacency.
    new = state + alpha * (A_norm @ state - state)
    """
    return state + alpha * (A_norm @ state - state)


def thresholded_update(state: np.ndarray,
                       proposal: np.ndarray,
                       thresholds: ThresholdField,
                       eta: float = 0.5) -> np.ndarray:
    """
    Combine current state with proposed change, subject to thresholds.
    """
    delta = proposal - state
    damped = thresholds.apply(delta)
    return state + eta * damped


def multiwell_relaxation(state: np.ndarray,
                         potential: MultiWellPotential,
                         step: float = 0.05) -> np.ndarray:
    """
    Gradient descent on multi-well potential (toward attractor basins).
    """
    grad = potential.grad(state)
    return state - step * grad


# -------------------------------
# KURAMOTO ON LATTICE (PHASES)
# -------------------------------

def kuramoto_step(phases: np.ndarray,
                  omega: np.ndarray,
                  A: np.ndarray,
                  K: float = 0.5,
                  dt: float = 0.05) -> np.ndarray:
    """
    One Euler step of Kuramoto dynamics on a given adjacency A.
      dθ_i/dt = ω_i + (K / deg_i) * sum_j A_ij * sin(θ_j - θ_i)
    """
    deg = A.sum(axis=1)
    deg[deg == 0] = 1.0
    influence = (A * np.sin(phases[None, :] - phases[:, None])).sum(axis=1) / deg
    return phases + dt * (omega + K * influence)


def phase_locking_value(phases: np.ndarray) -> float:
    """
    Estimate global phase coherence via the Kuramoto order parameter R.
    R = |(1/N) * sum_j exp(i * θ_j)|
    """
    z = np.exp(1j * phases)
    R = np.abs(z.mean())
    return float(R)


# -------------------------------
# COHERENCE METRICS (EARTH LAYER)
# -------------------------------

def variance_coherence(x: np.ndarray) -> float:
    """Variance-based coherence (1 - variance), normalized to [0,1] with guard."""
    v = np.var(x)
    return float(1.0 - v / (v + 1.0))  # monotone: higher when variance small


def combined_coherence(signal: np.ndarray, phases: np.ndarray) -> float:
    """
    Combine amplitude coherence (variance-based) and phase coherence (PLV).
    Returns a simple average in [0,1].
    """
    amp = variance_coherence(signal)
    phs = phase_locking_value(phases)
    return 0.5 * (amp + phs)


# -------------------------------
# EARTH SIMULATION STEP (COMPOSITE)
# -------------------------------

@dataclass
class EarthStepConfig:
    alpha_diffusion: float = 0.15     # diffusion strength
    eta_threshold: float = 0.5        # threshold mixing
    multiwell_step: float = 0.05      # attraction step
    K_kuramoto: float = 0.6           # coupling for phases
    dt_kuramoto: float = 0.05         # time step for phases


def earth_step(state_scalar: np.ndarray,
               phases: np.ndarray,
               omega: np.ndarray,
               A: np.ndarray,
               A_norm: np.ndarray,
               thresholds: ThresholdField,
               potential: MultiWellPotential,
               cfg: EarthStepConfig = EarthStepConfig()) -> tuple[np.ndarray, np.ndarray]:
    """
    One composite update that:
      1) diffuses scalar state on lattice
      2) applies thresholded update (Earth inertia)
      3) relaxes toward attractor basins (multi-well)
      4) advances Kuramoto phases on the same lattice

    Returns: (new_state_scalar, new_phases)
    """
    # (1) diffusion over structure
    proposal = diffuse_on_lattice(state_scalar, A_norm, alpha=cfg.alpha_diffusion)

    # (2) threshold (inertia) mixing
    state_after_thresh = thresholded_update(state_scalar, proposal, thresholds, eta=cfg.eta_threshold)

    # (3) relax into attractor basins
    state_after_wells = multiwell_relaxation(state_after_thresh, potential, step=cfg.multiwell_step)

    # (4) Kuramoto phases on Earth lattice
    phases_new = kuramoto_step(phases, omega, A, K=cfg.K_kuramoto, dt=cfg.dt_kuramoto)

    return state_after_wells, phases_new


# -------------------------------
# OPTIONAL: QUICK DEMO (CLI)
# -------------------------------

if __name__ == "__main__":
    # Minimal sanity demo (no plotting required to run)
    rng = np.random.default_rng(42)

    n_rows, n_cols = 20, 20
    N = n_rows * n_cols

    # Structure
    A = lattice_adjacency(n_rows, n_cols, periodic=True)
    A_norm = row_normalize(A)

    # Fields
    thresholds = ThresholdField.gradient(n_rows, n_cols, low=0.05, high=0.25)
    potential = MultiWellPotential.triwell(centers=(-0.8, 0.0, 0.8), weights=(1.0, 0.5, 1.0), stiffness=0.8)

    # States
    state = rng.normal(0.0, 0.4, size=N).astype(float)     # scalar field (e.g., “density”)
    phases = rng.uniform(0, 2*np.pi, size=N).astype(float) # phase field for Kuramoto
    omega  = rng.normal(0.0, 0.05, size=N).astype(float)   # intrinsic frequencies

    cfg = EarthStepConfig()

    # Run a few steps
    for t in range(200):
        state, phases = earth_step(state, phases, omega, A, A_norm, thresholds, potential, cfg)

    # Report coherence
    amp_coh = variance_coherence(state)
    phs_coh = phase_locking_value(phases)
    combo   = combined_coherence(state, phases)

    print(f"[Earth Demo] amplitude coherence: {amp_coh:.4f}")
    print(f"[Earth Demo] phase coherence    : {phs_coh:.4f}")
    print(f"[Earth Demo] combined coherence : {combo:.4f}")
