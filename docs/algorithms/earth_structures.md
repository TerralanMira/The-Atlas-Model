# Earth Structures: Lattices, Thresholds, Attractors

The Earth layer gives the Atlas Model **structure and stability**.  
This page explains how the code in `algorithms/earth_structures.py` models grounding.

---

## Components

### 1) Lattices (Grid Graphs)
- A 2D grid with 4-neighborhood connectivity (optionally **periodic** → torus).
- Provides **channels** for diffusion and synchronization.
- Functions: `lattice_adjacency`, `row_normalize`, `lattice_laplacian`.

**Why:** Structure is the container that prevents flows from scattering.

---

### 2) Threshold Field (Inertia)
- A spatial field representing **resistance to change**.
- If a proposed change is below the local threshold, it’s damped to zero.
- Class: `ThresholdField` with `constant()` and `gradient()` builders.

**Why:** Earth holds shape. Small, noisy perturbations shouldn’t move the ground.

---

### 3) Multi-Well Potential (Attractor Basins)
- A **multi-stable** landscape (biwell/triwell) that states relax into.
- Class: `MultiWellPotential` with `grad()` for descent.

**Why:** Grounding prefers certain stable forms; basins encode those preferences.

---

### 4) Kuramoto on Lattice (Phase Coherence)
- Phase oscillators on the same grid.
- Neighbor influence induces **synchronization** (phase locking).
- Functions: `kuramoto_step`, `phase_locking_value`.

**Why:** Coherence isn’t only amplitude; **phase alignment** matters.

---

## Composite Earth Step

Function: `earth_step(...)`  
Order of operations:
1. **Diffuse** scalar state on lattice.  
2. Apply **threshold** damping (inertia).  
3. **Relax** into attractor basins (multi-well).  
4. Advance **Kuramoto** phases (lattice synchronization).

Outputs: updated scalar field + phases.

---

## Coherence Metrics
- **Amplitude coherence**: `variance_coherence(x)` → higher when variance is low.  
- **Phase coherence**: `phase_locking_value(phases)` (Kuramoto order parameter).  
- **Combined**: average of the two.

---

## Usage

See `sims/earth_demo.py` for a runnable example that:
- Builds a periodic grid
- Applies a gradient threshold field
- Uses a tri-well potential
- Runs composite steps and prints coherence

---

## Interpretation

- Rising **amplitude coherence** → the scalar field is stabilizing.
- Rising **phase coherence** → oscillators are synchronizing.
- Stable **combined coherence** → grounded, resilient structure.

> Earth is not static; it is **stable motion**: diffusion within bounds,  
> change above thresholds, and convergence toward form.
