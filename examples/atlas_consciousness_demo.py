# examples/atlas_consciousness_demo.py
from atlas_model.consciousness_architecture import ConsciousnessArchitecture

signals = ["resonance", "ethics", "choice", "sovereignty", "weave"]
cfg = {"E": True, "S": 1.0, "Ω": 1.0, "lock_threshold": 0.5, "resonant_cut": 0.7}

engine = ConsciousnessArchitecture(cfg)
for s in signals:
    f = engine.receive_signal(s)
    print(f"[input] {s} -> {f} Hz")

engine.recursive_resonance(depth=4)
coh = engine.integrate()
print("[coherence]", coh)

print("[expression]", engine.express())
print("[embodiment]", engine.embody())
