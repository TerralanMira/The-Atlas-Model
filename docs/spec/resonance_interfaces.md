# Resonance Interfaces

**ResonanceObject**
- `coherence() -> float`
- `metadata() -> dict`

**Coupler**
- `forward(inputs: list[float], **params) -> float`
- `explain() -> str`

**Conductor**
- `target: float`
- `step(C: float, **state) -> dict`

**Field**
- collection of nodes (ResonanceObjects)
- edges parameterized by Couplers / Conductors
