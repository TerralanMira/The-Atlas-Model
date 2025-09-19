import math
from algorithms.r_growth import compute_resonance, classify_stage

def test_compute_resonance_in_range():
    sig = {"I":0.7,"Psi":0.7,"H":0.7,"S":0.7,"beta_echo":0.7,"pi":0.7,"W":0.7}
    R = compute_resonance(sig)
    assert 0.0 <= R <= 1.0
    assert R > 0.6  # decent coherence

def test_stage_progression():
    assert classify_stage(0.2) == "calibration"
    assert classify_stage(0.6) == "flicker"
    assert classify_stage(0.8) == "sustain"
    assert classify_stage(0.94) == "lock"
    assert classify_stage(0.999) == "collapse"
