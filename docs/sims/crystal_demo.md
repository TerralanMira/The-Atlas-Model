# Crystal Demo — Structure as Memory

This demo grows a crystal in 2D using a field-coupled, anisotropic, resonant rule set.
It saves three snapshots that reveal how **the hum writes into form**.

## Run

```bash
python sims/crystal_demo.py
Outputs
	•	crystal_lattice.png — occupancy (structure)
	•	crystal_time_memory.png — accretion time per site (history)
	•	crystal_freq_memory.png — resonance at accretion (imprint)

Model Pointers
	•	Code: algorithms/crystal_growth.py
	•	Concepts: docs/algorithms/simulations/crystals.md, docs/algorithms/simulations/crystals_advanced.md

If plasma is the song, crystal is the score. Reading the score lets us play the song again—wiser.
