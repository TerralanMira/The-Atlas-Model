"""
Crystal Growth — Field-Coupled, Anisotropic, Resonant
-----------------------------------------------------

A 2D cellular model that grows crystal lattices from seeds under an energy field E,
directional anisotropy A, impurities I, and an external resonance R(t).

Outputs (if run as __main__):
- Saves .npy arrays: lattice (0/1), time_memory, freq_memory
- Optionally prints simple coherence metrics

Dependencies: numpy, (matplotlib only if you plot externally)
"""

from dataclasses import dataclass
import numpy as np

@dataclass
class CrystalConfig:
    size: int = 128
    steps: int = 600
    seeds: int = 3
    seed_radius: int = 2

    # Field weights
    alpha_E: float = 1.0   # energy field weight
    beta_R: float = 0.6    # resonance weight
    gamma_I: float = 0.8   # impurity penalty
    kappa_A: float = 0.9   # anisotropy gain

    threshold_T: float = 0.55  # growth threshold

    # Resonance
    base_freq: float = 0.015   # temporal frequency of resonance
    phase_jitter: float = 0.3  # randomize local phase
    amp_R: float = 0.75        # resonance amplitude

    # Energy field shape
    E_center_boost: float = 0.3  # radial boost center-out
    E_noise: float = 0.15        # background noise

    # Impurities
    impurity_rate: float = 0.02  # fraction of sites with defects
    impurity_strength: float = 0.6

    # Anisotropy: number of preferred directions (e.g., 6 for hexagonal)
    n_axes: int = 6

def radial_energy(size: int, boost: float, noise: float, rng: np.random.Generator) -> np.ndarray:
    y, x = np.indices((size, size))
    cy = cx = (size - 1) / 2.0
    r = np.sqrt((x - cx)**2 + (y - cy)**2)
    r_norm = (r / r.max())
    base = 1.0 - r_norm  # higher energy toward center
    return np.clip(base + boost * base + noise * rng.normal(0, 1, (size, size)), 0, None)

def random_impurities(size: int, rate: float, strength: float, rng: np.random.Generator) -> np.ndarray:
    I = np.zeros((size, size))
    mask = rng.random((size, size)) < rate
    I[mask] = strength * (0.7 + 0.6 * rng.random(mask.sum()))
    return I

def anisotropy_kernel(n_axes: int, kappa: float) -> np.ndarray:
    """
    Build a 3x3 directional mask where directions closest to the n_axes spokes
    get higher gain. Returns weights for the 8-neighborhood (Moore), mapped later.
    """
    # Angles for kernel offsets (exclude center)
    offsets = [(-1,-1),(-1,0),(-1,1),
               ( 0,-1),        ( 0,1),
               ( 1,-1),( 1,0),( 1,1)]
    angs = np.array([np.arctan2(dy, dx) for dy, dx in offsets])  # [-pi, pi]
    # Preferred axes
    spokes = np.linspace(0, 2*np.pi, n_axes, endpoint=False)
    w = np.zeros(8)
    for i, theta in enumerate(angs):
        # distance to nearest spoke
        d = np.min(np.abs(((theta - spokes + np.pi) % (2*np.pi)) - np.pi))
        # sharper peak near spokes -> higher gain
        w[i] = 1.0 + kappa * np.exp(-(d**2) / (2 * (np.pi / (2*n_axes))**2))
    # normalize relative scale
    return w / w.mean()

def neighbors8(y: int, x: int, size: int):
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy == 0 and dx == 0:
                continue
            ny, nx = y + dy, x + dx
            if 0 <= ny < size and 0 <= nx < size:
                yield ny, nx, dy, dx

def resonance_field(t: int, size: int, base_freq: float, amp: float,
                    phase_jitter: float, rng: np.random.Generator) -> np.ndarray:
    """
    Global sinusoid with local phase jitter — the 'hum' that writes into memory.
    """
    y, x = np.indices((size, size))
    # spatial slow wave + temporal base
    spatial = 0.5 * np.sin(0.03 * x + 0.025 * y)
    local_phase = phase_jitter * rng.normal(0, 1, (size, size))
    R = amp * (0.5 + 0.5 * np.sin(2*np.pi*base_freq * t + spatial + local_phase))
    return R

def seed_lattice(size: int, n_seeds: int, r: int, rng: np.random.Generator):
    L = np.zeros((size, size), dtype=np.uint8)
    coords = []
    for _ in range(n_seeds):
        y = rng.integers(r, size - r)
        x = rng.integers(r, size - r)
        yy, xx = np.ogrid[-r:r+1, -r:r+1]
        mask = (yy**2 + xx**2) <= r*r
        L[y-r:y+r+1, x-r:x+r+1][mask] = 1
        coords.append((y, x))
    return L, coords

def grow_crystal(cfg: CrystalConfig, rng: np.random.Generator):
    S = cfg.size
    # Fields
    E = radial_energy(S, cfg.E_center_boost, cfg.E_noise, rng)
    I = random_impurities(S, cfg.impurity_rate, cfg.impurity_strength, rng)
    A = anisotropy_kernel(cfg.n_axes, cfg.kappa_A)  # 8-neighborhood gains

    # Lattice + memory
    L, seeds = seed_lattice(S, cfg.seeds, cfg.seed_radius, rng)  # 0/1
    time_mem = -np.ones((S, S), dtype=int)   # when each site accreted
    freq_mem = np.zeros((S, S), dtype=float) # dominant resonance at accretion
    for (sy, sx) in seeds:
        time_mem[sy, sx] = 0

    for t in range(1, cfg.steps + 1):
        R = resonance_field(t, S, cfg.base_freq, cfg.amp_R, cfg.phase_jitter, rng)

        frontier = np.argwhere(L == 1)
        # Mark neighbors of frontier as candidates
        cand_mask = np.zeros_like(L, dtype=bool)
        for y, x in frontier:
            for ny, nx, dy, dx in neighbors8(y, x, S):
                if L[ny, nx] == 0:
                    cand_mask[ny, nx] = True

        ys, xs = np.where(cand_mask)
        if ys.size == 0:
            break

        # Evaluate candidates
        grow_sites = []
        for y, x in zip(ys, xs):
            # Sum directional anisotropy based on which neighbors are filled
            ani_gain = 0.0
            for ny, nx, dy, dx in neighbors8(y, x, S):
                if L[ny, nx] == 1:
                    # map (dy,dx) to the 8-neigh index order in anisotropy kernel
                    idx = (dy+1)*3 + (dx+1)  # 0..8 with center at 4
                    if idx > 4: idx -= 1     # remove center shift
                    elif idx == 4: continue
                    ani_gain += A[idx]

            # Local drive
            D = cfg.alpha_E * E[y, x] + cfg.beta_R * R[y, x] - cfg.gamma_I * I[y, x]
            G = 1.0 + ani_gain  # aggregate directional gain
            score = D * G

            if score > cfg.threshold_T:
                grow_sites.append((y, x, score, R[y, x]))

        # Accrete sites with highest scores first (prevents flooding)
        if grow_sites:
            grow_sites.sort(key=lambda z: z[2], reverse=True)
            # admit top K% per step to control rate
            K = max(1, int(0.08 * len(grow_sites)))
            for (y, x, sc, rloc) in grow_sites[:K]:
                L[y, x] = 1
                time_mem[y, x] = t
                freq_mem[y, x] = rloc

    return L, time_mem, freq_mem, E, I

def coherence_index(L: np.ndarray, time_mem: np.ndarray) -> float:
    """
    Simple coherence: earlier, smoother growth fronts → higher score.
    Here: inverse of perimeter roughness normalized by occupied area.
    """
    S = L.shape[0]
    # perimeter estimate via 4-neighborhood differences
    diff = 0
    diff += np.sum(np.abs(L[1:, :] - L[:-1, :]))
    diff += np.sum(np.abs(L[:, 1:] - L[:, :-1]))
    perim = float(diff)
    area = float(L.sum() + 1e-8)
    roughness = perim / np.sqrt(area + 1e-8)
    # map to [0,1] monotonically
    return 1.0 / (1.0 + 0.02 * roughness)

if __name__ == "__main__":
    rng = np.random.default_rng(7)
    cfg = CrystalConfig()
    L, Tm, Fm, E, I = grow_crystal(cfg, rng)

    ci = coherence_index(L, Tm)
    print(f"[Crystal] coherence index: {ci:.4f}")
    # Save arrays for plotting elsewhere
    np.save("crystal_lattice.npy", L)
    np.save("crystal_time_memory.npy", Tm)
    np.save("crystal_freq_memory.npy", Fm)
    np.save("crystal_energy.npy", E)
    np.save("crystal_impurities.npy", I)
