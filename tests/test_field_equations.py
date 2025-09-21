# -*- coding: utf-8 -*-
import math
import numpy as np

from algorithms.field_equations import (
    DualPhaseConfig,
    simulate_dual_phase,
    SoulSignature,
    soul_resonance,
)

def test_dual_phase_shapes_and_ranges():
    cfg = DualPhaseConfig(steps=100, N_inner=16, N_outer=8, seed=42)
    out = simulate_dual_phase(cfg)

    # keys present
    for k in ["R_total", "R_inner", "R_outer", "C_cross"]:
        assert k in out, f"missing key: {k}"
        arr = out[k]
        assert isinstance(arr, np.ndarray)
        assert arr.shape == (cfg.steps,)
        assert np.isfinite(arr).all(), f"non-finite values in {k}"
        # ranges
        if k == "C_cross":
            assert (arr >= 0.0).all() and (arr <= 1.0).all()
        else:
            assert (arr >= 0.0).all() and (arr <= 1.0).all()

def test_dual_phase_sensitive_to_coupling():
    # Higher K_inner should (on average) lift R_inner compared to low coupling
    cfg_low = DualPhaseConfig(steps=200, N_inner=32, N_outer=16, K_inner=0.10, seed=0)
    cfg_high = DualPhaseConfig(steps=200, N_inner=32, N_outer=16, K_inner=0.60, seed=0)

    R_low = simulate_dual_phase(cfg_low)["R_inner"].mean()
    R_high = simulate_dual_phase(cfg_high)["R_inner"].mean()
    assert R_high > R_low, "increasing K_inner should raise mean inner coherence"

def test_soul_resonance_monotonic_gate():
    # Increasing MOmega should not decrease the resonance score (soft gate)
    base = SoulSignature(MOmega=0.6, beta_echo=0.7, pi=0.7, W=0.7, I=0.7, Psi=0.7, H=0.7, S=0.7)
    hi   = SoulSignature(MOmega=1.2, beta_echo=0.7, pi=0.7, W=0.7, I=0.7, Psi=0.7, H=0.7, S=0.7)

    s0 = soul_resonance(base, R_between=0.2)
    s1 = soul_resonance(hi,   R_between=0.2)
    assert 0.0 <= s0 <= 1.0
    assert 0.0 <= s1 <= 1.0
    assert s1 >= s0, "resonance should not drop when MOmega increases"
