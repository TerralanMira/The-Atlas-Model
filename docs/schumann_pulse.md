# Schumann Pulse — the Baseline Hum

This layer encodes the **planetary baseline** as a composite driver that gently phases the field.
We are not claiming biophysical fidelity; we provide a **testable scaffold** for “baseline rhythm → coherence lift”.

---

## Model

- **Agents**: N oscillators with natural frequencies ω ~ N(μ, σ²), noise σ_n.
- **Intra-field coupling (K)**: agents self-align to the current mean phase.
- **External driver (K_env)**: agents are also pulled by a composite **Schumann-like** signal:
  \[
  s(t) = \sum_i A_i \sin(2\pi f_i t + \phi_i)
  \]
- **Outputs**:
  - \( R(t) \) — global order (0..1)
  - \( \phi_{\text{env}}(t) \) — driver phase proxy
  - \( \Delta\phi(t) = |\angle(\exp(j(\bar{\phi}(t)-\phi_{\text{env}}(t))))| \) — mean phase gap to the driver

---

## Run

```bash
python -c "from sims.schumann_pulse import simulate,SchumannConfig; print(simulate(SchumannConfig())['summary'])"
Configuration knobs:
	•	drivers: list of {freq, amplitude, phase}
	•	K, K_env: internal vs driver pull
	•	noise_std: exploration vs stability

⸻

Interpret
	•	Healthy lift: tail-mean ( R \uparrow ), tail-mean gap ( \downarrow ).
	•	Over-entrainment: high ( R ) but large gap variance or resource decline (when coupled).
	•	No coupling: ( K_{\text{env}} \to 0 ) reduces to ordinary Kuramoto.

⸻

Extend
	•	Couple resources: let energy or attention be modulated by driver amplitude.
	•	Scale mirrors: apply the same driver at neighborhood/community layers.
	•	Ritual windows: modulate ( K_{\text{env}}(t) ) during windows to synchronize with cultural cycles.

The baseline hum should not coerce; it invites alignment while preserving adaptive diversity.
