"""
Shared helper functions for Atlas algorithms.
Avoid duplication across examples.
"""

from functools import reduce

def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))

def signals_product(signals: dict, default: float = 0.8) -> float:
    seeds = ["I","Ψ","H","S","β","π","W"]
    vals = [float(signals.get(k, default)) for k in seeds]
    prod = reduce(lambda a, b: a * b, vals, 1.0)
    return clamp(prod)

def recommend_K_range(resonance: float) -> tuple[float, float]:
    r = clamp(resonance)
    if r < 0.3:
        return (0.2, 0.4)
    elif r < 0.6:
        return (0.4, 0.6)
    else:
        return (0.6, 0.8)
