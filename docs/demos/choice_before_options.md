# Demo: Choice Before Options

This demo shows how structure + permeability (π) + choice-practice change coherence.

We compare two presets:

- **circle6_center** — Flower-of-Life petal (agency-preserving), `offer_two_paths=true`, `π=0.8`
- **grid_rect** — rectangular lattice (compressive), `offer_two_paths=false`, `π=0.5`

## Run

```bash
pip install -r requirements.txt
python sims/multi_scale_kuramoto.py --preset circle6_center --csv logs/circle.csv
python sims/multi_scale_kuramoto.py --preset grid_rect        --csv logs/grid.csv
python scripts/ingest_sessions.py logs/circle.csv logs/grid.csv --out sessions/suggestions.json
Read
	•	higher R_total + cross_sync in circle6_center
	•	choice_score > 0 only when offer_two_paths=true and consent_to_log=true
	•	sessions/suggestions.json proposes small Δπ, ΔK

Teaching: Coherence is not forced. It emerges when structure, permeability, and choice align.
