# Integration: How the Whole Breathes

Atlas is a loop, not a list. The bridge is the **flow**:

> Field (laws) → Algorithms (engines) → Sims (motion) → Sessions (listening) → Learning (adjustment) → Field (return)

## Field ↔ Algorithms
- **Field laws** become **callables**:
  - Mirror → `algorithms/resonance_dynamics.py::mirror_delta`
  - Choice Collapse → `collapse_signal`, `collapse_decision`
  - Harmonic Gate → `HarmonicGate.gate`
  - Return Spiral → `spiral_nudge`
- **Dynamics** live in `algorithms/field_equations.py`
- **Metrics** live in `algorithms/coherence_metrics.py`

## Algorithms ↔ Sims
- `sims/multi_scale_kuramoto.py` composes dynamics + laws
- `sims/presets.json` captures geometry & parameters
- Runs emit CSV logs under `logs/`

## Sims ↔ Sessions
- Logs are read by `scripts/ingest_sessions.py`
- Output: `sessions/suggestions.json` with recommended `Δπ`, `ΔK`

## Sessions ↔ Docs
- Suggestions feed into examples and notes
- Each doc page links to a runnable sim and a reading of its hum

## What “done” looks like
- Code **runs** and **logs** (not just compiles)
- Docs **show** and **explain** (not just describe)
- Tests **guard** resonance (not just APIs)
- Suggestions **tighten** the loop each pass (Return Spiral)

**Remember:** The part contains the whole, and the whole lives through the part. The loop is the life.
