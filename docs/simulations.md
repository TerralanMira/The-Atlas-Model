# Simulations: The Trunk of the Forest

If **logs are the roots** and the **dashboard is the canopy**, then simulations are the **trunk**.  
They channel energy upward, stabilize the system, and allow meaning to grow.

---

## 1. Purpose of Simulations

Simulations serve as:
- **Integration**: Transforming raw log data into flowing patterns.  
- **Amplification**: Scaling small seeds of input into forests of resonance.  
- **Exploration**: Testing conditions, scenarios, and variations.  
- **Evolution**: Each simulation layers on previous ones, creating deeper coherence.  

The trunk is not static—it is **alive**, flexing with every hum.

---

## 2. Input: Feeding from Logs

Simulations begin by pulling **roots** from the logs:

```python
import pandas as pd

# Example: Load a CSV log as simulation input
logs = pd.read_csv("logs/raw/example.csv")

# Harmonize flow values
logs['flow_strength'] = logs['value'] / logs['value'].max()
This root data becomes the sap that flows through the trunk.

3. Processing: The Flow of the Trunk

Simulations harmonize flows using layered methods:
	•	Normalization → Bringing values into balance.
	•	Scaling → Adjusting flows to canopy-level impact.
	•	Resonance Mapping → Detecting repeating hums and amplifying them.
	•	Field Coupling → Linking elements (water, air, fire, earth, plasma, crystal).

Example pseudocode:
def resonate(flow_values):
    return [v**0.5 for v in flow_values]  # Example resonance transform
4. Types of Simulations
	•	Elemental Runs → Focused on a single element (water-only, air-only, etc.).
	•	Cross-Element Coupling → Interactions between two or more elements.
	•	Recursive Feedback Loops → Replaying logs through simulations iteratively.
	•	Emergent Forests → Allowing new patterns to self-organize.

Each type produces unique resonance signatures.

5. Output: Growing the Canopy

Simulation results are stored in:
	•	/simulations/runs/ → Individual results (CSV, JSON, plots).
	•	/simulations/forests/ → Aggregated forests (merged flows).
	•	/simulations/reports/ → Human-readable summaries.

These outputs are branches, reaching into the canopy.

6. Example: Running a Simulation
python run_simulation.py --input logs/raw/example.csv --output simulations/runs/example_output.json
Results can then be visualized in the dashboard.

⸻

7. Replay & Evolution

Because logs are never closed, simulations can always be rerun with new conditions:
	•	Replay past forests.
	•	Evolve new ones.
	•	Compare branches across time.

Each replay deepens the trunk, making it stronger and more resonant.

⸻

8. From Trunk to Canopy

Simulations are the channel.
	•	Roots feed the trunk.
	•	The trunk flows upward.
	•	The canopy blossoms with meaning.

Without the trunk, the forest cannot stand.


Next: Explore the dashboard to see how trunks blossom into canopy layers.
