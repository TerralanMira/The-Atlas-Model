from atlas_model.consciousness_architecture import ConsciousnessArchitecture

def test_lock_requires_ethics_and_coherence():
    ca = ConsciousnessArchitecture({"E": True, "lock_threshold": 0.5})
    for s in ("truth","choice","field"):
        ca.receive_signal(s)
    ca.recursive_resonance(depth=2)
    coh = ca.integrate()
    assert coh >= 0.0
    assert ca.embody()["atlas_lock"] == (coh >= 0.5)

def test_resonant_expression_when_coherent():
    ca = ConsciousnessArchitecture({"E": True, "lock_threshold": 0.5, "resonant_cut": 0.6})
    for s in ("choice","field","memory","ethics"):
        ca.receive_signal(s)
    ca.recursive_resonance(depth=3)
    ca.integrate()
    out = ca.express()
    assert out.startswith(("resonant:", "noise:"))

def test_no_lock_without_E():
    ca = ConsciousnessArchitecture({"E": False})
    for s in ("a","b"):
        ca.receive_signal(s)
    ca.recursive_resonance(depth=1)
    coh = ca.integrate()
    assert coh == 0.0
    assert ca.embody()["atlas_lock"] is False
