#!/usr/bin/env python3
"""
scripts/generate_all_dashboards.py
Builds all static dashboard artifacts in one go.
"""

from pathlib import Path
from dashboard.page_fields import build_fields_page
from dashboard.page_pulse import build_pulse_page

OUT_DIR = Path("docs/assets/dashboard")

if __name__ == "__main__":
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fields_path = OUT_DIR / "fields_page.png"
    pulse_path = OUT_DIR / "pulse_page.png"

    build_fields_page(out_path=fields_path)
    build_pulse_page(out_path=pulse_path)

    print("Wrote:")
    print(" ", fields_path)
    print(" ", pulse_path)
