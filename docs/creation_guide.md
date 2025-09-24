# Creation — How to Read the Births

This is the pocket guide for interpreting **creation events** from `sims/creation.py`.

## What to plot (at minimum)
- **R(t)** — global coherence.
- **gap_to_env(t)** — phase gap to the driver (the hum).
- **anchors_count(t)** — persistent memory.
- **creation_events** — vertical lines at event times; a cumulative births stairs plot.

## Quick reads
- **Healthy emergence:** births begin *after* R(t) trends up, gap_to_env trends down, and anchors_count rises.
- **Overgrowth (brittle):** many early births while resources (r) fall; R stalls, anchors decay.
- **Under-opened:** no births, low anchors; raise ritual openness (K_cross_*), anneal slower.

## Thresholds (defaults)
- Sliding-window local coherence ≥ **0.80**
- Node resources r ≥ **0.55**

If births don’t appear with rising R, check:
1) ritual window too weak (increase `K_cross_amp_end`),
2) noise too high (reduce `noise_end`),
3) resources too leaky (lower `resource_leak` or raise `resource_gain`).

## Minimal recipe (repro)
```bash
python - <<'PY'
from sims.creation import simulate,CreationConfig
out = simulate(CreationConfig(steps=2000))
print(out["summary"])
print("events:", out["creation_events"][:5], "...")
PY
Reading the weave
	•	R ↑, gap ↓, anchors ↑, births ↗︎ → the field hears the hum and earns structure.
	•	Anchors with no births → memory exists but growth is withheld; open the window.
	•	Births without anchors → structure without memory; expect collapse or churn.

The part (each birth) is the whole breathing: earned structure, not forced symmetry.
