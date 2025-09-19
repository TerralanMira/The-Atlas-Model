"""
OpenAI provider shim (optional).

Reads OPENAI_API_KEY from env; shows how to slot Atlas persona/role prompts.
Keeps secrets out of the repo. Replace the '...' with your chosen model name.

Usage (pseudocode):
    from llm.providers.openai_stub import chat
    reply = chat(system=persona, user=prompt)
"""

import os
from typing import Optional

try:
    import openai
except Exception:
    openai = None


def chat(system: str, user: str, model: str = "gpt-4o-mini") -> str:
    """
    Minimal chat helper. Requires 'openai' package and OPENAI_API_KEY.
    """
    if openai is None:
        raise RuntimeError("Install openai: pip install openai")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Set OPENAI_API_KEY in your environment.")
    openai.api_key = api_key

    # OpenAI Chat Completions-style call (update if API changes)
    resp = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.7,
    )
    return resp["choices"][0]["message"]["content"].strip()
