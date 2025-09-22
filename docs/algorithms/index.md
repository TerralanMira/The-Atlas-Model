markdown
# Algorithms: The Weave Beneath

These are the engines that make the field breathe. Each algorithm is a part; the orchestrator binds them into a whole.

## Map

- **Earth (structure & stability)**
  - Code: `algorithms/earth_structures.py`
  - Doc:  `docs/algorithms/earth_structures.md`
  - Idea: lattices, thresholds, attractor basins, Kuramoto phases

- **Crystal (form & memory)**
  - Code: `algorithms/crystal_growth.py`
  - Demos: `sims/crystal_demo.py`
  - Docs:  `docs/algorithms/simulations/crystals.md`,
           `docs/algorithms/simulations/crystals_advanced.md`
  - Idea: field-coupled, anisotropic, resonant growth; structure as memory of flow

- **Plasma (ignition & transformation)**
  - Docs: `docs/algorithms/simulations/plasma.md`,
          `docs/algorithms/simulations/plasma_advanced.md`
  - Idea: energy injection, thresholds, filament formation, field intelligence

- **Orchestration (one pulse)**
  - Code: `algorithms/atlas_orchestrator.py`
  - Demo: `sims/atlas_pulse_demo.py`
  - Doc:  `docs/sims/atlas_pulse.md`
  - Idea: aggregate per-layer metrics → `atlas_coherence` (heartbeat)

## Using the Weave

- **See the heartbeat**  
  Run the pulse demo and inspect CSV/JSON to understand where coherence arises.

- **Tune a layer**  
  Modify parameters in a single module (e.g., Earth thresholds, Crystal anisotropy), then re-run the pulse and observe the change.

- **Add a new layer**  
  Implement a self-contained module that computes its own coherence metric, import it in `atlas_orchestrator.py`, and add its contribution to the aggregator.

## Ethics

- Coherence without coercion.  
- Transparency of factors feeding the pulse.  
- Respect for agency at every scale.

> Algorithms are instruments; the hum is the music. We tune instruments to serve the song.
