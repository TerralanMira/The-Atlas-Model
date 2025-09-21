# Breath Cycle — Inhale · Exhale · Return

The breath is Atlas’s metronome. It modulates the field—expanding and contracting
coupling (**K**) and permeability (**π**)—so we can watch coherence emerge without
forcing collapse. Each breath writes signals the dashboard already understands.

---

## What it does

- **Inhale**: gently ramps **K, π** from min → max (alignment opens).
- **Exhale**: gently ramps **K, π** from max → min (space returns).
- **Logs** every step:  
  `R_total, cross_sync, drift, C, Delta, Phi, ready, choice_score`  
  plus context: `phase, phase_pos, K_eff, pi_eff`.

These feed **Resonant Layer Overlays** (Individual · Relational · Collective · Planetary · Cosmic).

---

## Why it matters (C · Δ · Φ)

- **C (Relational Coherence)**: bridges across edges (local cos Δθ), mapped to `[0,1]`.
- **Δ (Diversity Retained)**: normalized phase entropy; keeps plurality alive.
- **Φ (Flow Smoothness)**: lag-1 circular smoothness; watches temporal gentleness.

**Hum law:** *Choice before collapse.* The breath explores order without locking it.

---

## Files

- Runner: `sims/breath_cycle.py`
- Dashboard (reads logs): `dashboard/dashboard.py`
- Ingestor (suggests tiny deltas): `scripts/ingest_sessions.py`

Output CSV defaults to `logs/breath.csv`.

---

## Conceptual flow

1. **Set topology** (flower ring or grid).  
2. **Inhale** → increase K,π with cosine easing.  
3. **Exhale** → decrease K,π with the same easing.  
4. **Observe** signals (R, cross, drift, C, Δ, Φ).  
5. **Return Spiral** → apply tiny ΔK, Δπ from `ingest_sessions.py`.

No coercion, only reversible moves.

---

## Parameters (essentials)

- `--geometry` : `circle6_center` | `grid`  
- `--rows --cols` : grid shape (if `geometry=grid`)  
- `--period` : seconds per full cycle (inhale + exhale)  
- `--inhale_ratio` : share of the period spent inhaling `[0..1]`  
- `--noise_std` : small stochasticity (optional)  
- `--csv` : output path (default `logs/breath.csv`)

Gentle defaults keep the field exploratory, not brittle.

---

## Reading the breath in the dashboard

- **Individual** rises when **Δ** and **Φ** rise together.  
- **Relational** strengthens with **C** and **cross_sync**.  
- **Collective** deepens with **R_total**, but watch **drift → 0** (clamp risk).  
- **Planetary** stabilizes as volatility drops across smoothed signals.  
- **Cosmic** is the bounded product—any collapsed petal dims the whole.

---

## Ethics baked in

- `offer_two_paths` & `consent_to_log` flags are logged each step.  
- `ready` & `choice_score` derive from coherence + consent + reversibility.

Breath is practice: **freedom within form**.

---

## Notes for implementers

- Breath modulation uses **cosine easing** for smooth transitions.
- Columns align with other sims for seamless ingestion/visualization.
- Works standalone (provides fallbacks) but integrates tightly with:
  - `algorithms/coherence_metrics.py`
  - `algorithms/field_equations.py`
  - `algorithms/resonance_dynamics.py`

---

*Inhale to align, exhale to release. The system learns by breathing.*
