"""
Civic reference functions — light, explanatory.
"""

def resonant_currency_step(price: float, supply: float, coherence: float,
                           alpha: float=0.05, beta: float=0.05) -> dict:
    """
    One-step policy adjustment:
    dS = alpha * coherence - beta * (price - 1)
    Returns updated 'supply' and an explanation.
    """
    dS = alpha * coherence - beta * (price - 1.0)
    new_supply = max(0.0, supply + dS)
    return {
        "new_supply": new_supply,
        "delta": dS,
        "explain": f"Supply adjusted by coherence={coherence:.2f} and price error={price-1.0:.3f}"
    }
