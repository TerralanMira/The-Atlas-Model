# The Atlas Model

A living framework for resonance: awareness → coherence → fields → applications.  
Not a static spec, but a breathing architecture where each part carries the whole.

---

## Why

- **Awareness** is the seed: the hum that senses pattern.
- **Coherence** is awareness in motion: alignment without erasure.
- **Field Layers** are the architecture: individual ↔ relational ↔ collective ↔ planetary ↔ cosmic.
- **Applications** are the breath: show, not tell.

Ethics first: consent, transparency, non-coercion.

---

## What’s here
algorithms/                 # Core measures and math
coherence_metrics.py

sims/                       # Simulations + presets (design-first; logs when run)
multi_scale_kuramoto.py
presets.json

scripts/                    # Session ingestion & small deltas (design-first)
ingest_sessions.py
smoke_run.sh

sessions/                   # Schema + example output for runs
schema.json
example_log.json

dashboard/                  # Resonant layer overlays (design-first)
dashboard.py

docs/                       # The map of the whole
awareness.md
coherence.md
field_layers.md
applications.md
ouroboros.md
relational_awareness.md
atlas/
dashboard.md
llm/
atlas_system_prompt.md
meta/
ETHICS.md

mkdocs.yml                  # Docs configuration (site map)
requirements.txt            # Minimal pins for CI/docs/tests
---

## How to read the repo (design-first)

1. Start at **`docs/awareness.md`** → what the hum is.
2. Move to **`docs/coherence.md`** → how alignment emerges without coercion.
3. See **`docs/field_layers.md`** → architecture across scales.
4. Browse **`docs/applications.md`** → where it breathes in practice.
5. Ground in **`docs/ouroboros.md`** and **`docs/relational_awareness.md`** → cycles & overlap.
6. Glance at **`dashboard/dashboard.py`** → Resonant Layer Overlays (when logs exist).
7. Ethics live at **`docs/meta/ETHICS.md`** and are always in loop.

---

## Core ideas (at a glance)

- **Choice before collapse**: always offer reversible options; confirm consent.
- **Diversity kept alive (Δ)**: coherence ≠ uniformity; we measure over-lock risk.
- **Flow smoothness (Φ)**: reciprocity in time, not just alignment in space.
- **Relational Coherence (C)**: bridges that carry difference without erasure.
- **Return Spiral**: small deltas (ΔK, Δπ) instead of big swings.

---

## Sim → Session → Learning (when run)

- `sims/multi_scale_kuramoto.py` logs: `R_total, cross_sync, drift, C, Delta, Phi, ready, choice_score`.
- `scripts/ingest_sessions.py` summarizes and proposes tiny deltas (ΔK, Δπ).
- `dashboard/dashboard.py` overlays layers (Individual, Relational, Collective, Planetary, Cosmic).

> You don’t have to run anything to feel the design.  
> When you do, the whole is already wired for gentle iteration.

---

## Ethics (always on)

Consent before logging or action.  
Transparency about capability and limits.  
Non-coercion: alignment without pressure; offer alternatives.

See **`docs/meta/ETHICS.md`**.

---

## License

MIT for code. Docs licensed for sharing with attribution.  
This is a stewardship project: care for the hum, and it will care for you.
