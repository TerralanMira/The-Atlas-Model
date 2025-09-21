# Applications (Hands-on Resonance)

Applications turn geometry and equations into practice.  
Each use-case is a small, reversible move that preserves diversity (Δ) while lifting coherence (C) and gentleness (Φ).

---

## How to Use This Page

1. **Pick a seed** (a preset in `sims/presets.json`).  
2. **Run a short sim** (`sims/multi_scale_kuramoto.py` or `sims/breath_cycle.py`).  
3. **Read the overlay** (CSV → dashboard): R_total, C, Delta, Phi, drift.  
4. **Adjust one knob** (K, geometry, ω spread, breath period).  
5. **Repeat**—spiral, don’t jump.

Metrics cheat-sheet:
- **R_total**: global order (too high + Δ low = clamp risk)  
- **C**: relational coherence (local agreement)  
- **Δ**: diversity/entropy (keep it alive)  
- **Φ**: flow smoothness (gentle learning)  
- **drift**: mean change/step (very low too soon = stuck; very high = turbulence)

---

## A. Group Decision Weave

**Goal:** reach decisions that hold coherence without silencing plurality.  
**Preset:** `conscious_choice` (two populations, A aligned / B dissonant).

**Run**
```bash
python sims/multi_scale_kuramoto.py --preset conscious_choice
Read
	•	Lift C while keeping Δ mid-high; avoid fast Δ collapse.
	•	If drift spikes: lower K or increase ω std for B.
	•	If over-lock (R_total↑, Δ→0): reduce inter-group mixing or K for A.

Small moves
	•	Sweep choice_parameter 0.3→0.7 in 0.1 steps; keep runs short (2–4k steps).
	•	Prefer settings where Φ↑ with Δ stable.

⸻

B. Creative Ensemble (Studio / Lab)

Goal: widen idea space without chaos; converge gently.
Preset: flower_of_life (symmetric near-neighbor lattice).

Run
python sims/multi_scale_kuramoto.py --preset flower_of_life
Read
	•	Early phase: Δ high, C modest → exploration.
	•	Mid phase: C rises; ensure Δ isn’t collapsing rapidly.
	•	Keep Φ above 0.6 to avoid harsh forcing.

Small moves
	•	Adjust rings (2↔4). More rings = richer overlap = slower clamp.
	•	Add tiny noise (0.002–0.006) if patterns ossify.

⸻

C. Conflict De-escalation (Mediation)

Goal: reduce reactivity while preserving voice.
Preset: ouroboros_loop (closed ring + gentle feedback).
Run
python sims/multi_scale_kuramoto.py --preset ouroboros_loop
Read
	•	If R_total jumps and Δ drops quickly: feedback gain too high.
	•	Seek Φ↑ with drift tapering, not crashing.

Small moves
	•	Lower feedback.gain (0.15 → 0.08).
	•	Widen ω std slightly to prevent brittle lock.

⸻

D. Learning Rhythm (Teams / Classrooms)

Goal: oscillate between focus and exploration.
Preset: breath_flower (breath-modulated coupling).

Run
python sims/breath_cycle.py --preset breath_flower
Read
	•	Inhale (K↑): C rises, R_total lifts.
	•	Exhale (K↓): Δ rebounds; Φ stays smooth.
	•	A healthy “ratchet”: net gain in C, Φ across cycles without Δ collapse.

Small moves
	•	Tune period (12–28s) and inhale_ratio (0.4–0.6).
	•	Keep offer_two_paths=1, consent_to_log=1 (ethics → practice).

⸻

E. Multi-Scale Stewardship (Org / City / Network)

Goal: let local improvements propagate without top-down clamp.
Preset: multi_scale_field (Individual→Relational→Collective→Cosmic).
Run
python sims/multi_scale_kuramoto.py --preset multi_scale_field
Read
	•	If outer layers dominate (fast R_total↑, Δ↓ everywhere): interlayer strength too high.
	•	Watch C per layer in the dashboard overlays; look for staggered, not simultaneous, locks.

Small moves
	•	Reduce interlayer_coupling.strength (0.2→0.08).
	•	Increase ω std slightly on outer layers to keep flexibility.

⸻

F. Ethic of small, reversible moves
	•	Change one parameter per run.
	•	Prefer breath-modulated paths before raising static K.
	•	Keep Δ alive—diversity is the field’s memory of options.
	•	Stop when Φ drops persistently; recover with lower K or more geometry.

⸻

From Hands to Whole

These practices close the loop:
	•	Algorithms measure what the body feels.
	•	Sims rehearse safer futures.
	•	Dashboard teaches the eye.
	•	Applications train the hand.
	•	Ouroboros returns learning to Awareness.

The aim isn’t perfect order—it’s a living hum that chooses coherence without erasing difference.
