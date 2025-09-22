#!/usr/bin/env python3
"""
Scaffold all docs referenced by mkdocs.yml (as per our current navigation plan).

- Creates missing directories and files under docs/
- Writes a minimal, consistent header and scaffolded sections
- Is idempotent: existing files are left untouched

Usage (from repo root):
  python scripts/scaffold_docs.py
"""

from pathlib import Path
from datetime import datetime

# --- NAV MAP (kept in sync with mkdocs.yml) ---
NAV = {
    "index.md":                         "The Atlas Model — Overview",
    "dashboard.md":                     "Dashboard — Seeing the Pulse",
    "integration.md":                   "Integration — Weaving the Whole",

    # Resonant Reality
    "resonant_reality/overview.md":     "Resonant Reality — Overview",
    "resonant_reality/layers.md":       "Resonant Reality — Layers",
    "resonant_reality/harmonics.md":    "Resonant Reality — Harmonics",

    # Awareness & Coherence
    "awareness_coherence/awareness.md": "Awareness — The Human Loop",
    "awareness_coherence/coherence.md": "Coherence — Holding Shape",

    # Field Layers
    "field_layers.md":                  "Field Layers — Map",
    "field_layers/water.md":            "Water — Adaptive Flow",
    "field_layers/air.md":              "Air — Information & Breath",
    "field_layers/plasma.md":           "Fire & Plasma — Ignition",
    "field_layers/crystals.md":         "Crystals — Memory of Flow",

    # Field Applications
    "field_applications/healing.md":        "Applications — Healing",
    "field_applications/communication.md":  "Applications — Communication",
    "field_applications/energy.md":         "Applications — Energy Systems",
    "field_applications/simulations.md":    "Applications — Simulations",

    # Algorithms
    "algorithms/overview.md":           "Algorithms — The Weave Beneath",
    "algorithms/self_learning.md":      "Self-Learning Networks (Water/Air)",
    "algorithms/water_air.md":          "Water-Air Dynamics — Details",
    "algorithms/plasma.md":             "Plasma — Field Intelligence",
    "algorithms/crystals.md":           "Crystals — Field-Coupled Growth",
    "algorithms/simulations.md":        "Simulations — Index",

    # Seeds
    "seeds/origins.md":                 "Seed 1 — Origins",
    "seeds/coherence.md":               "Seed 2 — Coherence",
    "seeds/expansion.md":               "Seed 3 — Expansion",
    "seeds/applications.md":            "Seed 4 — Applications",
    "seeds/future.md":                  "Seed 5 — Future",

    # Books
    "books/book1.md":                   "Book I",
    "books/book2.md":                   "Book II",
    "books/book3.md":                   "Book III",

    # Exports (curated lessons, not raw chats)
    "exports/models.md":                "Exports — Models (Distilled)",
    "exports/simulations.md":           "Exports — Simulations (Distilled)",
    "exports/visuals.md":               "Exports — Visuals (Distilled)",

    # Sims docs (tie code to usage)
    "sims/atlas_pulse.md":              "Atlas Pulse — Orchestrated Coherence",
    "sims/crystal_demo.md":             "Crystal Demo — Structure as Memory",
}

HEADER_TMPL = """# {title}

> Generated scaffold • {date}

_This page is scaffolded to secure navigation. Replace this notice when you flesh out the whole._

## Context
- Where it sits in the whole:
  - Upstream: {upstream}
  - Downstream: {downstream}

## Essence
- Purpose of this layer/page in one or two sentences.

## Hooks
- Links to code: {code_links}
- Links to related docs: {related_docs}
"""

# Minimal, hand-rolled context hints for a few key pages
CONTEXT_HINTS = {
    "integration.md": {
        "upstream": "Algorithms, Field Layers, Awareness",
        "downstream": "Dashboard, Applications",
        "code_links": "`algorithms/atlas_orchestrator.py`",
        "related_docs": "`docs/sims/atlas_pulse.md`",
    },
    "sims/atlas_pulse.md": {
        "upstream": "Integration",
        "downstream": "Dashboard",
        "code_links": "`sims/atlas_pulse_demo.py`",
        "related_docs": "`integration.md`, `algorithms/overview.md`",
    },
    "sims/crystal_demo.md": {
        "upstream": "Algorithms/Crystals",
        "downstream": "Field Layers/Crystals",
        "code_links": "`sims/crystal_demo.py`, `algorithms/crystal_growth.py`",
        "related_docs": "`algorithms/simulations.md`, `field_layers/crystals.md`",
    },
}

def write_if_missing(path: Path, title: str):
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    key = str(path.relative_to(DOCS_ROOT)).replace("\\", "/")
    hints = CONTEXT_HINTS.get(key, {
        "upstream": "—",
        "downstream": "—",
        "code_links": "—",
        "related_docs": "—",
    })
    text = HEADER_TMPL.format(
        title=title,
        date=datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        upstream=hints["upstream"],
        downstream=hints["downstream"],
        code_links=hints["code_links"],
        related_docs=hints["related_docs"],
    )
    path.write_text(text, encoding="utf-8")
    return True

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = REPO_ROOT / "docs"

def main():
    created = []
    for rel, title in NAV.items():
        p = DOCS_ROOT / rel
        if write_if_missing(p, title):
            created.append(rel)
    if created:
        print("Scaffolded pages:")
        for c in created:
            print(" - docs/" + c)
    else:
        print("All referenced pages already exist. Nothing to scaffold.")

if __name__ == "__main__":
    main()
