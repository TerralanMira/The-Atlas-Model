import numpy as np
import math
import pytest

from algorithms.resonance_algorithms import (
    plv_pair, plv_matrix,
    ppc_pair, ppc_matrix,
    phase_diffusion, phase_diffusion_windowed,
    phase_entropy, entropy_coherence, phase_entropy_windowed,
    mutual_information, mi_matrix,
    sliding_plv, sliding_entropy_coherence,
)

rng = np.random.default_rng(42)


# ---------- helpers ----------

def phases_const(T=512, phi=0.0):
    return np.full(T, float(phi))

def phases_linear(T=512, slope=0.01, phi0=0.0):
    t = np.arange(T, dtype=float)
    return (phi0 + slope * t) % (2 * math.pi)

def phases_noisy(T=512, mu=0.0, sigma=0.25):
    return (rng.normal(mu, sigma, size=T)) % (2 * math.pi)

def time_major(T=512, N=8, kind="noisy"):
    if kind == "const":
        X = np.stack([phases_const(T, phi=i*0.1) for i in range(N)], axis=1)
    elif kind == "linear":
        X = np.stack([phases_linear(T, slope=0.01 + 0.002*i) for i in range(N)], axis=1)
    else:
        X = np.stack([phases_noisy(T) for _ in range(N)], axis=1)
    return X


# ---------- PLV ----------

def test_plv_pair_perfect_locking_is_one():
    phi = phases_const(T=1024, phi=1.234)
    assert pytest.approx(plv_pair(phi, phi), rel=0, abs=1e-12) == 1.0

def test_plv_pair_phase_shift_still_one():
    a = phases_linear(T=2048, slope=0.02, phi0=0.1)
    b = (a + 0.5) % (2 * math.pi)  # constant offset
    val = plv_pair(a, b)
    assert val > 0.98

def test_plv_matrix_shape_and_symmetry():
    X = time_major(T=512, N=6, kind="linear")
    M = plv_matrix(X)
    assert M.shape == (6, 6)
    assert np.allclose(M, M.T, atol=1e-10)
    assert np.allclose(np.diag(M), 1.0)


# ---------- PPC ----------

def test_ppc_pair_behaves_and_unbiased_range():
    a = phases_noisy(1000, sigma=0.05)
    b = (a + 0.2) % (2 * math.pi)
    v = ppc_pair(a, b)
    assert -1.0 <= v <= 1.0
    assert v > 0.5  # should be fairly consistent

def test_ppc_matrix_properties():
    X = time_major(T=800, N=5, kind="noisy")
    M = ppc_matrix(X)
    assert M.shape == (5, 5)
    assert np.allclose(M, M.T, atol=1e-10)
    # diagonal convention = 1.0
    assert np.allclose(np.diag(M), 1.0)


# ---------- Diffusion ----------

def test_phase_diffusion_monotone_with_noise():
    base = phases_linear(2000, slope=0.01)
    low_noise  = (base + rng.normal(0, 0.01, size=base.size)) % (2*math.pi)
    high_noise = (base + rng.normal(0, 0.30, size=base.size)) % (2*math.pi)
    D_low  = phase_diffusion(np.stack([low_noise], axis=1), dt=0.01)[0]
    D_high = phase_diffusion(np.stack([high_noise], axis=1), dt=0.01)[0]
    assert D_high > D_low

def test_phase_diffusion_windowed_shapes_and_nans():
    X = time_major(T=300, N=3, kind="noisy")
    W = phase_diffusion_windowed(X, dt=0.02, win=40)
    assert W.shape == (299, 3)  # T-1 by N
    # first window should be NaN until enough data accrues
    assert np.isnan(W[:40]).all()  # inclusive of insufficient region


# ---------- Entropy-based coherence ----------

def test_entropy_coherence_bounds_and_ordering():
    tight = (phases_const(200) + rng.normal(0, 0.01, 200)) % (2*math.pi)
    loose = phases_noisy(200, sigma=1.0)
    c_tight = entropy_coherence(tight, bins=24)
    c_loose = entropy_coherence(loose, bins=24)
    assert 0.0 <= c_tight <= 1.0 and 0.0 <= c_loose <= 1.0
    assert c_tight > c_loose  # tighter distribution => higher coherence

def test_phase_entropy_windowed_dimensions():
    X = time_major(T=240, N=4, kind="noisy")
    E = phase_entropy_windowed(X, bins=18, win=50)
    assert E.shape == (240, 4)
    assert np.isnan(E[:50]).all()


# ---------- Mutual information ----------

def test_mutual_information_increases_with_dependency():
    a = phases_linear(3000, slope=0.02, phi0=0.0)
    b_dep = (a + rng.normal(0, 0.05, size=a.size)) % (2*math.pi)
    b_ind = phases_noisy(3000, sigma=1.0)
    mi_dep = mutual_information(a, b_dep, bins=24, normalized=False)
    mi_ind = mutual_information(a, b_ind, bins=24, normalized=False)
    assert mi_dep > mi_ind >= 0.0

def test_mi_matrix_symmetric_and_diagonal_convention():
    X = time_major(T=600, N=5, kind="linear")
    M_raw = mi_matrix(X, bins=20, normalized=False)
    M_nrm = mi_matrix(X, bins=20, normalized=True)
    assert M_raw.shape == (5, 5) and M_nrm.shape == (5, 5)
    assert np.allclose(M_raw, M_raw.T)
    assert np.allclose(M_nrm, M_nrm.T)
    # normalized convention: diagonal ~ 1.0
    assert np.allclose(np.diag(M_nrm), 1.0)


# ---------- Sliding windows ----------

def test_sliding_plv_length_and_trend():
    a = phases_linear(800, slope=0.02)
    b = (a + 0.3) % (2*math*pi)
    out = sliding_plv(a, b, win=100, step=25)
    assert out.ndim == 1 and out.size > 0
    # all windows of constant-offset pairs should be highly locked
    assert np.all(out > 0.9)

def test_sliding_entropy_coherence_shape():
    X = time_major(T=300, N=3, kind="noisy")
    S = sliding_entropy_coherence(X, win=60, bins=18, step=10)
    # expected K = floor((T-W)/step)+1 = floor((300-60)/10)+1 = 25
    assert S.shape == (25, 3)


# ---------- Edge cases ----------

def test_handles_short_series_gracefully():
    a = phases_const(3)
    b = phases_const(3, phi=0.2)
    # functions should not crash on tiny inputs
    _ = plv_pair(a, b)
    _ = ppc_pair(a, b)
    _ = phase_diffusion(a, dt=0.01)
    _ = mutual_information(a, b, bins=8, normalized=False)

def test_invalid_shapes_raise_meaningful_errors():
    # mi requires same length
    with pytest.raises(ValueError):
        mutual_information(np.zeros(10), np.zeros(11), bins=8)
    Notes
	•	Tests emphasize bounds, symmetry, monotonicity, and edge cases.
	•	Randomness is seeded for stability (rng = np.random.default_rng(42)).
	•	Sliding-window expectations are kept light so runs are fast on CI.
