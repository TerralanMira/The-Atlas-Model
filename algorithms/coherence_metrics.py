"""
coherence_metrics.py

Implements coherence metrics for the Atlas Model.
Designed to evaluate awareness, synchronization, and resonance across scales.

These functions do not reduce coherence to a number —
they frame coherence as a dynamic relational measure, always contextual.
"""

import numpy as np

# -------------------------------
# Core Metrics
# -------------------------------

def phase_coherence(phases: np.ndarray) -> float:
    """
    Measure global phase coherence using the Kuramoto order parameter.
    
    Args:
        phases (np.ndarray): Array of oscillator phases (radians).
        
    Returns:
        float: Coherence value in [0,1].
    """
    complex_order = np.exp(1j * phases).mean()
    return np.abs(complex_order)


def local_coherence(phases: np.ndarray, adjacency: np.ndarray) -> float:
    """
    Measure local coherence weighted by adjacency (graph).
    
    Args:
        phases (np.ndarray): Array of oscillator phases (radians).
        adjacency (np.ndarray): Graph adjacency matrix (N x N).
        
    Returns:
        float: Weighted local coherence.
    """
    n = len(phases)
    norm = adjacency.sum()
    if norm == 0:
        return 0.0
    
    local_sum = 0.0
    for i in range(n):
        for j in range(n):
            if adjacency[i, j] > 0:
                local_sum += adjacency[i, j] * np.cos(phases[i] - phases[j])
    return local_sum / norm


def entropy_coherence(distribution: np.ndarray) -> float:
    """
    Shannon entropy as a measure of coherence diversity.
    
    Args:
        distribution (np.ndarray): Probability distribution (sums to 1).
        
    Returns:
        float: Normalized coherence (1 = max order, 0 = max entropy).
    """
    eps = 1e-12
    entropy = -np.sum(distribution * np.log(distribution + eps))
    max_entropy = np.log(len(distribution))
    return 1.0 - (entropy / max_entropy)


# -------------------------------
# Composite Resonance Metric
# -------------------------------

def resonance_score(phases: np.ndarray, adjacency: np.ndarray, distribution: np.ndarray) -> dict:
    """
    Combine global, local, and entropy coherence into a resonance score.
    
    Args:
        phases (np.ndarray): Oscillator phases.
        adjacency (np.ndarray): Graph adjacency.
        distribution (np.ndarray): Probability distribution (e.g. states, layers).
        
    Returns:
        dict: Resonance metrics {global, local, entropy, composite}.
    """
    global_c = phase_coherence(phases)
    local_c = local_coherence(phases, adjacency)
    entropy_c = entropy_coherence(distribution)

    composite = np.mean([global_c, local_c, entropy_c])
    
    return {
        "global_coherence": float(global_c),
        "local_coherence": float(local_c),
        "entropy_coherence": float(entropy_c),
        "composite_resonance": float(composite),
    }
