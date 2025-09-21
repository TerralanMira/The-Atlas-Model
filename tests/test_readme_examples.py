# -*- coding: utf-8 -*-
"""
Smoke-test a couple of README-level imports so refactors don't silently break the public API.
"""
import numpy as np

def test_imports_are_available():
    from algorithms.field_equations import DualPhaseConfig, simulate_dual_phase, SoulSignature, soul_resonance
    cfg = DualPhaseConfig(steps=10, N_inner=8, N_outer=4, seed=1)
    out = simulate_dual_phase(cfg)
    assert set(out.keys()) == {"R_total","R_inner","R_outer","C_cross"}

    sig = SoulSignature()
    s = soul_resonance(sig, R_between=0.1)
    assert 0.0 <= s <= 1.0

def test_metrics_bundle_contract():
    from algorithms.coherence_metrics import metrics_bundle, wrap_phase
    import numpy as np
    n = 10
    A = np.zeros((n,n)); 
    for i in range(n-1):
        A[i,i+1]=A[i+1,i]=1.0
    t0 = np.zeros(n)
    t1 = wrap_phase(t0 + 0.1)
    R, cross01, drift, C01, Delta = metrics_bundle(t1, t0, A)
    assert 0.0 <= R <= 1.0 and 0.0 <= cross01 <= 1.0 and 0.0 <= C01 <= 1.0 and 0.0 <= Delta <= 1.0
