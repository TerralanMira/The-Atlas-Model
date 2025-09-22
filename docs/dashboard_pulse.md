# Dashboard — Ouroboric Pulse

The Pulse page shows the **full cycle** at a glance:
- **Pulse:** the orchestrated `atlas_coherence` time series.
- **Layers:** normalized contribution across Water, Air, Plasma, Crystal.
- **Thresholds:** plasma ignition/arc sketch.
- **Stabilization:** crystal lattice snapshot.

## Generate

From repo root:

```bash
python -m dashboard.page_pulse \
  --series logs/atlas_pulse/atlas_pulse_series.csv \
  --layers logs/atlas_pulse/atlas_pulse_layers.json \
  --out docs/assets/dashboard/pulse_page.png
If logs are missing, synthetic fallbacks will render so you can see the layout.

View

Open the generated image:
docs/assets/dashboard/pulse_page.png
