# dashboard/dashboard.py

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from algorithms.coherence_metrics import global_coherence, phase_entropy
from sims.multi_scale_kuramoto import simulate_kuramoto

st.set_page_config(page_title="Atlas Dashboard", layout="wide")

st.title("🌌 Atlas Model Dashboard")
st.markdown("Real-time view into coherence, resonance, and emergent patterns.")

# --- Sidebar controls ---
st.sidebar.header("Simulation Controls")
N = st.sidebar.slider("Number of oscillators", 50, 500, 200, step=50)
timesteps = st.sidebar.slider("Timesteps", 500, 5000, 2000, step=500)
K = st.sidebar.slider("Coupling Strength (K)", 0.0, 5.0, 2.0, step=0.1)
noise = st.sidebar.slider("Noise Level", 0.0, 1.0, 0.1, step=0.05)
seed = st.sidebar.number_input("Random Seed", min_value=0, value=42)

# --- Run simulation ---
if st.sidebar.button("Run Simulation"):
    st.subheader("Simulation Results")

    phases = simulate_kuramoto(N=N, timesteps=timesteps, K=K, noise=noise, seed=seed)

    # Compute metrics
    coherence = global_coherence(phases)
    entropy = phase_entropy(phases)

    st.metric("Global Coherence", f"{coherence:.3f}")
    st.metric("Phase Entropy", f"{entropy:.3f}")

    # Plot phases
    fig, ax = plt.subplots(figsize=(10, 4))
    for i in range(min(20, N)):  # only plot first 20 for clarity
        ax.plot(phases[i], alpha=0.7)
    ax.set_title("Oscillator Phase Trajectories")
    ax.set_xlabel("Time")
    ax.set_ylabel("Phase")
    st.pyplot(fig)

    # Distribution snapshot
    st.subheader("Phase Distribution")
    fig2, ax2 = plt.subplots(figsize=(6, 6))
    snapshot = phases[:, -1]
    ax2.hist(snapshot, bins=30, density=True, alpha=0.7)
    ax2.set_title("Final Phase Distribution")
    st.pyplot(fig2)

else:
    st.info("Adjust parameters and click **Run Simulation** to begin.")
  streamlit run dashboard/dashboard.py
