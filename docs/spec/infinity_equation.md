# Infinity Equation (Spec)
∞ = (whole ∈ part) = (part ∈ whole)
In software terms:

- Every `ResonanceObject` must expose:
  - `coherence()` → float in `[0,1]`
  - `metadata()` → dict (scale, role, provenance)

- Every `Coupler` must expose:
  - `forward(inputs: list[float], **params) -> float`  (returns new coherence)
  - `explain()` → human-readable description

- Every `Conductor` must expose:
  - `step(C: float, **state) -> dict` (returns parameter updates)
  - `target` property (e.g., `C*=0.7`)

These contracts let you build Earth↔Human↔Civic↔Cosmos graphs that compute and explain coherence.
