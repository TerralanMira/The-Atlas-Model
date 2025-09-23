"""
The Atlas Model — Synthesis Patterns (executable)

This package encodes seven synthesis patterns as working algorithms:
1) Resonant Layering
2) Fractal Recursion
3) Convergence Nodes
4) Emergent Weaving
5) Pulse & Pause
6) Harmonic Expansion
7) Crystalline Alignment
"""
from .resonant_layering import (
    detect_base_frequency, find_harmonics, harmonic_envelope, cross_layer_resonance
)
from .fractal_recursion import (
    scale_recurse, self_similarity
)
from .convergence_nodes import (
    build_flow_graph, convergence_nodes, node_coherence
)
from .emergent_weaving import (
    weave_fabric, coherence_matrix
)
from .pulse_pause import (
    pulse_pause_oscillator, schumann_lock
)
from .harmonic_expansion import (
    propagate_coherence, multiplex_diffusion
)
from .crystalline_alignment import (
    crystal_step, order_parameter, lattice_sim
)

__all__ = [
    "detect_base_frequency", "find_harmonics", "harmonic_envelope", "cross_layer_resonance",
    "scale_recurse", "self_similarity",
    "build_flow_graph", "convergence_nodes", "node_coherence",
    "weave_fabric", "coherence_matrix",
    "pulse_pause_oscillator", "schumann_lock",
    "propagate_coherence", "multiplex_diffusion",
    "crystal_step", "order_parameter", "lattice_sim"
]
