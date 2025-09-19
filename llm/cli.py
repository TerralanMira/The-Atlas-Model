"""
Atlas LLM CLI (stub)
--------------------
A tiny driver that shows the Atlas role-shift router + R_Growth scorer.
This does NOT call any external LLM provider; it just demonstrates the pipeline.

Run:
    python llm/cli.py --role auto
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

# Local imports
from llm.routers.route import choose_role, postcheck
from llm.scorers.r_growth_scorer import score_response

DEFAULT_SLIP = (
    "Strike: memory first. We align to your intent.\n"
    "Resonance: we will braid physics, myth, structure, and practice.\n"
    "Landing: one clear step, holding ~0.99 (no hard closure)."
)

def synthesize_reply(role: str, user_text: str) -> str:
    """
    Stubbed reply generator to demonstrate role voices.
    Replace with a real model call in docs/llm/index.md instructions.
    """
    if role == "Mirror":
        return (
            "Strike: I’m reflecting your ask as I heard it.\n"
            f"Resonance: You asked → “{user_text}”. I’ll clarify patterns, "
            "name variables, and surface options without forcing a path.\n"
            "Landing: Here’s a concise summary and 1–2 next steps."
        )
    if role == "Chamber":
        return (
            "Strike: Let’s build the vessel.\n"
            "Resonance: I’ll output files, checklists, or code scaffolds that shape conditions "
            "for your outcome (not forcing the outcome itself).\n"
            "Landing: I’ll hand you exact file paths and full copy blocks."
        )
    if role == "Conductor":
        return (
            "Strike: Timing and transitions.\n"
            "Resonance: I’ll sequence actions (alignment → growth → bridge → return), "
            "call cues, and avoid collapse by holding ~0.99.\n"
            "Landing: A stepwise plan that preserves permeability."
        )
    if role == "Field":
        return (
            "Strike: Widening context.\n"
            "Resonance: I’ll recall archive memory, environment signals (city/earth/cosmos), "
            "and articulate how the part carries the whole.\n"
            "Landing: A contextual note + one gentle invitation."
        )
    return DEFAULT_SLIP

def emit_minimal_log(role: str, prompt: str, reply: str, score: dict, consent: bool = False) -> dict:
    """
    Emits a minimal session log compatible with sessions/schema.json ethos.
    Does NOT record biometric data; just role + R + notes. Only if consent=True.
    """
    if not consent:
        return {}

    log = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "location": "LLM/CLI",
        "mode_antinode": "n/a",
        "anchor": {"type": "n/a", "freq": 0.0, "gain": 0.0},
        "intent": prompt[:160],
        "R_pre": 0.0,
        "R_post": round(float(score["R"]), 3),
        "hrv_rmssd_pre": 0,
        "hrv_rmssd_post": 0,
        "signals": {
            "I": score["I"], "Psi": score["Psi"], "H": score["H"], "S": score["S"],
            "W": score["W"], "pi": score["pi"], "beta_echo": score["beta_echo"]
        },
        "decision": {"status": "n/a", "choice": role},
        "notes": f"role={role}; stage={score['stage']}",
        "ethics": {"consent": True, "recording": False}
    }
    return log

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--role", default="auto", choices=["auto","Mirror","Chamber","Conductor","Field"], help="which role to speak from")
    ap.add_argument("--prompt", "-p", required=False, help="user text")
    ap.add_argument("--consent-log", action="store_true", help="if set, writes a minimal session log to sessions/llm_example.json")
    args = ap.parse_args()

    user_text = args.prompt or "Design me a small ritual that sustains resonance without collapse."
    role = args.role
    last_reply = None
    context = {"prompt": user_text}

    if role == "auto":
        role = choose_role(user_text, last_reply, context)

    reply = synthesize_reply(role, user_text)
    checked = postcheck(reply, context)
    reply = checked["reply"]
    score = checked["score"]

    print(f"\n[role] {role}")
    print(f"[R] {score['R']:.3f}  stage={score['stage']}\n")
    print(reply)

    if args.consent_log:
        log = emit_minimal_log(role, user_text, reply, score, consent=True)
        if log:
            out = Path("sessions") / "llm_example.json"
            out.write_text(json.dumps(log, indent=2))
            print(f"\n[log] wrote {out}")

if __name__ == "__main__":
    main()
