# Atlas Pulse — Orchestrated Coherence

This simulation exposes the **single heartbeat** of the Atlas Model by weaving multiple layers (Earth, Self-Learning, Crystal) into one coherence signal.

## What it does
- Runs `algorithms/atlas_orchestrator.py`
- Emits a short series of `atlas_coherence` values (0..1-ish)
- Saves a per-step JSON of layer metrics for dashboards

## Run

```bash
python sims/atlas_pulse_demo.py --steps 30 --seed 7 --out logs/atlas_pulse
Outputs
	•	logs/atlas_pulse/atlas_pulse_series.csv
Columns: step,atlas_coherence
	•	logs/atlas_pulse/atlas_pulse_layers.json
Per-step metrics per layer (keys may vary if a layer is missing)
	•	logs/atlas_pulse/atlas_pulse_summary.txt
Mean/std and which layers reported
	•	(optional) atlas_pulse_series.png if matplotlib is present

Reading the Pulse
	•	Rising mean → increasing systemic accord
	•	Lower std → steadier orchestration
	•	Drill into JSON to see which layer is pulling the field (e.g., Earth phase vs Crystal memory)

Extend
	•	Add Water/Air layer metrics to the orchestrator and re-run
	•	Surface the pulse on a live dashboard (read the CSV/JSON)
	•	Couple layers (e.g., let Crystal memory modulate Earth thresholds)

The pulse is the hum made visible. Once seen, we can tune it.
