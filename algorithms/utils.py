"""
Shared helper functions for Atlas algorithms.
Avoids duplication across examples.
"""

from functools import reduce

def signals_product(signals: dict[str, float], default: float = 0.8) -> float:
    """
    Compute the product of all 7 signals, defaulting missing ones.
    """
    seeds = ["I","Ψ","H","S","β","π","W"]
    vals = [signals.get(k, default) for k in seeds]
    prod = reduce(lambda x, y: x * y, vals, 1.0)
    return max(0.0, min(1.0, prod))

def recommend_K_range(resonance: float) -> tuple[float,float]:
    """
    Recommend Kuramoto coupling range based on resonance.
    """
    if resonance < 0.3:
        return (0.2, 0.4)
    elif resonance < 0.6:
        return (0.4, 0.6)
    else:
        return (0.6, 0.8)
def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))
