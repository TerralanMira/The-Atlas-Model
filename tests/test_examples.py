import math

from algorithms.utils import signals_product, recommend_K_range


def test_signals_product_range_and_defaults():
    # Missing keys should default internally and stay within [0,1]
    prod = signals_product({"I": 0.8, "H": 0.9})
    assert 0.0 <= prod <= 1.0

    # All ones should saturate to 1 (or very close)
    prod_all = signals_product({"I":1,"Ψ":1,"H":1,"S":1,"β":1,"π":1,"W":1})
    assert math.isclose(prod_all, 1.0, rel_tol=1e-9, abs_tol=1e-9)


def test_recommend_k_range_monotone_and_bounded():
    # Lower resonance → lower K range; higher resonance → higher K range
    lo_low, hi_low = recommend_K_range(0.2)
    lo_mid, hi_mid = recommend_K_range(0.5)
    lo_hi, hi_hi = recommend_K_range(0.8)

    for lo, hi in [(lo_low, hi_low), (lo_mid, hi_mid), (lo_hi, hi_hi)]:
        assert 0.0 <= lo < hi <= 1.0

    assert lo_low < lo_mid < lo_hi
    assert hi_low < hi_mid < hi_hi
