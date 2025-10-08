# Synchronization-Led Emergence (Toy Kuramoto Model)

**Scope.** A computational experiment showing how **phase coupling + bounded growth**
can yield an abrupt, stable structure (an emergent “event”).  
**Not a claim** about cosmology or biology.

## Equations

Oscillators \(i=1..N\):
\[
\dot{\theta_i} = \omega_i + \frac{K(t)}{N} \sum_j \sin(\theta_j - \theta_i) + A_{\text{drive}}\sin(2\pi f_{\text{drive}} t + \phi)
\]

Order parameter:
\[
R(t)e^{i\psi(t)} = \frac{1}{N}\sum_j e^{i\theta_j(t)},\quad R\in[0,1]
\]

Coupling growth:
\[
\dot{K} = \alpha\;\max(0,\;R - R_{\text{thresh}})\,(K_{\max}-K) - \beta\,(K-K_{\min})
\]

**Event** (see `algorithms/creation_protocols.py`):
- Upward crossing through \(R_{\text{event}}\) with hold time \(T_{\text{hold}}\);
- Guards on \(K\) and (optionally) on a local anchor fraction.

## How to run

```bash
python -m sims.creation_demo
# Outputs:
#   data/creation/run_{seed}.csv
#   figures/creation_R_K_{seed}.png
What to look for
	•	(R(t)) rises above the event threshold and stays elevated (hold time).
	•	(K(t)) increases only when (R(t) > R_{\text{thresh}}) and saturates below (K_{\max}).
	•	Event markers (red lines) align with the sustained high-coherence plateau.

Claims & Limits
	•	Demonstrates: a clear mechanism by which coherence + growth rules
can trigger abrupt stability (emergence) in a coupled-oscillator field.
	•	Does NOT claim: cosmological “creation,” biological “genesis,” or brain-equivalence.
	•	Use: as an intuitive bridge between resonance reasoning and testable dynamics.
