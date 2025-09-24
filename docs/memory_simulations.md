# Memory Simulations

Memory is not a static archive — it is a living resonance field.  
What communities remember, and how those memories are revisited, determines the strength of their shared patterns.  

In this simulation, we explore **how events echo through collective memory**, gaining or losing strength depending on whether they are shared, revisited, or left behind.  

---

## Core Idea

- **Events** create **echoes** in the collective field.  
- **Shared experiences** amplify resonance.  
- **Neglected or isolated experiences** decay over time.  
- **Revisited experiences** evolve into new patterns, carrying memory forward.  

This mirrors how stories, rituals, and cultural practices sustain coherence across generations.

---

## Simulation Model (Python)

```python
from collections import defaultdict

class MemorySimulation:
    def __init__(self):
        self.memory_echoes = defaultdict(lambda: {"strength": 0, "pattern": None})

    def shared(self, event):
        # Define logic for "shared" (could be multiple agents, wide attention, etc.)
        return event.get("shared", False)

    def revisited(self, event):
        # Define logic for "revisited" (if the event is brought back into awareness later)
        return event.get("revisited", False)

    def evolve_pattern(self, pattern):
        # A simple placeholder evolution mechanism
        return f"{pattern}_evolved" if pattern else "seed"

    def process_event(self, event):
        event_id = event["event"]

        # Increase or decrease resonance strength
        if self.shared(event):
            self.memory_echoes[event_id]["strength"] += 1
        else:
            self.memory_echoes[event_id]["strength"] -= 0.5

        # If revisited, evolve the pattern
        if self.revisited(event):
            current_pattern = self.memory_echoes[event_id]["pattern"]
            self.memory_echoes[event_id]["pattern"] = self.evolve_pattern(current_pattern)

    def report(self):
        return dict(self.memory_echoes)


# Example usage
events = [
    {"event": "community_gathering", "shared": True},
    {"event": "shared_meal", "shared": True},
    {"event": "conflict", "shared": False},
    {"event": "resolution", "shared": True, "revisited": True}
]

sim = MemorySimulation()
for e in events:
    sim.process_event(e)

print(sim.report())

Example Output
{
  "community_gathering": {"strength": 1, "pattern": null},
  "shared_meal": {"strength": 1, "pattern": null},
  "conflict": {"strength": -0.5, "pattern": null},
  "resolution": {"strength": 1, "pattern": "seed"}
}
Interpretation
	•	Community gatherings and shared meals increase resonance strength.
	•	Conflicts that are not integrated weaken the field.
	•	Resolutions that are revisited do more than restore balance — they seed new cultural patterns.

⸻

Next Expansions
	•	Add time decay (memories fade unless maintained).
	•	Introduce agent-based models (different groups may amplify or dampen echoes differently).
	•	Visualize resonance as wave interference patterns across layers.
	•	Compare stable traditions vs. emergent adaptations.
