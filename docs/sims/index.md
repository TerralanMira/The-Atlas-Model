# Sim Stack: Field → Algorithms → Sims → Sessions → Learning

> Simulations here are not displays; they are instruments. Each run turns field laws into motion, logs the hum, and returns learning signals.

---

## One Loop (at a glance)

1. **Field → Algorithms**  
   - Dynamics & laws: Kuramoto coupling, Mirror Law, Choice-Collapse, Harmonic Gate, Return Spiral.  
   - Modules:  
     - `algorithms/resonance_dynamics.py` (Mirror, Collapse readiness/decision, HarmonicGate, Spiral)  
     - `algorithms/resonance_algorithms.py` (PLV, PPC, entropy coherence, MI)  
     - `algorithms/attractors.py` (maps/flows for driving)

2. **Algorithms → Sims**  
   - Runner: `sims/multi_scale_kuramoto.py`  
   - Presets: `sims/presets.json` (e.g., `circle6_center`, `grid_rect`)  
   - Output: CSV logs of `R_total, cross_sync, drift, ready, choice_score, …`

3. **Sims → Sessions**  
   - Ingest: `scripts/ingest_sessions.py` → `sessions/suggestions.json`  
   - Suggests small parameter deltas: `Δπ`, `ΔK` (Return Spiral)

4. **Sessions → Learning**  
   - You fold suggestions back into presets; next runs improve stability without coercion.

---

## Quickstart (two ways)

### A) Zero-friction smoke run (no long sim)
Creates tiny sample logs and runs ingest to prove the loop.

```bash
# deps
pip install -r requirements.txt

# make the script executable once
chmod +x scripts/smoke_run.sh

# run end-to-end
./scripts/smoke_run.sh
Expect:
	•	logs/sample_circle.csv, logs/sample_grid.csv created (if missing)
	•	sessions/suggestions.json printed with notes and small deltas

Actual sim runs (short examples)
Run two contrasting presets and ingest their logs.
# deps
pip install -r requirements.txt

# run sims (short examples)
python sims/multi_scale_kuramoto.py --preset circle6_center --csv logs/circle.csv
python sims/multi_scale_kuramoto.py --preset grid_rect        --csv logs/grid.csv

# summarize & propose small deltas
python scripts/ingest_sessions.py logs/circle.csv logs/grid.csv --out sessions/suggestions.json
cat sessions/suggestions.json
If you want to adjust steps, coupling, or permeability:
python sims/multi_scale_kuramoto.py \
  --preset circle6_center \
  --steps 2000 \
  --K 0.9 --pi 0.8 \
  --csv logs/circle_tuned.csv
Reading the Hum (how to interpret logs)
Each row represents a time step. Key columns:
	•	R_total — global coherence (0..1). Higher with smooth drift → healthy resonance.
	•	cross_sync — inter-cluster alignment (bridges between subfields).
	•	drift — mean wrapped phase change per step (lower is calmer; too low can over-lock).
	•	ready — choice-collapse readiness (high only when coherence and cross-sync support it).
	•	choice_score — >0 only when two reversible paths exist and consent is present.

Heuristics
	•	R_total↑ + cross_sync↑ + drift modest → resonance without coercion.
	•	R_total↑ + drift↓ near zero + ready high → risk of over-locking; consider lowering K or π.
	•	ready high but choice_score == 0 → structure lacks reversible options; adjust preset (offer_two_paths=true).

⸻

Presets (structure as teaching)

Examples in sims/presets.json:
	•	circle6_center — flower node (1 center + 6 ring).
	•	Encourages agency, often higher cross_sync without compressing diversity.
	•	grid_rect — rectangular lattice.
	•	Efficient, but prone to over-locking if K/π are too high.

You can add presets; include:
{
  "name": "my_preset",
  "geometry": "grid",
  "rows": 10,
  "cols": 10,
  "K": 0.8,
  "pi": 0.7,
  "offer_two_paths": true,
  "consent_to_log": true
}
From Sims to Learning (Return Spiral)

After ingest:
	•	Inspect sessions/suggestions.json.
	•	If note suggests Δπ = -0.05, edit the preset to reduce permeability slightly.
	•	Re-run; look for improved R_total with smooth drift, not clamp.

This small-delta loop embodies the Return Spiral — improvement without force.

⸻

Troubleshooting
	•	No CSV created? Ensure the --csv path’s directory exists (mkdir -p logs).
	•	Import errors? Check __init__.py files exist in algorithms/ and sims/.
	•	Long runtimes? Reduce --steps, or run the smoke test first.
	•	Docs fail to build? See mkdocs.yml and ensure pages listed there exist.

⸻

Pointers
	•	Algorithms: algorithms/resonance_dynamics.py, algorithms/resonance_algorithms.py
	•	Attractors: algorithms/attractors.py (for driving/experiments)
	•	Sessions: scripts/ingest_sessions.py, sessions/schema.json
	•	Philosophy & map: docs/awareness.md, docs/coherence.md, docs/field_layers.md, docs/integration.md

Principle: Coherence is invited, not forced. Choice before options, consent before collapse.
