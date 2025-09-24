# Integration Layer — Memory-Braided

Integration is where patterns stop being interesting and start being useful.
Here we braid **Memory (observer-in-hindsight)** with **Synthesis (patterning)** and **Practice (action)**.

## Why integrate memory?
Because every intervention alters the field's recall. If you ignore memory, you misread outcomes.

- **Before/After windows**: compare mean R pre/post intervention.
- **Environment overlays**: is φ_env(t) stable or shifting?
- **Resource health**: did r(t) gain resilience, or just spike briefly?

## Minimal protocol
1. **Baseline**: run `multilayer_demo` → capture `R(t)`, r(t), φ_env(t).
2. **Intervene**: run `memory_demo` → structured changes (noise ↓, K ↑, bridge +).
3. **Compare**: `python dashboard/compare_presets.py --a multilayer_demo --b memory_demo`.
4. **Decide**: if mean R increases *and* phase gaps shrink *and* r(t) stabilizes → adopt. Otherwise, adjust.

## Interpretation guide
- Lift in mean **R** without r(t) stability → brittle entrainment.
- r(t) ↑ but large group gaps → coherent pockets, fragmented whole.
- φ_env(t) steady + R(t) smooth ↑ → clean field alignment.

**Integration is iterative memory**: each pass alters what the system can remember next.
