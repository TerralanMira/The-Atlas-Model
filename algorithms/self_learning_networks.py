"""
Self-Learning Networks — Elemental Adaptive Simulation
------------------------------------------------------

This module implements adaptive networks inspired by the four grounding elements:
- Mycelium (Earth/Network roots)
- Water (Flow/Diffusion)
- Air (Breath/Expansion)
- Fire/Plasma (Ignition/Transformation)

Each element contributes a principle of adaptation, woven into a dynamic self-learning network
that tunes itself based on coherence metrics.

"""

import numpy as np

class SelfLearningNetwork:
    def __init__(self, num_nodes=100, learning_rate=0.05):
        """
        Initialize the self-learning network.
        
        Args:
            num_nodes (int): Number of nodes in the network.
            learning_rate (float): Base rate for adaptation.
        """
        self.num_nodes = num_nodes
        self.learning_rate = learning_rate
        
        # State of each node
        self.states = np.random.rand(num_nodes)
        
        # Connectivity matrix (initially sparse, like mycelium roots)
        self.connections = np.random.choice([0, 1], 
                                            size=(num_nodes, num_nodes), 
                                            p=[0.95, 0.05]).astype(float)
        
        # Normalize connectivity
        self._normalize_connections()

    def _normalize_connections(self):
        """Ensure connections sum to 1 for each node (probabilistic spreading)."""
        row_sums = self.connections.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1.0
        self.connections /= row_sums

    def step(self):
        """
        Advance the network by one adaptive update step.
        Integrates elemental principles into the update rules.
        """
        new_states = np.zeros(self.num_nodes)

        # Mycelium (network spreading)
        spread = self.connections @ self.states

        # Water (diffusion + coherence drift)
        diffusion = self.states + 0.1 * (spread - self.states)

        # Air (expansion / oscillation dynamics)
        air_term = np.sin(2 * np.pi * diffusion) * 0.05

        # Fire/Plasma (ignition — nonlinear amplification)
        fire_term = np.where(diffusion > 0.8, diffusion**2, 0.0)

        # Combine terms
        new_states = (0.6 * diffusion) + (0.2 * air_term) + (0.2 * fire_term)

        # Normalize
        new_states = (new_states - np.min(new_states)) / (np.max(new_states) - np.min(new_states) + 1e-8)
        
        # Update with learning
        self.states = (1 - self.learning_rate) * self.states + self.learning_rate * new_states

    def run(self, steps=100):
        """
        Run the network for a given number of steps.
        
        Args:
            steps (int): Number of time steps to simulate.
        """
        history = []
        for _ in range(steps):
            self.step()
            history.append(self.states.copy())
        return np.array(history)

    def coherence_metric(self):
        """
        Compute a basic coherence metric:
        variance reduction across the network.
        Lower variance = higher coherence.
        """
        return 1.0 - np.var(self.states)

# Example usage (for testing):
if __name__ == "__main__":
    sln = SelfLearningNetwork(num_nodes=200, learning_rate=0.1)
    trajectory = sln.run(steps=200)
    print("Final coherence:", sln.coherence_metric())
