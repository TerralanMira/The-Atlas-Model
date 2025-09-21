```markdown
# Sims Layer

Simulations let the field **move** so coherence can be seen, not just asserted.

- **Runner**: `sims/multi_scale_kuramoto.py` (schema-driven)
- **Seeds**: `sims/presets.json` (v1.0.0 schema; engines, geometries, groups/layers, feedback, ethics)
- **Docs**: `docs/sims/presets.md` (explanations, run notes, metrics)

## Design Notes
- Topologies: grid, circular, nested_spheres, flower_of_life
- Dynamics: Kuramoto coupling, optional ouroboros feedback
- Signals: `R_total, cross_sync, drift, C, Delta, Phi` (+ consent flags)

## Why it matters
Sims are the **practice ground**: where equations, ethics, and embodiment
converge. They feed the dashboard and teach the system to breathe.
