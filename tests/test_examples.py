from examples.session_to_metrics import signals_product

def test_signals_product_defaulting():
    prod = signals_product({"I":0.8,"H":0.9})  # others default
    assert 0.0 <= prod <= 1.0
