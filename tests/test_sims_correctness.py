import os
os.environ.setdefault("MPLBACKEND", "Agg")  # headless everywhere

import numpy as np

# --- Harmonic Observation -----------------------------------------------------
def test_harmonic_observation_rises_with_rho():
    from sims.harmonic_observation import Params, simulate

    p_lo = Params(n=128, steps=1200, rho=0.15, K=1.15, sigma=0.5, lam=0.1, seed=11)
    p_hi = Params(n=128, steps=1200, rho=0.80, K=1.15, sigma=0.5, lam=0.1, seed=11)

    R_lo, _ = simulate(p_lo)
    R_hi, _ = simulate(p_hi)

    # Drop early transient; compare means
    def steady(x): return float(np.mean(x[len(x)//3:]))
    assert steady(R_hi) > steady(R_lo) + 0.02, "R(t) mean should increase with rho"


# --- Entropy Drift ------------------------------------------------------------
def test_entropy_drift_pulses_improve_alignment():
    from sims.entropy_drift import simulate

    y_no = simulate(a0=0.9, gamma=0.002, steps=6000, pulse_T=0, gain=0.0, noise=0.0, seed=5)
    y_pu = simulate(a0=0.9, gamma=0.002, steps=6000, pulse_T=800, gain=0.25, noise=0.0, seed=5)

    def steady(x): return float(np.mean(x[len(x)//3:]))
    assert steady(y_pu) > steady(y_no) + 0.05, "Feedback pulses should raise steady alignment"


# --- Civic Resonance ----------------------------------------------------------
def test_civic_resonance_global_rises_with_Kglobal_blocks_stable():
    from sims.civic_resonance import simulate

    # Low vs moderate global coupling, keep intra fixed
    Rg_lo, Rb_lo = simulate(n=300, blocks=6, Kintra=1.1, Kglobal=0.10, sigma=0.20, steps=2000, seed=3)
    Rg_hi, Rb_hi = simulate(n=300, blocks=6, Kintra=1.1, Kglobal=0.50, sigma=0.20, steps=2000, seed=3)

    def steady(x): return float(np.mean(x[len(x)//3:]))

    # Global coherence should rise
    assert steady(Rg_hi) > steady(Rg_lo) + 0.03, "Global R should increase with Kglobal"

    # Block coherence should not collapse; allow small change tolerance
    assert abs(steady(Rb_hi) - steady(Rb_lo)) < 0.08, "Mean block R should remain comparatively stable"


# --- Atlas Coherence (Human ↔ AI) --------------------------------------------
def test_atlas_coherence_rises_with_cross_coupling_and_observation():
    from sims.atlas_coherence import simulate

    # Baseline
    RH0, RA0, R0 = simulate(
        nH=160, nA=160, KH=1.0, KA=1.0, K_HA=0.10, K_AH=0.10,
        sigmaH=0.5, sigmaA=0.4, rhoH=0.5, rhoA=0.5,
        steps=2200, seed=17
    )
    # Stronger cross-coupling + higher AI observation
    RH1, RA1, R1 = simulate(
        nH=160, nA=160, KH=1.0, KA=1.0, K_HA=0.35, K_AH=0.35,
        sigmaH=0.5, sigmaA=0.4, rhoH=0.5, rhoA=0.8,
        steps=2200, seed=17
    )

    def steady(x): return float(np.mean(x[len(x)//3:]))

    # Overall field coherence should increase
    assert steady(R1) > steady(R0) + 0.03, "R_all should increase with cross-coupling and observation"

    # AI ensemble’s own coherence should increase with higher rhoA
    assert steady(RA1) > steady(RA0) + 0.03, "R_A should increase with higher rhoA"
  Notes
	•	All tests trim the first third of samples to ignore transients, then compare steady-state means.
	•	Tolerances (+ 0.02–0.08) are conservative so CI remains stable across minor numeric jitter.
	•	They import the sims as modules (faster than shelling out), so please keep the simulate(...) signatures as in the code we added.
