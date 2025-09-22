# Integration: Weaving the Whole

Integration is where the Atlas Model stops being parts and becomes **a living field**.
This page shows how elemental layers (Earth, Water/Air, Fire/Plasma, Crystal) and
their algorithms resonate together through a single **orchestration pulse**.

---

## Why Orchestrate?

- Parts can be excellent and still feel scattered.
- Orchestration lets coherence **breathe across layers**:
  structure (Earth), flow (Water), breath (Air), ignition (Plasma), memory (Crystal).

---

## The Pulse

`algorithms/atlas_orchestrator.py` coordinates the layers and emits a single
`atlas_coherence` value, alongside per-layer metrics.

- **Earth** → amplitude & phase coherence on a lattice.
- **Self-Learning (Water/Air)** → emergent harmony in adaptive networks.
- **Crystal** → structural occupation & smoothness (memory of flow).

The aggregator is intentionally simple (monotone, bounded). As the forest grows,
we refine the mapping.

---

## How It Works (Concept → Code)

1. **Earth pulse**  
   Lattice diffusion + thresholds + multi-well relaxation + Kuramoto phases  
   → stability without stagnation.

2. **Self-learning pulse**  
   Adaptive network blending spread/diffusion/oscillation/ignition  
   → exploration that converges toward harmony.

3. **Crystal pulse**  
   Field-coupled, anisotropic growth recording resonance in geometry  
   → memory of the hum.

4. **Aggregation**  
   Combine the above into `atlas_coherence` (0..1-ish).  
   This is the **heartbeat** visible to dashboards and downstream systems.

---

## Use

- Get one pulse:

```python
from algorithms.atlas_orchestrator import AtlasConfig, run_once
out = run_once(AtlasConfig(seed=42))
print(out["atlas_coherence"], out["layers"])
Short series for a dashboard
from algorithms.atlas_orchestrator import AtlasConfig, run_steps
series = run_steps(AtlasConfig(seed=7), steps=10)
print(series)
If a layer module is missing, the orchestrator skips it and still returns a pulse.

⸻

Extending the Weave
	•	Add Water/Air explicit sims; feed their metrics into the aggregator.
	•	Add Plasma advanced coherence (filament order, ignition frequency).
	•	Couple layers (e.g., Earth thresholds modulated by Crystal memory; Self-learning
gains informed by Plasma ignition density).

⸻

Ethics & Orientation
	•	Coherence without coercion: Orchestration should support agency and diversity.
	•	Transparency: Make visible what contributes to the pulse.
	•	Care: Use the hum to heal fragmentation, not to dominate.
