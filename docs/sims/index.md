# Sim Stack: Field → Algorithms → Sims → Sessions → Learning

Atlas simulations are not displays; they are *instruments*. Each run turns field laws into motion, logs the hum, and returns learning signals.

## Stack (one loop)

1. **Field → Algorithms**  
   - Kuramoto / LC grid / multi-scale coupling (dynamics)  
   - Mirror / Choice Collapse / Harmonic Gate / Return Spiral (laws)  

2. **Algorithms → Sims**  
   - Presets define structure (geometry, π, K, cadence, breath)  
   - Runs produce phase arrays over time and coherence metrics

3. **Sims → Sessions**  
   - CSV logs: `R_total, R_mean, cross_sync, drift, ready, choice_score`  
   - Stored under `logs/` (input to learning)

4. **Sessions → Learning**  
   - `scripts/ingest_sessions.py` summarizes runs and proposes small parameter deltas (`Δπ, ΔK`) into `sessions/suggestions.json`

5. **Learning → Field**  
   - Suggestions inform the next preset or doc examples (Return Spiral)

## Run a demo

```bash
pip install -r requirements.txt

# Two contrasting presets
python sims/multi_scale_kuramoto.py --preset circle6_center --csv logs/circle.csv
python sims/multi_scale_kuramoto.py --preset grid_rect        --csv logs/grid.csv

# Summarize + propose small deltas
python scripts/ingest_sessions.py logs/circle.csv logs/grid.csv --out sessions/suggestions.json
Read the hum
	•	Higher R_total and cross_sync with smoother drift → resonance is stable.
	•	ready high but R_total low → over-lock risk → reduce π or K.
	•	choice_score > 0 only when ≥2 reversible paths + consent.

Principle: Coherence is not forced. It emerges when structure, permeability, and choice align.
