"""
Quick demo wiring all seven synthesis patterns.
Run: python -m sims.pattern_suite_demo
"""
import numpy as np
import networkx as nx

from algorithms.patterns import *

def demo():
    # 1) Resonant Layering
    fs = 100.0
    t = np.arange(0, 10, 1/fs)
    sig1 = np.sin(2*np.pi*7.83*t) + 0.3*np.sin(2*np.pi*16*t)
    sig2 = np.sin(2*np.pi*7.83*t + 0.8) + 0.2*np.sin(2*np.pi*32*t)
    base = detect_base_frequency(sig1, fs)
    env_res = cross_layer_resonance(sig1, sig2)

    # 2) Fractal Recursion
    seed = np.sin(2*np.pi*1.5*t)
    combo = scale_recurse(seed, [1, 0.5, 0.25], combine=lambda a,b: a + 0.5*b)
    sim_ss = self_similarity(seed, combo)

    # 3) Convergence Nodes
    flows = [("ecology","health",3), ("health","community",5), ("community","algorithms",2), ("ecology","algorithms",1)]
    G = build_flow_graph(flows)
    hubs = convergence_nodes(G, top_k=3)

    # 4) Emergent Weaving
    fabric = weave_fabric([sig1, sig2, combo], warp_index=0)
    C = coherence_matrix([sig1, sig2, combo])

    # 5) Pulse & Pause
    x = pulse_pause_oscillator(T=len(t), dt=1/fs, f_target=7.83, duty=0.55, noise=0.01)
    locked = schumann_lock(x, fs=fs)

    # 6) Harmonic Expansion
    N = 6
    A = np.ones((N, N)) - np.eye(N)
    A = A / A.sum(axis=1, keepdims=True)
    init = np.zeros(N); init[0] = 1.0
    spread = propagate_coherence(init, A, steps=60, alpha=0.25)

    # 7) Crystalline Alignment
    theta, op = lattice_sim(H=24, W=24, steps=150, J=0.6, noise=0.05)

    print("Base freq:", round(base, 2), "Hz  | Env resonance:", round(env_res, 3))
    print("Fractal self-similarity:", round(sim_ss, 3))
    print("Convergence hubs:", hubs)
    print("Weaving fabric shape:", fabric.shape, "| Mean coherence:", round(C.mean(), 3))
    print("Pulse sample:", round(float(x[:100].mean()), 3), " | Locked sample:", round(float(locked[:100].mean()), 3))
    print("Harmonic spread:", np.round(spread, 3))
    print("Crystalline order parameter:", round(op, 3))

if __name__ == "__main__":
    demo()
