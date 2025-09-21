# Sim Stack — Field → Algorithms → Sims → Sessions → Learning

> These simulations are instruments, not demos.  
> Each run turns field laws into motion, logs the hum, and returns small deltas.

## One Loop

1. **Field → Algorithms**  
   Kuramoto dynamics, harmonic gating, readiness/choice, C/Δ/Φ signals.

2. **Algorithms → Sims**  
   `sims/multi_scale_kuramoto.py` + `sims/presets.json`  
   Output → CSV with: `R_total, cross_sync, drift, C, Delta, Phi, ready, choice_score`.

3. **Sims → Sessions**  
   `scripts/ingest_sessions.py` → `sessions/suggestions.json`  
   Gentle Return-Spiral nudges: `ΔK`, `Δπ`, and notes.

4. **Sessions → Learning**  
   You fold suggestions back into presets; the field improves without coercion.

## Presets

- **circle6_center** — center node with 6 around (flower geometry).  
- **grid_rect** — rectangular lattice (good stress test; watch for over-lock).

## Log Columns (interpreting the hum)

- `R_total` — global coherence (0..1)  
- `cross_sync` — bridge alignment across edges (0..1)  
- `drift` — mean wrapped phase change per step  
- `C` — coherence (local/edge-weighted)  
- `Delta` — diversity retained (phase-entropy, 0..1)  
- `Phi` — flow smoothness (lag-1 circular smoothness, 0..1)  
- `ready` — ethical readiness (consent + coherence + flow)  
- `choice_score` — >0 only when two paths + consent

## Return Spiral (small moves)

- Over-lock (Δ low, drift ~0) → reduce **K** a little, increase **π** a touch.  
- Under-coupled (R low, Δ high) → increase **K** slightly.  
- Flow rough (Φ low) → reduce noise/destabilizer or nudge **π** up.

**Principle:** Choice before collapse. Consent before logging. Reversibility before commitment.
