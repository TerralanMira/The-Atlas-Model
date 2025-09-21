#!/usr/bin/env python3
# dashboard/dashboard.py
#
# Atlas Resonant Dashboard — Layer Overlays
# Reads sim CSV logs and renders multi-layer resonance overlays:
#   Individual (Δ, Φ) • Relational (C, cross_sync) • Collective (R_total)
#   Planetary (rolling field stability) • Cosmic (bounded composite)
#
# Design goal: "show, not tell" — each layer overlays onto the others;
# the whole breathes through every part.

import os
import glob
import math
import json
import numpy as np
import pandas as pd

# Streamlit + Matplotlib (no custom styles/colors required)
import streamlit as st
import matplotlib.pyplot as plt

# --- Helpers ------------------------------------------------------------------

REQUIRED_COLS = [
    "step","t","R_total","cross_sync","drift","C","Delta","Phi",
    "ready","choice_score","offer_two_paths","consent_to_log"
]

def load_logs(pattern: str = "logs/*.csv") -> dict:
    files = sorted(glob.glob(pattern))
    runs = {}
    for f in files:
        try:
            df = pd.read_csv(f)
            # tolerate older headers by mapping
            if "R" in df.columns and "R_total" not in df.columns:
                df = df.rename(columns={"R": "R_total"})
            missing = [c for c in REQUIRED_COLS if c not in df.columns]
            if missing:
                # gracefully skip; show a small note later
                runs[f] = {"df": df, "ok": False, "missing": missing}
            else:
                runs[f] = {"df": df, "ok": True, "missing": []}
        except Exception as e:
            runs[f] = {"df": None, "ok": False, "missing": [f"error: {e}"]}
    return runs

def norm01(x):
    if not len(x):
        return 0.0
    x = np.array(x, dtype=float)
    if np.all(np.isnan(x)):
        return 0.0
    x = np.nan_to_num(x, nan=np.nanmean(x))
    lo, hi = np.nanmin(x), np.nanmax(x)
    if hi - lo < 1e-12:
        return 0.0
    return float((x[-1] - lo) / (hi - lo))

def rolling_mean(y, w=50):
    if w <= 1:
        return y
    s = pd.Series(y)
    return s.rolling(window=w, min_periods=max(1, w//4)).mean().to_numpy()

def bounded_product(values, eps=1e-9):
    v = [max(0.0, min(1.0, float(x))) for x in values]
    prod = 1.0
    for x in v:
        prod *= max(eps, x)
    return float(prod)

def overlay_scores(df: pd.DataFrame, roll: int = 50) -> dict:
    """
    Derive per-layer overlay scores (0..1) from the CSV columns.
    """
    R = df["R_total"].to_numpy()
    X = df["cross_sync"].to_numpy()
    D = df["Delta"].to_numpy()
    P = df["Phi"].to_numpy()
    drift = df["drift"].to_numpy()

    # Smooth versions (Planetary stability layer)
    Rm = rolling_mean(R, roll)
    Xm = rolling_mean(X, roll)
    Dm = rolling_mean(D, roll)
    Pm = rolling_mean(P, roll)
    drift_m = rolling_mean(drift, roll)

    # INDIVIDUAL: diversity + flow retained (Δ, Φ)
    indiv = float(0.5 * (Dm[-1] + Pm[-1])) if len(Dm) else 0.0

    # RELATIONAL: bridges & local coherence (C + cross_sync)
    if "C" in df.columns:
        Ccol = df["C"].to_numpy()
        Cm = rolling_mean(Ccol, roll)
        rel = float(0.5 * (Cm[-1] + Xm[-1])) if len(Cm) else float(Xm[-1])
    else:
        rel = float(Xm[-1]) if len(Xm) else 0.0

    # COLLECTIVE: global coherence (R_total), but avoid over-lock (punish ultra-low drift)
    coll = float(Rm[-1]) if len(Rm) else 0.0
    if len(drift_m) and drift_m[-1] < 0.02 and coll > 0.8:
        coll *= 0.9  # gentle penalty for clamp risk

    # PLANETARY: stability of the field (low volatility across signals)
    # Invert average rolling variance to get a 0..1 stability score
    def inv_var(a):
        if len(a) < 5:
            return 0.0
        v = float(np.nanvar(a[-min(200, len(a)):]))
        return 1.0 / (1.0 + v)  # bounded, higher = more stable
    plan = float(np.mean([inv_var(Rm), inv_var(Xm), inv_var(Dm), inv_var(Pm)]))

    # COSMIC: bounded product of the four
    cosmic = bounded_product([indiv, rel, coll, plan])

    return {
        "individual": max(0.0, min(1.0, indiv)),
        "relational": max(0.0, min(1.0, rel)),
        "collective": max(0.0, min(1.0, coll)),
        "planetary": max(0.0, min(1.0, plan)),
        "cosmic": max(0.0, min(1.0, cosmic)),
        "series": {
            "t": df["t"].to_numpy() if "t" in df.columns else np.arange(len(R)),
            "R": R, "R_smooth": Rm,
            "X": X, "X_smooth": Xm,
            "D": D, "D_smooth": Dm,
            "P": P, "P_smooth": Pm,
            "drift": drift, "drift_smooth": drift_m
        }
    }

def gauge(ax, value: float, title: str):
    ax.set_title(title)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.barh([0.5], [max(0.0, min(1.0, value))], height=0.3)
    ax.set_yticks([])
    ax.set_xticks([0, 0.5, 1.0])
    ax.set_xlabel("0 … 1")

# --- UI -----------------------------------------------------------------------

st.set_page_config(page_title="Atlas Resonant Dashboard", layout="wide")
st.title("🌌 Atlas Resonant Dashboard — Layer Overlays")
st.markdown(
    "Overlaying **Individual → Relational → Collective → Planetary → Cosmic** signals "
    "so the whole breathes through every part."
)

with st.sidebar:
    st.header("Source")
    path_hint = st.text_input("Log glob pattern", "logs/*.csv")
    roll = st.slider("Rolling window (stability)", 10, 200, 50, step=10)
    st.caption("Tip: even if you’re not running sims yet, this design shows where the hum will flow.")

runs = load_logs(path_hint)
ok_runs = {k: v for k, v in runs.items() if v["ok"]}
bad_runs = {k: v for k, v in runs.items() if not v["ok"]}

if not runs:
    st.info("No logs found yet. Design-first view is loaded — place CSVs in `logs/` when ready.")
else:
    if bad_runs:
        with st.expander("Some logs were skipped (missing columns or errors)"):
            for k, meta in bad_runs.items():
                st.write(f"- {os.path.basename(k)} → missing {meta['missing']}")

if not ok_runs:
    st.stop()

# Select a run
sel = st.selectbox("Select a run", list(ok_runs.keys()), index=len(ok_runs)-1, format_func=os.path.basename)
df = ok_runs[sel]["df"]

# Compute overlays
ov = overlay_scores(df, roll=roll)
series = ov["series"]

# --- Top gauges ---------------------------------------------------------------

colA, colB, colC, colD, colE = st.columns(5)
with colA:
    fig, ax = plt.subplots()
    gauge(ax, ov["individual"], "Individual (Δ·Φ)")
    st.pyplot(fig)
with colB:
    fig, ax = plt.subplots()
    gauge(ax, ov["relational"], "Relational (C·cross)")
    st.pyplot(fig)
with colC:
    fig, ax = plt.subplots()
    gauge(ax, ov["collective"], "Collective (R_total w/ clamp check)")
    st.pyplot(fig)
with colD:
    fig, ax = plt.subplots()
    gauge(ax, ov["planetary"], "Planetary (stability)")
    st.pyplot(fig)
with colE:
    fig, ax = plt.subplots()
    gauge(ax, ov["cosmic"], "Cosmic (bounded product)")
    st.pyplot(fig)

st.markdown("---")

# --- Time series overlays -----------------------------------------------------

st.subheader("Field Signals Over Time")

# Row 1: R_total + smooth
fig1, ax1 = plt.subplots()
ax1.plot(series["t"], series["R"], label="R_total")
ax1.plot(series["t"], series["R_smooth"], label="R_total (smooth)")
ax1.set_title("Global Coherence (R)")
ax1.set_xlabel("t")
ax1.set_ylabel("level")
ax1.legend()
st.pyplot(fig1)

# Row 2: cross_sync / C
fig2, ax2 = plt.subplots()
ax2.plot(series["t"], series["X"], label="cross_sync")
if "C" in df.columns:
    ax2.plot(series["t"], df["C"].to_numpy(), label="C")
ax2.plot(series["t"], series["X_smooth"], label="cross_sync (smooth)")
ax2.set_title("Relational Bridges (cross/C)")
ax2.set_xlabel("t")
ax2.set_ylabel("level")
ax2.legend()
st.pyplot(fig2)

# Row 3: Delta and Phi
fig3, ax3 = plt.subplots()
ax3.plot(series["t"], series["D"], label="Delta (diversity)")
ax3.plot(series["t"], series["P"], label="Phi (flow smoothness)")
ax3.plot(series["t"], series["D_smooth"], label="Delta (smooth)")
ax3.plot(series["t"], series["P_smooth"], label="Phi (smooth)")
ax3.set_title("Individual Signals (Δ, Φ)")
ax3.set_xlabel("t")
ax3.set_ylabel("level")
ax3.legend()
st.pyplot(fig3)

# Row 4: Drift (for clamp awareness)
fig4, ax4 = plt.subplots()
ax4.plot(series["t"], series["drift"], label="drift")
ax4.plot(series["t"], series["drift_smooth"], label="drift (smooth)")
ax4.set_title("Drift (collapse/clamp awareness)")
ax4.set_xlabel("t")
ax4.set_ylabel("speed")
ax4.legend()
st.pyplot(fig4)

st.markdown("---")

# --- Narrative overlay (design-first) ----------------------------------------

st.subheader("Narrative Overlay — How the Layers Breathe")
st.write("""
- **Individual** rises when *diversity (Δ)* and *flow (Φ)* are both alive.
- **Relational** strengthens as *bridges (cross_sync)* and *local coherence (C)* align.
- **Collective** deepens as **R_total** lifts — but beware clamp when drift → 0.
- **Planetary** settles as volatility lowers across smoothed signals.
- **Cosmic** is a bounded product of all four — a humility check: any collapsed petal dims the whole.
""")

st.caption(
    "This dashboard is a design instrument. Even without running code, "
    "it shows where the hum flows and how the whole breathes through each layer."
)
