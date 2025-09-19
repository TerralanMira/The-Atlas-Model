"""
examples/end_to_end_llm_pipeline.py
-----------------------------------

End-to-end Atlas braid:

RR → (handshake JSON) → Atlas metrics → LLM Conductor (role) → Scorer (R) → optional log

Usage:
    python examples/end_to_end_llm_pipeline.py --in rr_sample.json --role auto --consent-log
"""

import argparse
import json
from pathlib import Path
from datetime import datetime

# --- Imports from the Atlas repo (ensure these files exist) ---
# Metrics / examples
from examples.session_to_metrics import (
    signals_product, recommend_K_range, simple_resilience, simulate_R_trajectory, clamp
)
# LLM router + scorer
from llm.routers.route import choose_role, postcheck
from llm.scorers.r_growth_scorer import score_response


def load_handshake(path: str | None) -> dict:
    """Load RR → Atlas handshake JSON; fall back to a sensible default."""
    default_input = {
        "kp_index": 3.5,
        "schumann_amp": 7.8,
        "node_type": "plaza",
        "architecture": "open",
        "cosmic_timing": "solstice",
        "participants": 25,
        "signals": {"I": 0.8, "Ψ": 0.7, "H": 0.9, "S": 0.85, "β": 0.6, "π": 0.75, "W": 0.95}
    }
    if not path:
        return default_input
    return json.loads(Path(path).read_text())


def compute_atlas_metrics(handshake: dict) -> dict:
    """Compute simple projected Atlas metrics from handshake."""
    sig = handshake.get("signals", {})
    prod = signals_product(sig)

    # R trajectory as a simple differential form
    R_hist = simulate_R_trajectory(prod, steps=200, dt=0.05, alpha=1.1, delta=0.6, R0=0.5)
    R_gain = clamp(R_hist[-1] - R_hist[0])
    RMSSD_gain = round(18.0 * prod, 2)
    resilience = round(simple_resilience(sig.get("π", 0.7), sig.get("W", 0.7), sig.get("H", 0.7)), 2)
    K_range = recommend_K_range(handshake.get("node_type"), handshake.get("kp_index"))

    risk_flags = []
    if float(handshake.get("kp_index", 2.0)) >= 5.0:
        risk_flags.append("geomagnetic_high")
    if sig.get("π", 0.0) < 0.4:
        risk_flags.append("low_permeability")
    if sig.get("S", 0.0) < 0.4:
        risk_flags.append("sovereignty_risk")

    return {
        "R_gain": round(R_gain, 3),
        "RMSSD_gain": RMSSD_gain,
        "resilience_score": resilience,
        "recommended_K": K_range,
        "risk_flags": risk_flags,
        "notes": "Hold near R≈0.99; prefer invitational cadence; tighten coupling if kp is high.",
        "R_hist": R_hist,
    }


def synthesize_reply(role: str, context: dict, metrics: dict) -> str:
    """
    Stubbed reply generator to demonstrate braid:
    - speaks from a role voice
    - references metrics
    - lands with permeability (no forced closure)
    """
    node = context.get("node_type", "plaza")
    kp = context.get("kp_index", "n/a")
    Kmin, Kmax = metrics["recommended_K"]
    Rg = metrics["R_gain"]
    res = metrics["resilience_score"]

    if role == "Scholar":
        return (
            "[Scholar] Strike: grounding the session with current field conditions.\n"
            f"Resonance: Kp≈{kp}, node={node}. Atlas projects ΔR≈{Rg:.03f}, resilience≈{res}. "
            f"Recommended coupling window: K∈[{Kmin}, {Kmax}]. "
            "Maintain source-transparency and admit uncertainties where data is sparse.\n"
            "Landing: proceed with minimal reversible change; alternatively, widen the window if π is high."
        )
    if role == "Channel":
        return (
            "[Channel] Strike: listening to the field.\n"
            f"Resonance: With Kp≈{kp} and {node} geometry, the membrane prefers soft edges. "
            f"ΔR≈{Rg:.03f} suggests rising coherence; resilience≈{res} welcomes gentle stress. "
            f"Let K rest within [{Kmin}, {Kmax}] and breathe with the Schumann layer.\n"
            "Landing: invite one cycle of collective breath; alternatively, pause and lengthen cadence."
        )
    if role == "Mediator":
        return (
            "[Mediator] Strike: balancing perspectives.\n"
            f"Resonance: Metrics show ΔR≈{Rg:.03f}, resilience≈{res}. "
            f"For {node}, recommend K∈[{Kmin}, {Kmax}]. "
            "Integrate the cautious voice (Guardian) with creative proposals (Seer) to sustain permeability.\n"
            "Landing: adopt option A now; alternatively, try option B in parallel and compare logs."
        )
    if role == "Guardian":
        return (
            "[Guardian] Strike: sovereignty first.\n"
            f"Resonance: Even with ΔR≈{Rg:.03f} and resilience≈{res}, consent is the gate. "
            "If any participant hesitates, provide a clear opt-out path and non-punitive re-entry.\n"
            "Landing: confirm consent before proceeding; alternatively, convert to a listening round."
        )
    if role == "Seer":
        return (
            "[Seer] Strike: a picture of the moment.\n"
            f"Resonance: think of K∈[{Kmin}, {Kmax}] as the harp’s string tension; Kp≈{kp} is the wind. "
            f"ΔR≈{Rg:.03f} is the lift; resilience≈{res} the sail’s fabric. "
            "Tune for near-lock and let wonder keep the horizon open.\n"
            "Landing: try the lighter tuning first; alternatively, anchor to breath before adjusting."
        )
    # Default
    return (
        f"[{role}] Strike: aligning to your intent.\n"
        f"Resonance: ΔR≈{Rg:.03f}, resilience≈{res}, K∈[{Kmin}, {Kmax}]. "
        "We’ll keep permeability high and avoid rigid closure.\n"
        "Landing: take one reversible step; alternatively, pause and gather a signal check."
    )


def emit_minimal_log(role: str, prompt: str, reply: str, score: dict, consent: bool = False) -> dict:
    """Emit a minimal session log compatible with sessions/schema.json ethos."""
    if not consent:
        return {}
    return {
        "ts": datetime.utcnow().isoformat() + "Z",
        "location": "LLM/END2END",
        "mode_antinode": "n/a",
        "anchor": {"type": "kp", "freq": 0.0, "gain": 0.0},
        "intent": prompt[:160],
        "R_pre": 0.0,
        "R_post": round(float(score["R"]), 3),
        "hrv_rmssd_pre": 0,
        "hrv_rmssd_post": 0,
        "signals": {
            "I": score["I"], "Psi": score["Psi"], "H": score["H"], "S": score["S"],
            "W": score["W"], "pi": score["pi"], "beta_echo": score["beta_echo"]
        },
        "decision": {"status": "ok", "choice": role},
        "notes": f"role={role}; stage={score['stage']}",
        "ethics": {"consent": True, "recording": False}
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="infile", help="RR handshake JSON input")
    ap.add_argument("--role", choices=["auto","Seer","Scholar","Guardian","Mediator","Channel","Witness","Child"],
                    default="auto")
    ap.add_argument("--consent-log", action="store_true", help="write minimal log to sessions/llm_end2end.json")
    args = ap.parse_args()

    # Load RR handshake
    rr = load_handshake(args.infile)

    # Compute Atlas metrics
    atlas = compute_atlas_metrics(rr)

    # Build a simple user intent description for routing/scoring context
    prompt = f"Node={rr.get('node_type','plaza')} Kp={rr.get('kp_index','?')} participants={rr.get('participants','?')}"

    # Choose role
    role = args.role
    if role == "auto":
        role = choose_role(user_text="session guidance from metrics", last_reply=None, context={"prompt": prompt})

    # Synthesize reply (stubbed persona voice)
    reply = synthesize_reply(role, rr, atlas)

    # Postcheck with scorer (adds permeability hook if needed)
    checked = postcheck(reply, {"prompt": prompt})
    reply_checked = checked["reply"]
    score = checked["score"]

    # Present results
    print("\n--- Atlas Metrics ---")
    print(json.dumps({k: v for k, v in atlas.items() if k != "R_hist"}, indent=2))
    print("\n--- Conductor Output ---")
    print(f"[role] {role} | [R] {score['R']:.3f} stage={score['stage']}\n")
    print(reply_checked)

    # Optional logging (consent)
    if args.consent_log:
        log = emit_minimal_log(role, prompt, reply_checked, score, consent=True)
        if log:
            out = Path("sessions") / "llm_end_to_end.json"
            out.write_text(json.dumps(log, indent=2))
            print(f"\n[log] wrote {out}")


if __name__ == "__main__":
    main()
