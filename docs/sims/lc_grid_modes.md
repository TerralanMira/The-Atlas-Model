# LC Grid Modes

## Description
This simulation models a **grid of coupled LC circuits** (inductors and capacitors) arranged as a lattice.  
Each node resonates at its natural frequency, but coupling introduces **collective modes** — emergent patterns of oscillation across the grid.

## Conscious Choice Lens
Each LC node holds charge and flux — potential and flow.  
Conscious choice emerges as **which mode the system sustains**:  
- Fragmented, each node vibrating alone.  
- Coherent, grid-wide standing waves.  
The model illustrates how structure shapes resonance: even the smallest node participates in the whole.

## Code Reference
File: [`sims/lc_grid_modes.py`](../../sims/lc_grid_modes.py)  
Implements nodal equations for an LC lattice with configurable dimensions and boundary conditions.

## Running the Simulation
```bash
python sims/lc_grid_modes.py --nx 10 --ny 10 --tmax 200
	•	--nx, --ny: grid dimensions
	•	--tmax: simulation duration

Expected Output
	•	Visualizations of voltage distribution across the grid
	•	Frequency spectrum of emergent modes
	•	Identification of fundamental and higher-order grid resonances

Interpretation

The LC grid reveals how geometry shapes resonance.
Even when each unit is simple, their connections give rise to patterns — waves, beats, fields.
Like human networks: structure is choice, and choice is structure.

When tuned, the grid becomes an atlas of harmonics — a map not of objects, but of relationships.
