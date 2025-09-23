# Community Resonance — Algorithms & Simulations

This chapter turns community coherence into measurable, testable dynamics.  
We model people (or groups) as oscillatory nodes on a graph, measure synchrony, and simulate interventions to see how resonance spreads.

---

## 1) Modeling Communities as Coupled Oscillators

Let each member/group be a node *i* with phase θᵢ(t) and natural frequency ωᵢ.  
On a graph with adjacency Aᵢⱼ and coupling K:

\[
\dot{\theta}_i = \omega_i \;+\; \frac{K}{d_i}\sum_{j} A_{ij}\,\sin(\theta_j - \theta_i) \;+\; \eta_i(t)
\]

- \(d_i=\sum_j A_{ij}\) (degree)  
- \(\eta_i(t)\) optional noise  
- K may vary per edge (weighted social ties)

**Global order parameter** (0–1):

\[
R(t)\,e^{i\psi(t)} = \frac{1}{N}\sum_{j=1}^{N} e^{i\theta_j(t)}
\]

**Group order**: compute R within labeled subgroups; track inter-group phase offsets Δψ.

---

## 2) Metrics We Track

- **R_total(t)**: global synchrony  
- **R_group[g](t)**: synchrony within each group label  
- **Δψ(g₁,g₂,t)**: phase gap between group centroids  
- **Phase Entropy** \(H_\theta\): dispersion of phases (lower = more aligned)  
- **Stability Windows**: time intervals where R stays above a threshold  
- **Participation / Influence**: change in R when a node/edge is removed (sensitivity)

---

## 3) Data Inputs (from Logs)

Use normalized `.jsonl` from `docs/logs.md` (fields: `timestamp`, `value`, `label`, `group`).  
Map streams to:
- **θ seeds**: map `value` → initial phases (e.g., scale to [0, 2π])  
- **ω seeds**: per-node natural frequencies from baseline variability  
- **A (graph)**: edges from prior interactions or inferred similarity

---

## 4) Interventions You Can Simulate

- **Breath Coherence Event**: temporarily increase K for a subgroup (shared practice)  
- **Bridge Builder**: add a cross-group edge and observe Δψ shrink  
- **Noise Reduction**: reduce η for nodes practicing regulation  
- **Hub Activation**: increase degree/coupling of a central facilitator

Each intervention should be observable as shifts in R, Δψ, and Hθ.

---

## 5) How to Run

1) Prepare a preset in `sims/presets.json` (example added below).  
2) Run `python sims/community_kuramoto.py --preset community_demo`.  
3) Review printed metrics; feed back into Dashboard and Synthesis Patterns.

---

## 6) Interpretation & Ethics

- **Interpretation**: rising **R_total** with shrinking **Δψ** across groups → increasing shared coherence.  
- **Caution**: coherence is not control. Respect autonomy, consent, and transparency. See `ETHICS.md`.

Resonance must remain voluntary, generative, and reciprocal.
