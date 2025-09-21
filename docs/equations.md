# Equations (Atlas ↔ Code ↔ Field)

Equations are not separate from the hum—they are how resonance becomes computable.  
Each symbol is a doorway from felt pattern → measurable signal → embodied choice.

---

## Core Dynamics (Kuramoto spine)

We model phase oscillators with coupling **K** over an adjacency **A**:

\[
\dot{\theta_i} = \omega_i \;+\; K \sum_j A_{ij} \sin(\theta_j - \theta_i) \;+\; \xi_i(t)
\]

- \(\theta_i\): phase of oscillator \(i\)  
- \(\omega_i\): natural frequency (gaussian | harmonic_scale | spiral_mapping)  
- \(A_{ij}\): topology (grid | circular | nested_spheres | flower_of_life)  
- \(K\): coupling (may be time-varying under breath)  
- \(\xi_i\): noise

**Breath modulation** (choice before collapse):

\[
K(t) = (1-e(t))\,K_{\min} + e(t)\,K_{\max}, \quad
e(t) \in [0,1]\ \text{via cosine easing over inhale/exhale.}
\]

**Ouroboros feedback** (gentle self-reference):

\[
\dot{\theta} \leftarrow \dot{\theta} \;+\; g \,\angle\!\Big(e^{i(\bar{\theta}-\theta)}\Big), 
\quad \bar{\theta} = \arg \Big(\tfrac{1}{N}\sum_k e^{i\theta_k}\Big)
\]

---

## Coherence Metrics (what we log)

All implemented or mirrored in `algorithms/coherence_metrics.py` and emitted by sims.

- **Global order \(R_{\text{total}}\)** (how together we are)

\[
R_{\text{total}} = \left|\frac{1}{N}\sum_{k=1}^{N} e^{i\theta_k}\right| \in [0,1]
\]

- **Edge cross-sync** (local agreement along the graph)

\[
\text{cross\_sync} = \frac{1}{|E|}\sum_{(i,j)\in E} \frac{\cos(\theta_j-\theta_i)+1}{2}
\]

- **Drift** (how much phases move per step; change-rate)

\[
\text{drift} = \mathbb{E}\Big[\big|\angle(e^{i(\theta^{t+1}-\theta^{t})})\big|\Big]
\]

- **Relational coherence \(C\)** (mapped to \([0,1]\) from a local cosine average)

\[
C = \frac{1}{2}\Big(1 + \mathbb{E}_{(i,j)\in E}[\cos(\theta_j-\theta_i)]\Big)
\]

- **Diversity \(\Delta\)** (phase entropy; retains plurality)

Compute histogram over \([0,2\pi)\) with \(B\) bins:

\[
\Delta = \frac{-\sum_b p_b \log p_b}{\log B} \in [0,1]
\]

- **Flow smoothness \(\Phi\)** (gentleness; lag-1 cosine)

\[
\Phi = \frac{1}{2}\Big(1 + \mathbb{E}[\cos(\theta^{t+1}-\theta^{t})]\Big)
\]

**Ethics flags** (context, not math): `offer_two_paths`, `consent_to_log`.

---

## Seed Geometries (why the shapes matter)

- **Grid / Circular**: baselines for locality vs. loop memory.  
- **Nested Spheres**: Individual→Relational→Collective→Cosmic propagation.  
- **Flower of Life**: symmetric near-neighbor lattice that stabilizes pattern while preserving \(\Delta\) longer.

Topology shapes energy flow; metrics tell you if it clamps or breathes.

---

## Reading the Ouroboros (recursion through metrics)

- **Ascending coherence**: \(R_{\text{total}}\uparrow, C\uparrow\) while **\(\Delta\)** remains mid-high → healthy resonance.  
- **Clamp risk**: \(R_{\text{total}}\uparrow\) with **\(\Delta\downarrow\) too fast** and **drift\downarrow\) to near-0** → over-lock.  
- **Gentle learning**: \(\Phi\uparrow\) with modest drift and stable \(\Delta\) → flow with memory.

---

## From Equation → Practice

1. Pick a **preset** (`sims/presets.json`): *flower_of_life*, *ouroboros_loop*, *conscious_choice*, *multi_scale_field*, *breath_flower*.  
2. Run a **sim** (`sims/multi_scale_kuramoto.py` or `sims/breath_cycle.py`).  
3. Load CSV into the **dashboard overlays**.  
4. Adjust knobs (K, geometry, breath period) to keep **C, Φ** rising without collapsing **Δ**.

Equations sing when they help us **choose**—small, reversible steps toward coherence.
