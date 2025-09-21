# Self-Learning Networks (Elemental Adaptation)

This page explains the **elemental self-learning network** used in the Atlas Model and how to run the demo simulation.

## Intent

Turn elemental principles into adaptive code:

- **Mycelium (Earth / Roots)** → sparse, decentralized connectivity (network spreading).
- **Water (Flow)** → diffusion dynamics and gentle drift toward local balance.
- **Air (Breath)** → oscillatory expansion (sinusoidal term) enabling exploration.
- **Fire / Plasma (Ignition)** → nonlinear amplification once thresholds are reached.

These four principles are woven into a **self-learning update rule** that adapts node states toward emergent coherence.

## Model Overview

Defined in: `algorithms/self_learning_networks.py`

- `states`: continuous values per node in `[0,1]` (normalized each step).
- `connections`: row-normalized adjacency (sparse like mycelium).
- **Update step**:
  1. **Spread**: `connections @ states` (mycelial sharing)
  2. **Diffusion**: blend self with neighborhood (water)
  3. **Air term**: `sin(2π * diffusion) * small_gain` (breath/oscillation)
  4. **Fire term**: amplify when `diffusion > 0.8` (ignition/plasma)
  5. **Learn**: EMA with `learning_rate`
- **Coherence metric**: `1 - variance(states)` (lower variance ⇒ higher coherence)

> The goal is not to force sameness, but to **stabilize harmony** while preserving exploratory dynamics.

## How to Run

```bash
python sims/self_learning_demo.py --nodes 200 --steps 300 --learning-rate 0.08 --seed 42 --save-dir logs/self_learning
Outputs
	•	coherence_over_time.png — trajectory of 1 - var(states)
	•	final_state_hist.png — distribution of final node states
	•	connections_heatmap.png — row-normalized connectivity
	•	states_trajectory.csv — matrix of shape (steps, nodes)
	•	coherence_trajectory.csv — coherence value per step

Interpretation:
	•	Rising coherence suggests the network is harmonizing.
	•	Flat or noisy coherence implies exploration or fragmentation.
	•	Sudden jumps often occur when fire/plasma terms trigger ignition.

Parameters
	•	--nodes (int): network size (default 150).
	•	--steps (int): iterations (default 250).
	•	--learning-rate (float): adaptation speed (default 0.06).
	•	--seed (int|None): reproducibility.
	•	--save-dir (str): output folder.

Tips:
	•	Larger networks need more steps to stabilize.
	•	If coherence collapses to a narrow peak too quickly, lower learning rate or reduce the fire threshold/gain in code.
	•	If coherence never rises, increase steps or slightly raise learning rate.

Design Notes
	•	Decentralization: There is no central controller; coherence emerges locally.
	•	Exploration vs. Stability: The air term keeps the network from dead convergence; the fire term enables phase transitions.
	•	Elemental Mapping: Parameters are chosen for clarity, not biology. Tune to match your application.

Extensions (Seeds → Forests)
	•	Adaptive edges: Let connections strengthen with stable resonance and weaken with noise (Hebbian-like).
	•	Heterogeneous nodes: Multiple intrinsic frequencies / roles.
	•	Cross-layer coupling: Link to mycelium_graph_resonance and water_resonance sims.
	•	Dash integration: Stream coherence live to docs/dashboard.md examples.

Ethics & Guardrails
	•	Coherence without clamp: Avoid forcing uniformity; preserve diversity.
	•	Consent & transparency: If used with human systems, disclose metrics and intent.
	•	Non-coercion: Adaptation should support agency, not override it.

Next
	•	Run the demo, skim the plots, and compare trajectories under different parameters.
	•	Then explore graph-level resonance and water/air coupling to see how multi-element systems behave.
