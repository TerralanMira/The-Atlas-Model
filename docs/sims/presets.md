# Simulation Presets (Schema v1.0.0)

Presets encode **seed geometries** and **run params** the engine can read directly.
They are the living “starting chords” of resonance experiments.

---

## Schema (essentials)

- **meta.defaults**: global fallbacks for `engine, steps, dt, seed, noise_std, output_csv, metrics`.
- **presets[NAME]**: one experiment each. Common fields:
  - `engine`: `kuramoto` | `breath`
  - `geometry`: `{ name: grid|circular|nested_spheres|flower_of_life, ... }`
  - `num_oscillators` *or* `groups[]` *or* `layers[]`
  - `coupling_strength` or per-group/per-layer `K`
  - `omega`: `{ distribution: gaussian|harmonic_scale|spiral_mapping, ... }`
  - `noise_std`, `steps`, `dt`, `seed`, `output_csv`
  - optional `feedback` (e.g., `{type: "ouroboros", gain: 0.15}`)
  - ethics flags: `offer_two_paths`, `consent_to_log` (for `engine: breath`)

---

## Included Presets

### 1) `default`
Baseline grid Kuramoto with Gaussian ω.  
Use to sanity-check the runner and dashboard ingestion.

### 2) `flower_of_life`
**Geometry**: 3-ring Flower-of-Life lattice (center + hex rings).  
**Why**: tests how symmetry + near-neighbors stabilize phase patterns.  
**Watch**: `R_total` rise without Δ (diversity) collapsing too fast.

### 3) `ouroboros_loop`
**Geometry**: circular ring; **Feedback**: loop-average phase nudges each node.  
**Why**: probe self-reference and clamp risk.  
**Watch**: `R_total↑`, `drift↓`; if `Delta` drops too quickly, clamp alert.

### 4) `conscious_choice`
**Groups**: A (aligned, high K) vs B (dissonant, lower K), blended by `choice_parameter ∈ [0,1]`.  
**Why**: model decision dynamics between coherence and plurality.  
**Watch**: `C` vs `Delta` trade; sweet spot keeps both alive.

### 5) `multi_scale_field`
**Layers**: Individual → Relational → Collective → Cosmic with increasing N, K.  
**Why**: field propagation across scales.  
**Watch**: interlayer stability; radial couplings too strong can over-lock.

### 6) `breath_flower` (engine: `breath`)
**Modulation**: cosine easing of K,π over a breath period.  
**Why**: explore reversible coherence—*choice before collapse*.  
**Watch**: `Phi` (smoothness) and ethics flags in logs.

---

## Metrics (CSV columns)

- `R_total` (global order)  
- `cross_sync` (edge-pair phase agreement)  
- `drift` (mean phase change per step)  
- `C` (relational coherence, mapped to [0,1])  
- `Delta` (phase entropy; diversity retained)  
- `Phi` (lag-1 smoothness; flow gentleness)  
- ethics context: `offer_two_paths`, `consent_to_log`

These align with the dashboard overlays (Individual, Relational, Collective, Planetary, Cosmic).

---

## How to Run

```bash
# default baseline
python sims/multi_scale_kuramoto.py --preset default

# sacred geometry
python sims/multi_scale_kuramoto.py --preset flower_of_life

# self-reference
python sims/multi_scale_kuramoto.py --preset ouroboros_loop

# decision dynamics
python sims/multi_scale_kuramoto.py --preset conscious_choice

# layers across scales
python sims/multi_scale_kuramoto.py --preset multi_scale_field

# breath-modulated lattice (if breath engine runner is available)
# python sims/breath_cycle.py --preset breath_flower
