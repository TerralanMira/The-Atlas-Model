"""
Reference coherence utilities.
Dependency-free; these are illustrative baselines.
"""
from math import sqrt

def clamp01(x: float) -> float:
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x

def kuramoto_order_parameter(phases) -> float:
    """
    Minimal Kuramoto order parameter R ∈ [0,1].
    'phases' is an iterable of angles in radians.
    """
    import cmath
    N = 0
    z = 0+0j
    for th in phases:
        z += cmath.exp(1j*th); N += 1
    if N == 0: return 0.0
    return clamp01(abs(z)/N)
