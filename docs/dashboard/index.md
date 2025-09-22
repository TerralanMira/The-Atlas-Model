# Dashboard — The Living Canopy

The dashboard is Atlas’ sensory canopy. It shows **Fields → Pulse → Awareness → Overlays** so you can see life moving and steer by meaning.

## Panels

- **Fields** (`page_fields.py`)  
  Four elemental lenses: Water · Air · Plasma · Crystal. Compare balances/turbulence.

- **Pulse** (`page_pulse.py`)  
  Time-evolving coherence: spikes, settling, interference.

- **Awareness** (`page_awareness.py`)  
  Attention & salience maps. Where focus gathers, patterns lock.

- **Overlays (Live)** (`page_overlays_live.py`)  
  Geometry (coherence→hex), Plasma (series→ripples), Hybrid, and Stamped (resonant grid + archetype).

## Flow
logs → overlay_loader → algorithms → pages → docs/assets/dashboard/*.png
- **Data in:** `logs/atlas_pulse/atlas_pulse_series.csv`, `logs/coherence_matrix.npy`  
- **Algorithms:** `algorithms/resonant_overlays.py`, `algorithms/archetypes.py`  
- **Meaning:** `docs/dashboard/archetypes.md`

## First Run

See **Quickstart** for copy-paste commands, and **Data Inputs** for exact file shapes.
