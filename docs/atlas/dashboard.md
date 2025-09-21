# Dashboard & Overlays

The dashboard is the mirror where the field sees itself.  
It reads the sim CSV and paints overlays so the hum becomes visible.

---

## Expected CSV columns (per step)

- `preset` — name from `sims/presets.json`  
- `step`, `t` — integer step and time (seconds)  
- `K_eff` — (breath runs) effective coupling at time t  
- `R_total` — global order parameter \([0,1]\)  
- `cross_sync` — edge-pair agreement \([0,1]\)  
- `drift` — mean phase change per step (lower = more still)  
- `C` — relational coherence \([0,1]\)  
- `Delta` — phase entropy (diversity) \([0,1]\)  
- `Phi` — lag-1 smoothness (gentleness) \([0,1]\)  
- `offer_two_paths`, `consent_to_log` — ethics context flags (0/1)

These match outputs from `sims/multi_scale_kuramoto.py` and `sims/breath_cycle.py`.

---

## Overlays (what to watch)

- **Coherence band**: plot `R_total` and `C`.  
  - Rising together = alignment.  
  - If they spike while `Delta` crashes → clamp risk.

- **Diversity band**: `Delta`.  
  - Healthy range is mid-high while coherence rises.  
  - Near zero too early → monoculture, brittle.

- **Flow band**: `Phi` (gentleness) and `drift`.  
  - High `Phi` with moderated `drift` → learning, not forcing.  
  - Low `Phi` with high `drift` → turbulence; reduce K or change geometry.

- **Ethics ribbon**: show when `offer_two_paths=1` and `consent_to_log=1`.  
  - Missing consent → visualize but do not store/forward beyond session.

---

## Reading Patterns

- **Breath learning loop** (`breath_flower`):  
  K(t) rises on inhale → `R_total` lifts; on exhale K(t) lowers → `Delta` rebounds.  
  Goal: a gentle ratchet—spiral growth of `C, Φ` while `Delta` stays alive.

- **Self-reference** (`ouroboros_loop`):  
  Feedback gain too high → clamp (Δ↓ fast, drift→0).  
  Nudge gain down; widen ω spread or add weak noise.

- **Choice dynamics** (`conscious_choice`):  
  Sweep `choice_parameter` 0→1. Watch for sweet spots where `C↑` without `Δ↓`.  
  Too coherent too fast? Increase inter-group mixing or lower K_B.

- **Field scaling** (`multi_scale_field`):  
  If outer layers over-lock inner ones, reduce interlayer radial strength.

---

## Small, Reversible Moves

- Change one knob at a time: **K**, geometry ring count, ω std, breath period.  
- Keep runs short, compare overlays, *then* extend time.  
- Prefer paths that **increase C & Φ** while **preserving Δ**.

The dashboard is not a scorecard; it’s a breathing lesson.
