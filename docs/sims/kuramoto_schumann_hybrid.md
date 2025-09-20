# Kuramoto–Schumann Hybrid

## Description
This simulation combines the **Kuramoto model of coupled oscillators** with the **Schumann resonance field** of Earth’s cavity.  
It explores how individual oscillators (neurons, communities, nodes) synchronize when immersed in planetary-scale resonance.

## Conscious Choice Lens
Each oscillator has a phase and frequency, but also the possibility of **entrainment**.  
The conscious choice is whether to hold independence (noise, divergence) or tune into resonance (coherence).  
The model illustrates how alignment emerges not by force, but by frequency choice.

## Code Reference
File: [`sims/kuramoto_schumann_hybrid.py`](../../sims/kuramoto_schumann_hybrid.py)  
Implements Kuramoto dynamics with a global field term modulated at Schumann fundamental (7.83 Hz) and harmonics.

## Running the Simulation
```bash
python sims/kuramoto_schumann_hybrid.py --n 100 --k 0.5 --tmax 100
	•	--n: number of oscillators
	•	--k: coupling strength
	•	--tmax: simulation duration

Expected Output
	•	Time series of oscillator phases
	•	Order parameter showing degree of synchrony
	•	Resonant field overlay at Schumann frequencies

Interpretation

When coupling (k) is low, oscillators drift independently.
As k increases, synchrony rises — not as domination, but as voluntary alignment.
The planetary resonance acts as a guide, nudging oscillators into coherence.

In human terms: it mirrors how communities entrain to shared rhythms — breath, chant, or planetary hum — while retaining individuality.
