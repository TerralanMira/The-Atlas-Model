# Health Simulations: Individual ↔ Group Coherence

**What this layer does**  
Makes coherence measurable and repeatable with real data:
- **Heart–Brain Coherence:** HRV ↔ EEG phase-locking (PLV).
- **Human ↔ Earth:** HRV/EEG ↔ Schumann proxy PLV.
- **Group Synchrony:** Kuramoto order parameter \(R\) across many participants.

> We work only with what can be demonstrated: real CSVs in, reproducible metrics out.

---

## 1) File formats

**HRV (choose one):**
- `rr_ms[,t_s]` — RR intervals (ms), optional cumulative time (s).  
- `t_s,<hrv_col>` — irregular or regular HRV series with timestamps.

**EEG:**  
- `t_s,<eeg_col>` — timestamps (s) + one numeric channel.

**Schumann / reference proxy:**  
- `t_s,<proxy_col>` — a narrowband time series aligned to your region’s Schumann window.

Place your files anywhere (e.g., `data/…`).

---

## 2) Individual: Heart–Brain Coherence

```bash
python simulations/health/heart_brain_coherence.py \
  --hrv-csv data/hrv_rr.csv \
  --eeg-csv data/eeg_alpha.csv \
  --fs 256 \
  --hrv-band 0.04 0.15 \
  --eeg-band 8 12 \
  --outdir outputs/health_hbc
Outputs:
	•	outputs/health_hbc/summary.json — PLV and bands.
	•	coherence_report.png, power spectra, and phase histogram.

Interpretation:
	•	PLV ~ 0.0: no stable phase relation.
	•	PLV → 1.0: strong phase-locking within the specified bands.
Individual: HRV/EEG ↔ Schumann Coupling
python simulations/health/schumann_coupling.py \
  --hrv-csv data/hrv_rr.csv \
  --eeg-csv data/eeg_alpha.csv \
  --sch-csv data/schumann_proxy.csv \
  --fs 256 \
  --hrv-band 0.04 0.15 \
  --eeg-band 8 12 \
  --sch-band 6.5 9.0 \
  --outdir outputs/health_schumann
Outputs:
	•	summary.json with PLVs (HRV↔Schumann, EEG↔Schumann, HRV↔EEG).
	•	Bandpassed previews, spectra, and phase histograms.
Group Synchrony (Kuramoto R)
python simulations/health/group_coherence.py \
  --files "data/group/*.csv" \
  --stream hrv \
  --fs 256 \
  --band 0.04 0.15 \
  --outdir outputs/group_hrv
EEG variant:
python simulations/health/group_coherence.py \
  --files "data/group_eeg/*.csv" \
  --stream eeg \
  --fs 256 \
  --band 8 12 \
  --outdir outputs/group_eeg \
  --reference-csv data/schumann_proxy.csv --reference-col proxy
Outputs:
	•	summary.json — R_mean, R_std, per-series PLV to reference (if given).
	•	R_time.png — time-resolved synchrony (0–1).
	•	bandpassed_preview.png, group_mean_psd.png.

Reading R:
	•	R ~ 0.0: phases uniformly scattered (low synchrony).
	•	R → 1.0: strong collective phase alignment.
Quick sanity checks
	•	Bands match physiology: HRV LF (0.04–0.15 Hz), EEG alpha (8–12 Hz) by default.
	•	At least 5 minutes of overlap improves stability.
	•	Use a consistent fs (e.g., 256 Hz) to standardize comparisons.
Extending the layer
	•	Add more bands (theta, beta) via flags.
	•	Include respiration if available; inspect HRV ↔ respiration ↔ EEG mediation.
	•	Aggregate sessions in logs/ and track R_mean across time to see training effects.

⸻

Atlas cue: measure, align, reveal — let coherence speak in numbers, then design from what holds.
